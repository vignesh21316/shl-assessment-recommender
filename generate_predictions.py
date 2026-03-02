"""
Generate predictions on the test set and save as CSV
Format: query, assessment_url
"""

import openpyxl
import csv
import os
from rag_engine import SHLRecommendationEngine

def generate_predictions(
    data_path: str = "/mnt/user-data/uploads/Gen_AI_Dataset.xlsx",
    output_file: str = "V S S V Manikanta_Pepakayala.csv"  # Change to your firstname_lastname.csv
):
    """Generate predictions for all test set queries."""
    
    # Load test queries
    wb = openpyxl.load_workbook(data_path)
    ws = wb["Test-Set"]
    
    test_queries = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0]:
            test_queries.append(row[0])
    
    print(f"Found {len(test_queries)} test queries")
    
    # Initialize engine
    engine = SHLRecommendationEngine()
    engine.initialize()
    
    # Generate predictions
    rows = []
    for i, query in enumerate(test_queries, 1):
        print(f"\n[{i}/{len(test_queries)}] Query: {query[:100]}...")
        
        recommendations = engine.recommend(query, max_results=10)
        
        for rec in recommendations:
            rows.append({
                "query": query,
                "assessment_url": rec["url"]
            })
        
        print(f"  Recommended {len(recommendations)} assessments")
    
    # Save to CSV
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["query", "assessment_url"])
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"\n✅ Saved {len(rows)} predictions to {output_file}")
    return rows


if __name__ == "__main__":
    # IMPORTANT: Change output file to firstname_lastname.csv format
    output = "tania_goyal.csv"  # Replace with your actual name
    generate_predictions(output_file=output)
