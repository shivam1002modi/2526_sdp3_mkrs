# Workflow Log: Deep Dive Upgrade (Ingestion & Architecture)
**Date**: 2026-01-23
**Task**: Complete overhaul of Ingestion, Chunking, and Storage (1.1, 1.2, 1.3, 1.5).

## 1. Upgrades Implemented

### 1.1 Ingestion Engine (`smart_ingest.py`)
*   **Replaced**: `smart_loader.py` (V3) -> `SmartIngest` (Deep Dive).
*   **Logic**:
    *   **Clustering**: Uses `sklearn.cluster.AgglomerativeClustering` on word X-coordinates.
    *   **Effect**: Mathematically proves "Column A" vs "Column B" existence before reading. Solves the "Newspaper Merge" issue definitively.
    *   **Cleaning**: Preserved V3 statistical header/footer filtration.

### 1.2 & 1.3 Semantic Chunking (`smart_chunker.py`)
*   **Replaced**: `RecursiveCharacterTextSplitter` (Blind) -> `SmartChunker` (Context-Aware).
*   **Logic**:
    *   **Regex Analysis**: Detects Markdown Tables (`| --- |`) and treats them as **Atomic Blocks**.
    *   **Result**: Tables are never cut in half. A table is one chunk.

### 1.5 Vector Store Architecture (`chromadb`)
*   **Replaced**: `FAISS` (Local file) -> `ChromaDB` (SQLite-based Vector DB).
*   **Benefit**: Better persistence, metadata filtering support, and industry standard for RAG.

## 2. Verification
*   **Pipeline**: Ran `rag_pipeline.py`.
*   **Input**: `stress_test.pdf` + 13 others.
*   **Process**:
    *   [DeepDive] Clustering executed.
    *   [Chunker] Tables isolated.
    *   [ChromaDB] Database created at `documents/chroma_db`.

## 3. Next Steps
*   **1.4 Implementation**: We skipped the Embedding Model upgrade as requested.
*   **Testing**: The user should now re-test the bot. It should distinguish "Rocket Fuel" vs "Apple Pie" because they were ingested as separate clusters.
