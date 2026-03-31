# === tools/retrieve_hyde.py ===
from langchain.tools import tool
from typing import List
from langchain_core.documents import Document
from tools.retrieve_core import retrieve_docs_raw
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from sentence_transformers import CrossEncoder

model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

load_dotenv()


# === LLM 初始化 ===
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)


# =========================================================
# 🔹 1. HyDE Query Generation
# =========================================================


def generate_hyde_queries(question: str, n: int = 5) -> List[str]:
    """
    Generate multiple hypothetical queries for retrieval
    """

    prompt = f"""
    You are an expert in ESG and financial reports.

    Generate {n} hypothetical paragraphs that could appear in an ESG or sustainability report.

    Requirements:
    - Each output should be a short paragraph (3–5 sentences)
    - Write in formal disclosure/report style
    - Describe processes for identifying, assessing, and managing climate-related risks
    - Include specific frameworks (e.g., enterprise risk management, materiality assessment, ISO 14001)
    - Use terminology commonly found in ESG reports
    - Avoid questions; write as if it is part of the report
    - Output as a Python list of strings
    {question}
    """

    response = llm.invoke(prompt).content

    try:
        queries = eval(response)
        if not isinstance(queries, list):
            raise ValueError
    except:
        # fallback（避免模型亂輸出）
        queries = [question]

    # 保底：加入原始 query
    queries.append(question)

    # 去重
    queries = list(set(q.strip() for q in queries if q.strip()))

    return queries


# =========================================================
# 🔹 2. Deduplicate
# =========================================================


def deduplicate_docs(docs: List[Document]) -> List[Document]:
    """
    Deduplicate documents based on content
    """

    seen = set()
    unique_docs = []

    for doc in docs:
        key = doc.metadata["chunk_uid"]

        if key not in seen:
            seen.add(key)
            unique_docs.append(doc)

    return unique_docs


# =========================================================
# 🔹 3.Re-rank
# =========================================================
def rerank_documents(query, docs, top_k=5):
    pairs = [[query, doc.page_content] for doc in docs]

    scores = model.predict(pairs)

    scored_docs = list(zip(docs, scores))
    scored_docs.sort(key=lambda x: x[1], reverse=True)

    return [doc for doc, _ in scored_docs[:top_k]]


@tool
def retrieve_hyde(question: str) -> str:
    """
    Advanced retrieval using HyDE (multi-query expansion).
    """

    print("\n=== [HyDE START] ===")

    # 1️⃣ generate queries
    queries = generate_hyde_queries(question)

    print("\n[HyDE Queries]")
    for i, q in enumerate(queries, 1):
        print(f"{i}. {q}")

    # 2️⃣ multi-query retrieval
    all_docs = []

    for q in queries:
        docs = retrieve_docs_raw(q, k=5, debug=False)
        all_docs.extend(docs)

    print(f"\n[HyDE] Total retrieved before dedup: {len(all_docs)}")

    # 3️⃣ deduplicate
    unique_docs = deduplicate_docs(all_docs)

    print(f"[HyDE] After dedup: {len(unique_docs)}")

    if not unique_docs:
        return "No relevant documents found."

    # rerank（最重要）

    rerank_query = question

    reranked_docs = rerank_documents(rerank_query, unique_docs, top_k=5)
  
    formatted = []
    for i, doc in enumerate(reranked_docs, start=1):
        formatted.append(
            f"[Document {i}] source={doc.metadata.get('source', 'unknown')}\n"
            f"{doc.page_content}"
        )

    return "\n\n".join(formatted)
