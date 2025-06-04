from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os

def get_recommendation(symptoms: str) -> str:
    prompt = ChatPromptTemplate.from_template(
        "You are a licensed dentist. When you examine you found that patient has: {symptoms}. tooth"
        "Provide a professional treatment recommendation."
    )
    llm = ChatOpenAI(openai_api_key="", temperature=0.2)
    chain = prompt | llm
    result = chain.invoke({"symptoms": symptoms})
    return result.content
