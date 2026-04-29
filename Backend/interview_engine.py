import os
from openai import OpenAI
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo

# Import extract_skills from match.py
try:
    from Backend.match import extract_skills
except ImportError:
    from match import extract_skills

client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)

# ─────────────────────────────────────────────────────────────────
# VECTOR DB SETUP (Self-Query Retriever)
# ─────────────────────────────────────────────────────────────────

CHROMA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "chroma_db"))
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

vectorstore = Chroma(
    collection_name="interview_questions",
    persist_directory=CHROMA_PATH,
    embedding_function=embeddings
)

metadata_field_info = [
    AttributeInfo(
        name="category",
        description="The category of the interview question (e.g., Machine Learning, Data Science, etc.)",
        type="string",
    ),
]
document_content_description = "Technical and behavioral interview questions"

llm_for_retriever = ChatOpenAI(
    model="mistral-7b-instruct",
    openai_api_base="http://localhost:1234/v1",
    openai_api_key="lm-studio",
    temperature=0
)

retriever = SelfQueryRetriever.from_llm(
    llm_for_retriever,
    vectorstore,
    document_content_description,
    metadata_field_info,
    verbose=True,
    search_kwargs={"k": 6}
)

# ─────────────────────────────────────────────────────────────────
# PROMPT TEMPLATES
# ─────────────────────────────────────────────────────────────────

QUESTION_BUILD_TEMPLATE = """You are a professional technical interviewer.

Based on the candidate's resume and the job description provided below, generate exactly 8 interview questions.

Rules:
- Questions 1-6 must be TECHNICAL: focused on skills, tools, and technologies mentioned in the resume and job description.
- Questions 7-8 must be BEHAVIORAL: focused on past experiences, problem-solving, and soft skills relevant to the role.
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
  "score": [Integer from 0 to 10] if it is a technical question, [Integer from 0 to 20] if it is a behavioral question,
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
    
    # 1. Extract skills from JD
    jd_skills = extract_skills(jd)
    skills_str = ", ".join(jd_skills) if jd_skills else "General technical skills"

    # 2. Retrieve 10 relevant questions from ChromaDB using SelfQueryRetriever
    try:
        retrieval_query = f"Retrieve 10 interview questions related to: {skills_str}"
        retrieved_docs = retriever.get_relevant_documents(retrieval_query)
        retrieved_context = "\n".join([f"- {doc.page_content}" for doc in retrieved_docs])
        print(f"✅ Retrieved {len(retrieved_docs)} reference questions from ChromaDB.")
        
    except Exception as e:
        print(f"⚠️ SelfQueryRetriever failed: {e}. Falling back to standard vector search.")
        try:
            standard_retriever = vectorstore.as_retriever(search_kwargs={"k": 10})
            retrieved_docs = standard_retriever.get_relevant_documents(skills_str)
            retrieved_context = "\n".join([f"- {doc.page_content}" for doc in retrieved_docs])
        except Exception as fallback_e:
            print(f"⚠️ Fallback vector search also failed: {fallback_e}")
            retrieved_context = "No reference questions retrieved."

    # 3. Construct the prompt for the final 8 questions
    prompt = f"""You are a professional technical interviewer.

Based on the candidate's resume, the job description, and the retrieved reference questions provided below, generate exactly 8 interview questions.

Reference Questions (use these for inspiration or direct use if highly relevant):
{retrieved_context}

Rules:
- Questions 1-6 must be TECHNICAL: focused on skills, tools, and technologies mentioned in the resume and job description. Use the reference questions to ensure high quality and relevance.
- Questions 7-8 must be BEHAVIORAL: focused on past experiences, problem-solving, and soft skills relevant to the role.
- Every question must be directly relevant to the candidate's specific profile and the job role.
- Do NOT generate generic or random questions.
- Do NOT repeat similar questions.
- Output ONLY a numbered list of 8 questions. No extra text, no introduction, no explanation.

Resume:
{resume[:1500]}

Job Description:
{jd[:1000]}

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

    # Initialize before try so Pylance knows it is always bound
    response = None
    try:
        response = client.chat.completions.create(
            model="mistral-7b-instruct",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
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
