from langchain.tools import tool
from langchain_chroma import Chroma 
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "db"

load_dotenv()

_db = None

def get_db():
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


@tool
def retrieve_docs(question: str) -> str:
    """Retrieve relevant documents from the vector database."""
    db = get_db()
    results = db.similarity_search(question, k=3)

    if not results:
        return "No relevant documents found."

    formatted = []
    for i, doc in enumerate(results, start=1):
        formatted.append(
            f"[Document {i}] source={doc.metadata.get('source', 'unknown')}\n"
            f"{doc.page_content}"
        )

    return "\n\n".join(formatted)


if __name__ == "__main__":
    print("Testing retrieval...")

    if not DB_DIR.exists():
        print("❌ DB not found. Please run build script first.")
    else:
        db = get_db()
        results = db.similarity_search("climate", k=2)

        for i, r in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(r.page_content)