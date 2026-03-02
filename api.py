"""
FastAPI Backend for SHL Assessment Recommendation System
Endpoints:
  GET  /health       - Health check
  POST /recommend    - Get assessment recommendations
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import requests
from bs4 import BeautifulSoup
import re

from rag_engine import SHLRecommendationEngine

# ============================================================
# APP SETUP
# ============================================================
app = FastAPI(
    title="SHL Assessment Recommendation API",
    description="RAG-based API to recommend SHL assessments from job descriptions or natural language queries",
    version="1.0.0"
)

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engine once at startup
engine = SHLRecommendationEngine()

@app.on_event("startup")
async def startup_event():
    print("Initializing recommendation engine...")
    engine.initialize()
    print("Engine ready!")


# ============================================================
# MODELS
# ============================================================
class RecommendRequest(BaseModel):
    query: str


class AssessmentResult(BaseModel):
    url: str
    name: str
    adaptive_support: str
    description: str
    duration: int
    remote_support: str
    test_type: List[str]


class RecommendResponse(BaseModel):
    recommended_assessments: List[AssessmentResult]


# ============================================================
# ENDPOINTS
# ============================================================
@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/recommend", response_model=RecommendResponse)
def recommend_assessments(request: RecommendRequest):
    """
    Recommend SHL assessments based on a job description or natural language query.
    Also accepts a URL (will scrape the page text automatically).
    """
    query = request.query.strip()
    
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    # Check if query is a URL - scrape the page
    if query.startswith("http://") or query.startswith("https://"):
        try:
            query = scrape_url_text(query)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {str(e)}")
    
    # Get recommendations
    try:
        results = engine.recommend(query, max_results=10)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation error: {str(e)}")
    
    if not results:
        raise HTTPException(status_code=404, detail="No assessments found for the given query")
    
    # Format response
    assessments = []
    for r in results:
        assessments.append(AssessmentResult(
            url=r.get("url", ""),
            name=r.get("name", ""),
            adaptive_support=r.get("adaptive_support", "No"),
            description=r.get("description", ""),
            duration=int(r.get("duration") or 30),
            remote_support=r.get("remote_support", "Yes"),
            test_type=r.get("test_type", [])
        ))
    
    return RecommendResponse(recommended_assessments=assessments)


def scrape_url_text(url: str) -> str:
    """Scrape text content from a URL (for JD URLs)."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    }
    resp = requests.get(url, headers=headers, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    
    # Remove script and style elements
    for elem in soup(["script", "style", "nav", "footer", "header"]):
        elem.decompose()
    
    text = soup.get_text(separator=" ", strip=True)
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:3000]  # Limit to 3000 chars


# ============================================================
# RUN
# ============================================================
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
