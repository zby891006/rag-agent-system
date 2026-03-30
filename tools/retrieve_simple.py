from langchain.tools import tool
from tools.retrieve_core import retrieve_docs_raw  

@tool
def retrieve_simple(question: str) -> str:
    """Retrieve relevant documents from the vector database."""

    docs = retrieve_docs_raw(question, k=3)  # 👈 只呼叫

    if not docs:
        return "No relevant documents found."

    formatted = []
    for i, doc in enumerate(docs, start=1):
        formatted.append(
            f"[Document {i}] source={doc.metadata.get('source', 'unknown')}\n"
            f"{doc.page_content}"
        )

    return "\n\n".join(formatted)