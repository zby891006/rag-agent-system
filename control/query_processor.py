from control.router import classify_query
from control.controller import run_retrieval_pipeline
from utils.formatter import format_docs_for_llm

def process_query(user_input: str, memory: dict):

    router_result = classify_query(user_input)

    route = router_result["route"]
    need_entity = router_result.get("need_entity", False)

    query = user_input

    # ==============================
    # 🔥 用 memory 補 entity
    # ==============================
    if route == "retrieval":

        if need_entity and memory.get("company"):
            query = f"{memory['company']} {user_input}"
            print(f"[REWRITE-ENTITY] {query}")

        # 🔥（加這個）
        if memory.get("topic"):
            query = f"{query} {memory['topic']}"
            print(f"[REWRITE-TOPIC] {query}")

    # ==============================
    # 🔹 Retrieval
    # ==============================
    context = None

    if route == "retrieval":
        docs = run_retrieval_pipeline(query)

        if docs:
            context = format_docs_for_llm(docs)

    return context, router_result