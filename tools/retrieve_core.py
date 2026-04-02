# === tools/retrieval_core.py ===

from typing import List
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
from pathlib import Path

# === 初始化 ===

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "db"

_db = None


def get_db():
    """
    Lazy initialization for vector database
    """
    global _db
    if _db is None:
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001"
        )
        _db = Chroma(
            persist_directory=str(DB_DIR),
            embedding_function=embeddings
        )
    return _db


# === Core Retrieval Function ===

def retrieve_docs_raw(
    query: str,
    k: int = 3,
    debug: bool = False
) -> List[Document]:
    """
    Core retrieval function (Single Source of Truth)

    This function should be the ONLY place that directly interacts with the vector DB.

    Args:
        query (str): query string (user query or HyDE query)
        k (int): number of documents to retrieve
        debug (bool): whether to print debug info

    Returns:
        List[Document]: raw documents (no formatting)
    """
    db = get_db()

    results = db.similarity_search(query, k=k)

    if debug:
        print("\n=== [RETRIEVAL DEBUG] ===")
        print(f"Query: {query}")
        print(f"Retrieved: {len(results)} docs")

        for i, doc in enumerate(results, 1):
            preview = doc.page_content[:100].replace("\n", " ")
            print(f"[Doc {i}] {preview}...")

    return results


def retrieve_docs(
    query: str,
    k: int = 3,
    debug: bool = False,
    retrieval_type: str = "simple" 
        ):
    
    raw_docs = retrieve_docs_raw(query, k=k, debug=debug)

    results = []

    for doc in raw_docs:
        results.append({
            "text": doc.page_content,
            "metadata": doc.metadata,
            "score": None,
            "source_query": query,
            "retrieval_type": retrieval_type
        })

    return results