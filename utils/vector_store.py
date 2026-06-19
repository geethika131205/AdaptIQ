from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


def create_vectorstore(chunks):

    db = FAISS.from_texts(
        texts=chunks,
        embedding=embedding_model
    )

    return db


def get_resume_context(db):

    docs = db.similarity_search(
        "skills projects experience technologies",
        k=5
    )

    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )

    return context