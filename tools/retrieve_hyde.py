from langchain.tools import tool
from typing import List
from tools.retrieve_core import retrieve_docs
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from sentence_transformers import CrossEncoder

load_dotenv()

# === reranker ===
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

# === LLM ===
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)



# HyDE Query Generation


def generate_hyde_queries(question: str, n: int = 5) -> List[str]:

    prompt = f"""
    You are an expert in ESG and financial reports.

    Generate {n} hypothetical paragraphs that could appear in the ESG, sustainability, or annual report of the specific company mentioned in the user question.

    Requirements:
    - Each output should be a short paragraph (3–5 sentences)
    - Formal disclosure style
    - The company name mentioned in the question must be explicitly preserved and repeated naturally in every paragraph
    - Always include the company name from the question in every generated query
    - Do not replace the company name with generic terms such as "the company", "the group", "the issuer", or "the organization" unless the full company name also appears in the same paragraph
    - Focus only on ESG, sustainability, governance, risk management, climate, environmental, health and safety, supply chain, compliance, or materiality topics relevant to that company
    - Include frameworks and report terminology where appropriate, such as ERM, materiality assessment, ISO 14001, climate-related risk management, stakeholder engagement, and governance oversight
    - Keep the content plausible for that specific company, and do not drift into generic industry-wide language that is not tied to the named company
    - No questions
    - Output as a Python list of strings only
    

    User question:
    {question}
    """

    response = llm.invoke(prompt).content

    try:
        queries = eval(response)
        if not isinstance(queries, list):
            raise ValueError
    except:
        queries = [question]

    queries.append(question)
    queries = list(set(q.strip() for q in queries if q.strip()))

    return queries



# Deduplicate（改為 dict）


def deduplicate_docs(docs):

    seen = set()
    unique_docs = []

    for doc in docs:
        key = doc["metadata"].get("chunk_uid", doc["text"][:50])

        if key not in seen:
            seen.add(key)
            unique_docs.append(doc)

    return unique_docs



# Re-rank（改為 dict）


def rerank_documents(query, docs, top_k=5):

    pairs = [[query, doc["text"]] for doc in docs]

    scores = reranker.predict(pairs)

    for doc, score in zip(docs, scores):
        doc["score"] = float(score)

    docs.sort(key=lambda x: x["score"], reverse=True)

    return docs[:top_k]



# System-level HyDE（核心）


def retrieve_hyde_structured(question: str, k: int = 5):

    print("\n=== [HyDE START] ===")

    # 1️⃣ generate queries
    queries = generate_hyde_queries(question)

    print("\n[HyDE Queries]")
    for i, q in enumerate(queries, 1):
        print(f"{i}. {q}")

    # retrieval（用retrieve_docs）
    all_docs = []

    for q in queries:
        docs = retrieve_docs(
            q,
            k=k,
            retrieval_type="hyde"   # 🔥 關鍵
        )

        all_docs.extend(docs)

    print(f"\n[HyDE] Total retrieved: {len(all_docs)}")

    # 3️⃣ deduplicate
    unique_docs = deduplicate_docs(all_docs)

    print(f"[HyDE] After dedup: {len(unique_docs)}")

    if not unique_docs:
        return queries, []

    # 4️⃣ rerank
    reranked_docs = rerank_documents(question, unique_docs, top_k=k)

    return queries, reranked_docs



# Tool 保留工具接口 


@tool
def retrieve_hyde(question: str) -> str:
    """
    HyDE retrieval tool (formatted for LLM)
    """

    queries, docs = retrieve_hyde_structured(question)

    if not docs:
        return "No relevant documents found."

    formatted = []

    for i, doc in enumerate(docs, start=1):
        formatted.append(
            f"[Document {i}] "
            f"source={doc['metadata'].get('source', 'unknown')}\n"
            f"{doc['text']}"
        )

    return "\n\n".join(formatted)