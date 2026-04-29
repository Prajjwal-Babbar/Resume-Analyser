"""
ResumeIQ - AI-Powered Resume Analyser
======================================
Install deps:
    pip install streamlit plotly anthropic pypdf python-docx
Run:
    streamlit run Home.py
"""

import streamlit as st
import plotly.graph_objects as go
import json
import re
import io
import os
import sys

# Add parent directory to path so we can import from Backend and mock_interview
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Backend.parser import extract_text
from Backend.match import extract_skills, calculate_match
from Backend.MyLLM import query_llm, build_prompt
from Backend.RAG import chunker, create_embeddings, build_faiss_index, retrieve_relevant_chunks

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResumeIQ – AI Career Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── GLOBAL CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;0,9..40,800;1,9..40,400&family=DM+Serif+Display&display=swap');

/* ── Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; }

html, body, [class*="css"] {
    font-family: 'DM Sans', -apple-system, sans-serif;
}

.stApp {
    background: #e3d5c8;
    font-family: 'DM Sans', sans-serif;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 3rem 2rem !important; max-width: 1160px !important; }

/* Remove white section backgrounds that Streamlit injects */
[data-testid="stVerticalBlock"] > div > div,
[data-testid="stVerticalBlockBorderWrapper"] {
    background: transparent !important;
    box-shadow: none !important;
    border: none !important;
}
/* Hide sidebar completely */
[data-testid="stSidebar"] { display: none !important; }
[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
.st-emotion-cache-6q9sum.ef3ps4l2 { display: none !important; }

/* ── Navbar ── */
.navbar {
    position: sticky;
    top: 0;
    z-index: 999;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 2.5rem;
    height: 62px;
    background: rgba(244, 244, 242, 0.82);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border-bottom: 1px solid rgba(0,0,0,0.07);
}
.navbar-logo {
    font-family: 'DM Serif Display', serif;
    font-size: 1.4rem;
    color: #111;
    letter-spacing: -0.3px;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.navbar-logo span { color: #e8701a; }
.navbar-links { display: flex; gap: 2rem; list-style: none; }
.navbar-links li a {
    color: #555;
    text-decoration: none;
    font-size: 0.88rem;
    font-weight: 500;
    letter-spacing: 0.2px;
    transition: color 0.2s;
}
.navbar-links li a:hover { color: #111; }
.nav-pill {
    background: #0f6640;
    color: #fff !important;
    padding: 0.35rem 1.1rem;
    border-radius: 20px;
    font-size: 0.84rem !important;
    font-weight: 600 !important;
}

/* ── Hero ── */
.hero {
    padding: 3.5rem 2.5rem 0;
    max-width: 1160px;
    margin: 0 auto;
}
.hero-eyebrow {
    display: inline-block;
    background: linear-gradient(90deg, #f59e0b22, #f9731622);
    border: 1px solid #f9731655;
    color: #c2640f;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 0.3rem 0.9rem;
    border-radius: 20px;
    margin-bottom: 1.1rem;
}
.hero h1 {
    font-family: 'DM Serif Display', serif;
    font-size: 3.4rem;
    color: #111;
    letter-spacing: -1.5px;
    line-height: 1.12;
    margin-bottom: 1rem;
    font-weight: 400;
}
.hero h1 em {
    font-style: italic;
    background: linear-gradient(125deg, #f59e0b 10%, #e8701a 55%, #0f6640 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    font-size: 1.05rem;
    color: #666;
    max-width: 500px;
    line-height: 1.65;
    margin-bottom: 2rem;
}

/* ── Cards ── */
.card {
    background: #fff;
    border-radius: 20px;
    padding: 1.6rem 1.8rem;
    border: 1px solid rgba(0,0,0,0.05);
    box-shadow: 0 2px 18px rgba(0,0,0,0.055);
    transition: transform 0.22s, box-shadow 0.22s;
    height: 100%;
}
.card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.09);
}
.card-label {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #999;
    margin-bottom: 0.4rem;
}
.card-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.35rem;
    color: #111;
    margin-bottom: 0.5rem;
}

/* Orange gradient card */
.card-orange {
    background: linear-gradient(140deg, #fbbf24 0%, #f97316 55%, #ea580c 100%);
    border: none;
    color: white;
}
.card-orange .card-label { color: rgba(255,255,255,0.7); }
.card-orange .card-title { color: white; }
.card-orange p { color: rgba(255,255,255,0.85); font-size: 0.9rem; line-height: 1.55; }

/* Green gradient card */
.card-green {
    background: linear-gradient(140deg, #059669 0%, #0f6640 60%, #064e2e 100%);
    border: none;
    color: white;
}
.card-green .card-label { color: rgba(255,255,255,0.7); }
.card-green .card-title { color: white; }
.card-green p { color: rgba(255,255,255,0.85); font-size: 0.9rem; line-height: 1.55; }

/* Dark card */
.card-dark {
    background: #1a1a1a;
    border: none;
    color: white;
}
.card-dark .card-label { color: rgba(255,255,255,0.45); }
.card-dark .card-title { color: white; }

/* ── Score Badge ── */
.score-ring-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.4rem;
}
.score-label-main {
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #999;
    margin-top: 0.2rem;
}

/* ── Skill Tags ── */
.tags-wrap { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.6rem; }
.tag {
    padding: 0.28rem 0.75rem;
    border-radius: 10px;
    font-size: 0.8rem;
    font-weight: 500;
    letter-spacing: 0.1px;
}
.tag-green { background: #dcfce7; color: #14532d; border: 1px solid #bbf7d0; }
.tag-red   { background: #fee2e2; color: #7f1d1d; border: 1px solid #fecaca; }
.tag-blue  { background: #dbeafe; color: #1e3a5f; border: 1px solid #bfdbfe; }
.tag-amber { background: #fef3c7; color: #78350f; border: 1px solid #fde68a; }

/* ── Chat Bubbles ── */
.chat-scroll {
    max-height: 360px;
    overflow-y: auto;
    padding: 0.5rem 0;
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
}
.bubble {
    padding: 0.75rem 1.1rem;
    border-radius: 16px;
    font-size: 0.88rem;
    line-height: 1.55;
    max-width: 88%;
    white-space: pre-wrap;
}
.bubble-user {
    background: linear-gradient(135deg, #059669, #0f6640);
    color: white;
    align-self: flex-end;
    border-radius: 16px 16px 4px 16px;
}
.bubble-ai {
    background: #f0f0ee;
    color: #1a1a1a;
    align-self: flex-start;
    border-radius: 16px 16px 16px 4px;
}
.bubble-ai strong { color: #0f6640; }

/* ── Tip Cards ── */
.tip-item {
    display: flex;
    gap: 0.8rem;
    align-items: flex-start;
    padding: 0.8rem;
    background: #f9f9f7;
    border-radius: 12px;
    border-left: 3px solid #059669;
    margin-bottom: 0.6rem;
    font-size: 0.88rem;
    line-height: 1.5;
    color: #333;
}
.tip-num {
    background: #059669;
    color: white;
    border-radius: 50%;
    width: 22px;
    height: 22px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.72rem;
    font-weight: 700;
    flex-shrink: 0;
}

/* ── Section padding ── */
.section-wrap { max-width: 1160px; margin: 0 auto; padding: 1.5rem 2.5rem 3rem; }

/* ── Streamlit overrides ── */
.stFileUploader > div > div {
    background: #fafaf8 !important;
    border: 2px dashed #ddd !important;
    border-radius: 14px !important;
    padding: 1rem !important;
}
.stFileUploader > div > div:hover { border-color: #059669 !important; }

.stButton > button {
    background: linear-gradient(135deg, #059669 0%, #0f6640 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 25px !important;
    padding: 0.65rem 2.2rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.2px !important;
    box-shadow: 0 4px 14px rgba(15,102,64,0.35) !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 7px 20px rgba(15,102,64,0.45) !important;
}

.stTextArea textarea, .stTextInput input {
    border-radius: 12px !important;
    border: 1.5px solid #e0e0dc !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    background: #fafaf8 !important;
    color: #111111 !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: #059669 !important;
    box-shadow: 0 0 0 3px rgba(5,150,105,0.12) !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: #ebebea;
    border-radius: 12px;
    padding: 4px;
    gap: 2px;
    border: none;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 9px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    font-size: 0.88rem;
    color: #666;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    color: #0f6640 !important;
    font-weight: 700 !important;
    box-shadow: 0 1px 6px rgba(0,0,0,0.1);
}

div[data-testid="stHorizontalBlock"] { gap: 1.2rem; }

.stSpinner > div { border-top-color: #059669 !important; }
div[data-testid="stSpinner"], div[data-testid="stSpinner"] * {
    color: #0f6640 !important;
    font-weight: 600 !important;
}

/* Sidebar */
section[data-testid="stSidebar"] .stTextInput input {
    background: #2a2a2a !important;
    border-color: #444 !important;
    color: #eee !important;
}

/* Roadmap output box */
.stream-box {
    background: linear-gradient(140deg, #7a1a00, #c0390b);
    border: none;
    border-radius: 14px;
    padding: 1.4rem 1.8rem;
    font-size: 0.92rem;
    line-height: 1.75;
    color: #ffe8d6;
    min-height: 80px;
    white-space: pre-wrap;
    box-shadow: 0 4px 20px rgba(192,57,11,0.3);
}

.divider { height: 1px; background: #e5e5e2; margin: 2rem 0; }

/* Metric row */
.metric-row { display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1rem; }
.metric-box {
    background: white;
    border: 1px solid rgba(0,0,0,0.05);
    border-radius: 14px;
    padding: 1rem 1.3rem;
    flex: 1;
    min-width: 130px;
    box-shadow: 0 1px 8px rgba(0,0,0,0.04);
}
.metric-val { font-family: 'DM Serif Display', serif; font-size: 2rem; color: #111; line-height:1; }
.metric-lbl { font-size: 0.72rem; font-weight: 600; color: #999; letter-spacing: 0.8px; text-transform: uppercase; margin-top: 0.2rem; }
</style>
""", unsafe_allow_html=True)


# ─── UTILITIES ─────────────────────────────────────────────────────────────────

def run_analysis(resume_text: str, jd_text: str) -> dict:
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)
    score, matched, missing = calculate_match(resume_skills, jd_skills)

    prompt = f"""You are an expert ATS and career coach. Deeply analyse the resume against the job description.

RESUME:
{resume_text[:1500]}

JOB DESCRIPTION:
{jd_text[:1000]}

Reply ONLY with a valid JSON object matching EXACTLY this format (no extra text):
{{
  "strengths": ["point1", "point2", "point3", "point4"],
  "weaknesses": ["point1", "point2", "point3"],
  "improvement_tips": ["tip1", "tip2", "tip3", "tip4"],
  "overall_summary": "A 2-3 sentence honest summary of their profile match."
}}"""

    raw = query_llm(prompt).strip()
    
    analysis = {
        "match_score": int(score),
        "matching_skills": matched,
        "missing_skills": missing,
        "strengths": ["Good formatting", "Clear experience"],
        "weaknesses": ["Missing some key skills"],
        "improvement_tips": ["Add more technical details"],
        "overall_summary": "Solid candidate but lacks some specific requirements."
    }

    try:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            parsed = json.loads(match.group(0))
            for k in ["strengths", "weaknesses", "improvement_tips", "overall_summary"]:
                if k in parsed:
                    analysis[k] = parsed[k]
    except Exception as e:
        print("JSON parse error:", e)

    return analysis


def chat_with_resume(history: list, user_msg: str, index, chunks) -> str:
    results = retrieve_relevant_chunks(user_msg, index, chunks)
    prompt = build_prompt(user_msg, results)
    
    # We can inject history context into the prompt
    history_text = "\n".join([f"{m['role']}: {m['content']}" for m in history[-3:]])
    
    full_prompt = f"Chat History:\n{history_text}\n\n{prompt}"
    return query_llm(full_prompt)


def make_pie(score: int):
    remaining = 100 - score
    color_match = "#059669" if score >= 70 else ("#f59e0b" if score >= 45 else "#ef4444")
    fig = go.Figure(go.Pie(
        values=[score, remaining],
        labels=["Match", "Gap"],
        hole=0.68,
        marker=dict(colors=[color_match, "#f0f0ee"], line=dict(width=0)),
        textinfo="none",
        direction="clockwise",
        sort=False,
    ))
    fig.update_layout(
        showlegend=False,
        margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        annotations=[dict(
            text=f"<b>{score}%</b>",
            x=0.5, y=0.5,
            font=dict(size=30, color="#111", family="DM Sans"),
            showarrow=False,
        )],
        height=200,
        width=200,
    )
    return fig


# ─── SESSION STATE ──────────────────────────────────────────────────────────────
defaults = {
    "analysis": None,
    "resume_text": "",
    "jd_text": "",
    "chat_history": [],
    "deep_feedback": "",
    "index": None,
    "chunks": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v




# ─── NAVBAR ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="navbar">
  <div class="navbar-logo">🎯 Resume<span>IQ</span></div>
  <ul class="navbar-links">
    <li><a href="#">Analyser</a></li>
    <li><a href="#">Features</a></li>
    <li><a href="#">About</a></li>
    <li><a class="nav-pill" href="#">Pro ✦</a></li>
  </ul>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# PAGE CONTENT
# ════════════════════════════════════════════════════════════════════════════════

st.markdown('<div class="section-wrap">', unsafe_allow_html=True)

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-eyebrow">✦ AI-Powered Career Tool</div>
  <h1>Land your dream job<br>with <em>smarter</em> analysis</h1>
  <p class="hero-sub">Upload your resume and a job description — our AI gives you an instant match score, identifies skill gaps, and shows you exactly how to bridge them.</p>
</div>
""", unsafe_allow_html=True)


# ── UPLOAD SECTION ─────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("#### 📂 Upload Your Documents")

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("""<div style='font-size:0.8rem;font-weight:700;letter-spacing:0.8px;
    text-transform:uppercase;color:#999;margin-bottom:0.4rem;'>Your Resume</div>""",
                unsafe_allow_html=True)
    resume_file = st.file_uploader(
        "Resume",
        type=["pdf", "docx", "txt"],
        label_visibility="collapsed",
        key="resume_up",
    )
    if resume_file:
        st.markdown(f"""<div style='font-size:0.82rem;color:#059669;font-weight:500;
        margin-top:0.3rem;'>✓ {resume_file.name}</div>""", unsafe_allow_html=True)

with col2:
    st.markdown("""<div style='font-size:0.8rem;font-weight:700;letter-spacing:0.8px;
    text-transform:uppercase;color:#999;margin-bottom:0.4rem;'>Job Description</div>""",
                unsafe_allow_html=True)
    jd_file = st.file_uploader(
        "Job Description",
        type=["pdf", "docx", "txt"],
        label_visibility="collapsed",
        key="jd_up",
    )
    if jd_file:
        st.markdown(f"""<div style='font-size:0.82rem;color:#059669;font-weight:500;
        margin-top:0.3rem;'>✓ {jd_file.name}</div>""", unsafe_allow_html=True)

st.markdown("""<div style='font-size:0.8rem;font-weight:600;color:#555;
margin:0.8rem 0 0.3rem;'>Or paste the Job Description as text:</div>""",
            unsafe_allow_html=True)
jd_text_area = st.text_area(
    "JD text",
    placeholder="Paste the full job description here...",
    height=140,
    label_visibility="collapsed",
)

c1, c2, c3 = st.columns([1.5, 2, 1.5])
with c2:
    analyse_btn = st.button("🔍  Analyse My Resume", use_container_width=True)

if analyse_btn:
    if not resume_file:
        st.error("⚠️  Please upload your resume.")
    else:
        resume_text = extract_text(resume_file)
        jd_text = extract_text(jd_file) if jd_file else jd_text_area.strip()

        if not jd_text:
            st.error("⚠️  Please upload or paste a job description.")
        elif not resume_text:
            st.error("⚠️  Could not read the resume file. Try a different format.")
        else:
            st.session_state.resume_text = resume_text
            st.session_state.jd_text = jd_text
            st.session_state.chat_history = []
            st.session_state.deep_feedback = ""

            with st.spinner("🧠  Analysing with AI — this takes ~15 seconds..."):
                try:
                    # RAG setup
                    combined_text = resume_text + " \n " + jd_text
                    chunks = chunker(combined_text)
                    embeddings = create_embeddings(chunks)
                    index = build_faiss_index(embeddings)
                    st.session_state.index = index
                    st.session_state.chunks = chunks

                    st.session_state.analysis = run_analysis(resume_text, jd_text)
                    st.success("✅  Analysis complete! Scroll down to see results.")
                except Exception as e:
                    st.error(f"Analysis failed: {e}")


# ════════════════════════════════════════════════════════════════════════════════
# RESULTS (shown only after analysis)
# ════════════════════════════════════════════════════════════════════════════════
if st.session_state.analysis:
    a = st.session_state.analysis
    score = a.get("match_score", 0)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── Score row ────────────────────────────────────────────────────────────
    st.markdown("#### 📊 Your Match Score")

    r1, r2, r3 = st.columns([1.2, 1.2, 1.6], gap="large")

    with r1:
        st.plotly_chart(make_pie(score), use_container_width=False, config={"displayModeBar": False})
        color = "#059669" if score >= 70 else ("#f59e0b" if score >= 45 else "#ef4444")
        label = "Strong match 🎉" if score >= 70 else ("Decent fit 👍" if score >= 45 else "Needs work 📚")
        st.markdown(f"""<div style='text-align:center;'>
            <div style='font-size:1.05rem;font-weight:700;color:{color};'>{label}</div>
            <div style='font-size:0.78rem;color:#999;margin-top:0.2rem;'>Overall compatibility</div>
        </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with r2:
        st.markdown(f"""
        <div class="card card-orange" style="height:100%;">
          <div class="card-label">Summary</div>
          <div class="card-title">AI Verdict</div>
          <p style="margin-top:0.6rem;">{a.get('overall_summary','')}</p>
        </div>""", unsafe_allow_html=True)

    with r3:
        st.markdown(f"""
        <div class="card card-green" style="height:100%;">
          <div class="card-label">Quick Metrics</div>
          <div class="card-title">At a Glance</div>
          <div style="margin-top:0.8rem;display:flex;flex-direction:column;gap:0.7rem;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
              <span style="color:rgba(255,255,255,0.8);font-size:0.88rem;">Matching Skills</span>
              <span style="background:rgba(255,255,255,0.2);color:#fff;font-weight:700;
              padding:0.15rem 0.7rem;border-radius:10px;font-size:0.88rem;">
                {len(a.get('matching_skills',[]))}</span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;">
              <span style="color:rgba(255,255,255,0.8);font-size:0.88rem;">Skill Gaps</span>
              <span style="background:rgba(255,255,255,0.2);color:#fff;font-weight:700;
              padding:0.15rem 0.7rem;border-radius:10px;font-size:0.88rem;">
                {len(a.get('missing_skills',[]))}</span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;">
              <span style="color:rgba(255,255,255,0.8);font-size:0.88rem;">Strengths</span>
              <span style="background:rgba(255,255,255,0.2);color:#fff;font-weight:700;
              padding:0.15rem 0.7rem;border-radius:10px;font-size:0.88rem;">
                {len(a.get('strengths',[]))}</span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;">
              <span style="color:rgba(255,255,255,0.8);font-size:0.88rem;">Action Tips</span>
              <span style="background:rgba(255,255,255,0.2);color:#fff;font-weight:700;
              padding:0.15rem 0.7rem;border-radius:10px;font-size:0.88rem;">
                {len(a.get('improvement_tips',[]))}</span>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── Skills breakdown ──────────────────────────────────────────────────────
    st.markdown("#### 🧩 Skills Breakdown")
    s1, s2 = st.columns(2, gap="large")

    with s1:
        matching_tags = " ".join(
            f'<span class="tag tag-green">{s}</span>'
            for s in a.get("matching_skills", [])
        )
        st.markdown(f"""
        <div class="card">
          <div class="card-label">✅ You already have</div>
          <div class="card-title">Matching Skills</div>
          <div class="tags-wrap">{matching_tags}</div>
        </div>""", unsafe_allow_html=True)

    with s2:
        missing_tags = " ".join(
            f'<span class="tag tag-red">{s}</span>'
            for s in a.get("missing_skills", [])
        )
        st.markdown(f"""
        <div class="card">
          <div class="card-label">❌ You need to build</div>
          <div class="card-title">Skill Gaps</div>
          <div class="tags-wrap">{missing_tags}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── Strengths & Weaknesses + Tips ─────────────────────────────────────────
    st.markdown("#### 🔎 Deep Analysis")
    d1, d2 = st.columns(2, gap="large")

    with d1:
        strengths_html = "".join(
            f'<div class="tip-item"><div class="tip-num">✓</div><div>{s}</div></div>'
            for s in a.get("strengths", [])
        )
        weaknesses_html = "".join(
            f'<div class="tip-item" style="border-left-color:#ef4444;">'
            f'<div class="tip-num" style="background:#ef4444;">!</div><div>{w}</div></div>'
            for w in a.get("weaknesses", [])
        )
        st.markdown(f"""
        <div class="card">
          <div class="card-label">💪 What works</div>
          <div class="card-title" style="margin-bottom:0.8rem;">Your Strengths</div>
          {strengths_html}
          <div style="height:1rem"></div>
          <div class="card-label" style="margin-top:0.5rem;">⚠️ What needs work</div>
          <div class="card-title" style="margin-bottom:0.8rem;">Areas to Improve</div>
          {weaknesses_html}
        </div>""", unsafe_allow_html=True)

    with d2:
        tips_html = "".join(
            f'<div class="tip-item"><div class="tip-num">{i}</div><div>{tip}</div></div>'
            for i, tip in enumerate(a.get("improvement_tips", []), 1)
        )
        st.markdown(f"""
        <div class="card">
          <div class="card-label">🗺 Action plan</div>
          <div class="card-title" style="margin-bottom:0.8rem;">How to Bridge the Gap</div>
          {tips_html}
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── AI Detailed Feedback (streaming) ──────────────────────────────────────
    st.markdown("#### 🧠 Get a Detailed AI Roadmap")
    st.markdown("""<p style='font-size:0.9rem;color:#666;margin-bottom:1rem;'>
    Click below for a personalised, in-depth analysis of your profile vs this role —
    including a step-by-step plan to make yourself the ideal candidate.</p>""",
                unsafe_allow_html=True)

    fb_col1, fb_col2, _ = st.columns([1.5, 1.5, 2])
    with fb_col1:
        deep_btn = st.button("✨  Generate Full Roadmap", use_container_width=True)

    if deep_btn:
        prompt = f"""You are a top-tier career strategist and resume coach.
Based on the resume, job description and analysis below, write a DETAILED, PERSONALISED career roadmap.

MATCH SCORE: {score}/100
MATCHING SKILLS: {', '.join(a.get('matching_skills',[]))}
MISSING SKILLS: {', '.join(a.get('missing_skills',[]))}
STRENGTHS: {', '.join(a.get('strengths',[]))}
WEAKNESSES: {', '.join(a.get('weaknesses',[]))}

RESUME (excerpt):
{st.session_state.resume_text[:1000]}

JOB DESCRIPTION (excerpt):
{st.session_state.jd_text[:1000]}

Write a comprehensive 400-600 word roadmap covering:
1. Honest assessment of the candidate's current profile
2. The 3 most critical skill gaps and exactly HOW to address each
3. How to reframe/reword existing experience to resonate with this role
4. Quick wins (things they can do this week)
5. A realistic timeline to become a strong candidate
Be specific, actionable, and encouraging."""

        with st.spinner("Generating roadmap..."):
            feedback_text = query_llm(prompt, m = 2048)
        
        st.session_state.deep_feedback = feedback_text
        st.markdown(
            f'<div style="font-size:1rem;line-height:1.75;color:#c0390b;font-weight:500;'
            f'padding:1.2rem 1.6rem;border-radius:14px;background:rgba(192,57,11,0.07);'
            f'border-left:4px solid #c0390b;white-space:pre-wrap;">{feedback_text}</div>',
            unsafe_allow_html=True
        )

    elif st.session_state.deep_feedback:
        st.markdown(
            f'<div style="font-size:1rem;line-height:1.75;color:#c0390b;font-weight:500;'
            f'padding:1.2rem 1.6rem;border-radius:14px;background:rgba(192,57,11,0.07);'
            f'border-left:4px solid #c0390b;white-space:pre-wrap;">{st.session_state.deep_feedback}</div>',
            unsafe_allow_html=True
        )

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── CHATBOT ───────────────────────────────────────────────────────────────
    st.markdown("#### 💬 Ask Anything About Your Resume")
    st.markdown("""<p style='font-size:0.9rem;color:#666;margin-bottom:1rem;'>
    Chat with AI about your resume, the role, how to improve your application, 
    or anything else career-related.</p>""", unsafe_allow_html=True)

    # Render chat history
    if st.session_state.chat_history:
        chat_html = '<div class="chat-scroll">'
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                chat_html += f'<div class="bubble bubble-user">{msg["content"]}</div>'
            else:
                chat_html += f'<div class="bubble bubble-ai">{msg["content"]}</div>'
        chat_html += "</div>"
        st.markdown(chat_html, unsafe_allow_html=True)

    user_q = st.text_input(
        "Ask a question",
        placeholder="e.g. How should I rewrite my experience section for this role?",
        label_visibility="collapsed",
        key="chat_input",
    )

    cc1, cc2, _ = st.columns([1.5, 1.2, 3])
    with cc1:
        send_btn = st.button("Send →", use_container_width=True)
    with cc2:
        if st.button("Clear chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

    if send_btn and user_q.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_q.strip()})
        with st.spinner("Thinking..."):
            reply = chat_with_resume(
                st.session_state.chat_history[:-1],
                user_q.strip(),
                st.session_state.index,
                st.session_state.chunks
            )
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── MOCK INTERVIEW CTA ────────────────────────────────────────────────────
    st.markdown("""
    <div class="card card-dark" style="text-align:center;padding:2.2rem;border-radius:24px;margin-top:0.5rem;">
      <div style="font-size:0.75rem;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;
      color:rgba(255,255,255,0.4);margin-bottom:0.6rem;">Next Step</div>
      <div style="font-family:'DM Serif Display',serif;font-size:1.9rem;color:white;margin-bottom:0.7rem;letter-spacing:-0.5px;">
        Ready to ace the interview?
      </div>
      <p style="color:rgba(255,255,255,0.6);font-size:0.95rem;max-width:480px;margin:0 auto 1.5rem;line-height:1.6;">
        Practice with our AI mock interviewer tailored to this exact job role. 
        Get instant feedback on your answers and body language.
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="height:2rem"></div>', unsafe_allow_html=True)
    mc1, mc2, mc3 = st.columns([1.5, 2, 1.5])
    with mc2:
        if st.button("🎤  Start Mock Interview →", use_container_width=True):
            st.switch_page("pages/1_Mock_Interviewer.py")

st.markdown("</div>", unsafe_allow_html=True)  # close section-wrap

# ─── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:2rem;border-top:1px solid #e5e5e2;
font-size:0.8rem;color:#aaa;margin-top:1rem;">
  ResumeIQ · Built with Streamlit & Claude AI &nbsp;·&nbsp; 
  <span style='color:#e8701a;'>♥</span> for your college project
</div>
""", unsafe_allow_html=True)
