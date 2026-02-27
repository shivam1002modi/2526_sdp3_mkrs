# MKRS BRAIN V1.0 — ULTRA-DEEP DIVE LOGIC
## Detailed Code-Level Breakdown

This document provides a line-by-line conceptual breakdown of the logic implemented in the MBS V1.0 Sequential PDR system.

---

### 1. `smart_ingest.py`: Multi-Stage Column-Aware Extraction

The ingestion engine is designed to solve the "PDF Reading" problem—where text is stored as individual characters with (x,y) coordinates, not as structured paragraphs.

#### A. Global Artifact Suppression
The engine first scans the header (top 10%) and footer (bottom 10%) of every page. 
*   **Logic:** It builds a frequency map of every line found in these zones.
*   **Threshold:** If a line (e.g., "Confidential Report v1") appears in more than 60% of pages, the engine flags it as a "document-level artifact." 
*   **Result:** These lines are automatically stripped from the final text stream, preventing them from polluting the vector database and confusing the LLM.

#### B. The Y-Band Segmentation Algorithm
Standard PDF readers read top-to-bottom, which mixes columns. `SmartIngest` uses a vertical density histogram.
1.  It projects all characters onto the Y-axis.
2.  It identifies "Solid Bands" (where text exists) and "Transition Gaps" (where vertical space is > 12px).
3.  **Key Insight:** By treating each horizontal band as a unique zone, we can detect if a specific section has two columns while another (like a title) is full-width.

#### C. Per-Band X-Histogram Analysis
For every horizontal band:
1.  Project characters onto the X-axis.
2.  Find gaps in character density.
3.  **Logic:** If a gap > 15px exists in the middle of a band, it is split into "Column A" and "Column B."
4.  **Reading Order:** The characters in Column A are sorted and read fully before moving to Column B. This ensures that a multi-column article is read logically, not from the first line of Col A to the first line of Col B.

#### D. Table Masking & Atomic Extraction
*   **Logic:** The engine uses `pdfplumber`'s table detection to find bounding boxes of tables.
*   **Action:** It extracts these as Markdown (preserving structure) and then "masks" those areas for the text extractor. This prevents the "Cell A1 Cell B1" reading error.

---

### 2. `smart_chunker.py`: Two-Tier PDR & Semantic Boundaries

#### A. Semantic Splitting Priority
Instead of splitting text at exactly 500 characters, the `SemanticSplitter` looks for the "softest" point to cut:
1.  **Double Newline (\n\n):** Best case, preserves paragraph integrity.
2.  **Sentence Enders (. ! ?):** Preserves complete thoughts.
3.  **Clause Enders (, ; :):** Preserves phrase context.
4.  **Whitespace:** The absolute last resort.
*   **Never-Cut Rule:** The regex logic ensures we never split mid-word or mid-number (e.g., "19|99").

#### B. Parent-Child Relationship (The PDR Hook)
*   **Parent Chunks:** 1500 chars. Large enough to contain 2-3 full paragraphs. This is what the LLM reads.
*   **Child Chunks:** 300-500 chars. Small enough that the embedding model (`IndicBERT`) can represent the "essence" of the text perfectly.
*   **The Link:** Every child chunk in the vector store has a metadata field `parent_id`. This is the ID of its larger parent in the JSON store.

#### C. Atomic Tables with Context
When a table is found:
1.  It is NOT split, no matter its size.
2.  **Enrichment:** The chunker prepends the last 2 sentences of text found *before* the table to the table chunk itself. Note: "Financial Results" followed by a table makes the table searchable by the term "Financial Results."

---

### 3. `actions.py`: The Retrieval & Re-ranking Brain

#### A. Broad Retrieval (Record Breaker Config)
*   The system doesn't just get 3 documents; it gets **60**.
*   **Rationale:** Initial vector search is fast but "blunt." By pulling 60 candidates, we ensure that even if the "perfect" document is ranked #40 due to phrasing differences, we still capture it.

#### B. Cross-Encoder Re-Ranking
*   We use `cross-encoder/ms-marco-MiniLM-L-6-v2`. 
*   Unlike vector search (which compares two vectors), a Cross-Encoder looks at the `Query` and the `Document` together. 
*   **Logic:** It performs a deep semantic comparison. It re-scores all 60 results. The document that was #40 in the vector list might jump to #1 here.

#### C. Context Limit & Deduplication
*   The system picks the top 15 child chunks after re-ranking.
*   It then expands them to their 1500-char parents.
*   **Deduplication:** If Child 1 and Child 2 both belong to Parent A, Parent A is only sent once. 
*   **Final Limit:** The prompt is capped at 5 unique parents to prevent the LLM from being overwhelmed by "noise."

---

### 4. `indic_embeddings.py`: The Mathematical Foundation
*   **Model:** `ai4bharat/IndicBERT-v3-1B`.
*   **Batching:** Implements batch processing (size=8) to ensure the system doesn't run out of GPU/CPU memory during massive ingestion.
*   **Normalization:** L2 Normalization ensures that "distance" between vectors is calculated reliably, making retrieval scores consistent.
