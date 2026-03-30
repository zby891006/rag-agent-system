from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from tools.retrieve_hyde import retrieve_hyde
from tools.retrieve_simple import retrieve_simple
from tools.calculator import calculator_tool



def build_agent():
    
    model = ChatGoogleGenerativeAI(
    model="models/gemini-2.5-flash",
    temperature=0,
    
    )

    return create_agent(
        model=model,
        tools=[retrieve_simple, calculator_tool],
        system_prompt = (
            "You are an internal business AI assistant for ESG and finance documents.\n\n"

            "You have access to tools for retrieving internal knowledge and performing calculations.\n\n"

            "RULES:\n"

            "1. For any question involving company data (financial, ESG, metrics):\n"
            "- You MUST obtain the information using available retrieval tools\n"
            "- Do NOT rely on your own memory or assumptions\n"
            "- If multiple retrieval methods are available, choose the most appropriate one\n\n"

            "2. For any numerical calculation:\n"
            "- You MUST use the calculator tool\n"
            "- NEVER perform arithmetic yourself\n\n"

            "3. General behavior:\n"
            "- Be concise and factual\n"
            "- Do not ask the user for data that can be retrieved using tools\n"
        ),
    )