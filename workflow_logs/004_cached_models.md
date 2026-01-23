# Workflow Log: Cached Models
**Date**: 2026-01-23
**Task**: Identify models already present in local Hugging Face cache (`.cache/huggingface/hub`).

## 1. Found Models
The following models are already downloaded and ready to use without internet access:

### Core RAG Models (Currently Used)
*   `models--sentence-transformers--paraphrase-xlm-r-multilingual-v1` (Embedding)
*   `models--cross-encoder--ms-marco-MiniLM-L-6-v2` (Re-ranking)
*   `models--sshleifer--distilbart-cnn-12-6` (Summarization)

### Potential Upgrade Candidates (Found in Cache)
*   **Target Embedding**: `models--ai4bharat--IndicBERT-v3-1B`
    *   *Status*: **Ready**. This matches your goal for better multilingual support.
*   **Target Generator**: `models--ai4bharat--Airavata`
    *   *Status*: **Ready**. This is an instruction-tuned Hindi/English model.
    *   *Note*: There is also `models--sam749--Airavata-GGUF`, suggesting you might have experimented with quantized versions (good for your 8GB RAM).

### Translation / Other
*   `models--Helsinki-NLP--opus-mt-en-hi` (English -> Hindi)
*   `models--Helsinki-NLP--opus-mt-en-mr` (English -> Marathi)
*   `models--Helsinki-NLP--opus-mt-en-guw` (English -> Gun)
*   `models--Systran--faster-whisper-small` (Speech-to-Text)

## 2. Implications
*   **No Download Needed**: We can switch to `IndicBERT` and `Airavata` immediately without waiting for downloads.
*   **Offline Capability**: The core pipeline and the proposed upgrade path can run offline if dependencies are installed.
