from pathlib import Path
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

# === 路徑 ===
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_DIR = BASE_DIR / "db"


def load_docs():
    docs = []

    for pdf_file in DATA_DIR.glob("*.pdf"):
        loader = PyPDFLoader(str(pdf_file))
        pages = loader.load()

        for page in pages:
            docs.append(
                Document(
                    page_content=page.page_content,
                    metadata={
                        "source": pdf_file.name,
                        "page": page.metadata.get("page", None),
                    }
                )
            )

    return docs


def main():
    docs = load_docs()

    if not docs:
        print("❌ No documents found in data/")
        return

    # 👉 ESG 報告適合較大 chunk（避免語意破碎）
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )

    split_docs = splitter.split_documents(docs)

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001"
    )

    print(f"📄 Loaded {len(docs)} pages → {len(split_docs)} chunks")

    db = Chroma.from_documents(
        split_docs,
        embedding=embeddings,
        persist_directory=str(DB_DIR)
    )


    print(f"✅ Vector DB built at: {DB_DIR}")


if __name__ == "__main__":
    main()