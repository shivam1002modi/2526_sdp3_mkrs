# Workflow Log: Initial Repository Analysis
**Date**: 2026-01-23
**Task**: Analyze the architecture of `shivam1002modi/2526_sdp3_mkrs`.

## 1. Research & Exploration
*   **Action**: Cloned repository from usage `https://github.com/shivam1002modi/2526_sdp3_mkrs`.
*   **Action**: Listed files and read `README.md` to understand the high-level architecture.
*   **Action**: Deep-dived into `ai-service` directory, specifically `rag_pipeline.py` and `actions/actions.py`.
*   **Findings**:
    *   **Architecture**: Microservices (React Frontend, Node Backend, Python/Rasa AI Service).
    *   **Ingestion**: `rag_pipeline.py` uses `PyPDFDirectoryLoader` and `FAISS` with `paraphrase-xlm-r-multilingual-v1` embeddings.
    *   **Inference**: `actions/actions.py` uses `ActionQueryDoc` class.
    *   **Current Models**:
        *   Embedding: `paraphrase-xlm-r-multilingual-v1`
        *   Reranking: `cross-encoder/ms-marco-MiniLM-L-6-v2`
        *   Generation: `sshleifer/distilbart-cnn-12-6`

## 2. Implementation Status
*   **Completed**:
    *   Repository cloning.
    *   Architecture mapping.
    *   Identification of code locations for model upgrades.
*   **Pending**:
    *   Creation of `requirements.txt` (file was missing).

## 3. Architecture Notes
The system relies on a unified embedding model for both ingestion and retrieval. Any change to the embedding model requires a full re-ingestion of documents. The generation is currently handled by a simple summarization model, which limits the "chat" capability. Upgrading to a generative LLM will significantly improve quality but requires careful resource management.
