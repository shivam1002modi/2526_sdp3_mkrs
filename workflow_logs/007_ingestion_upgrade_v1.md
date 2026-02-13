# Workflow Log: Ingestion Engine Upgrade (Phase 1)
**Date**: 2026-01-23
**Task**: Upgrade PDF ingestion from Level-0 (text) to Layout-Aware (coordinates).

## 1. Problem Addressed
*   **Legacy**: `pypdf` extracted text as a flat stream.
*   **Issues**: Loss of layout, no coordinate access, inability to filter headers/footers.
*   **Goal**: Enable "Smart Loading" using `pdfplumber`.

## 2. Changes Implemented
### A. Dependencies
*   Added `pdfplumber` to `requirements.txt`.

### B. New Component: `SmartPDFLoader` (`ai-service/smart_loader.py`)
*   **Library**: `pdfplumber` was chosen for its access to `.chars`, `.lines`, and `.rects`.
*   **Features**:
    1.  **Layout-Aware Extraction**: Uses `page.extract_text(layout=True)` to better respect physical spacing.
    2.  **Scan Detection**: Skips pages with zero characters (preventing silent empty ingestion).
    3.  **Robust Loop**: Processes files individually to isolate errors (crashes on one PDF don't kill the batch).
    4.  **Metadata**: Cleans and normalizes `source` and `page` metadata.

### C. Pipeline Integration
*   Modified `rag_pipeline.py` to import and use `SmartPDFLoader`.
*   Verified successfully with the existing 13 PDFs.

## 3. Next Steps (Refinement)
According to the "Iterative Resolution Loop", we have solved **P3 (Level-0 Tool)** and **P4 (Zero Layout Awareness)**.
Next targets:
*   **P5 (Element Types)**: Distinguish Headers vs Body using font size.
*   **P6 (Columns)**: Detect multi-column layouts using x-coordinate clustering.
*   **P7 (Tables)**: Explicit table extraction using `page.extract_tables()`.
