from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma   # ✅ 新版
from dotenv import load_dotenv

load_dotenv()

# === 路徑設定（只寫一次）===
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_DIR = BASE_DIR / "db"


def load_docs():
    docs = []
    for f in DATA_DIR.glob("*.txt"):
        docs.append(
            Document(
                page_content=f.read_text(encoding="utf-8"),
                metadata={"source": f.name}
            )
        )
    return docs


def main():
    docs = load_docs()

    if not docs:
        print("❌ No documents found in data/")
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50
    )
    split_docs = splitter.split_documents(docs)

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001"
    )

    print(f"📄 Loaded {len(docs)} docs → {len(split_docs)} chunks")

    Chroma.from_documents(
        split_docs,
        embedding=embeddings,
        persist_directory=str(DB_DIR)
    )

    print(f"✅ Vector DB built at: {DB_DIR}")


if __name__ == "__main__":
    main()