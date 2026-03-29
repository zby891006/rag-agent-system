# === 載入套件 ===
from app.agent_build import build_agent
from dotenv import load_dotenv
from app.callbacks import DebugHandler
load_dotenv()

THREAD_ID = "demo-user-001"



# def stream_response(agent, user_input):
#     stream = agent.stream(
#         {"messages": [{"role": "user", "content": user_input}]},
#         config={"configurable": {"thread_id": THREAD_ID}}
#     )

#     prev = ""

#     for chunk in stream:
#         if "messages" in chunk:
#             msg = chunk["messages"][-1]
#             if msg.content:
#                 new = msg.content[len(prev):]
#                 print(new, end="", flush=True)
#                 prev = msg.content


# === CLI 對話介面 ===
# def chat():
#     agent = build_agent()
    
#     print("=== ESG / Finance RAG Agent ===")
#     print("Type 'exit' to quit.\n")

#     while True:
#         user_input = input("You: ").strip()
#         if user_input.lower() in {"exit", "quit"}:
#             print("Bye.")
#             break

#         response = agent.invoke(
#             {
#                 "messages": [
#                     {"role": "user", "content": user_input}
#                 ]
#             },
#             config={
#                 "configurable": {
#                     "thread_id": THREAD_ID
#                 }
#             }
#         )

#         assistant_messages = response["messages"]
#         # print(f"\nAssistant: {assistant_messages[-1].content}\n")
        
#         content = assistant_messages[-1].content

#         text = content[0]["text"] if isinstance(content, list) else content

#         print(f"\nAssistant: {text}\n")
from app.callbacks import DebugHandler  # 確保有 import

def chat():
    agent = build_agent()
    
    print("=== ESG / Finance RAG Agent ===")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Bye.")
            break

        handler = DebugHandler()   # ⭐ 每次建立

        response = agent.invoke(
            {
                "messages": [
                    {"role": "user", "content": user_input}
                ]
            },
            config={
                "callbacks": [handler],   # ⭐ 加這行（關鍵）
                "configurable": {
                    "thread_id": THREAD_ID
                }
            }
        )

        assistant_messages = response["messages"]

        content = assistant_messages[-1].content
        text = content[0]["text"] if isinstance(content, list) else content

        print(f"\nAssistant: {text}\n")

if __name__ == "__main__":
    chat()