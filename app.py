"""
SHL Assessment Recommendation System — Premium UI
Runs engine DIRECTLY inside Streamlit (no external API needed)
"""

import streamlit as st
import pandas as pd
import sys
import os

st.set_page_config(
    page_title="SHL Recommender",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, .stApp { background: #0a0a0f !important; color: #e8e6f0 !important; font-family: 'DM Sans', sans-serif !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2rem !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none; }

.hero { padding: 64px 0 48px; border-bottom: 1px solid #1a1a2e; margin-bottom: 40px; }
.hero-eyebrow { display: inline-flex; align-items: center; gap: 8px; font-size: 10px; font-weight: 600; letter-spacing: 0.2em; text-transform: uppercase; color: #6366f1; background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.25); padding: 5px 14px; border-radius: 100px; margin-bottom: 24px; }
.hero-title { font-family: 'Syne', sans-serif; font-size: clamp(36px, 4.5vw, 64px); font-weight: 800; line-height: 1.0; letter-spacing: -0.03em; color: #ffffff; margin-bottom: 16px; }
.hero-title span { background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.hero-sub { font-size: 16px; font-weight: 300; color: #6b6b8f; max-width: 500px; line-height: 1.7; }
.hero-stats { display: flex; gap: 48px; margin-top: 40px; }
.stat-num { font-family: 'Syne', sans-serif; font-size: 26px; font-weight: 700; color: #fff; letter-spacing: -0.02em; }
.stat-label { font-size: 11px; color: #4a4a6a; text-transform: uppercase; letter-spacing: 0.12em; margin-top: 3px; }

.section-label { font-size: 10px; font-weight: 600; letter-spacing: 0.2em; text-transform: uppercase; color: #3a3a5a; margin-bottom: 12px; margin-top: 24px; }

.stTextArea label { color: #3a3a5a !important; font-size: 10px !important; font-weight: 600 !important; letter-spacing: 0.2em !important; text-transform: uppercase !important; }
.stTextArea textarea { background: #0f0f1a !important; border: 1px solid #2a2a3e !important; border-radius: 12px !important; color: #e8e6f0 !important; font-family: 'DM Sans', sans-serif !important; font-size: 14px !important; line-height: 1.65 !important; padding: 16px !important; resize: none !important; transition: border-color 0.2s !important; }
.stTextArea textarea:focus { border-color: #6366f1 !important; box-shadow: 0 0 0 3px rgba(99,102,241,0.1) !important; }
.stTextArea textarea::placeholder { color: #2a2a42 !important; }

.stButton > button { width: 100% !important; border-radius: 10px !important; font-family: 'Syne', sans-serif !important; font-weight: 600 !important; font-size: 14px !important; letter-spacing: 0.04em !important; height: 48px !important; transition: all 0.2s !important; border: none !important; background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; color: white !important; }
.stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 25px rgba(99,102,241,0.4) !important; }

.pipeline { margin-top: 4px; }
.pipe-step { display: flex; align-items: flex-start; gap: 14px; padding: 11px 0; border-bottom: 1px solid #141428; }
.pipe-step:last-child { border-bottom: none; }
.pipe-icon { width: 30px; height: 30px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 14px; flex-shrink: 0; }
.pipe-body strong { font-size: 13px; font-weight: 500; color: #d0ceea; display: block; margin-bottom: 2px; }
.pipe-body span { font-size: 11px; color: #4a4a6a; line-height: 1.5; }

.result-hdr { display: flex; align-items: center; justify-content: space-between; margin-bottom: 28px; }
.result-title { font-family: 'Syne', sans-serif; font-size: 20px; font-weight: 700; color: #fff; letter-spacing: -0.02em; }
.result-pill { font-size: 11px; font-weight: 600; color: #6366f1; background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.2); padding: 4px 14px; border-radius: 100px; letter-spacing: 0.06em; }

.mrow { display: grid; grid-template-columns: repeat(4,1fr); gap: 14px; margin-bottom: 32px; }
.mcard { background: #0d0d18; border: 1px solid #1e1e2e; border-radius: 12px; padding: 16px 18px; }
.mval { font-family: 'Syne', sans-serif; font-size: 24px; font-weight: 700; color: #fff; letter-spacing: -0.02em; line-height: 1; margin-bottom: 5px; }
.mkey { font-size: 10px; color: #4a4a6a; text-transform: uppercase; letter-spacing: 0.13em; }

.acard { background: #0d0d18; border: 1px solid #1e1e2e; border-radius: 14px; padding: 22px 26px; margin-bottom: 14px; transition: border-color 0.2s, transform 0.2s; position: relative; overflow: hidden; }
.acard:hover { border-color: #2e2e50; transform: translateX(3px); }
.acard::before { content: ''; position: absolute; top: 0; left: 0; width: 3px; height: 100%; background: linear-gradient(180deg, #6366f1, #a855f7); border-radius: 3px 0 0 3px; opacity: 0; transition: opacity 0.2s; }
.acard:hover::before { opacity: 1; }
.acard-num { font-size: 10px; font-weight: 600; color: #2e2e4a; font-family: 'Syne', sans-serif; letter-spacing: 0.12em; margin-bottom: 6px; }
.acard-name { font-family: 'Syne', sans-serif; font-size: 16px; font-weight: 700; color: #fff; text-decoration: none; letter-spacing: -0.01em; }
.acard-name:hover { color: #a5b4fc; }
.acard-desc { font-size: 13px; color: #5a5a7a; line-height: 1.6; margin: 10px 0 14px; }
.acard-meta { display: flex; align-items: center; gap: 18px; flex-wrap: wrap; }
.meta-i { font-size: 12px; color: #4a4a6a; }
.meta-i strong { color: #9090b0; font-weight: 500; }
.badges { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; }
.badge { font-size: 10px; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; padding: 3px 9px; border-radius: 100px; }
.bA { background: rgba(99,102,241,0.12); color: #818cf8; border: 1px solid rgba(99,102,241,0.2); }
.bK { background: rgba(20,184,166,0.12); color: #2dd4bf; border: 1px solid rgba(20,184,166,0.2); }
.bP { background: rgba(236,72,153,0.12); color: #f472b6; border: 1px solid rgba(236,72,153,0.2); }
.bC { background: rgba(245,158,11,0.12); color: #fbbf24; border: 1px solid rgba(245,158,11,0.2); }
.bB { background: rgba(16,185,129,0.12); color: #34d399; border: 1px solid rgba(16,185,129,0.2); }
.bE { background: rgba(239,68,68,0.12); color: #f87171; border: 1px solid rgba(239,68,68,0.2); }
.bS { background: rgba(139,92,246,0.12); color: #c4b5fd; border: 1px solid rgba(139,92,246,0.2); }
.bD { background: rgba(59,130,246,0.12); color: #93c5fd; border: 1px solid rgba(59,130,246,0.2); }

.empty { display: flex; flex-direction: column; align-items: center; padding: 80px 40px; text-align: center; }
.empty-icon { font-size: 44px; opacity: 0.3; margin-bottom: 16px; }
.empty-title { font-family: 'Syne', sans-serif; font-size: 18px; font-weight: 700; color: #2e2e4a; margin-bottom: 8px; }
.empty-sub { font-size: 13px; color: #1e1e32; line-height: 1.65; max-width: 300px; }
.hdiv { height: 1px; background: #161628; margin: 24px 0; }
::-webkit-scrollbar { width: 5px; } ::-webkit-scrollbar-track { background: #0a0a0f; } ::-webkit-scrollbar-thumb { background: #2a2a3e; border-radius: 3px; }
.stRadio label { font-size: 13px !important; color: #6b6b8f !important; }
.stSpinner > div { border-top-color: #6366f1 !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource(show_spinner="Loading recommendation engine…")
def load_engine():
    sys.path.insert(0, "/mount/src/shl-assessment-recommender")
    from rag_engine import SHLRecommendationEngine
    engine = SHLRecommendationEngine()
    engine.initialize()
    return engine

st.markdown("""
<div class="hero">
  <div class="hero-eyebrow">⬡ RAG · FAISS · Gemini 2.0 Flash</div>
  <div class="hero-title">Find the right<br><span>assessment, instantly.</span></div>
  <div class="hero-sub">Semantic retrieval over 389 SHL assessments, reranked by Gemini AI. No cold starts — engine runs directly in the app.</div>
  <div class="hero-stats">
    <div><div class="stat-num">389</div><div class="stat-label">Assessments indexed</div></div>
    <div><div class="stat-num">~5s</div><div class="stat-label">Avg response time</div></div>
    <div><div class="stat-num">RAG</div><div class="stat-label">Gemini reranking</div></div>
  </div>
</div>
""", unsafe_allow_html=True)

TYPE_MAP = {
    "Ability & Aptitude": ("A","bA"), "Knowledge & Skills": ("K","bK"),
    "Personality & Behavior": ("P","bP"), "Personality & Behaviour": ("P","bP"),
    "Competencies": ("C","bC"), "Biodata & Situational Judgement": ("B","bB"),
    "Assessment Exercises": ("E","bE"), "Simulations": ("S","bS"), "Development & 360": ("D","bD"),
}

def badge(t):
    for name, (letter, cls) in TYPE_MAP.items():
        if name.lower() in t.lower():
            return f'<span class="badge {cls}">{letter} · {name}</span>'
    return f'<span class="badge bK">{t}</span>'

left, right = st.columns([4, 6], gap="large")

with left:
    st.markdown('<div class="section-label">Input Type</div>', unsafe_allow_html=True)
    itype = st.radio("Input Type", ["Natural Language", "Job Description", "JD URL"],
                     horizontal=True, label_visibility="collapsed")

    ph = {"Natural Language": "e.g. Java developers who collaborate with business teams. Max 40 min.",
          "Job Description": "Paste the full job description here...",
          "JD URL": "https://www.linkedin.com/jobs/view/..."}

    q = st.text_area("Describe the Role", height=155, placeholder=ph[itype], key="qbox",
                     value=st.session_state.get("prefill", ""))

    c1, c2 = st.columns([3, 1])
    with c1:
        go = st.button("⬡  Get Recommendations", type="primary")
    with c2:
        if st.button("Clear"):
            st.session_state["prefill"] = ""
            st.rerun()

    st.markdown('<div class="section-label">Quick Samples</div>', unsafe_allow_html=True)
    samples = [
        "Java developers, business collaboration, 40 min max",
        "Python, SQL, JavaScript — mid-level, 60 min",
        "Senior Data Analyst — SQL, Excel, Python",
        "Customer support, English communication",
        "Cognitive + personality screening, 45 min",
    ]
    for i, s in enumerate(samples):
        if st.button(f"↗ {s}", key=f"s{i}"):
            st.session_state["prefill"] = s
            st.rerun()

    st.markdown('<div class="hdiv"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Pipeline</div>', unsafe_allow_html=True)
    st.markdown("""<div class="pipeline">
    <div class="pipe-step"><div class="pipe-icon" style="background:rgba(99,102,241,0.12)">🕷</div><div class="pipe-body"><strong>Scrape</strong><span>389 assessments via Selenium + BeautifulSoup</span></div></div>
    <div class="pipe-step"><div class="pipe-icon" style="background:rgba(168,85,247,0.12)">🔢</div><div class="pipe-body"><strong>Embed</strong><span>all-MiniLM-L6-v2 → 384-dim normalized vectors</span></div></div>
    <div class="pipe-step"><div class="pipe-icon" style="background:rgba(236,72,153,0.12)">🔍</div><div class="pipe-body"><strong>Retrieve</strong><span>FAISS IndexFlatIP → top-15 candidates</span></div></div>
    <div class="pipe-step"><div class="pipe-icon" style="background:rgba(20,184,166,0.12)">🤖</div><div class="pipe-body"><strong>Rerank</strong><span>Gemini 2.0 Flash — duration-aware selection</span></div></div>
    <div class="pipe-step"><div class="pipe-icon" style="background:rgba(245,158,11,0.12)">✅</div><div class="pipe-body"><strong>Return</strong><span>Structured JSON: name, URL, type, duration, flags</span></div></div>
    </div>""", unsafe_allow_html=True)

with right:
    if st.session_state.get("prefill"):
        q = st.session_state["prefill"]
        go = True

    def show(results):
        durs = [r.get("duration", 0) for r in results if r.get("duration")]
        types = [t for r in results for t in r.get("test_type", [])]
        rem = sum(1 for r in results if r.get("remote_support") == "Yes")
        avg = sum(durs) // len(durs) if durs else "—"

        st.markdown(f"""
        <div class="result-hdr"><div class="result-title">Recommended Assessments</div><div class="result-pill">{len(results)} results</div></div>
        <div class="mrow">
          <div class="mcard"><div class="mval">{len(results)}</div><div class="mkey">Assessments</div></div>
          <div class="mcard"><div class="mval">{avg}<span style="font-size:13px;color:#3a3a5a"> min</span></div><div class="mkey">Avg Duration</div></div>
          <div class="mcard"><div class="mval">{len(set(types))}</div><div class="mkey">Test Types</div></div>
          <div class="mcard"><div class="mval">{rem}<span style="font-size:13px;color:#3a3a5a">/{len(results)}</span></div><div class="mkey">Remote</div></div>
        </div>""", unsafe_allow_html=True)

        for i, r in enumerate(results, 1):
            bs = "".join(badge(t) for t in r.get("test_type", []))
            if not bs: bs = '<span class="badge bK">General</span>'
            desc = r.get("description", "")
            desc = desc[:175] + "…" if len(desc) > 175 else desc
            st.markdown(f"""
            <div class="acard">
              <div class="acard-num">#{i:02d}</div>
              <a class="acard-name" href="{r.get('url','#')}" target="_blank">{r.get('name','Unknown')}</a>
              <div class="badges" style="margin-top:8px">{bs}</div>
              <div class="acard-desc">{desc}</div>
              <div class="acard-meta">
                <div class="meta-i">⏱ <strong>{r.get('duration','?')} min</strong></div>
                <div style="width:3px;height:3px;background:#2a2a3e;border-radius:50%"></div>
                <div class="meta-i">🌐 Remote: <strong>{r.get('remote_support','?')}</strong></div>
                <div style="width:3px;height:3px;background:#2a2a3e;border-radius:50%"></div>
                <div class="meta-i">🔄 Adaptive: <strong>{r.get('adaptive_support','?')}</strong></div>
              </div>
            </div>""", unsafe_allow_html=True)

        st.markdown('<div class="hdiv"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Export</div>', unsafe_allow_html=True)
        df = pd.DataFrame([{
            "Name": r.get("name"), "URL": r.get("url"),
            "Types": ", ".join(r.get("test_type", [])),
            "Duration (min)": r.get("duration"),
            "Remote": r.get("remote_support"),
            "Adaptive": r.get("adaptive_support"),
        } for r in results])
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button("⬇ Download CSV", df.to_csv(index=False),
                           file_name="shl_recommendations.csv", mime="text/csv")

    if go and q and q.strip():
        with st.spinner("Retrieving and reranking assessments…"):
            try:
                engine = load_engine()
                results = engine.recommend(q.strip(), max_results=10)
                if results:
                    show(results)
                else:
                    st.warning("No results found. Try a different query.")
            except Exception as e:
                st.error(f"Error: {e}")
    elif go:
        st.warning("Please enter a query first.")
    else:
        st.markdown("""<div class="empty">
        <div class="empty-icon">⬡</div>
        <div class="empty-title">Ready to recommend</div>
        <div class="empty-sub">Enter a job description or natural language query on the left to get AI-curated SHL assessment recommendations.</div>
        </div>""", unsafe_allow_html=True)