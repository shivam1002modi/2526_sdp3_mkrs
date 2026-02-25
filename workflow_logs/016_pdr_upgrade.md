# Workflow Log 016: Parent Document Retrieval (PDR) Upgrade
**Date**: 2026-02-26
**Status**: ✅ COMPLETE
**Agent**: AI Agent

---

## 1. Problem Statement
The system was hitting a **45-52% SEC (Fact Accuracy) ceiling** despite 95% RHR (Retrieval Hit Rate). Root cause analysis across 29 tests showed:

- **Split Facts**: 500-char flat chunks often cut sentences in half, losing key details (dates, names, numbers).
- **Missing Context**: When the LLM received a small chunk, it lacked the surrounding paragraph to understand the full answer.
- **Table Isolation**: Table chunks were stored without their preceding headings, making them unsearchable by topic.

**Affected Questions** (consistently failing SEC):
- Q02: "Who coined the term black hole?" — "Wheeler, 1967" split across two chunks
- Q08: "When did the British shift capital?" — "1911, Calcutta" in a separate chunk
- Q12: "What caused dinosaur extinction?" — "asteroid, impact" context too small
- Q15: "Mars rocket fuel?" — "liquid hydrogen" lost in chunking
- Q19/Q20: Table data without contextual headings

## 2. Solution: Two-Tier Parent Document Retrieval (PDR)

### Architecture
```
INGESTION (rag_pipeline.py):
  SmartIngest → SmartChunker PDR → {
    CHILD chunks (300 chars) → ChromaDB (for retrieval)
    PARENT contexts (1500 chars) → parent_store.json (for expansion)
  }

QUERY TIME (actions.py):
  User Query → Embed → ChromaDB.search(k=15) → top-15 CHILDREN
    → CrossEncoder re-rank → top-5 CHILDREN
    → PDR Expand: child.parent_id → parent_store[parent_id]
    → Deduplicate parents → top-3 UNIQUE PARENT contexts
    → Ollama (Sarvam-1) generates answer from PARENT contexts
```

### Key Parameters
| Parameter | Old Value | New Value |
|:---|:---:|:---:|
| Retrieval chunk size | 500 chars | 300 chars (child) |
| LLM context size | 500 chars | 1500 chars (parent) |
| Chunk overlap | 50 chars | 50 child / 200 parent |
| Context deduplication | None | Parent-ID based |
| Table enrichment | None | Preceding paragraph prepended |

## 3. Files Modified

| File | Change |
|:---|:---|
| `smart_chunker.py` | Complete rewrite — PDR two-tier chunking with table enrichment |
| `rag_pipeline.py` | Updated to save child chunks to ChromaDB + parent store to JSON |
| `actions/actions.py` | Added parent store loading, PDR expansion, parent deduplication |

## 4. Ingestion Results
- **12 PDFs** processed
- **37 parent contexts** created (avg 869 chars, max 1493 chars)
- **Child chunks** stored in ChromaDB (precise, small, for similarity search)
- **parent_store.json** saved to disk (33.8 KB)

## 5. Expected Impact
| Metric | Before (Test 27) | Expected After |
|:---|:---:|:---:|
| SEC Score | 51.7% | 65-75% (+15-25%) |
| TMS Score | 77.96 | 82-88 |
| Context per query | ~500 chars × 3 | ~1200 chars × 3 |

## 6. Next Steps
- [ ] Run MBS benchmark: `.\ai-service\venv\Scripts\python.exe ai-service\eval_v1.py --name "PDR_UPGRADE"`
- [ ] Compare SEC scores per-question against Test 27 baseline
- [ ] If SEC improves, commit and push
