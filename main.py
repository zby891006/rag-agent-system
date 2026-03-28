# === 載入套件 ===
from agent.agent_build import build_agent


THREAD_ID = "demo-user-001"




# === CLI 對話介面 ===
def chat():
    agent = build_agent()
    
    print("=== ESG / Finance RAG Agent ===")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Bye.")
            break

        response = agent.invoke(
            {
                "messages": [
                    {"role": "user", "content": user_input}
                ]
            },
            config={
                "configurable": {
                    "thread_id": THREAD_ID
                }
            }
        )

        assistant_messages = response["messages"]
        print(f"\nAssistant: {assistant_messages[-1].content}\n")


if __name__ == "__main__":
    chat()