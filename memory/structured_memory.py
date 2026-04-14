from langchain_google_genai import ChatGoogleGenerativeAI
import json

# 小模型即可
llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.5-flash",
    temperature=0
)

# 全域 memory（簡單版）
structured_memory = {
    "company": None,
    "topic": None
}


# def update_structured_memory(user_input: str, assistant_output: str):
#     """
#     從對話中抽取結構化資訊
#     """

#     prompt = f"""
# Extract structured information from the conversation.

# User: {user_input}
# Assistant: {assistant_output}

# Return ONLY JSON:
# {{
#   "company": string or null,
#   "topic": string or null
# }}
# """

#     raw = llm.invoke(prompt).content.strip()

#     try:
#         data = json.loads(raw)

#         if data.get("company"):
#             structured_memory["company"] = data["company"]

#         if data.get("topic"):
#             structured_memory["topic"] = data["topic"]

#     except:
#         pass  # parsing fail 就忽略

#     return structured_memory


def get_structured_memory():
    return structured_memory

def update_structured_memory(chat_history: list):
    """
    每輪更新 memory（使用最近對話）
    """

    recent = chat_history[-4:]  # 最近兩輪

    convo = ""
    for msg in recent:
        role = msg["role"]
        content = msg["content"]
        convo += f"{role.upper()}: {content}\n"

    prompt = f"""
Extract structured information from the conversation.

Conversation:
{convo}

Return ONLY JSON:
{{
  "company": string or null,
  "topic": string or null
}}
"""

    raw = llm.invoke(prompt).content.strip()

    try:
        data = json.loads(raw)

        if data.get("company"):
            structured_memory["company"] = data["company"]

        if data.get("topic"):
            structured_memory["topic"] = data["topic"]

    except:
        pass

    return structured_memory
