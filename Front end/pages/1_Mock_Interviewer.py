"""
ResumeIQ – Mock Interviewer Page
"""

import streamlit as st
import json
import re
import os
import sys

# Add parent directory to path so we can import from mock_interview
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from Backend.interview_engine import fetch_interview_questions, assess_candidate_answer, compile_performance_report

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Mock Interview – ResumeIQ",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── CSS (same base + interview-specific) ──────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;0,9..40,800;1,9..40,400&family=DM+Serif+Display&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; }

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #e3d5c8; font-family: 'DM Sans', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 3rem 2rem !important; max-width: 1160px !important; }
/* Hide sidebar completely */
[data-testid="stSidebar"] { display: none !important; }
[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
.st-emotion-cache-6q9sum.ef3ps4l2 { display: none !important; }

/* Navbar */
.navbar {
    position: sticky; top:0; z-index:999;
    display:flex; align-items:center; justify-content:space-between;
    padding: 0 2.5rem; height:62px;
    background: rgba(244,244,242,0.82);
    backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
    border-bottom: 1px solid rgba(0,0,0,0.07);
}
.navbar-logo { font-family:'DM Serif Display',serif; font-size:1.4rem; color:#111; }
.navbar-logo span { color:#e8701a; }
.nav-back {
    color:#059669; text-decoration:none; font-size:0.88rem;
    font-weight:600; display:flex; align-items:center; gap:0.4rem;
}
.nav-back:hover { color:#0f6640; }

/* Section wrap */
.section-wrap { max-width:1100px; margin:0 auto; padding:2rem 2.5rem 3rem; }

/* Cards */
.card { background:#fff; border-radius:20px; padding:1.6rem 1.8rem;
  border:1px solid rgba(0,0,0,0.05); box-shadow:0 2px 18px rgba(0,0,0,0.055); }
.card-orange { background:linear-gradient(140deg,#fbbf24 0%,#f97316 55%,#ea580c 100%); border:none; color:white; }
.card-green  { background:linear-gradient(140deg,#059669 0%,#0f6640 60%,#064e2e 100%); border:none; color:white; }

/* Interview Q&A bubbles */
.iv-question {
    background: linear-gradient(140deg,#059669,#0f6640);
    color:white; border-radius:18px 18px 18px 4px;
    padding:1.1rem 1.4rem; font-size:0.95rem; line-height:1.6;
    font-weight:500; margin-bottom:0.8rem;
    box-shadow: 0 4px 16px rgba(5,150,105,0.25);
}
.iv-question .q-label {
    font-size:0.7rem; font-weight:700; letter-spacing:1px;
    text-transform:uppercase; color:rgba(255,255,255,0.6); margin-bottom:0.3rem;
}

.iv-answer {
    background:#fff; border:1px solid rgba(0,0,0,0.07);
    border-radius:18px 18px 4px 18px; padding:1.1rem 1.4rem;
    font-size:0.9rem; line-height:1.6; color:#222;
    box-shadow:0 2px 12px rgba(0,0,0,0.05); margin-bottom:0.8rem;
}
.iv-answer .a-label {
    font-size:0.7rem; font-weight:700; letter-spacing:1px;
    text-transform:uppercase; color:#aaa; margin-bottom:0.3rem;
}

.iv-feedback {
    background: #f0fdf4; border:1px solid #bbf7d0;
    border-radius:14px; padding:1rem 1.3rem;
    font-size:0.88rem; line-height:1.6; color:#14532d;
    margin-bottom:1.2rem;
}
.iv-feedback .fb-label {
    font-size:0.7rem; font-weight:700; letter-spacing:1px;
    text-transform:uppercase; color:#059669; margin-bottom:0.4rem;
}

/* Progress dots */
.progress-dots { display:flex; gap:0.4rem; margin:1rem 0; }
.dot { width:10px; height:10px; border-radius:50%; background:#e0e0dc; transition:background 0.3s; }
.dot-done { background:#059669; }
.dot-current { background:#f97316; transform:scale(1.25); }

/* Verdict card */
.verdict-great { background:linear-gradient(140deg,#059669,#064e2e); }
.verdict-ok    { background:linear-gradient(140deg,#f59e0b,#c2640f); }
.verdict-need  { background:linear-gradient(140deg,#ef4444,#7f1d1d); }

/* Starters grid */
.starters { display:flex; flex-wrap:wrap; gap:0.5rem; margin-top:0.6rem; }
.starter-chip {
    background:#f0fdf4; border:1px solid #bbf7d0;
    color:#059669; font-size:0.82rem; font-weight:500;
    padding:0.3rem 0.75rem; border-radius:10px; cursor:pointer;
}

/* Buttons */
.stButton > button {
    background:linear-gradient(135deg,#059669 0%,#0f6640 100%) !important;
    color:#fff !important; border:none !important;
    border-radius:25px !important; padding:0.65rem 2.2rem !important;
    font-family:'DM Sans',sans-serif !important; font-weight:600 !important;
    font-size:0.95rem !important; letter-spacing:0.2px !important;
    box-shadow:0 4px 14px rgba(15,102,64,0.35) !important;
    transition:all 0.2s !important;
}
.stButton > button:hover { transform:translateY(-2px) !important; box-shadow:0 7px 20px rgba(15,102,64,0.45) !important; }

.stTextArea textarea {
    border-radius:14px !important; border:1.5px solid #e0e0dc !important;
    font-family:'DM Sans',sans-serif !important; font-size:0.92rem !important;
    background:#fafaf8 !important; line-height:1.6 !important;
    color: #111111 !important;
}
.stTextArea textarea:focus { border-color:#059669 !important; box-shadow:0 0 0 3px rgba(5,150,105,0.12) !important; }

.stSelectbox > div > div {
    border-radius:12px !important; border:1.5px solid #e0e0dc !important;
    background:#fafaf8 !important;
    color: #111111 !important;
}

.divider { height:1px; background:#e5e5e2; margin:1.8rem 0; }

.stSpinner > div { border-top-color: #059669 !important; }
div[data-testid="stSpinner"], div[data-testid="stSpinner"] * {
    color: #0f6640 !important;
    font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)


# ─── SESSION STATE ──────────────────────────────────────────────────────────────
iv_defaults = {
    "iv_questions": [],
    "iv_current": 0,
    "iv_answers": [],      # list of {question, type, answer, eval}
    "iv_started": False,
    "iv_done": False,
    "iv_verdict": "",
    "iv_mode": "Standard",
}
for k, v in iv_defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v




# ─── NAVBAR ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="navbar">
  <div class="navbar-logo">🎯 Resume<span>IQ</span></div>
  <div style="display:flex;align-items:center;gap:1.5rem;">
    <span style="font-size:0.82rem;color:#666;font-weight:500;">🎤 Mock Interviewer</span>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-wrap">', unsafe_allow_html=True)

# ─── GO BACK ──────────────────────────────────────────────────────────────────
if st.button("← Back to Analyser"):
    st.switch_page("Home.py")

st.markdown('<div style="height:1.2rem"></div>', unsafe_allow_html=True)

# ─── HERO ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:1.8rem;">
  <div style="display:inline-block;background:linear-gradient(90deg,#f59e0b22,#f9731622);
  border:1px solid #f9731655;color:#c2640f;font-size:0.78rem;font-weight:700;
  letter-spacing:1px;text-transform:uppercase;padding:0.3rem 0.9rem;border-radius:20px;margin-bottom:1rem;">
    ✦ AI Interviewer</div>
  <h1 style="font-family:'DM Serif Display',serif;font-size:2.8rem;color:#111;
  letter-spacing:-1px;line-height:1.15;margin-bottom:0.6rem;">
    Practice like it's the <em style="font-style:italic;background:linear-gradient(125deg,#f59e0b,#e8701a,#0f6640);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">real thing</em>
  </h1>
  <p style="font-size:1rem;color:#666;max-width:560px;line-height:1.65;">
    AI questions generated from your resume and the job description. 
    Answer in your own words — get instant, detailed feedback after each response.
  </p>
</div>
""", unsafe_allow_html=True)

# ─── CHECK PREREQUISITES ───────────────────────────────────────────────────────
has_resume = bool(st.session_state.get("resume_text", "").strip())
has_jd = bool(st.session_state.get("jd_text", "").strip())

if not has_resume or not has_jd:
    st.markdown("""
    <div class="card card-orange" style="max-width:600px;text-align:center;padding:2.2rem;">
      <div style="font-size:2rem;margin-bottom:0.8rem;">📋</div>
      <div style="font-family:'DM Serif Display',serif;font-size:1.4rem;color:white;margin-bottom:0.6rem;">
        Analyse your resume first
      </div>
      <p style="color:rgba(255,255,255,0.85);font-size:0.92rem;line-height:1.6;">
        The mock interviewer uses your resume and job description to create 
        personalised questions. Please run the analyser on the Home page first.
      </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)
    if st.button("← Go Analyse My Resume"):
        st.switch_page("Home.py")
    st.stop()

resume_text = st.session_state.resume_text
jd_text     = st.session_state.jd_text


# ════════════════════════════════════════════════════════════════════════════════
#  NOT STARTED YET — Show start screen
# ════════════════════════════════════════════════════════════════════════════════
if not st.session_state.iv_started:

    # Info cards
    c1, c2, c3 = st.columns(3, gap="large")
    with c1:
        st.markdown("""<div class="card card-green" style="text-align:center;padding:1.8rem;">
          <div style="font-size:2rem;margin-bottom:0.6rem;">🎯</div>
          <div style="font-family:'DM Serif Display',serif;font-size:1.2rem;color:white;margin-bottom:0.4rem;">Personalised</div>
          <p style="color:rgba(255,255,255,0.8);font-size:0.84rem;line-height:1.5;">
            Questions crafted from your resume and the specific job role.</p>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class="card card-orange" style="text-align:center;padding:1.8rem;">
          <div style="font-size:2rem;margin-bottom:0.6rem;">⚡</div>
          <div style="font-family:'DM Serif Display',serif;font-size:1.2rem;color:white;margin-bottom:0.4rem;">Instant Feedback</div>
          <p style="color:rgba(255,255,255,0.8);font-size:0.84rem;line-height:1.5;">
            Get scored and coached after every single answer.</p>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""<div class="card" style="text-align:center;padding:1.8rem;">
          <div style="font-size:2rem;margin-bottom:0.6rem;">📈</div>
          <div style="font-family:'DM Serif Display',serif;font-size:1.2rem;color:#111;margin-bottom:0.4rem;">Final Report</div>
          <p style="color:#666;font-size:0.84rem;line-height:1.5;">
            Receive an overall hiring assessment and tailored prep advice at the end.</p>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown("""<div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:14px;
    padding:1rem 1.4rem;margin-bottom:1.5rem;font-size:0.88rem;color:#14532d;line-height:1.6;">
      💡 <strong>Tips for best results:</strong> Answer as if you're in a real interview.
      Use the STAR method for behavioural questions (Situation, Task, Action, Result).
      Aim for 3-5 sentence answers. Be specific with examples.
    </div>""", unsafe_allow_html=True)

    sc1, sc2, sc3 = st.columns([1.5, 2, 1.5])
    with sc2:
        start_btn = st.button("🎤  Begin Mock Interview", use_container_width=True)

    if start_btn:
        with st.spinner("Generating personalised interview questions..."):
            try:
                # fetch_interview_questions returns a list of strings
                qs_strings = fetch_interview_questions(resume_text, jd_text)
                
                # convert to the list of dictionaries expected by the UI
                qs = []
                for i, q_text in enumerate(qs_strings):
                    q_type = "Technical" if i < 6 else "Behavioural"
                    qs.append({
                        "id": i + 1,
                        "type": q_type,
                        "question": q_text
                    })

                # Questions are already formatted via interview_engine.py (8 total: 6 tech, 2 behavioral)

                st.session_state.iv_questions = qs
                st.session_state.iv_current = 0
                st.session_state.iv_answers = []
                st.session_state.iv_started = True
                st.session_state.iv_done = False
                st.rerun()
            except Exception as e:
                st.error(f"Failed to generate questions: {e}")


# ════════════════════════════════════════════════════════════════════════════════
#  INTERVIEW IN PROGRESS
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.iv_started and not st.session_state.iv_done:

    questions = st.session_state.iv_questions
    current   = st.session_state.iv_current
    total     = len(questions)

    # Progress dots
    dots_html = '<div class="progress-dots">'
    for i in range(total):
        if i < current:
            dots_html += '<div class="dot dot-done"></div>'
        elif i == current:
            dots_html += '<div class="dot dot-current"></div>'
        else:
            dots_html += '<div class="dot"></div>'
    dots_html += '</div>'

    st.markdown(f"""<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;">
        <div style="font-size:0.82rem;font-weight:700;letter-spacing:0.8px;text-transform:uppercase;color:#999;">
            Question {current+1} of {total}</div>
        <div style="font-size:0.8rem;color:#aaa;">{st.session_state.iv_mode} · {questions[current]['type']}</div>
    </div>""", unsafe_allow_html=True)
    st.markdown(dots_html, unsafe_allow_html=True)

    # Show previous Q&A
    for prev in st.session_state.iv_answers:
        st.markdown(f"""<div class="iv-question">
            <div class="q-label">🎤 Question · {prev['type']}</div>
            {prev['question']}
        </div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class="iv-answer">
            <div class="a-label">👤 Your answer</div>
            {prev['answer']}
        </div>""", unsafe_allow_html=True)
        ev = prev.get("eval", {})
        q_max_score = 10 if prev['type'] == 'Technical' else 20
        score_val = ev.get("score", 5)
        # Normalise for color logic (0-1)
        norm_score = score_val / q_max_score
        score_color = "#059669" if norm_score >= 0.7 else ("#f59e0b" if norm_score >= 0.5 else "#ef4444")
        
        st.markdown(f"""<div class="iv-feedback">
            <div class="fb-label">🤖 AI Feedback · Score: <span style='color:{score_color};font-weight:800;'>{score_val}/{q_max_score}</span> — {ev.get('verdict','')}</div>
            <strong>✅ Strengths:</strong> {ev.get('strengths','')}<br><br>
            <strong>🔧 Improve:</strong> {ev.get('improvements','')}<br><br>
            <strong>💡 Key point missed:</strong> {ev.get('ideal_hint','')}<br><br>
            <em>Follow-up an interviewer might ask: "{ev.get('follow_up','')}"</em>
        </div>""", unsafe_allow_html=True)
        st.markdown('<div style="height:0.3rem"></div>', unsafe_allow_html=True)

    # Current question
    q = questions[current]
    st.markdown(f"""<div class="iv-question">
        <div class="q-label">🎤 Question {current+1} · {q['type']}</div>
        {q['question']}
    </div>""", unsafe_allow_html=True)

    # Starter prompts
    starters = {
        "Behavioural": ["In my last role...", "A situation where I...", "Using the STAR method..."],
        "Technical":   ["My approach would be...", "From my experience with...", "The key concept here is..."],
        "Situational": ["I would first...", "My priority would be...", "In that scenario..."],
        "Motivation":  ["I'm drawn to this role because...", "My long-term goal is...", "What excites me is..."],
    }
    s_list = starters.get(q["type"], [""])
    chips = " ".join(f'<span class="starter-chip">{s}</span>' for s in s_list)
    st.markdown(f"""<div style="margin-bottom:0.5rem;">
        <div style="font-size:0.75rem;color:#aaa;margin-bottom:0.3rem;">💬 Starter phrases:</div>
        <div class="starters">{chips}</div>
    </div>""", unsafe_allow_html=True)

    answer = st.text_area(
        "Your answer",
        placeholder="Type your answer here... Be specific and use examples where possible.",
        height=160,
        label_visibility="collapsed",
        key=f"answer_{current}",
    )

    a1, a2, _ = st.columns([1.5, 1.5, 3])
    with a1:
        submit_btn = st.button("Submit Answer →", use_container_width=True)
    with a2:
        skip_btn = st.button("Skip Question", use_container_width=True)

    if submit_btn:
        if not answer.strip():
            st.warning("Please type your answer before submitting.")
        else:
            with st.spinner("Evaluating your answer..."):
                try:
                    ev = assess_candidate_answer(q["question"], answer.strip(), resume_text, jd_text)
                    st.session_state.iv_answers.append({
                        "question": q["question"],
                        "type": q["type"],
                        "answer": answer.strip(),
                        "eval": ev,
                    })
                    st.session_state.iv_current += 1
                    if st.session_state.iv_current >= total:
                        st.session_state.iv_done = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Evaluation error: {e}")

    if skip_btn:
        st.session_state.iv_answers.append({
            "question": q["question"],
            "type": q["type"],
            "answer": "[Skipped]",
            "eval": {"score": 0, "verdict": "Skipped", "strengths": "–",
                     "improvements": "Practice answering this type", "ideal_hint": "–", "follow_up": "–"},
        })
        st.session_state.iv_current += 1
        if st.session_state.iv_current >= total:
            st.session_state.iv_done = True
        st.rerun()


# ════════════════════════════════════════════════════════════════════════════════
#  INTERVIEW DONE — Results
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.iv_done:

    answers = st.session_state.iv_answers
    # Final percentage based on total max score (6 * 10 + 2 * 20 = 100)
    total_score = sum([r["eval"].get("score", 0) for r in answers])
    total_max = sum([10 if r['type'] == 'Technical' else 20 for r in answers])
    pct = round((total_score / total_max) * 100) if total_max > 0 else 0

    verdict_class = "verdict-great" if pct >= 70 else ("verdict-ok" if pct >= 50 else "verdict-need")
    verdict_emoji = "🎉" if pct >= 70 else ("👍" if pct >= 50 else "📚")
    verdict_text  = "Strong Candidate" if pct >= 70 else ("Decent Fit" if pct >= 50 else "Needs More Prep")

    # Score banner
    st.markdown(f"""
    <div class="card {verdict_class}" style="text-align:center;padding:2.5rem;border-radius:24px;margin-bottom:1.5rem;">
      <div style="font-size:3rem;margin-bottom:0.6rem;">{verdict_emoji}</div>
      <div style="font-family:'DM Serif Display',serif;font-size:2rem;color:white;margin-bottom:0.4rem;">
        {verdict_text}
      </div>
      <div style="font-size:3.5rem;font-weight:800;color:white;line-height:1;margin:0.5rem 0;">
        {pct}<span style="font-size:1.5rem;opacity:0.6;">%</span>
      </div>
      <div style="color:rgba(255,255,255,0.7);font-size:0.9rem;">
        Overall performance across technical and behavioural rounds
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Per-question scores
    st.markdown("#### 📋 Question-by-Question Breakdown")
    for i, r in enumerate(answers, 1):
        ev = r.get("eval", {})
        s  = ev.get("score", 0)
        q_max = 10 if r['type'] == 'Technical' else 20
        with st.expander(f"Q{i} [{r['type']}] — Score: {s}/{q_max} · {ev.get('verdict','')}"):
            st.markdown(f"**Question:** {r['question']}")
            st.markdown(f"**Your Answer:** {r['answer']}")
            st.markdown(f"✅ **Strengths:** {ev.get('strengths','–')}")
            st.markdown(f"🔧 **Improvements:** {ev.get('improvements','–')}")
            st.markdown(f"💡 **Key point:** {ev.get('ideal_hint','–')}")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Final verdict (streamed)
    st.markdown("#### 🤖 AI Final Verdict & Prep Advice")

    if not st.session_state.iv_verdict:
        vb1, vb2, _ = st.columns([1.5, 1.5, 3])
        with vb1:
            gen_verdict = st.button("✨ Generate Final Verdict", use_container_width=True)
        if gen_verdict:
            with st.spinner("Compiling final performance report..."):
                try:
                    # extract plain answers and questions
                    ans_list = [r["answer"] for r in answers]
                    q_list = [r["question"] for r in answers]
                    
                    report_text = compile_performance_report(ans_list, q_list, resume_text, jd_text)
                    st.session_state.iv_verdict = report_text
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to generate report: {e}")
    else:
        st.markdown(f"""<div style="background:#f9f9f7;border:1px solid #e5e5e2;border-radius:14px;
        padding:1.4rem 1.6rem;font-size:0.92rem;line-height:1.75;color:#333;">
        {st.session_state.iv_verdict}
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Retry / back
    rc1, rc2, rc3 = st.columns(3, gap="large")
    with rc1:
        if st.button("🔄 Retry Interview", use_container_width=True):
            for k, v in iv_defaults.items():
                st.session_state[k] = v
            st.rerun()
    with rc2:
        if st.button("← Back to Analyser", use_container_width=True):
            st.switch_page("Home.py")

st.markdown("</div>", unsafe_allow_html=True)  # close section-wrap

# ─── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:2rem;border-top:1px solid #e5e5e2;
font-size:0.8rem;color:#aaa;margin-top:1rem;">
  ResumeIQ Mock Interviewer · Powered by Claude AI
</div>
""", unsafe_allow_html=True)
