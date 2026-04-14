from app.agent_build import build_agent
from dotenv import load_dotenv
from app.callbacks import DebugHandler

from memory.structured_memory import (
    update_structured_memory,
    get_structured_memory
)

from memory.session_state import SessionState
from control.query_processor import process_query
from prompt.message_builder import build_messages
from utils.text import clean_input

load_dotenv()


def extract_text(response):
    content = response["messages"][-1].content
    return content[0]["text"] if isinstance(content, list) else content


def chat():
    agent = build_agent()
    state = SessionState()

    print("=== ESG / Finance RAG Agent ===")
    print("Type 'exit' to quit.\n")

    while True:
        user_input_raw = input("You: ")
        cleaned = clean_input(user_input_raw)

        if any(cmd in cleaned for cmd in ["exit", "quit"]):
            print("Bye.")
            break

        user_input = user_input_raw.strip()
        handler = DebugHandler()

        # ==============================
        # 🔹 Memory
        # ==============================
        memory = get_structured_memory()

        # ==============================
        # 🔹 Query Process（🔥抽出來）
        # ==============================
        context, router_result = process_query(user_input, memory)

        print(f"\n[ROUTER] route = {router_result['route']}")
        print(f"[ROUTER RAW] {router_result['raw']}")

        state.working_context = context

        # ==============================
        # 🔹 Build Prompt
        # ==============================
        messages = build_messages(
            user_input,
            state.chat_history,
            state.working_context,
            state.max_turns
        )

        # ==============================
        # 🔹 LLM
        # ==============================
        response = agent.invoke(
            {"messages": messages},
            config={"callbacks": [handler]}
        )

        text = extract_text(response)

        print(f"\nAssistant: {text}\n")

        # ==============================
        # 🔹 Update Memory
        # ==============================
        state.update_history(user_input, text)

        updated_memory = update_structured_memory(state.chat_history)
        print(f"[MEMORY] {updated_memory}")


if __name__ == "__main__":
    chat()
# from app.agent_build import build_agent
# from dotenv import load_dotenv
# from app.callbacks import DebugHandler
# from control.router import classify_query
# from control.controller import run_retrieval_pipeline
# from utils.formatter import format_docs_for_llm
# from memory.structured_memory import (
#     update_structured_memory,
#     get_structured_memory
# )
# import re

# load_dotenv()

# chat_history = []
# MAX_TURNS = 2
# working_context = None


# def clean_input(text: str) -> str:
#     text = re.sub(r"[^\x00-\x7F]+", " ", text)
#     return text.strip().lower()


# def build_messages(user_input: str, chat_history: list, working_context: str | None):
#     messages = []

#     # 檢索內容只放 system prompt，不放進 memory
#     if working_context:
#         messages.append({
#             "role": "system",
#             "content": f"""
#         You are an ESG and financial report assistant.

#         Use the following retrieved context as external reference.
#         Do NOT treat it as conversation memory.

#         Retrieved Context:
#         {working_context}
#         """
#         })

#     # memory 只保留對話
#     messages += chat_history[-MAX_TURNS * 2:]

#     # 本輪使用者問題
#     messages.append({
#         "role": "user",
#         "content": user_input
#     })

#     return messages


# def chat():
#     global chat_history, working_context

#     agent = build_agent()

#     print("=== ESG / Finance RAG Agent ===")
#     print("Type 'exit' to quit.\n")

#     while True:
#         user_input_raw = input("You: ")
#         cleaned = clean_input(user_input_raw)

#         if any(cmd in cleaned for cmd in ["exit", "quit"]):
#             print("Bye.")
#             break

#         user_input = user_input_raw.strip()
#         handler = DebugHandler()

#         # router 決定是否重查
#         router_result = classify_query(user_input)
#         route = router_result["route"]

#         print(f"\n[ROUTER] route = {route}")
#         print(f"[ROUTER RAW] {router_result['raw']}")

#         # 只有 router 說要查，才更新 working_context
#         if route == "retrieval":
#             docs = run_retrieval_pipeline(user_input)

#             if docs:
#                 working_context = format_docs_for_llm(docs)
#             else:
#                 working_context = None

#         messages = build_messages(user_input, chat_history, working_context)

#         response = agent.invoke(
#             {"messages": messages},
#             config={"callbacks": [handler]}
#         )

#         assistant_messages = response["messages"]
#         content = assistant_messages[-1].content
#         text = content[0]["text"] if isinstance(content, list) else content

#         print(f"\nAssistant: {text}\n")

#         # memory 只存 user / assistant
#         chat_history.append({
#             "role": "user",
#             "content": user_input
#         })
#         chat_history.append({
#             "role": "assistant",
#             "content": text
#         })

#         if len(chat_history) > MAX_TURNS * 2:
#             chat_history = chat_history[-MAX_TURNS * 2:]


# if __name__ == "__main__":
#     chat()