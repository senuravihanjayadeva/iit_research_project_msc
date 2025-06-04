from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os

def get_recommendation(symptoms: str) -> str:
    prompt = ChatPromptTemplate.from_template(
        "You are a licensed dentist. When you examine you found that patient has: {symptoms}. tooth"
        "Provide a professional treatment recommendation."
    )
    llm = ChatOpenAI(openai_api_key="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", temperature=0.2)
    chain = prompt | llm
    result = chain.invoke({"symptoms": symptoms})
    return result.content
