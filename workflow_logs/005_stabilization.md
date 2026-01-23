# Workflow Log: System Stabilization
**Date**: 2026-01-23
**Task**: Restore the system to a runnable state by installing all dependencies.

## 1. Environment Setup
*   **Virtual Environment**: Created `ai-service/venv` (Python 3.10).
*   **Requirements**: Reconstructed `ai-service/requirements.txt` from code analysis.
*   **Node.js**:
    *   `backend`: Installed successfully (`npm install`).
    *   `frontend`: Installing...

## 2. Python Dependency Installation
We are installing dependencies in groups to manage version conflicts and large downloads.
*   **Group 1: PyTorch (CUDA)**
    *   Command: `pip install torch==2.1.2 --index-url https://download.pytorch.org/whl/cu121`
    *   Status: **Downloading (2.5GB)**. This is large because it includes CUDA binaries for your GPU.
*   **Group 2: Transformers & Embeddings**
    *   Command: `pip install transformers==4.37.2 sentence-transformers==2.3.1`
    *   Status: Running.
*   **Group 3: LangChain**
    *   Command: `pip install langchain==0.1.0 langchain-community==0.0.10`
    *   Status: Running.
*   **Group 4: Rasa**
    *   Command: `pip install rasa==3.6.15 rasa-sdk==3.6.2`
    *   Status: Running.

## 3. Potential Issues
*   **Dependency Locking**: Running parallel pip installs might cause race conditions. If they fail, we will run them sequentially.
*   **Torch Version**: We are enforcing `torch==2.1.2+cu121`. Other packages might try to downgrade this to a CPU version. We will verify the final version with `python -c "import torch; print(torch.__version__, torch.version.cuda)"` once done.

## 4. Next Steps
Once installations complete:
1.  Verify `rag_pipeline.py` runs (ingestion).
2.  Verify `actions/actions.py` loads models (inference).
3.  Start the full system.
