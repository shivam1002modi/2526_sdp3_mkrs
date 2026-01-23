import os
import sys
import shutil
import traceback
import torch
from langchain_community.embeddings import HuggingFaceEmbeddings

# New Components
from smart_ingest import SmartIngest
from smart_chunker import SmartChunker
# Vector Store
from langchain_community.vectorstores import Chroma

# Paths
script_dir = os.path.dirname(__file__)
DOCUMENTS_PATH = os.path.join(script_dir, "documents")
PDFS_PATH = os.path.join(DOCUMENTS_PATH, "pdfs")
# Chroma DB path
DB_CHROMA_PATH = os.path.join(DOCUMENTS_PATH, "chroma_db")

def print_flush(*args, **kwargs):
    # Sanitize args to avoid Windows UnicodeEncodeError
    new_args = []
    for arg in args:
        if isinstance(arg, str):
            try:
                arg.encode(sys.stdout.encoding or 'utf-8')
                new_args.append(arg)
            except UnicodeEncodeError:
                new_args.append(arg.encode('ascii', 'replace').decode('ascii'))
        else:
            new_args.append(arg)
    print(*new_args, **kwargs)
    sys.stdout.flush()

def create_vector_db():
    """Deep Dive RAG Pipeline: Ingest -> Semantic Chunk -> ChromaDB"""
    print_flush("\n--- Starting Deep Dive RAG Pipeline ---")
    
    try:
        # 0. Cleanup Old DB ? (Optional: Chroma supports updates, but for fresh ingest we clean)
        # However, for 'Deep Dive' persistence we might want to keep it.
        # But for 'retraining' signal, we usually wipe. Let's wipe for consistency with old behavior.
        if os.path.exists(DB_CHROMA_PATH):
            print_flush(f"removing old ChromaDB at {DB_CHROMA_PATH}...")
            # Chroma locks files, this might fail if process running.
            # But we are the process.
            try:
                shutil.rmtree(DB_CHROMA_PATH)
            except Exception as e:
                print_flush(f"Warning: Could not delete old DB ({e}). Attempting overwrite...")

        # 1. Ingestion (Clustering + Cleaning)
        pdf_files = [f for f in os.listdir(PDFS_PATH) if f.lower().endswith('.pdf')]
        if not pdf_files:
            print_flush("WARNING: No PDFs found.")
            return

        print_flush(f"Found {len(pdf_files)} PDFs. Starting Deep Dive Ingestion (Clustering)...")
        
        raw_documents = []
        for pdf in pdf_files:
            try:
                loader = SmartIngest(os.path.join(PDFS_PATH, pdf))
                raw_documents.extend(loader.load())
            except Exception as e:
                print_flush(f"  [ERROR] {pdf} failed: {e}")

        if not raw_documents:
            print_flush("ERROR: No valid documents to process.")
            return
        
        # 2. Chunking (Semantic)
        print_flush("Splitting documents (Semantic + Table Preservation)...")
        chunker = SmartChunker(chunk_size=500, chunk_overlap=50)
        chunks = chunker.split_documents(raw_documents)
        print_flush(f"Created {len(chunks)} optimized chunks.")

        # 3. Embeddings (Keep existing model)
        print_flush("Loading Embeddings Model (paraphrase-xlm-r-multilingual-v1)...")
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        embeddings = HuggingFaceEmbeddings(
            model_name="paraphrase-xlm-r-multilingual-v1",
            model_kwargs={'device': device}
        )

        # 4. Vector Store (Chroma)
        print_flush(f"Creating ChromaDB at {DB_CHROMA_PATH}...")
        # Chroma handles persistence automatically in recent versions
        db = Chroma.from_documents(
            documents=chunks, 
            embedding=embeddings,
            persist_directory=DB_CHROMA_PATH
        )
        print_flush("--- ChromaDB built successfully. ---")

    except Exception as e:
        print_flush("\n--- FATAL ERROR ---")
        traceback.print_exc()

if __name__ == "__main__":
    create_vector_db()
