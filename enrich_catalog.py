"""
Catalog Enrichment Script
Fetches details (description, duration, test type) from each assessment's individual page
"""

import json
import time
import re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
}

TEST_TYPE_MAP = {
    "A": "Ability & Aptitude",
    "B": "Biodata & Situational Judgement",
    "C": "Competencies",
    "D": "Development & 360",
    "E": "Assessment Exercises",
    "K": "Knowledge & Skills",
    "P": "Personality & Behavior",
    "S": "Simulations"
}


def enrich_assessment(assessment: dict) -> dict:
    url = assessment.get("url", "")
    if not url:
        return assessment
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        
        meta_desc = soup.find("meta", {"name": "description"})
        if meta_desc:
            assessment["description"] = meta_desc.get("content", "")[:500]
        else:
            content = soup.find("div", class_=re.compile(r"content|description|overview|product", re.IGNORECASE))
            if content:
                assessment["description"] = content.get_text(strip=True)[:500]
        
        page_text = soup.get_text()
        
        duration_match = re.search(r"(\d+)\s*(?:min|minute)", page_text, re.IGNORECASE)
        if duration_match:
            assessment["duration"] = int(duration_match.group(1))
        
        test_types = []
        for letter, type_name in TEST_TYPE_MAP.items():
            if re.search(rf'\b{letter}\b', page_text) or type_name.lower() in page_text.lower():
                test_types.append(type_name)
        
        if test_types:
            assessment["test_type"] = test_types[:3]
        
        page_text_lower = page_text.lower()
        assessment["remote_support"] = "Yes" if "remote" in page_text_lower else "Yes"
        assessment["adaptive_support"] = "Yes" if "adaptive" in page_text_lower else "No"
        
    except Exception as e:
        print(f"  Error enriching {url}: {e}")
    
    return assessment


def enrich_catalog(input_file="shl_catalog_raw.json", output_file="shl_catalog_enriched.json"):
    with open(input_file) as f:
        assessments = json.load(f)
    
    print(f"Enriching {len(assessments)} assessments...")
    
    enriched = []
    for i, assessment in enumerate(assessments):
        print(f"[{i+1}/{len(assessments)}] {assessment.get('name', 'Unknown')[:60]}")
        enriched_a = enrich_assessment(assessment.copy())
        enriched.append(enriched_a)
        
        if (i + 1) % 50 == 0:
            with open(output_file, "w") as f:
                json.dump(enriched, f, indent=2)
            print(f"  Progress saved ({i+1} items)")
        
        time.sleep(0.3)
    
    with open(output_file, "w") as f:
        json.dump(enriched, f, indent=2)
    
    print(f"\nDone! Saved {len(enriched)} assessments to {output_file}")
    return enriched


if __name__ == "__main__":
    enrich_catalog()

