# === 工具 1：文件檢索 ===
from langchain.tools import tool

from vectorstore.store import VECTORSTORE


@tool
def retrieve_docs(question: str) -> str:
    """Retrieve relevant passages from the internal ESG/finance document library."""
    results = VECTORSTORE.similarity_search(question, k=3)

    if not results:
        return "No relevant documents found."

    formatted = []
    for i, doc in enumerate(results, start=1):
        formatted.append(
            f"[Document {i}] source={doc.metadata.get('source', 'unknown')}\n"
            f"{doc.page_content}"
        )

    return "\n\n".join(formatted)