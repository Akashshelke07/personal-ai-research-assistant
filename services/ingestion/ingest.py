import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- Environment Variables ---
ROOT = Path.cwd()
DATA_DIR = ROOT / "data"
CHROMA_DIR = os.getenv("CHROMA_DIR")
EMBED_MODEL = os.getenv("EMBEDDING_MODEL")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME")

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

def load_documents():
    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Create a folder named {DATA_DIR} and put files inside.")
    
    print("Loading documents from ./data...")
    docs = []
    for p in DATA_DIR.rglob("*"):
        if p.is_dir(): continue
        try:
            if p.suffix.lower() in [".txt", ".md"]:
                loader = TextLoader(str(p), encoding='utf-8')
                docs.extend(loader.load())
            elif p.suffix.lower() == ".pdf":
                loader = PyPDFLoader(str(p))
                docs.extend(loader.load())
        except Exception as e:
            print(f"  - Skipping {p.name} due to error: {e}")
    return docs

def split_documents(docs):
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
    return splitter.split_documents(docs)

def build(chunks):
    print("Loading embeddings model:", EMBED_MODEL)
    # This is the fix for the "meta tensor" error.
    model_kwargs = {'device': 'cpu'}
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        model_kwargs=model_kwargs
    )
    
    print(f"Creating Chroma DB at {CHROMA_DIR} with collection '{COLLECTION_NAME}'")
    Chroma.from_documents(
        chunks, 
        embeddings, 
        collection_name=COLLECTION_NAME, 
        persist_directory=CHROMA_DIR
    )
    print("✅ Chroma DB created and persisted successfully.")

if __name__ == "__main__":
    print("Starting ingestion...")
    docs = load_documents()
    if not docs:
        print("\nNo documents found in ./data — add .pdf/.txt/.md and rerun.")
        raise SystemExit(1)
    
    print(f"\nLoaded {len(docs)} source doc(s). Splitting into chunks...")
    chunks = split_documents(docs)
    
    print(f"Created {len(chunks)} chunks. Building vector DB...")
    build(chunks)
    
    print("\nIngestion finished.")