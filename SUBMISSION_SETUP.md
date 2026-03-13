# MKRS AI Brain Submission Setup Guide

This document provides exact instructions to set up the MKRS AI Brain system from scratch to achieve a TMS Score of **88+**.

## 1. Prerequisites
- **Python**: 3.10.x (Required for Rasa 3.6.15 compatibility)
- **Ollama**: [Download & Install Ollama](https://ollama.com/)
- **OS**: Windows (Commands below are for PowerShell/Command Prompt)

## 2. Lock to Stable Version
To ensure you are running the exact configuration that achieved TMS 88+, run this first:
```powershell
git checkout 7a70ad0db85d372d2dd001451bebd97cc0a12431
```

## 3. Environment Setup
From the project root (`D:\MKRS`), run:

```powershell
# 1. Create virtual environment
cd ai-service
python -m venv venv

# 2. Activate environment
.\venv\Scripts\activate

# 3. Install dependencies
# Note: We use specific versions to avoid the Transformers/Rasa conflict
pip install -r requirements.txt
```

## 3. External Model Dependencies (Ollama)
Ensure Ollama is running, then pull the necessary models:

```powershell
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

## 4. Database & Knowledge Base Initialization
This step processes the PDFs in `ai-service/documents/pdfs` and builds the vector store.

```powershell
# In the activated virtual environment inside ai-service/
python -m rag_pipeline
```
*Expected: You should see "SUCCESS: ChromaDB and Parent Store updated with XX documents."*

## 5. Rasa NLU Training
Train the intent classification and entity recognition model.

```powershell
# In the activated virtual environment inside ai-service/
python -m rasa train
```

## 6. How to Run the System
The easiest way is to use the provided batch script from the root:

```powershell
cd D:\MKRS
.\start_system.bat
```
This will launch:
1. **Frontend** (:3000)
2. **Backend** (:5001)
3. **AI Admin** (:8000)
4. **Action Server** (:5055) - Contains the RAG logic
5. **Rasa Server** (:5005)

## 7. How to Verify / Run Benchmark
To reproduce the TMS 88 score, run the MBS test:

```powershell
.\ai-service\venv\Scripts\python.exe ai-service\eval_v1.py --name "Final Submission Run"
```

## ⚠️ Critical Dependency Note
**Do NOT upgrade `transformers` above 4.45.0**. The Rasa 3.6.x server relies on TensorFlow utilities that were removed in later versions of the `transformers` library. The current `requirements.txt` is pinned to the functional "sweet spot."
