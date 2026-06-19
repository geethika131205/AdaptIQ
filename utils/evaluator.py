from langchain_core.prompts import ChatPromptTemplate

from utils.llm import model


EVALUATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are an expert interviewer.

            Evaluate the candidate answer.

            Score:

            - Technical Accuracy (0-10)
            - Communication (0-10)
            - Depth (0-10)

            Give constructive feedback.

            Return concise results.
            """
        ),
        (
            "human",
            """
            Question:

            {question}


            Candidate Answer:

            {answer}
            """
        )
    ]
)


def evaluate_answer(question,answer):

    chain = EVALUATION_PROMPT | model

    response = chain.invoke(
        {
            "question": question,
            "answer": answer
        }
    )

    return response.content