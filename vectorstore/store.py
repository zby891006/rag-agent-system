from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings

DATA_DIR = Path("data")



# === 建立小型文件庫 ===
def load_documents(data_dir: Path) -> List[Document]:
    docs = []
    for file_path in data_dir.glob("*.txt"):
        text = file_path.read_text(encoding="utf-8")
        docs.append(
            Document(
                page_content=text,
                metadata={"source": file_path.name}
            )
        )
    return docs


def build_vectorstore() -> FAISS:
    raw_docs = load_documents(DATA_DIR)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50
    )
    split_docs = splitter.split_documents(raw_docs)

    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vectorstore = FAISS.from_documents(split_docs, embeddings)
    return vectorstore


VECTORSTORE = build_vectorstore()