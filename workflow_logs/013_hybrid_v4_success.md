# Workflow Log: Deep Dive V4 (Hybrid)
**Date**: 2026-01-23
**Status**: SUCCESS (Hybrid Ingestion Active)

## The Final Architecture (V4)
To solve the "Column Merging" vs "Title Bridging" conflict, we implemented a **Hybrid Histogram Engine**:

1.  **Y-Axis Segmentation**: Only split the page horizontally if there is a massive text gap (finding the "Title Band").
2.  **X-Axis Histogram**: Inside each band (e.g. Body Band), calculate pixel-level text density.
3.  **Valley Detection**: If a center gap of >15px exists, it is mathematically proven to be Multi-Column.
4.  **Split & Read**: Divide the band into Col A / Col B and read linearly.

## Verification
*   **Stress Test**: `stress_test.pdf` was processed.
*   **Logs**: `[DeepDive V4] Ingesting... (Hybrid Mode)` confirmed.
*   **DB**: ChromaDB rebuilt from scratch.

## User Action
*   **Restart**: The Vector Store has changed structure. Restart `start_system.bat` to load the new index.
