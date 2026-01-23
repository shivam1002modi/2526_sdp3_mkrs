# Workflow Log: Troubleshooting Startup
**Date**: 2026-01-23
**Task**: Resolve system startup errors after stabilization.

## 1. Issues Encountered & Solved

### Issue A: "Knowledge Base Unavailable" (Error 409)
*   **Symptom**: `Rasa NLU Server` returned 409 Conflict.
*   **Cause**: The Rasa model was never trained, so the server had no "brain" to load.
*   **Fix**: Triggered `/retrain` endpoint to run the full training pipeline.

### Issue B: "KeyError: 'bbox' in PDF"
*   **Symptom**: Retraining crashed while loading PDFs.
*   **Cause**: `PyPDFDirectoryLoader` crashed on a single corrupt file (`delhi_.pdf`) and took down the whole process.
*   **Fix**: Modified `rag_pipeline.py` to use a robust loop that processes files one-by-one and skips corrupt ones.

### Issue C: "UnicodeEncodeError"
*   **Symptom**: Crashed when printing filenames with special characters (emojis/Hindi) on Windows console.
*   **Fix**: Patched `print_flush` in `rag_pipeline.py` to sanitize output strings.

### Issue D: "Numpy/FAISS Binary Incompatibility"
*   **Symptom**: `ValueError: numpy.dtype size changed` and `_faiss_import` failure.
*   **Cause**: `numpy` 2.x is incompatible with current `transformers` and `faiss-cpu`.
*   **Fix**: Downgraded and pinned `numpy<2.0.0` (installed 1.26.4).

### Issue E: "LangChain Version Mismatch"
*   **Symptom**: `TypeError: FAISS.__init__() got an unexpected keyword argument 'allow_dangerous_deserialization'`.
*   **Cause**: Code was written for a newer LangChain version than what was installed.
*   **Fix**: Removed the incompatible flag from `actions.py`.

## 2. Current State
*   System is **STABLE**.
*   Ingestion works (bad files skipped).
*   Inference works.
*   Ready for model upgrade.
