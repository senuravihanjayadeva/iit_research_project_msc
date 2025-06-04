from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os

def get_recommendation(symptoms: str) -> str:
    prompt = ChatPromptTemplate.from_template(
    "You are an AI-powered dental assistant with access to expert-level dental knowledge. Based on the findings: {symptoms},"
    " provide a clear and compassionate explanation of these conditions, suggest appropriate treatment plans, and offer preventive advice."
    "\n\nYour response should be written in a friendly, easy-to-understand tone — as if guiding the patient calmly through their next steps."
    "\n\nAvoid saying 'I will treat' or anything that implies. Instead, focus on helpful actions the patient can take or discuss with their real dentist."
    )
    llm = ChatOpenAI(openai_api_key="", temperature=0.2)
    chain = prompt | llm
    result = chain.invoke({"symptoms": symptoms})
    return result.content
