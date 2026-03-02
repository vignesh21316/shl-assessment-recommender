"""
SHL Assessment Recommendation System - Web Frontend
Built with Streamlit
"""

import streamlit as st
import requests
import json
import pandas as pd

# ============================================================
# CONFIG
# ============================================================
API_URL = "https://shl-recommender-manikanta.onrender.com"  # Change to deployed API URL

st.set_page_config(
    page_title="SHL Assessment Recommender",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# STYLING
# ============================================================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d6a9f 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
    }
    .assessment-card {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        border-left: 4px solid #2d6a9f;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    .assessment-card:hover {
        transform: translateX(4px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.8em;
        font-weight: bold;
        margin-right: 5px;
        margin-bottom: 5px;
    }
    .badge-A { background: #dbeafe; color: #1e40af; }
    .badge-K { background: #d1fae5; color: #065f46; }
    .badge-P { background: #fce7f3; color: #9d174d; }
    .badge-C { background: #ede9fe; color: #5b21b6; }
    .badge-B { background: #fef3c7; color: #92400e; }
    .badge-E { background: #fee2e2; color: #991b1b; }
    .badge-S { background: #f0fdf4; color: #166534; }
    .badge-D { background: #f0f9ff; color: #0369a1; }
    .metric-box {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 0.8rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================
st.markdown("""
<div class="main-header">
    <h1>🎯 SHL Assessment Recommender</h1>
    <p style="font-size: 1.1em; opacity: 0.9;">
        AI-powered assessment recommendations using RAG technology.<br>
        Enter a job description, role query, or paste a JD URL to get started.
    </p>
</div>
""", unsafe_allow_html=True)


# ============================================================
# INPUT SECTION
# ============================================================
col1, col2 = st.columns([3, 1])

with col1:
    input_type = st.radio(
        "Input type:",
        ["Natural Language Query", "Job Description Text", "JD URL"],
        horizontal=True
    )

# Placeholders based on input type
placeholders = {
    "Natural Language Query": "e.g., I need to hire Java developers who can collaborate with business teams. Assessment should be under 40 minutes.",
    "Job Description Text": "Paste the full job description here...",
    "JD URL": "https://www.linkedin.com/jobs/view/..."
}

query_input = st.text_area(
    "Your query:",
    height=150,
    placeholder=placeholders[input_type],
    label_visibility="collapsed"
)

col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
with col_btn1:
    submit_btn = st.button("🔍 Get Recommendations", type="primary", use_container_width=True)
with col_btn2:
    clear_btn = st.button("Clear", use_container_width=True)

# Sample queries
with st.expander("💡 Try sample queries"):
    sample_queries = [
        "I am hiring for Java developers who can also collaborate effectively with my business teams. Looking for an assessment that can be completed in 40 minutes.",
        "Looking to hire mid-level professionals proficient in Python, SQL and JavaScript. Max duration 60 minutes.",
        "I want to hire a Senior Data Analyst with 5 years of experience in SQL, Excel and Python.",
        "Need to hire Customer Support executives expert in English communication.",
        "I am hiring for an analyst and want to screen using Cognitive and personality tests within 45 mins.",
    ]
    for i, q in enumerate(sample_queries):
        if st.button(f"Sample {i+1}", key=f"sample_{i}"):
            st.session_state["query"] = q
            st.rerun()

# Auto-fill from session state
if "query" in st.session_state and not query_input:
    query_input = st.session_state["query"]


# ============================================================
# RECOMMENDATION RESULTS
# ============================================================
def get_test_type_badge(test_type_str: str) -> str:
    """Generate HTML badge for test type."""
    type_map = {
        "Ability & Aptitude": ("A", "badge-A"),
        "Knowledge & Skills": ("K", "badge-K"),
        "Personality & Behavior": ("P", "badge-P"),
        "Personality & Behaviour": ("P", "badge-P"),
        "Competencies": ("C", "badge-C"),
        "Biodata & Situational Judgement": ("B", "badge-B"),
        "Assessment Exercises": ("E", "badge-E"),
        "Simulations": ("S", "badge-S"),
        "Development & 360": ("D", "badge-D"),
    }
    
    for type_name, (letter, css_class) in type_map.items():
        if type_name.lower() in test_type_str.lower():
            return f'<span class="badge {css_class}">{letter} {type_name}</span>'
    
    return f'<span class="badge badge-K">{test_type_str}</span>'


def display_results(results):
    """Display recommendation results."""
    if not results:
        st.warning("No recommendations found. Try a different query.")
        return
    
    st.success(f"✅ Found **{len(results)} recommended assessments**")
    
    # Summary stats
    col1, col2, col3, col4 = st.columns(4)
    durations = [r.get("duration", 0) for r in results if r.get("duration")]
    all_types = []
    for r in results:
        all_types.extend(r.get("test_type", []))
    
    with col1:
        st.markdown(f"""<div class="metric-box"><h3>{len(results)}</h3><p>Assessments</p></div>""", unsafe_allow_html=True)
    with col2:
        avg_dur = sum(durations) // len(durations) if durations else 0
        st.markdown(f"""<div class="metric-box"><h3>{avg_dur} min</h3><p>Avg Duration</p></div>""", unsafe_allow_html=True)
    with col3:
        unique_types = len(set(all_types))
        st.markdown(f"""<div class="metric-box"><h3>{unique_types}</h3><p>Test Types</p></div>""", unsafe_allow_html=True)
    with col4:
        remote = sum(1 for r in results if r.get("remote_support") == "Yes")
        st.markdown(f"""<div class="metric-box"><h3>{remote}/{len(results)}</h3><p>Remote Ready</p></div>""", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Individual cards
    for i, result in enumerate(results, 1):
        name = result.get("name", "Unknown Assessment")
        url = result.get("url", "#")
        description = result.get("description", "")
        duration = result.get("duration", "N/A")
        remote = result.get("remote_support", "N/A")
        adaptive = result.get("adaptive_support", "N/A")
        test_types = result.get("test_type", [])
        
        # Build type badges
        type_badges = " ".join([get_test_type_badge(t) for t in test_types])
        if not type_badges:
            type_badges = '<span class="badge badge-K">General</span>'
        
        st.markdown(f"""
        <div class="assessment-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <h4 style="margin: 0; color: #1e3a5f;">
                        {i}. <a href="{url}" target="_blank" style="color: #2d6a9f; text-decoration: none;">{name}</a>
                    </h4>
                    <p style="color: #666; margin: 0.4rem 0; font-size: 0.9em;">{description[:200] + '...' if len(description) > 200 else description}</p>
                    <div style="margin-top: 0.5rem;">{type_badges}</div>
                </div>
                <div style="text-align: right; min-width: 150px; padding-left: 1rem;">
                    <div style="font-size: 0.85em; color: #555;">
                        ⏱️ <strong>{duration} min</strong><br>
                        🌐 Remote: <strong>{remote}</strong><br>
                        🔄 Adaptive: <strong>{adaptive}</strong>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Download as CSV
    st.markdown("### 📥 Export Results")
    df = pd.DataFrame([{
        "Assessment Name": r.get("name"),
        "URL": r.get("url"),
        "Test Types": ", ".join(r.get("test_type", [])),
        "Duration (min)": r.get("duration"),
        "Remote Support": r.get("remote_support"),
        "Adaptive Support": r.get("adaptive_support"),
    } for r in results])
    
    st.dataframe(df, use_container_width=True)
    
    csv_data = df.to_csv(index=False)
    st.download_button(
        "⬇️ Download CSV",
        csv_data,
        file_name="shl_recommendations.csv",
        mime="text/csv"
    )


# ============================================================
# HANDLE SUBMISSION
# ============================================================
if submit_btn and query_input:
    with st.spinner("🔍 Analyzing query and finding best assessments..."):
        try:
            response = requests.post(
                f"{API_URL}/recommend",
                json={"query": query_input},
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("recommended_assessments", [])
                display_results(results)
            else:
                st.error(f"API Error {response.status_code}: {response.text}")
        
        except requests.ConnectionError:
            st.error("⚠️ Cannot connect to API. Make sure the FastAPI server is running!")
            st.code("Run: python api.py", language="bash")
        except Exception as e:
            st.error(f"Error: {str(e)}")

elif submit_btn and not query_input:
    st.warning("Please enter a query first!")


# ============================================================
# SIDEBAR - API Info
# ============================================================
with st.sidebar:
    st.markdown("### ℹ️ About")
    st.markdown("""
    This app uses **RAG (Retrieval-Augmented Generation)** to recommend SHL assessments.
    
    **Pipeline:**
    1. 🕷️ Scrape SHL catalog (377+ assessments)
    2. 🔢 Create embeddings with sentence-transformers
    3. 🔍 Vector search with FAISS
    4. 🤖 Rerank with Google Gemini AI
    5. ✅ Return balanced results
    """)
    
    st.markdown("### 🔗 API Docs")
    st.markdown(f"[View API Documentation]({API_URL}/docs)")
    
    st.markdown("### 📊 Test Types")
    type_info = {
        "A": "Ability & Aptitude",
        "B": "Biodata & SJT",
        "C": "Competencies",
        "D": "Development & 360",
        "E": "Assessment Exercises",
        "K": "Knowledge & Skills",
        "P": "Personality & Behavior",
        "S": "Simulations"
    }
    for k, v in type_info.items():
        st.markdown(f"**{k}** - {v}")
