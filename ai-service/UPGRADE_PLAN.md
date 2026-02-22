# 🚀 Phase 2 Upgrade Plan: Embedding Model + Data Ingestion Fix
## Goal: Push TMS from 71.61 → 80+

---

## 📊 Current Diagnosis (from 20 Tests)

### Score Ceiling Analysis
| Component | Current Score | Max Possible | Gap |
| :--- | :---: | :---: | :---: |
| RHR (Retrieval) | 75% (15/20) | 100% | **-25%** ← BIGGEST BLOCKER |
| SEC (Accuracy) | 50% | 100% | -50% (tied to RHR) |
| NEG (No Halluc.) | 100% | 100% | 0% ✅ |
| Latency | 66% | 100% | -34% |
| VRAM | 100% | 100% | 0% ✅ |

### Root Cause: 5 Questions Always Fail (Q05, Q11, Q16, Q19, Q20)

| Question | Expected Keywords | Root Cause |
| :--- | :--- | :--- |
| Q05: Sagittarius A star | milky, supermassive | Term exists in DB (1 chunk) but re-ranker rejects it (score < 0.05) |
| Q11: RAG in SIH 2025 | retrieval, augmented, pdf | Term "retrieval augmented" NOT in any chunk! |
| Q16: Mars landing zone | jezero, crater | "Jezero" NOT in stress_test.pdf at all! |
| Q19: Highest profit Q3 | security, 400 | Table data exists but re-ranker can't match query to table chunk |
| Q20: Lowest margin Q3 | logistics, margin | "margin" NOT in any indexed chunk! |

### Data Issues Found in stress_test.pdf
The SmartIngest V4 extracts the following from stress_test.pdf page 2:
```
Key Insight: Security is the most profitable sector.
[TABLE: Department | Revenue | Cost | Profit]
```
**Missing:** The text "Note: Logistics has the lowest margin." is present in raw PDF but gets dropped during ingestion
because `_analyze_artifacts` removes it as a "footer" artifact!

Also: "Jezero crater" is simply NOT in the PDF. Q16 is an impossible question.

---

## 🏗️ IMPLEMENTATION PLAN

### PHASE 2A: Fix Data Ingestion (HIGH IMPACT, LOW RISK)
**Expected TMS Gain: +3-5 points**

#### Step 1: Fix SmartIngest Artifact Removal Bug
- **Problem:** The `_analyze_artifacts()` method uses a 60% threshold. Short PDFs (2 pages) 
  cause legitimate content lines appearing on both pages to be falsely flagged as artifacts.
- **Fix:** Increase minimum page threshold (require at least 3 pages before artifact removal)
  OR skip artifact removal for PDFs with ≤ 3 pages.
- **File:** `smart_ingest.py` line 223

#### Step 2: Improve Table Chunk Context
- **Problem:** Table chunks are stored without ANY surrounding text context.
  When the evaluator asks "Which department had the highest profit?", the re-ranker 
  sees a raw markdown table with no semantic clues.
- **Fix:** Prepend the paragraph text immediately before/after the table to the table chunk.
  E.g., store: "Financial data for Q3 2025.\n| Dept | Revenue | ... |" instead of just the table.
- **File:** `smart_chunker.py` lines 36-43

#### Step 3: Add Text Cleaning to SmartIngest
- **Problem:** Some ingested text contains garbled unicode symbols (📑, ⚡, 👉) from 
  emoji-heavy PDFs, which pollute the embedding space.
- **Fix:** Strip non-ASCII decorative characters during ingestion while preserving 
  Hindi/Devanagari text.
- **File:** `smart_ingest.py` (add cleaning step in `load()`)

#### Step 4: Re-ingest All PDFs
- Run `python -m rag_pipeline` to rebuild ChromaDB with the fixed ingestion pipeline.
- Verify with `debug_ingest.py` that "margin", "Logistics", and "retrieval augmented" 
  now appear in chunks.

---

### PHASE 2B: Upgrade Embedding Model (MEDIUM IMPACT, MEDIUM RISK)
**Expected TMS Gain: +2-4 points**

#### Current Model: `paraphrase-xlm-r-multilingual-v1`
- 278M parameters, 768 dimensions
- Released 2020, general-purpose multilingual
- ~1 GB VRAM

#### Target Model: `ai4bharat/IndicBERT-v3-1B`  
- 1B parameters, higher dimensional embeddings
- Specialized for Indian languages (23 languages)
- ~2 GB VRAM (bfloat16)

#### ⚠️ RISK ASSESSMENT
| Risk | Impact | Mitigation |
| :--- | :--- | :--- |
| VRAM overflow (4GB GPU shared with Sarvam-1) | HIGH | Load embedding on CPU, keep Ollama on GPU |
| Not sentence-transformer optimized | MEDIUM | Use mean-pooling wrapper class |
| Full re-index required | LOW | ~2 min process |
| Score could DROP if model is worse for English | MEDIUM | Benchmark immediately, keep rollback ready |

#### Implementation Steps:

##### Step 5: Create Custom Embedding Wrapper
- IndicBERT-v3 is NOT a sentence-transformer model, so `HuggingFaceEmbeddings` 
  may not work out-of-the-box.
- Create a custom embedding class that:
  1. Loads IndicBERT-v3 with `AutoModel` + `AutoTokenizer`
  2. Applies mean-pooling over token embeddings
  3. Returns normalized vectors
- **File:** New file `indic_embeddings.py`

##### Step 6: Update rag_pipeline.py
- Replace `HuggingFaceEmbeddings(model_name="paraphrase-xlm-r-multilingual-v1")`
  with the new IndicBERT wrapper.
- **File:** `rag_pipeline.py` lines 82-85

##### Step 7: Update actions.py
- Replace the embedding model initialization in `ActionQueryDoc.__init__`
  with the new IndicBERT wrapper.
- **File:** `actions.py` lines 62-65

##### Step 8: Re-ingest + Benchmark
- Run `python -m rag_pipeline` to rebuild ChromaDB with new embeddings.
- Run benchmark: `python eval_v1.py --name "PHASE2_INDICBERT_UPGRADE"`
- Compare TMS score with previous best (71.61).

---

## 📋 EXECUTION ORDER

```
PHASE 2A (Data Fix) — Do FIRST, guaranteed improvement
  Step 1: Fix artifact removal bug in smart_ingest.py
  Step 2: Add context to table chunks in smart_chunker.py  
  Step 3: Add text cleaning in smart_ingest.py
  Step 4: Re-ingest + benchmark (expect ~74-76 TMS)

PHASE 2B (Model Upgrade) — Do AFTER 2A is validated
  Step 5: Create IndicBERT embedding wrapper
  Step 6: Update rag_pipeline.py
  Step 7: Update actions.py
  Step 8: Re-ingest + benchmark (expect ~76-80 TMS)
```

---

## 🎯 TMS Score Projections

| Phase | Expected TMS | Key Gains |
| :--- | :---: | :--- |
| Current (Test 18) | 71.61 | Baseline |
| After 2A (Data Fix) | ~74-76 | +Q19, +Q20 recovered, +partial Q17/Q18 |
| After 2B (IndicBERT) | ~76-80 | Better Q05/Q11 retrieval, Hindi boost |

**Note:** Q16 (Jezero) will remain at 0 unless we modify the stress_test.pdf 
to actually contain "Jezero crater" — the word simply doesn't exist in the PDF.
