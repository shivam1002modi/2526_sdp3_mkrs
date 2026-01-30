# ai-service/rag_pipeline.py
import os
import sys
import shutil
from pathlib import Path
import traceback

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import torch

def print_flush(*args, **kwargs):
    # Sanitize args to avoid Windows UnicodeEncodeError
    new_args = []
    for arg in args:
        if isinstance(arg, str):
            try:
                # Try to print normally
                arg.encode(sys.stdout.encoding or 'utf-8')
                new_args.append(arg)
            except UnicodeEncodeError:
                # Fallback: force ascii with replacement
                new_args.append(arg.encode('ascii', 'replace').decode('ascii'))
        else:
            new_args.append(arg)
            
    print(*new_args, **kwargs)
    sys.stdout.flush()

# Paths relative to this file
script_dir = os.path.dirname(__file__)
DOCUMENTS_PATH = os.path.join(script_dir, "documents")
PDFS_PATH = os.path.join(DOCUMENTS_PATH, "pdfs")
DB_FAISS_PATH = os.path.join(DOCUMENTS_PATH, "vectorstore")

def create_vector_db():
    """Loads PDFs, splits them into chunks, and creates a FAISS vector store with metadata."""
    print_flush("\n--- Starting RAG pipeline ---")
    try:
        # Remove the old vector store if it exists
        if os.path.exists(DB_FAISS_PATH):
            print_flush(f"Removing old vector store at {DB_FAISS_PATH}...")
            shutil.rmtree(DB_FAISS_PATH)

        # Ensure PDFs folder exists and has files
        if not os.path.exists(PDFS_PATH) or not os.listdir(PDFS_PATH):
            print_flush("WARNING: The 'pdfs' directory is either missing or empty.")
            print_flush("--- RAG pipeline finished: No new vector store created. ---")
            sys.exit(0)

        print_flush(f"Loading PDFs from: {PDFS_PATH}")
        print_flush(f"Loading PDFs from: {PDFS_PATH}")
        
        # --- ROBUST LOADING: Load files one by one to catch errors ---
        from langchain_community.document_loaders import PyPDFLoader
        
        documents = []
        pdf_files = [f for f in os.listdir(PDFS_PATH) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            print_flush("WARNING: No PDF files found in the 'pdfs' folder.")
            return

        print_flush(f"Found {len(pdf_files)} PDF files. Processing...")

        for pdf_file in pdf_files:
            file_path = os.path.join(PDFS_PATH, pdf_file)
            try:
                # Load single PDF
                loader = PyPDFLoader(file_path)
                file_docs = loader.load()
                
                # Check for empty docs
                if not file_docs:
                    print_flush(f"  [WARN] Skipped empty file: {pdf_file}")
                    continue

                # Normalize metadata immediately
                for doc in file_docs:
                    meta = doc.metadata or {}
                    # Ensure source is just the filename, not full path
                    meta["source"] = pdf_file 
                    # Normalize page number (some loaders use 'page', some 'page_number')
                    page = meta.get("page") or meta.get("page_number") or meta.get("pageno")
                    if page is not None:
                        meta["page"] = page
                    doc.metadata = meta
                    documents.append(doc)
                
                print_flush(f"  [OK] Loaded {pdf_file} ({len(file_docs)} pages)")

            except Exception as e:
                print_flush(f"  [ERROR] Failed to load {pdf_file}: {str(e)[:100]}...")
                continue

        if not documents:
            print_flush("ERROR: No valid documents were loaded after checking all files.")
            return

        normalized_docs = documents 


        print_flush("Splitting documents into smaller text chunks...")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_documents(normalized_docs)
        print_flush(f"Created {len(chunks)} text chunks.")

        print_flush("Loading multilingual embeddings model (this may take a moment)...")
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        embeddings = HuggingFaceEmbeddings(
            model_name="paraphrase-xlm-r-multilingual-v1",
            model_kwargs={'device': device}
        )

        print_flush("Creating and saving new FAISS vector store...")
        db = FAISS.from_documents(chunks, embeddings)
        db.save_local(DB_FAISS_PATH)
        print_flush(f"--- Vector store created successfully at {DB_FAISS_PATH} ---")

    except Exception as e:
        print_flush("\n--- AN ERROR OCCURRED ---")
        print_flush("Error during RAG pipeline execution:", e)
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    create_vector_db()
