from tools.retrieve_simple import retrieve_docs
from tools.retrieve_hyde import retrieve_hyde_structured
from quality.rqc import evaluate_rqc


MAX_RETRY = 2


def run_retrieval_pipeline(query: str):

    use_hyde = False
    current_query = query

    for step in range(MAX_RETRY):

        print(f"\n=== [STEP {step}] ===")

        # 🔵 選 retrieval
        if use_hyde:
            hyde_queries, docs = retrieve_hyde_structured(current_query)
        else:
            docs = retrieve_docs(current_query)

        # RQC
        rqc_result = evaluate_rqc(query, docs)

        print("\n[RQC RESULT]")
        print(rqc_result)

        # PASS
        if rqc_result["decision"] == "PASS":
            return docs

        # RETRY → 調整策略
        if rqc_result["suggest_hyde"]:
            use_hyde = True

        # keyword refine
        if rqc_result["keywords"]:
            current_query = " ".join(rqc_result["keywords"])

    # fallback（非常重要）
    return docs