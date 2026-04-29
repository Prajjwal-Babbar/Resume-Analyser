# 🧠 ResumeAnalyzer

A local, AI-powered career assistant that analyzes resumes against job descriptions and conducts mock interviews — all running **100% offline** using a local LLM (Mistral-7B via LM Studio).

---

## ✨ Features

| Feature | Description |
|---|---|
| 📄 **Resume Analysis** | Upload your resume (PDF/DOCX/TXT) and a job description to get a match score, skill gaps, and an actionable improvement roadmap |
| 🎯 **Match Scoring** | Semantic similarity scoring using sentence-transformers + FAISS |
| 🎤 **Mock Interviewer** | Interactive AI mock interview with 8 tailored questions (6 Technical, 2 Behavioral) |
| 📂 **ChromaDB Integration** | Stores and retrieves relevant interview questions based on extracted skills for high-quality practice |
| 🧠 **Detailed Roadmap** | Generates a personalized 400-600 word career strategist report |
| 🔒 **100% Local** | No cloud API keys needed — runs on your machine via [LM Studio](https://lmstudio.ai/) |

---

## 🏗️ Project Structure

```
ResumeAnalyzer/
├── Backend/
│   ├── MyLLM.py            # LM Studio / OpenAI-compatible LLM client
│   ├── RAG.py              # Retrieval-Augmented Generation pipeline
│   ├── match.py            # Resume ↔ JD semantic matching
│   ├── parser.py           # PDF / DOCX text extraction
│   └── interview_engine.py # Mock interview session logic
├── Front end/
│   ├── Home.py             # Streamlit main page – resume analysis
│   └── pages/
│       └── 1_Mock_Interviewer.py  # Mock interview page
├── chroma_db/              # Vector database for interview questions
├── data/                   # Sample resume & JD (for quick testing)
├── requirements.txt
└── .gitignore
```

---

## 🚀 Getting Started

### 1. Prerequisites

- Python 3.10+
- [LM Studio](https://lmstudio.ai/) installed and running locally with **Mistral-7B-Instruct** loaded
  - Default server: `http://localhost:1234`

### 2. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ResumeAnalyzer.git
cd ResumeAnalyzer
```

### 3. Create a virtual environment & install dependencies

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Start LM Studio

Open LM Studio → load **Mistral-7B-Instruct** → click **Start Server** (listens on port 1234).

### 5. Run the app

```bash
cd "Front end"
streamlit run Home.py
```

---

## 📸 Screenshots

![Project Demo](Pics\SampleImage.png)

---

## 🛠️ Tech Stack

- **Frontend:** [Streamlit](https://streamlit.io/)
- **LLM Backend:** [LM Studio](https://lmstudio.ai/) + Mistral-7B-Instruct (OpenAI-compatible API)
- **Semantic Search:** `sentence-transformers` + `faiss-cpu` + `chromadb`
- **Document Parsing:** `pdfplumber`, `python-docx`
- **Visualisation:** `plotly`

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.

---

## 📄 License

[MIT](https://choosealicense.com/licenses/mit/)
