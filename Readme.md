# AI Interview Coach

An adaptive, AI-powered technical interview simulator. Upload a resume, and the app extracts your skills, indexes it with FAISS for semantic retrieval, conducts a context-aware mock interview that adapts question difficulty to your answers, and evaluates each response in real time.

Built with **Streamlit**, **LangChain**, **Groq** (Llama 3.3 70B), and **FAISS**.

---

## Features

- **Resume parsing** — Upload a PDF resume; text is extracted and chunked automatically.
- **Semantic indexing** — Resume chunks are embedded using `all-MiniLM-L6-v2` and indexed with FAISS; a similarity search retrieves the most relevant context (skills, projects, experience) before each interview question.
- **Skill extraction** — Technical skills are pulled directly from resume content using an LLM, with no hardcoded skill lists.
- **Adaptive interview** — Each question is generated from the FAISS-retrieved resume context *and* your full answer history, so the interviewer can increase difficulty after strong answers, probe deeper, or ease off after weak ones.
- **Real-time evaluation** — Every answer is critiqued (technical accuracy, communication, depth) immediately after submission.
- **Full session history** — All questions, answers, and evaluations are logged and viewable in an expandable history panel.
- **Modern dashboard UI** — Dark-themed SaaS-style layout with a sidebar for upload/progress and a main workspace for skills, interview flow, and evaluation results.

No skills, questions, or scores are hardcoded anywhere in the app — every value displayed comes from the backend LLM functions.

---

## Project Structure

```
.
├── app.py                     # Streamlit frontend — orchestrates the full interview flow
├── utils/
│   ├── llm.py                 # Shared Groq LLM client (Llama 3.3 70B via LangChain)
│   ├── pdf_parser.py          # PDF text extraction + chunking
│   ├── skill_extractor.py     # LLM-based skill extraction from resume text
│   ├── interviewer.py         # Adaptive question generation based on resume context + history
│   ├── evaluator.py           # LLM-based answer evaluation
│   └── vector_store.py        # FAISS vector store — embedding, indexing, and context retrieval
├── .env                        # Holds GROQ_API_KEY (not committed)
└── README.md
```

---

## How It Works

1. **Upload & Process** — The resume PDF is parsed (`pdf_parser.extract_chunks`) into full text and overlapping chunks.
2. **Semantic Indexing** — Chunks are embedded with `sentence-transformers/all-MiniLM-L6-v2` and stored in a FAISS index (`vector_store.create_vectorstore`). A similarity search against `"skills projects experience technologies"` retrieves the top 5 most relevant chunks, joined into a compact `resume_context` (`vector_store.get_resume_context`).
3. **Skill Extraction** — The full resume text (not the excerpt) is sent to the skill extractor (`skill_extractor.extract_skills`) to ensure no skills are missed, returning a list rendered as pills in the UI.
4. **Start Interview** — The first question is generated (`interviewer.generate_question`) using `resume_context` as context. No prior history exists yet, so the question is grounded purely in the retrieved resume excerpt.
5. **Submit Answer** — Your answer is evaluated (`evaluator.evaluate_answer`) against the current question, returning free-form feedback on accuracy, communication, and depth.
6. **Next Question** — The question/answer/evaluation triple is appended to session history, and the next question is generated using `resume_context` *and* the entire conversation so far — making each subsequent question adaptive to how you've performed.
7. **Repeat** — Steps 5–6 continue for as long as you want. All state is held in Streamlit's `session_state`, so progress persists across reruns within a browser session.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | [Streamlit](https://streamlit.io) |
| LLM orchestration | [LangChain](https://www.langchain.com) |
| LLM inference | [Groq](https://groq.com) — `llama-3.3-70b-versatile` |
| PDF parsing | [pypdf](https://pypdf.readthedocs.io) |
| Text chunking | LangChain `RecursiveCharacterTextSplitter` |
| Vector store | [FAISS](https://github.com/facebookresearch/faiss) via `langchain_community` |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` via `HuggingFaceEmbeddings` |

---

## Setup

### 1. Clone and install dependencies

```bash
git clone <your-repo-url>
cd <project-folder>
pip install -r requirements.txt
```

Required packages:

```
streamlit
python-dotenv
langchain
langchain-groq
langchain-community
langchain-text-splitters
pypdf
faiss-cpu
sentence-transformers
```

> **Note:** `sentence-transformers` will download the `all-MiniLM-L6-v2` model (~80 MB) on first run. Subsequent runs use the cached model.

### 2. Configure your API key

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Get a free key at [console.groq.com/keys](https://console.groq.com/keys).

### 3. Run the app

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## Usage

1. Open the app and upload a resume PDF from the sidebar.
2. Click **Process Resume** — the resume is parsed, semantically indexed with FAISS, and extracted skills appear as pills in the main panel.
3. Click **Start Interview** to receive your first question, grounded in the most relevant parts of your resume.
4. Type your answer and click **Submit Answer** to see your evaluation.
5. Click **Next Question** to receive an adaptive follow-up based on your resume context and performance so far.
6. Review the full question/answer/evaluation history at any point in the **Interview History** panel.
7. Use **Reset Session** in the sidebar to clear progress and start over with a new resume.

