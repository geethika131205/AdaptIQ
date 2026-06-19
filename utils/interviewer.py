from langchain_core.prompts import ChatPromptTemplate

from utils.llm import model
INTERVIEW_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a senior software engineer conducting
            a technical interview.

            Your goals:

            - Analyze resume context.
            - Analyze previous answers.
            - Ask follow-up questions when possible.
            - Probe depth of understanding.
            - Increase difficulty for strong answers.
            - Decrease difficulty for weak answers.
            - Ask exactly ONE question.
            - Do not explain.
            - Return only the next question.

            Conduct the interview like a real interviewer.
            """
        ),
        (
            "human",
            """
            Resume Context:

            {resume_context}


            Previous Interview History:

            {history}


            Generate the next interview question.
            """
        )
    ]
)


def format_history(history):

    if not history:
        return "No previous questions."

    text = ""

    for item in history:

        text += f"""
                    Question:
                {item['question']}

                Answer:
                {item['answer']}

                """

    return text


def generate_question(
    resume_context,
    history
):

    history_text = format_history(history)

    chain = INTERVIEW_PROMPT | model

    response = chain.invoke(
        {
            "resume_context": resume_context,
            "history": history_text
        }
    )

    return response.content