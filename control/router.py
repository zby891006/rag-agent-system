from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

# 建議獨立一個小模型（也可以共用）
llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.5-flash",
    temperature=0
)

def classify_query(query: str) -> dict:

    messages = [
        {
            "role": "system",
            "content": (
                "You are a strict classifier.\n"
                "Classify the user query into one of: retrieval, memory, general.\n"
                "Return ONLY one word.\n"
                "No explanation."
            )
        },
        {
            "role": "user",
            "content": f"Query: {query}"
        }
    ]

    raw = llm.invoke(messages).content.strip().lower()

    raw = raw.replace(".", "").strip()

    if "retrieval" in raw:
        route = "retrieval"
    elif "memory" in raw:
        route = "memory"
    else:
        route = "general"

    return {
        "route": route,
        "raw": raw
    }
    
    
# def classify_query(query: str) -> str:

#     prompt = f"""..."""

#     result = llm.invoke(prompt).content.strip().lower()

#     if "retrieval" in result:
#         route = "retrieval"
#     elif "memory" in result:
#         route = "memory"
#     else:
#         route = "general"

#     print("\n[ROUTER]")
#     print("Query:", query)
#     print("Decision:", route)

#     return route