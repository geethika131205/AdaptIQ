from langchain_core.prompts import ChatPromptTemplate
from utils.llm import model


SKILL_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            Extract technical skills from the resume.

            Return only a comma separated list.

            Example:

            Python, SQL, Machine Learning, AWS
            """
        ),
        (
            "human",
            "{resume_text}"
        )
    ]
)


def extract_skills(resume_text):

    chain = SKILL_PROMPT | model

    response = chain.invoke(
        {
            "resume_text": resume_text
        }
    )

    return response.content.split(",")