# from langchain_google_genai import ChatGoogleGenerativeAI
# from dotenv import load_dotenv

# load_dotenv()

# # 建議獨立一個小模型
# llm = ChatGoogleGenerativeAI(
#     model="models/gemini-2.5-flash",
#     temperature=0
# )

# def classify_query(query: str) -> dict:

#     messages = [
#         {
#             "role": "system",
#             "content": (
#                 "You are a strict classifier.\n"
#                 "Classify the user query into one of: retrieval, memory, general.\n"
#                 "Return ONLY one word.\n"
#                 "No explanation."
#             )
#         },
#         {
#             "role": "user",
#             "content": f"Query: {query}"
#         }
#     ]

#     raw = llm.invoke(messages).content.strip().lower()

#     raw = raw.replace(".", "").strip()

#     if "retrieval" in raw:
#         route = "retrieval"
#     elif "memory" in raw:
#         route = "memory"
#     else:
#         route = "general"

#     return {
#         "route": route,
#         "raw": raw
#     }
    
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import json

load_dotenv()

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
                "Your job:\n"
                "1. Classify query into: retrieval, memory, general\n"
                "2. Decide if the query needs a company/entity to be understood\n\n"

                "Rules for need_entity:\n"
                "- true: if query contains pronouns or missing subject (e.g. it, its, that, 那個)\n"
                "- false: if query is complete or general knowledge\n\n"

                "Return ONLY valid JSON:\n"
                "{\n"
                '  "route": "retrieval | memory | general",\n'
                '  "need_entity": true | false\n'
                "}\n"
                "No explanation."
            )
        },
        {
            "role": "user",
            "content": f"Query: {query}"
        }
    ]

    raw = llm.invoke(messages).content.strip()

    # ===== parsing =====
    try:
        result = json.loads(raw)
        route = result.get("route", "general")
        need_entity = result.get("need_entity", False)

    except:
        # fallback（避免模型亂輸出）
        text = raw.lower()

        if "retrieval" in text:
            route = "retrieval"
        elif "memory" in text:
            route = "memory"
        else:
            route = "general"

        need_entity = any(k in text for k in ["it", "its", "that", "they"])

    return {
        "route": route,
        "need_entity": need_entity,
        "raw": raw
    }    