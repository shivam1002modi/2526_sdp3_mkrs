# TECHNICAL SPECIFICATIONS — V1.0 (Sequential PDR Architecture)
## Project: MKRS Brain — Industry-Grade RAG System
**Version Name:** `MBS Baseline v1.0 - Hybrid PDR Architecture`
**Date:** 2026-02-27

---

## 1. Executive Summary
The V1.0 architecture is a high-accuracy, sequential RAG pipeline optimized for document extraction and retrieval factuality. It achieves reaching a **TMS Score of 84.86** by utilizing Parent Document Retrieval (PDR) combined with sophisticated column-aware PDF ingestion.

---

## 2. Core Components & Logic

### 2.1 Ingestion Engine (`SmartIngest V10`)
**Objective:** Accurate reconstruction of text flow from complex multi-column and tabular PDFs.

*   **Logic:**
    1.  **Statistical Artifact Detection:** Analyzes the first and last 10% of every page across the PDF. If a string (like a header or page number) appears in >60% of pages, it is flagged as an artifact and removed from the content stream.
    2.  **Y-Band Segmentation:** Instead of reading line-by-line, the engine segments the page vertically based on whitespace gaps (`BAND_GAP_PX=12`).
    3.  **Per-Band X-Histogram Analysis:** For each horizontal band, a histogram of character density is built. Gaps in characters (`COLUMN_GAP_MIN_PX=15`) identify column boundaries within that band only.
    4.  **Table Masking:** Uses `pdfplumber` to detect table regions, extracts them as Markdown, and "masks" those coordinates so the text extractor ignores them, preventing table data from being garbled into the prose.

### 2.2 Chunking & Storage (`SmartChunker V3`)
**Objective:** Solve the "Context-vs-Precision" trade-off.

*   **PDR Strategy:**
    *   **Child Chunks (300 chars):** Small, semantically dense snippets. These are stored in **ChromaDB** with embeddings. Small chunks lead to higher retrieval precision (higher RHR).
    *   **Parent Contexts (1500 chars):** Larger horizontal slices of the original document. These are stored in `parent_store.json`.
*   **Semantic Boundary Logic:** 
    *   Uses a `SemanticSplitter` that prioritizes `\n\n` (Paragraphs) > `.` (Sentences) > `,` (Clauses) > ` ` (Words).
    *   **Atomic Tables:** Tables are detected via regex and kept 100% atomic (never split) to preserve row-column relationships.

### 2.3 Embedding Layer (`IndicBERT-v3-1B`)
*   **Model:** `ai4bharat/IndicBERT-v3-1B`.
*   **Method:** Mean Pooling + L2 Normalization.
*   **Performance:** Optimized for Indian languages and technical English, providing 1024-dimensional vectors.

### 2.4 Retrieval & Re-ranking Agent (`ActionQueryDoc`)
*   **Step 1: Broad Retrieval:** Fetches top-60 child chunks from ChromaDB using cosine similarity.
*   **Step 2: Cross-Encoder Re-ranking:** Uses `ms-marco-MiniLM-L-6-v2` to score the 60 chunks against the query. Only those with a high semantic match are kept.
*   **Step 3: PDR Expansion:** For the top-ranked child chunks, the system looks up their `parent_id` and pulls the 1500-char parent context.
*   **Step 4: Deduplication:** If multiple child chunks point to the same parent, the parent is only sent to the LLM once.

### 2.5 Generation & Verification
*   **Model:** `mashriram/sarvam-1` (via Ollama).
*   **Prompting:** Uses an "Exhaustive Verbatim" prompt that forces the model to quote the context directly, minimizing hallucinations (NEG Score 100%).

---

## 3. Baseline Performance (TEST 52)
| Metric | Score | Status |
| :--- | :--- | :--- |
| **TMS (Total)** | **84.86** | 🟢 Good |
| RHR (Retrieval) | 100.0% | 🏆 Perfect |
| SEC (Factuality)| 70.8% | ⚠️ Improvement Needed |
| NEG (Hallucination)| 100.0% | 🏆 Perfect |
| Latency | ~5.5s | ⚡ Fast |

---

## 4. Current Limitations (Transitioning to V2)
1.  **Linear Flow:** If the re-ranker fails to find a good match in the top 60, the system returns a fallback. It cannot "retry" or "reflect."
2.  **Stateless:** Each query is independent. Conversation history is managed but not "agentically."
3.  **Local Scale:** ChromaDB and local file storage will hit I/O limits as document count exceeds 5,000.

---
*End of Technical Specification V1.0*
