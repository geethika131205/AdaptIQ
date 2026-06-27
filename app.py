import streamlit as st

from utils.pdf_parser import extract_chunks
from utils.skill_extractor import extract_skills
from utils.interviewer import generate_question
from utils.evaluator import evaluate_answer
from utils.vector_store import create_vectorstore, get_resume_context


# ----------------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Interview Coach",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ----------------------------------------------------------------------------
# Styling — modern SaaS dashboard look
# ----------------------------------------------------------------------------
st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(180deg, #0f1117 0%, #14161f 100%);
        }

        section[data-testid="stSidebar"] {
            background: #11131a;
            border-right: 1px solid rgba(255,255,255,0.06);
        }

        h1, h2, h3, h4 {
            font-family: "Inter", "Segoe UI", sans-serif;
            color: #f4f4f6;
        }

        p, span, label, li {
            color: #c7c9d3;
        }

        .card {
            background: #181a23;
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 14px;
            padding: 1.4rem 1.6rem;
            margin-bottom: 1.1rem;
            box-shadow: 0 4px 18px rgba(0,0,0,0.25);
        }

        .skill-pill {
            display: inline-block;
            background: rgba(99, 102, 241, 0.15);
            color: #a5b4fc;
            border: 1px solid rgba(99, 102, 241, 0.35);
            padding: 0.3rem 0.9rem;
            border-radius: 999px;
            margin: 0.25rem 0.35rem 0.25rem 0;
            font-size: 0.85rem;
            font-weight: 500;
        }

        .question-box {
            background: linear-gradient(135deg, rgba(99,102,241,0.12), rgba(56,189,248,0.08));
            border: 1px solid rgba(99,102,241,0.3);
            border-radius: 14px;
            padding: 1.4rem 1.6rem;
            font-size: 1.05rem;
            color: #f4f4f6;
            margin-bottom: 1rem;
        }

        .metric-card {
            background: #181a23;
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 12px;
            padding: 1rem;
            text-align: center;
        }

        .metric-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #a5b4fc;
        }

        .metric-label {
            font-size: 0.8rem;
            color: #9296a6;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }

        .history-item {
            background: #14161f;
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 10px;
            padding: 0.9rem 1.1rem;
            margin-bottom: 0.7rem;
        }

        .stButton > button {
            background: linear-gradient(135deg, #6366f1, #38bdf8);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.55rem 1.2rem;
            font-weight: 600;
            width: 100%;
        }

        .stButton > button:hover {
            opacity: 0.9;
            color: white;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------------
# Session state initialization
# ----------------------------------------------------------------------------
defaults = {
    "resume_text": None,
    "resume_chunks": None,
    "resume_context": None,   # FAISS-retrieved excerpt used as interview context
    "skills": None,
    "interview_started": False,
    "current_question": None,
    "history": [],          # list of {"question": ..., "answer": ..., "evaluation": ...}
    "last_evaluation": None,
    "questions_asked": 0,
    "questions_evaluated": 0,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def reset_interview_state():
    """Reset everything tied to a resume/interview session."""
    st.session_state.resume_text = None
    st.session_state.resume_chunks = None
    st.session_state.resume_context = None
    st.session_state.skills = None
    st.session_state.interview_started = False
    st.session_state.current_question = None
    st.session_state.history = []
    st.session_state.last_evaluation = None
    st.session_state.questions_asked = 0
    st.session_state.questions_evaluated = 0


# ----------------------------------------------------------------------------
# Sidebar — Upload & Progress
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🧠 AI Interview Coach")
    st.markdown("Upload a resume to begin an adaptive technical interview.")

    st.markdown("---")
    st.markdown("### 📄 Resume Upload")

    uploaded_file = st.file_uploader(
        "Upload resume (PDF)",
        type=["pdf"],
        help="Your resume is parsed locally to extract context and skills.",
    )

    if uploaded_file is not None:
        if st.button("Process Resume", use_container_width=True):
            with st.spinner("Extracting text from resume..."):
                reset_interview_state()

                text, chunks = extract_chunks(uploaded_file)
                st.session_state.resume_text = text
                st.session_state.resume_chunks = chunks

            with st.spinner("Indexing resume for semantic search..."):
                db = create_vectorstore(chunks)
                resume_context = get_resume_context(db)
                st.session_state.resume_context = resume_context

            with st.spinner("Extracting skills..."):
                skills = extract_skills(text)
                # Clean whitespace/empties without inventing or hardcoding any skill
                cleaned_skills = [s.strip() for s in skills if s and s.strip()]
                st.session_state.skills = cleaned_skills

            st.success("Resume processed successfully.")

    st.markdown("---")
    st.markdown("### 📊 Progress")

    if st.session_state.resume_text:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{st.session_state.questions_asked}</div>
                <div class="metric-label">Questions Asked</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("")
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{st.session_state.questions_evaluated}</div>
                <div class="metric-label">Answers Evaluated</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.caption("Upload and process a resume to see progress.")

    st.markdown("---")
    if st.button("🔄 Reset Session", use_container_width=True):
        reset_interview_state()
        st.rerun()


# ----------------------------------------------------------------------------
# Main area
# ----------------------------------------------------------------------------
st.markdown("# Interview Workspace")

if not st.session_state.resume_text:
    st.markdown(
        """
        <div class="card">
            <h3>👋 Welcome</h3>
            <p>Upload a resume PDF from the sidebar and click
            <b>Process Resume</b> to extract skills and begin
            an adaptive technical interview.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()


# ---- Extracted Skills -------------------------------------------------------
st.markdown("### 🛠️ Extracted Skills")

if st.session_state.skills:
    pills_html = "".join(
        f'<span class="skill-pill">{skill}</span>'
        for skill in st.session_state.skills
    )
    st.markdown(f'<div class="card">{pills_html}</div>', unsafe_allow_html=True)
else:
    st.markdown(
        '<div class="card">No skills were extracted from this resume.</div>',
        unsafe_allow_html=True,
    )

st.markdown("---")

# ---- Interview Controls ------------------------------------------------------
left, right = st.columns([2, 1], gap="large")

with left:
    st.markdown("### 💬 Interview")

    if not st.session_state.interview_started:
        if st.button("🚀 Start Interview", use_container_width=True):
            with st.spinner("Preparing your first question..."):
                question = generate_question(
                    st.session_state.resume_context,
                    st.session_state.history,
                )
                st.session_state.current_question = question
                st.session_state.interview_started = True
                st.session_state.questions_asked += 1
            st.rerun()
    else:
        if st.session_state.current_question:
            st.markdown(
                f'<div class="question-box"><b>Question {st.session_state.questions_asked}:</b><br>{st.session_state.current_question}</div>',
                unsafe_allow_html=True,
            )

            answer = st.text_area(
                "Your answer",
                key=f"answer_input_{st.session_state.questions_asked}",
                height=180,
                placeholder="Type your answer here...",
            )

            submit_col, next_col = st.columns(2)

            with submit_col:
                submit_clicked = st.button(
                    "✅ Submit Answer", use_container_width=True
                )

            with next_col:
                next_clicked = st.button(
                    "➡️ Next Question",
                    use_container_width=True,
                    disabled=st.session_state.last_evaluation is None
                    or (
                        st.session_state.history
                        and st.session_state.history[-1]["question"]
                        != st.session_state.current_question
                    ),
                )

            if submit_clicked:
                if not answer or not answer.strip():
                    st.warning("Please provide an answer before submitting.")
                else:
                    with st.spinner("Evaluating your answer..."):
                        evaluation = evaluate_answer(
                            st.session_state.current_question, answer
                        )

                        st.session_state.history.append(
                            {
                                "question": st.session_state.current_question,
                                "answer": answer,
                                "evaluation": evaluation,
                            }
                        )
                        st.session_state.last_evaluation = evaluation
                        st.session_state.questions_evaluated += 1
                    st.rerun()

            if next_clicked:
                with st.spinner("Generating adaptive follow-up question..."):
                    next_question = generate_question(
                        st.session_state.resume_context,
                        st.session_state.history,
                    )
                    st.session_state.current_question = next_question
                    st.session_state.last_evaluation = None
                    st.session_state.questions_asked += 1
                st.rerun()

with right:
    st.markdown("### 📈 Latest Evaluation")

    if st.session_state.last_evaluation:
        st.markdown(
            f'<div class="card">{st.session_state.last_evaluation}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="card">Submit an answer to see evaluation results here.</div>',
            unsafe_allow_html=True,
        )

st.markdown("---")

# ---- Question & Answer History ----------------------------------------------
st.markdown("### 🗂️ Interview History")

if st.session_state.history:
    for i, item in enumerate(reversed(st.session_state.history), start=1):
        idx = len(st.session_state.history) - i + 1
        with st.expander(f"Q{idx}: {item['question'][:80]}"):
            st.markdown(f"**Question:**\n\n{item['question']}")
            st.markdown(f"**Answer:**\n\n{item['answer']}")
            st.markdown(f"**Evaluation:**\n\n{item['evaluation']}")
else:
    st.markdown(
        '<div class="card">No interview history yet. Start the interview to begin.</div>',
        unsafe_allow_html=True,
    )
