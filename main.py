# === 載入套件 ===
from app.agent_build import build_agent
from dotenv import load_dotenv
load_dotenv()

THREAD_ID = "demo-user-001"

def stream_response(agent, user_input):
    stream = agent.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        config={"configurable": {"thread_id": THREAD_ID}}
    )

    prev = ""

    for chunk in stream:
        if "messages" in chunk:
            msg = chunk["messages"][-1]
            if msg.content:
                new = msg.content[len(prev):]
                print(new, end="", flush=True)
                prev = msg.content


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