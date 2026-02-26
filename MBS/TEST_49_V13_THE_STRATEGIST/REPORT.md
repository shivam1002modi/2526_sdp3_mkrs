# TEST 49 — V13_THE_STRATEGIST
## MKRS Brain Snapshot

> **Date**: 2026-02-27 00:50:36
> **MBS Version**: 1.0
> **TMS Score**: **85.26 / 100**
> **Grade**: 🟢 GOOD — Solid, minor improvements possible

---

## 📊 SCORE BREAKDOWN

| Metric | Raw Value | Score | Weight | Points |
| :--- | :--- | :--- | :--- | :--- |
| RHR – Retrieval Hit Rate | 100.0% | 1.0000 | ×40 | **40.00** |
| SEC – Fact Accuracy | 75.0% | 0.7500 | ×30 | **22.50** |
| NEG – No Hallucination | 90.0% | 0.9000 | ×10 | **9.00** |
| LAT – Speed | avg 5.32s | 0.3762 | ×10 | **3.76** |
| VRAM – GPU Memory | 0 MB | 1.0000 | ×10 | **10.00** |
| **TOTAL TMS** | | | | **85.26** |

---

## 🗂️ QUESTION-BY-QUESTION RESULTS

| ID | Domain & Query | RHR | SEC | NEG | Latency | Verdict |
| :-- | :--- | :---: | :---: | :---: | ---: | :--- |
| Q01 | [MAIN] What is a black hole? | ✅ | 0.67 |  | 6.0s | ⚠️ Partial |
| Q02 | [MAIN] Who coined the term black hole and when? | ✅ | 1.00 |  | 6.3s | ✅ Pass |
| Q03 | [MAIN] What is the Event Horizon of a black hole? | ✅ | 1.00 |  | 5.8s | ✅ Pass |
| Q04 | [MAIN] What is Hawking Radiation? | ✅ | 1.00 |  | 5.7s | ✅ Pass |
| Q05 | [MAIN] What is Sagittarius A star? | ✅ | 1.00 |  | 4.7s | ✅ Pass |
| Q06 | [MAIN] What is the historical significance of Delhi? | ✅ | 0.67 |  | 5.4s | ⚠️ Partial |
| Q07 | [MAIN] Who built the Red Fort and what city did they foun | ✅ | 0.67 |  | 5.0s | ⚠️ Partial |
| Q08 | [MAIN] When did the British shift India's capital to Delh | ✅ | 1.00 |  | 5.3s | ✅ Pass |
| Q09 | [MAIN] What is Navratri festival? | ✅ | 0.67 |  | 6.3s | ⚠️ Partial |
| Q10 | [MAIN] Who is Mahishasura in the Navratri legend? | ✅ | 1.00 |  | 4.7s | ✅ Pass |
| Q11 | [MAIN] What is RAG's role in the SIH 2025 chatbot? | ✅ | 0.00 |  | 5.1s | ❌ Failed SEC |
| Q12 | [MAIN] What caused dinosaur extinction 66 million years a | ✅ | 1.00 |  | 5.4s | ✅ Pass |
| Q13 | [MAIN] What is Robert Sternberg's Triangular Theory of Lo | ✅ | 1.00 |  | 5.6s | ✅ Pass |
| Q14 | [STRESS] What is the Mars Mission about? | ✅ | 0.33 |  ✅ | 4.6s | ⚠️ Partial |
| Q15 | [STRESS] What type of fuel does the Mars rocket use? | ✅ | 1.00 |  ✅ | 5.6s | ✅ Pass |
| Q16 | [STRESS] What is the landing zone for the Mars mission? | ✅ | 1.00 |  ✅ | 4.6s | ✅ Pass |
| Q17 | [STRESS] How long do you bake Apple Pie? | ✅ | 0.00 |  ❌HALL | 5.4s | ❌ HALLUCINATED |
| Q18 | [STRESS] What temperature to preheat oven for Apple Pie? | ✅ | 1.00 |  ✅ | 4.9s | ✅ Pass |
| Q19 | [STRESS] Which department had the highest profit in Q3 2025 | ✅ | 0.00 |  ✅ | 4.6s | ❌ Failed SEC |
| Q20 | [STRESS] Which department has the lowest margin in the Q3 2 | ✅ | 1.00 |  ❌HALL | 5.1s | ✅ Pass |

