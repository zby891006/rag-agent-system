# === 載入套件 ===
from app.agent_build import build_agent
from dotenv import load_dotenv
from app.callbacks import DebugHandler
from control.router import classify_query
from control.controller import run_retrieval_pipeline
from utils.formatter import format_docs_for_llm
import re

load_dotenv()

# === Memory 設定 ===
chat_history = []
MAX_TURNS = 2  # 保留最近 2 輪（user + assistant）


def clean_input(text: str) -> str:
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    return text.strip().lower()


# def chat():

#     agent = build_agent()

#     print("=== ESG / Finance RAG Agent (Controlled) ===")
#     print("Type 'exit' to quit.\n")

#     global chat_history

#     while True:
#         user_input_raw = input("You: ")

#         cleaned = clean_input(user_input_raw)

#         if any(cmd in cleaned for cmd in ["exit", "quit"]):
#             print("Bye.")
#             break

#         user_input = user_input_raw.strip()

#         handler = DebugHandler()

#         # ==============================
#         # 🔹 Retrieval pipeline（不變）
#         # ==============================
#         docs = run_retrieval_pipeline(user_input)

#         if not docs:
#             print("\nAssistant: No relevant information found.\n")
#             continue

#         context = format_docs_for_llm(docs)

#         # ==============================
#         # 🔹 Prompt（加入 memory 規則）
#         # ==============================
#         prompt = f"""
# You are an ESG and financial report assistant.

# Answer the question ONLY based on the provided context.

# If the context is insufficient, say:
# "Insufficient information in the retrieved documents."

# You may use previous conversation ONLY if:
# - it is directly relevant
# - and does NOT conflict with the retrieved context

# If there is any conflict, ALWAYS prioritize the retrieved context.

# ----------------------
# Question:
# {user_input}

# ----------------------
# Context:
# {context}
# """

#         # ==============================
#         # 🔹 組 messages（關鍵）
#         # ==============================
#         messages = chat_history[-MAX_TURNS * 2:] + [
#             {"role": "user", "content": prompt}
#         ]

#         response = agent.invoke(
#             {
#                 "messages": messages
#             },
#             config={
#                 "callbacks": [handler]
#             }
#         )

#         assistant_messages = response["messages"]

#         content = assistant_messages[-1].content
#         text = content[0]["text"] if isinstance(content, list) else content

#         print(f"\nAssistant: {text}\n")

#         # ==============================
#         # 🔹 更新 memory
#         # ==============================
#         chat_history.append({
#             "role": "user",
#             "content": user_input
#         })

#         chat_history.append({
#             "role": "assistant",
#             "content": text
#         })

#         # 控制長度（避免爆掉）
#         if len(chat_history) > MAX_TURNS * 2:
#             chat_history = chat_history[-MAX_TURNS * 2:]


# if __name__ == "__main__":
#     chat()

def chat():

    agent = build_agent()

    print("=== ESG / Finance RAG Agent (Controlled) ===")
    print("Type 'exit' to quit.\n")

    global chat_history

    while True:
        user_input_raw = input("You: ")

        cleaned = clean_input(user_input_raw)

        if any(cmd in cleaned for cmd in ["exit", "quit"]):
            print("Bye.")
            break

        user_input = user_input_raw.strip()

        handler = DebugHandler()

        # ==============================
        # 🔹 🧠 Router（關鍵新增）
        # ==============================
        router_result = classify_query(user_input)
        route = router_result["route"]

        print(f"\n[ROUTER] route = {route}")
        print(f"[ROUTER RAW] {router_result['raw']}")

        # ==============================
        # 🔹 Retrieval（有條件執行）
        # ==============================
        if route == "retrieval":
            docs = run_retrieval_pipeline(user_input)

            if not docs:
                print("\nAssistant: No relevant information found.\n")
                continue

            context = format_docs_for_llm(docs)
        else:
            docs = None
            context = None

        # ==============================
        # 🔹 Prompt（支援 memory / no context）
        # ==============================
        if context:
            prompt = f"""
        You are an ESG and financial report assistant.

        Answer the question ONLY based on the provided context.

        If the context is insufficient, say:
        "Insufficient information in the retrieved documents."

        You may use previous conversation ONLY if:
        - it is directly relevant
        - and does NOT conflict with the retrieved context

        If there is any conflict, ALWAYS prioritize the retrieved context.

        ----------------------
        Question:
        {user_input}

        ----------------------
        Context:
        {context}
        """
        else:
            prompt = f"""
        You are an ESG and financial report assistant.

        No external documents are provided.

        Answer the question based on the conversation history only.

        Be concise and do NOT hallucinate unknown facts.

        ----------------------
        Question:
        {user_input}
            """

        # ==============================
        # 🔹 組 messages（memory）
        # ==============================
        messages = chat_history[-MAX_TURNS * 2:] + [
            {"role": "user", "content": prompt}
        ]

        response = agent.invoke(
            {
                "messages": messages
            },
            config={
                "callbacks": [handler]
            }
        )

        assistant_messages = response["messages"]

        content = assistant_messages[-1].content
        text = content[0]["text"] if isinstance(content, list) else content

        print(f"\nAssistant: {text}\n")

        # ==============================
        # 🔹 更新 memory
        # ==============================
        chat_history.append({
            "role": "user",
            "content": user_input
        })

        chat_history.append({
            "role": "assistant",
            "content": text
        })

        # 控制長度
        if len(chat_history) > MAX_TURNS * 2:
            chat_history = chat_history[-MAX_TURNS * 2:]
            
if __name__ == "__main__":
    chat()