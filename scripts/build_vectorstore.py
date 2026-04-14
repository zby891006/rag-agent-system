# from pathlib import Path
# from dotenv import load_dotenv

# from langchain_core.documents import Document
# from langchain_community.document_loaders import PyPDFLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from langchain_chroma import Chroma
# import uuid

# load_dotenv()

# # === 路徑 ===
# BASE_DIR = Path(__file__).resolve().parent.parent
# DATA_DIR = BASE_DIR / "data"
# DB_DIR = BASE_DIR / "db"


# def load_docs():
#     docs = []

#     for pdf_file in DATA_DIR.glob("*.pdf"):
#         loader = PyPDFLoader(str(pdf_file))
#         pages = loader.load()

#         for page in pages:
#             docs.append(
#                 Document(
#                     page_content=page.page_content,
#                     metadata={
#                         "source": pdf_file.name,
#                         "page": page.metadata.get("page", None),
#                         "uid": str(uuid.uuid4())  # 🔥 每頁唯一 ID
#                     }
#                 )
#             )

#     return docs


# def main():
#     docs = load_docs()

#     if not docs:
#         print("❌ No documents found in data/")
#         return

    
#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=800,
#         chunk_overlap=150
#     )

#     split_docs = splitter.split_documents(docs)

# # 🔥 為每個 chunk 建立 UID（關鍵）
#     for doc in split_docs:
#         doc.metadata["chunk_uid"] = str(uuid.uuid4())



#     embeddings = GoogleGenerativeAIEmbeddings(
#         model="models/gemini-embedding-001"
#     )

#     print(f" Loaded {len(docs)} pages → {len(split_docs)} chunks")

#     db = Chroma.from_documents(
#         split_docs,
#         embedding=embeddings,
#         persist_directory=str(DB_DIR)
#     )


#     print(f"✅ Vector DB built at: {DB_DIR}")


# if __name__ == "__main__":
#     main()

from pathlib import Path
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
import uuid

load_dotenv()

# === 路徑 ===
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_DIR = BASE_DIR / "db"


# 🔥 從檔名推公司名稱（可依你檔名格式調整）
def infer_company_from_filename(filename: str):
    name = filename.replace(".pdf", "").strip()

    # 👉 如果你的檔名像 wolfspeed_esg_2023.pdf
    if "_" in name:
        name = name.split("_")[0]

    return name.capitalize()


def load_docs():
    docs = []

    for pdf_file in DATA_DIR.glob("*.pdf"):
        loader = PyPDFLoader(str(pdf_file))
        pages = loader.load()

        company = infer_company_from_filename(pdf_file.name)

        for page in pages:
            docs.append(
                Document(
                    page_content=page.page_content,
                    metadata={
                        "source": pdf_file.name,
                        "page": page.metadata.get("page", None),
                        "uid": str(uuid.uuid4()),
                        "company": company  # 🔥 先寫進 metadata（page 層）
                    }
                )
            )

    return docs


def main():
    docs = load_docs()

    if not docs:
        print("❌ No documents found in data/")
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )

    split_docs = splitter.split_documents(docs)

    # 🔥 關鍵：每個 chunk 強制加入公司名稱 + metadata
    for doc in split_docs:
        company = doc.metadata.get("company", "Unknown")

        # ✅ 把公司名稱寫進內容（影響 embedding）
        doc.page_content = f"""
Company: {company}
{doc.page_content}
"""

        # ✅ chunk 層 metadata
        doc.metadata["company"] = company
        doc.metadata["chunk_uid"] = str(uuid.uuid4())

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001"
    )

    print(f" Loaded {len(docs)} pages → {len(split_docs)} chunks")

    db = Chroma.from_documents(
        split_docs,
        embedding=embeddings,
        persist_directory=str(DB_DIR)
    )

    print(f"✅ Vector DB built at: {DB_DIR}")


if __name__ == "__main__":
    main()