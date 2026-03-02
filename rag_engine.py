"""
RAG-based SHL Assessment Recommendation Engine
"""
import json
import os
import numpy as np
import pickle
from typing import List, Dict, Optional
import requests
import re

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
CATALOG_FILE = "shl_catalog_enriched.json"
EMBEDDINGS_FILE = "shl_embeddings.pkl"

_model = None

def get_embedding_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        print("Loading embedding model...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        print("Model loaded!")
    return _model

def embed_texts(texts: List[str]) -> np.ndarray:
    model = get_embedding_model()
    return model.encode(texts, show_progress_bar=False, normalize_embeddings=True)

class SHLVectorStore:
    def __init__(self):
        self.assessments = []
        self.embeddings = None
        self.index = None

    def build(self, assessments: List[Dict]):
        import faiss
        self.assessments = assessments
        texts = [self._assessment_to_text(a) for a in assessments]
        print(f"Building embeddings for {len(texts)} assessments...")
        self.embeddings = embed_texts(texts)
        dim = self.embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(self.embeddings.astype(np.float32))
        print("Vector store built!")

    def _assessment_to_text(self, a: Dict) -> str:
        test_types = ", ".join(a.get("test_type", []))
        return f"{a.get('name','')}. {a.get('description','')}. Test types: {test_types}. Duration: {a.get('duration','varies')} minutes."

    def search(self, query: str, top_k: int = 20) -> List[Dict]:
        import faiss
        q_emb = embed_texts([query]).astype(np.float32)
        scores, indices = self.index.search(q_emb, min(top_k, len(self.assessments)))
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.assessments):
                a = self.assessments[idx].copy()
                a["similarity_score"] = float(score)
                results.append(a)
        return results

    def save(self, path: str = EMBEDDINGS_FILE):
        import faiss
        with open(path, "wb") as f:
            pickle.dump({"assessments": self.assessments, "embeddings": self.embeddings}, f)
        faiss.write_index(self.index, path + ".faiss")
        print(f"Saved vector store to {path}")

    def load(self, path: str = EMBEDDINGS_FILE):
        import faiss
        with open(path, "rb") as f:
            data = pickle.load(f)
        self.assessments = data["assessments"]
        self.embeddings = data["embeddings"]
        self.index = faiss.read_index(path + ".faiss")
        print(f"Loaded vector store with {len(self.assessments)} assessments")

def call_gemini(prompt: str, max_tokens: int = 1000) -> str:
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": max_tokens, "topP": 0.8}
    }
    try:
        resp = requests.post(f"{GEMINI_URL}?key={GEMINI_API_KEY}", headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"Gemini API error: {e}")
        return ""

def extract_duration_constraint(query: str) -> Optional[int]:
    patterns = [
        r"(?:within|max|maximum|under|less than|no more than|at most|not more than)\s*(\d+)\s*(?:min|minute|mins|minutes|hr|hour|hrs|hours)",
        r"(\d+)\s*(?:min|minute|mins|minutes|hr|hour|hrs|hours)\s*(?:long|max|limit|duration)",
        r"(\d+)[-\s](?:min|minute|hr|hour)",
    ]
    query_lower = query.lower()
    for pattern in patterns:
        match = re.search(pattern, query_lower)
        if match:
            val = int(match.group(1))
            if "hr" in match.group(0).lower() or "hour" in match.group(0).lower():
                val *= 60
            return val
    return None

def rerank_with_gemini(query: str, candidates: List[Dict], max_results: int = 10) -> List[Dict]:
    candidate_text = ""
    for i, c in enumerate(candidates[:25]):
        types = ", ".join(c.get("test_type", ["Unknown"]))
        candidate_text += f"{i+1}. {c['name']} | Types: {types} | Duration: {c.get('duration','unknown')} min | URL: {c['url']}\n"

    max_duration = extract_duration_constraint(query)
    duration_note = f"\nIMPORTANT: Only recommend assessments with duration <= {max_duration} minutes." if max_duration else ""

    prompt = f"""You are an expert HR assessment consultant for SHL. Select the BEST 5-10 assessments for this query.

HIRING QUERY:
{query}

CANDIDATE ASSESSMENTS:
{candidate_text}
{duration_note}

RULES:
1. Return 5-10 most relevant assessments
2. Balance technical AND soft skills if role needs both
3. Respect duration constraints strictly
4. Prioritize most relevant assessments

Respond with ONLY a JSON array like: [1, 3, 5, 7, 9]"""

    response = call_gemini(prompt)
    try:
        match = re.search(r'\[[\d,\s]+\]', response)
        if match:
            indices = json.loads(match.group())
            selected = []
            for idx in indices:
                if 1 <= idx <= len(candidates[:25]):
                    selected.append(candidates[idx - 1])
            return selected[:max_results]
    except Exception as e:
        print(f"Failed to parse Gemini response: {e}")
    return candidates[:max_results]

