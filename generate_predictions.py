"""
Generate predictions on the test set and save as CSV
"""
import openpyxl
import csv
from rag_engine import SHLRecommendationEngine

def generate_predictions(
    data_path: str = "Gen_AI_Dataset.xlsx",
    output_file: str = "manikanta_pepakayala.csv"
):
    wb = openpyxl.load_workbook(data_path)
    ws = wb["Test-Set"]
    
    test_queries = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0]:
            test_queries.append(row[0])
    
    print(f"Found {len(test_queries)} test queries")
    
    engine = SHLRecommendationEngine()
    engine.initialize()
    
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
    
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["query", "assessment_url"])
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"\nSaved {len(rows)} predictions to {output_file}")
    return rows

if __name__ == "__main__":
    generate_predictions()