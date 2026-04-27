from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)

# ─────────────────────────────────────────────────────────────────
# PROMPT TEMPLATES
# ─────────────────────────────────────────────────────────────────

QUESTION_BUILD_TEMPLATE = """You are a professional technical interviewer.

Based on the candidate's resume and the job description provided below, generate exactly 8 interview questions.

Rules:
- Questions 1-4 must be TECHNICAL: focused on skills, tools, and technologies mentioned in the resume and job description.
- Questions 5-8 must be BEHAVIORAL: focused on past experiences, problem-solving, and soft skills relevant to the role.
- Every question must be directly relevant to the candidate's specific profile and the job role.
- Do NOT generate generic or random questions.
- Do NOT repeat similar questions.
- Output ONLY a numbered list of 8 questions. No extra text, no introduction, no explanation.

Resume:
{resume}

Job Description:
{jd}

Output format (strictly follow this):
1. [Question]
2. [Question]
3. [Question]
4. [Question]
5. [Question]
6. [Question]
7. [Question]
8. [Question]
"""

ANSWER_REVIEW_TEMPLATE = """You are a professional technical interviewer evaluating a candidate's answer.

Evaluate the answer strictly based on the context of the resume, job description, and the question asked.

Question:
{question}

Candidate's Answer:
{answer}

Resume Context:
{resume}

Job Description Context:
{jd}

Provide your evaluation in EXACTLY this JSON format (no extra text, no markdown fences):
{{
  "score": [Integer from 1 to 10],
  "verdict": "[Excellent | Good | Average | Needs Work]",
  "strengths": "[One sentence on what was done well]",
  "improvements": "[One actionable specific suggestion to improve]",
  "ideal_hint": "[A key point or structure they missed]",
  "follow_up": "[One natural follow-up question an interviewer might ask]"
}}
"""

REPORT_BUILD_TEMPLATE = """You are a senior hiring manager writing a comprehensive interview performance report.

Below are the interview questions and the candidate's answers. Evaluate the overall performance based on the resume and job description provided.

Resume:
{resume}

Job Description:
{jd}

Interview Q&A:
{qa_text}

Write a detailed final report in EXACTLY this format:

OVERALL PERFORMANCE:
[2-3 sentence overall assessment of the candidate's interview performance]

STRENGTHS:
- [Specific strength observed]
- [Specific strength observed]
- [Specific strength observed]

WEAK AREAS:
- [Specific weak area observed]
- [Specific weak area observed]

SUGGESTIONS FOR IMPROVEMENT:
- [Actionable suggestion]
- [Actionable suggestion]
- [Actionable suggestion]

HIRING RECOMMENDATION:
[Strong Yes / Yes / Maybe / No — with a one-sentence reason]
"""

# ─────────────────────────────────────────────────────────────────
# FUNCTIONS
# ─────────────────────────────────────────────────────────────────


def fetch_interview_questions(resume: str, jd: str) -> list[str]:
    """
    Sends a prompt to the local LLM to produce 8 tailored interview questions
    based on the candidate's resume and the job description.
    Returns a list of question strings (max 8).
    """
    prompt = QUESTION_BUILD_TEMPLATE.format(
        resume=resume[:1500],
        jd=jd[:1000]
    )

    # Initialize before try so Pylance knows it is always bound
    response = None
    try:
        response = client.chat.completions.create(
            model="mistral-7b-instruct",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,
            temperature=0.5
        )
    except Exception as e:
        raise RuntimeError(
            "❌ Could not connect to LM Studio.\n\n"
            "Please make sure:\n"
            "1. LM Studio is open and running\n"
            "2. A model (mistral-7b-instruct) is loaded\n"
            "3. The local server is started on port 1234\n\n"
            f"Original error: {e}"
        ) from e

    raw: str = response.choices[0].message.content.strip()

    questions: list[str] = []
    for raw_line in raw.splitlines():
        raw_line = raw_line.strip()
        # Parse lines that start with a number and a dot/period e.g. "1. "
        if raw_line and raw_line[0].isdigit() and "." in raw_line:
            parts = raw_line.split(".", 1)
            if len(parts) == 2:
                q = parts[1].strip()
                if q:
                    questions.append(q)

    # Fallback: if parsing fails, split by newlines and clean up
    if not questions:
        questions = [ln.strip() for ln in raw.splitlines() if ln.strip()]

    return questions[:8]  # Cap at 8


def assess_candidate_answer(question: str, answer: str, resume: str, jd: str) -> dict:
    """
    Sends the candidate's answer to the local LLM for structured evaluation.
    Returns a dict with keys: score, verdict, strengths, improvements, ideal_hint, follow_up.
    """
    prompt = ANSWER_REVIEW_TEMPLATE.format(
        question=question,
        answer=answer if answer.strip() else "(No answer provided)",
        resume=resume[:800],
        jd=jd[:500]
    )

    # Initialize before try so Pylance knows it is always bound
    response = None
    try:
        response = client.chat.completions.create(
            model="mistral-7b-instruct",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=256,
            temperature=0.3
        )
    except Exception as e:
        raise RuntimeError(
            "❌ Could not connect to LM Studio. Please ensure it is running on port 1234."
            f" Original error: {e}"
        ) from e

    raw: str = response.choices[0].message.content.strip()

    import json, re
    feedback = {
        "score": 5,
        "verdict": "Average",
        "strengths": "Answer recorded.",
        "improvements": "Provide more specific details.",
        "ideal_hint": "-",
        "follow_up": "Can you elaborate?"
    }

    try:
        # Extract JSON using regex
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            parsed = json.loads(match.group(0))
            for k in feedback.keys():
                if k in parsed:
                    feedback[k] = parsed[k]
            # Ensure score is an integer
            if isinstance(feedback["score"], str):
                nums = re.search(r"\d+", feedback["score"])
                feedback["score"] = int(nums.group()) if nums else 5
    except Exception as e:
        feedback["strengths"] = raw[:200] + "..."

    return feedback


def compile_performance_report(answers: list[str], questions: list[str], resume: str, jd: str) -> str:
    """
    Builds the final performance report after the entire mock interview session.
    Returns the report as a formatted string.
    """
    qa_lines: list[str] = []
    for i, (q, a) in enumerate(zip(questions, answers), 1):
        qa_lines.append(f"Q{i}: {q}")
        qa_lines.append(f"A{i}: {a if a.strip() else '(No answer provided)'}")
        qa_lines.append("")

    qa_text = "\n".join(qa_lines)

    prompt = REPORT_BUILD_TEMPLATE.format(
        resume=resume[:1000],
        jd=jd[:700],
        qa_text=qa_text[:2000]
    )

    # Initialize before try so Pylance knows it is always bound
    response = None
    try:
        response = client.chat.completions.create(
            model="mistral-7b-instruct",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.4
        )
    except Exception as e:
        raise RuntimeError(
            "❌ Could not connect to LM Studio. Please ensure it is running on port 1234."
            f" Original error: {e}"
        ) from e

    return response.choices[0].message.content.strip()
