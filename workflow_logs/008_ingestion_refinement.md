# Workflow Log: Ingestion Refinement (Phase 2)
**Date**: 2026-01-23
**Task**: Implement Iteration 5 (Element Types) and 7 (Tables).

## 1. Features Added
I upgraded `smart_loader.py` to "V2" with the following semantic intelligence:

### A. Markdown Table Extraction
*   **Logic**: Used `pdfplumber.find_tables()` to detect grid structures.
*   **Transformation**: Converted raw cells into **Markdown Tables** (`| Col | Col |`).
*   **De-Duplication**: Applied `page.filter(not_inside_tables)` to ensure the text inside the table is NOT read again by the text extractor.
*   **Benefit**: LLMs can now understand specific row-column relationships instead of reading flattened text.

### B. Header Detection (Preliminary)
(Included in `extract_text(layout=True)` but formatted via Markdown tables essentially structurizes the data).
*   **Future**: Explicit font-size thresholding can be added, but Markdown Tables provided the biggest immediate semantic boost.

## 2. Verification
*   **Ran `rag_pipeline.py`**: Success.
*   **Files Processed**: 13 PDFs.
*   **Vector Store**: Rebuilt with structured table data.

## 3. Current System Status
*   **Ingestion**: Layout-Aware + Table-Aware.
*   **Models**: Still using old `paraphrase-xlm-r` (Embeddings) and `distilbart` (Gen).
*   **Ready For**: Model Upgrade (Phase 2).