class SHLRecommendationEngine:
    def __init__(self):
        self.vector_store = SHLVectorStore()
        self.loaded = False

    def initialize(self, catalog_path: str = CATALOG_FILE):
        if os.path.exists(EMBEDDINGS_FILE) and os.path.exists(EMBEDDINGS_FILE + ".faiss"):
            print("Loading existing vector store...")
            self.vector_store.load()
            self.loaded = True
        elif os.path.exists(catalog_path):
            print("Building vector store from catalog...")
            with open(catalog_path) as f:
                assessments = json.load(f)
            self.vector_store.build(assessments)
            self.vector_store.save()
            self.loaded = True
        else:
            raise FileNotFoundError(f"No catalog found at {catalog_path}. Run scraper first!")

    def recommend(self, query: str, max_results: int = 10) -> List[Dict]:
        if not self.loaded:
            self.initialize()
        candidates = self.vector_store.search(query, top_k=30)
        if not candidates:
            return []
        max_duration = extract_duration_constraint(query)
        if max_duration:
            filtered = [c for c in candidates if c.get("duration") is None or c.get("duration", 9999) <= max_duration]
            if len(filtered) >= 5:
                candidates = filtered
        if GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
            selected = rerank_with_gemini(query, candidates, max_results)
        else:
            selected = candidates[:max_results]
        results = []
        for a in selected:
            results.append({
                "name": a.get("name", ""),
                "url": a.get("url", ""),
                "description": a.get("description", ""),
                "duration": a.get("duration", 30),
                "remote_support": a.get("remote_support", "Yes"),
                "adaptive_support": a.get("adaptive_support", "No"),
                "test_type": a.get("test_type", []),
            })
        return results

def recall_at_k(predicted_urls: List[str], relevant_urls: List[str], k: int = 10) -> float:
    if not relevant_urls:
        return 0.0
    def normalize_url(u):
        return u.rstrip("/").lower()
    pred_set = {normalize_url(u) for u in predicted_urls[:k]}
    relevant_set = {normalize_url(u) for u in relevant_urls}
    return len(pred_set & relevant_set) / len(relevant_set)

def evaluate_on_train_set(engine, train_data_path=None):
    import openpyxl
    train_data_path = train_data_path or "Gen_AI_Dataset.xlsx"
    wb = openpyxl.load_workbook(train_data_path)
    ws = wb["Train-Set"]
    query_map = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        query, url = row
        if query not in query_map:
            query_map[query] = []
        query_map[query].append(url)
    print(f"Evaluating on {len(query_map)} train queries...")
    recall_scores = []
    for query, relevant_urls in query_map.items():
        recommendations = engine.recommend(query, max_results=10)
        predicted_urls = [r["url"] for r in recommendations]
        score = recall_at_k(predicted_urls, relevant_urls, k=10)
        recall_scores.append(score)
        print(f"Query: {query[:80]}...")
        print(f"  Recall@10: {score:.3f}")
    mean_recall = np.mean(recall_scores) if recall_scores else 0
    print(f"\n=== Mean Recall@10: {mean_recall:.4f} ===")
    return mean_recall

if __name__ == "__main__":
    engine = SHLRecommendationEngine()
    engine.initialize()
    test_query = "I am hiring for Java developers who can also collaborate effectively with my business teams."
    results = engine.recommend(test_query)
    print(f"\nRecommendations for: {test_query[:80]}")
    for r in results:
        print(f"  - {r['name']}: {r['url']}")
