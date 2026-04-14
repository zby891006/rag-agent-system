def build_messages(user_input: str, chat_history: list, working_context: str | None, max_turns: int):
    messages = []

    # 🔹 context（不進 memory）
    if working_context:
        messages.append({
            "role": "system",
            "content": f"""
You are an ESG and financial report assistant.

Use the following retrieved context as external reference.
Do NOT treat it as conversation memory.

Retrieved Context:
{working_context}
"""
        })

    # 🔹 memory（只保留對話）
    messages += chat_history[-max_turns * 2:]

    # 🔹 本輪 user
    messages.append({
        "role": "user",
        "content": user_input
    })

    return messages