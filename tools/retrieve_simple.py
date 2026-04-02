from langchain.tools import tool
from tools.retrieve_core import retrieve_docs


@tool
def retrieve_simple(question: str) -> str:
    """Retrieve relevant documents from the vector database."""

    docs = retrieve_docs(question, k=3, retrieval_type="simple")

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