---

## ⚠️ ROOT CAUSE ANALYSIS

- **Q11** (`What is RAG's role in the SIH 2025 chatb`): Generation model failed to extract relevant facts
- **Q17** (`How long do you bake Apple Pie?`): Generation model blended wrong context into answer
- **Q19** (`Which department had the highest profit `): Generation model failed to extract relevant facts

---

## 🛠️ FULL SYSTEM SNAPSHOT

> Every component, model, config, and parameter as they existed during this test.

---

### 1. EMBEDDING MODEL
| Property | Value |
| :--- | :--- |
| Model Name | `ai4bharat/IndicBERT-v3-1B` |
| Library | Custom Wrapper (Transformers + Mean Pooling) |
| Dimensions | 1024 |
| Device | CPU |

### 2. GENERATION MODEL (LLM)
| Property | Value |
| :--- | :--- |
| Model Name | `unknown` |
| Pipeline Type | `unknown` |
| Device | CPU |
| Note | This is a summarization model, not an instruction-following LLM |

### 3. RE-RANKER
| Property | Value |
| :--- | :--- |
| Model Name | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| Confidence Threshold | 0.0 |
| Retrieval k (candidates) | 60 (top-3 after re-ranking) |
| Device | CPU |

### 4. TRANSLATION LAYER
  - `hi` → `Helsinki-NLP/opus-mt-en-hi`


### 5. INGESTION ENGINE
| Property | Value |
| :--- | :--- |
| Method | `SmartIngest (: )` |
| Library | pdfplumber |
| Features | Layout-aware reading, Y/X histogram column detection, table masking, header/footer artifact removal |

### 6. CHUNKING ENGINE
| Property | Value |
| :--- | :--- |
| Chunk Size | 1500 characters |
| Chunk Overlap | 200 characters |
| Table Handling | Regex-based atomic preservation (unsplit) |
| Splitter | RecursiveCharacterTextSplitter |

### 7. VECTOR STORE
| Property | Value |
| :--- | :--- |
| Type | ChromaDB |
| Path | `d:\MKRS\ai-service\documents\chroma_db` |
| Exists | True |

### 8. RASA NLU
| Property | Value |
| :--- | :--- |
| NLU Feature Model | `bert-base-multilingual-cased` |
| Pipeline | WhitespaceTokenizer → CountVectors → LanguageModelFeaturizer → DIETClassifier |

### 9. COMPUTE DEVICE
| Property | Value |
| :--- | :--- |
| Device | CPU |
| GPU | N/A (CPU fallback) |

---

## 📄 KNOWLEDGE BASE

**12 PDFs indexed:**
  - `1759248623779-navratri.pdf`
  - `1765007523589-delhi_.pdf`
  - `Black Holes â A Knowledge Guide.pdf`
  - `dinasours.pdf`
  - `love.pdf`
  - `sih 2025 prototype (1).pdf`
  - `sih 2025 prototype (2).pdf`
  - `sih 2025 prototype.pdf`
  - `SIH_2025_Blueprint.pdf`
  - `stress_test.pdf`
  - `Untitled document (5).pdf`
  - `Untitled document (6).pdf`

---

## 🔗 DATA FLOW (End-to-End)

```
[User Query]
    ↓
[Rasa NLU :5005] → intent detection (bert-base-multilingual-cased)
    ↓
[Rasa Actions :5055] → ActionQueryDoc.run()
    ├─ langdetect → detect language
    ├─ ai4bharat/IndicBERT-v3-1B → embed query (dim=1024)
    ├─ ChromaDB.similarity_search(k=60) → top-60 chunks
    ├─ cross-encoder/ms-marco-MiniLM-L-6-v2 → re-rank → top-3
    │       └─ if score < 0.0 → "not confident"
    ├─ unknown → generate answer
    └─ Translation (if needed)
    ↓
[JSON {text, sources[]}] → Backend :5001 → Frontend :3000
```

---

## 📁 FILES IN THIS TEST FOLDER

| File | Description |
| :--- | :--- |
| `REPORT.md` | This document — full system snapshot and results |
| `raw_scores.json` | Machine-readable per-question data |

---

*Archived 2026-02-27 00:50:36 — MBS v1.0*
