# Workflow Log: System Compatibility Check
**Date**: 2026-01-23
**Task**: Verify system hardware and software compatibility for model upgrades.

## 1. System Specifications
*   **OS**: Windows
*   **Python Version**: 3.10.11
*   **CPU**: 11th Gen Intel(R) Core(TM) i5/i7 (implied from generation).
*   **RAM**: 8 GB
*   **GPU**: NVIDIA GeForce RTX 3050 (4GB VRAM) [Confirmed from user history].

## 2. Compatibility Analysis
*   **VRAM Constraints (4GB)**:
    *   **Critical**: 4GB VRAM is very tight for modern LLMs.
    *   **Limit**: A standard 7B model (float16) requires ~14GB.
    *   **Solution**: We MUST use **4-bit quantization (GGUF or BitsAndBytes)**.
        *   TinyLlama-1.1B (Float16: ~2.2GB, 4-bit: ~0.7GB) - *Safe*.
        *   Phi-2 (2.7B) (Float16: ~5.4GB, 4-bit: ~1.8GB) - *Safe*.
        *   Gemma-2B (Float16: ~4GB, 4-bit: ~1.5GB) - *Safe*.
        *   Mistral-7B / Llama-3-8B (4-bit: ~5GB) - *Risky/Likely OOM* on 4GB VRAM alone, would spill to system RAM.
*   **System RAM Constraints (8GB)**:
    *   Running the OS + VS Code + Browser + Node Backend + Python Service + Model inference will saturate 8GB quickly.
    *   **Recommendation**: We must stick to smaller, efficient models (SLMs) rather than full LLMs.

## 3. Recommended Stack
Given the 8GB RAM / 4GB VRAM constraint:
1.  **Embedding**: `ai4bharat/IndicBERT-v3-1B` (or `sentence-transformers/all-MiniLM-L6-v2` for speed).
2.  **Reranker**: Keep `cross-encoder/ms-marco-MiniLM-L-6-v2` (Very small, efficient).
3.  **Generator (LLM)**:
    *   **Option A (Speed/Safety)**: `TinyLlama-1.1B-Chat` or `Gemma-2b-it`.
    *   **Option B (Quality/Risk)**: `Phi-3-mini` (3.8B) quantized to 4-bit (might fit tightly).
    *   **Recommendation**: Start with **Gemma-2b-it** or **TinyLlama** for guaranteed stability.

## 4. Next Steps
*   Install `torch` with CUDA support.
*   Set up a `requirements.txt`.
*   Implement the model swap using `CTransformers` or `LlamaCpp` for GGUF support to save RAM.
