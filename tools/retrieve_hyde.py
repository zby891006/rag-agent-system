# === tools/retrieve_hyde.py ===
from langchain.tools import tool
from typing import List
from langchain_core.documents import Document
from tools.retrieve_core import retrieve_docs_raw
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

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
        You are an expert in financial and ESG reports.

        Given a user question, generate {n} different search queries that could appear in formal reports (e.g., ESG reports, 10-K).

        Requirements:
        - Use formal, report-style language
        - Focus on concrete terms (metrics, actions, policies)
        - Each query should be a complete sentence
        - Avoid repeating wording
        - Output as a Python list of strings

        User question:
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
        key = doc.page_content[:100]  # 簡單但有效

        if key not in seen:
            seen.add(key)
            unique_docs.append(doc)

    return unique_docs


# =========================================================
# 🔹 3. HyDE Tool
# =========================================================


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
        docs = retrieve_docs_raw(q, k=3, debug=False)
        all_docs.extend(docs)

    print(f"\n[HyDE] Total retrieved before dedup: {len(all_docs)}")

    # 3️⃣ deduplicate
    unique_docs = deduplicate_docs(all_docs)

    print(f"[HyDE] After dedup: {len(unique_docs)}")

    if not unique_docs:
        return "No relevant documents found."

    # 4️⃣ formatting（給 agent）
    formatted = []
    for i, doc in enumerate(unique_docs[:5], start=1):  # 控制長度
        formatted.append(
            f"[Document {i}] source={doc.metadata.get('source', 'unknown')}\n"
            f"{doc.page_content}"
        )

    return "\n\n".join(formatted)
