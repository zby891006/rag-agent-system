def format_docs_for_llm(docs: list[dict]) -> str:

    formatted = []

    for i, doc in enumerate(docs, 1):
        formatted.append(
            f"[Document {i}] source={doc['metadata'].get('source', 'unknown')}\n"
            f"{doc['text']}"
        )

    return "\n\n".join(formatted)