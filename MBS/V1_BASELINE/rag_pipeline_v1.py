"""
rag_pipeline.py — Deep Dive RAG Pipeline with Parent Document Retrieval (PDR)
==============================================================================
Ingestion flow:
    1. SmartIngest extracts text from PDFs (column-aware, table-preserving).
    2. SmartChunker splits into PARENT contexts (1500 chars) and CHILD chunks (300 chars).
    3. CHILD chunks are embedded and stored in ChromaDB (for retrieval).
    4. PARENT contexts are saved to parent_store.json (for expansion at query time).

At query time (in actions.py):
    - Retrieve top CHILD chunks from ChromaDB.
    - Look up their parent_id in parent_store.json.
    - Send the full PARENT context to the LLM.
"""

import os
import sys
import json
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
# Chroma DB path (child chunks)
DB_CHROMA_PATH = os.path.join(DOCUMENTS_PATH, "chroma_db")
# Parent store path (parent contexts)
PARENT_STORE_PATH = os.path.join(DOCUMENTS_PATH, "parent_store.json")


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
    """Deep Dive RAG Pipeline: Ingest -> PDR Chunk -> ChromaDB + Parent Store"""
    print_flush("\n--- Starting Deep Dive RAG Pipeline (PDR Mode) ---")

    try:
        # 0. Cleanup Old DB
        if os.path.exists(DB_CHROMA_PATH):
            print_flush(f"Removing old ChromaDB at {DB_CHROMA_PATH}...")
            try:
                shutil.rmtree(DB_CHROMA_PATH)
            except Exception as e:
                print_flush(f"Warning: Could not delete old DB ({e}). Attempting overwrite...")

        if os.path.exists(PARENT_STORE_PATH):
            print_flush(f"Removing old parent store at {PARENT_STORE_PATH}...")
            os.remove(PARENT_STORE_PATH)

        # 1. Ingestion (Column-Aware + Cleaning)
        pdf_files = [f for f in os.listdir(PDFS_PATH) if f.lower().endswith('.pdf')]
        if not pdf_files:
            print_flush("WARNING: No PDFs found.")
            return

        print_flush(f"Found {len(pdf_files)} PDFs. Starting Deep Dive Ingestion...")

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

        # 2. Chunking (PDR: Parent 1500 + Child 500)
        print_flush("Splitting documents (PDR: Parent 1500 + Child 500)...")
        chunker = SmartChunker(
            parent_chunk_size=1500,
            parent_chunk_overlap=200,
            child_chunk_size=500,
            child_chunk_overlap=200,
        )
        child_chunks, parent_store = chunker.split_documents(raw_documents)

        print_flush(f"Created {len(child_chunks)} child chunks from {len(parent_store)} parent contexts.")

        if not child_chunks:
            print_flush("ERROR: No chunks generated.")
            return

        # 3. Save Parent Store to disk
        print_flush(f"Saving parent store ({len(parent_store)} entries) to {PARENT_STORE_PATH}...")
        with open(PARENT_STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(parent_store, f, ensure_ascii=False, indent=2)
        print_flush("Parent store saved successfully.")

        # 4. Embeddings (Upgrade to IndicBERT-v3-1B)
        from indic_embeddings import IndicBERTEmbeddings
        print_flush("Loading IndicBERT-v3-1B Embeddings Model...")
        embeddings = IndicBERTEmbeddings()

        # 5. Vector Store (Chroma) — stores CHILD chunks only
        print_flush(f"Creating ChromaDB at {DB_CHROMA_PATH} (child chunks only)...")
        db = Chroma.from_documents(
            documents=child_chunks,
            embedding=embeddings,
            persist_directory=DB_CHROMA_PATH
        )

        print_flush("=" * 60)
        print_flush("--- PDR Pipeline Complete ---")
        print_flush(f"  Child chunks in ChromaDB: {len(child_chunks)}")
        print_flush(f"  Parent contexts on disk:  {len(parent_store)}")
        print_flush(f"  ChromaDB path: {DB_CHROMA_PATH}")
        print_flush(f"  Parent store:  {PARENT_STORE_PATH}")
        print_flush("=" * 60)

    except Exception as e:
        print_flush("\n--- FATAL ERROR ---")
        traceback.print_exc()


if __name__ == "__main__":
    create_vector_db()
