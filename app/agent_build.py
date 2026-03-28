from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from tools.retrieval import retrieve_docs
from tools.calculator import calculator

model = ChatGoogleGenerativeAI(
    model="models/gemini-2.5-flash",
    temperature=0
)

def build_agent():
    
    model = ChatGoogleGenerativeAI(
    model="models/gemini-2.5-flash",
    temperature=0
    )

    return create_agent(
        model=model,
        tools=[retrieve_docs, calculator],
        system_prompt=(
            "You are an internal business AI assistant for ESG and finance documents. "
            "Use retrieve_docs for internal knowledge and calculator for math. "
            "Be concise and factual."
        ),
    )