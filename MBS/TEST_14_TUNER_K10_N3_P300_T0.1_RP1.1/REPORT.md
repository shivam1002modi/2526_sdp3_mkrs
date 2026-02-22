# TEST 14 — TUNER_k10_n3_p300_t0.1_rp1.1
## MKRS Brain Snapshot

> **Date**: 2026-02-22 11:51:53
> **MBS Version**: 1.0
> **TMS Score**: **70.9 / 100**
> **Grade**: 🟠 MODERATE — Working but unreliable

---

## 📊 SCORE BREAKDOWN

| Metric | Raw Value | Score | Weight | Points |
| :--- | :--- | :--- | :--- | :--- |
| RHR – Retrieval Hit Rate | 75.0% | 0.7500 | ×40 | **30.00** |
| SEC – Fact Accuracy | 53.3% | 0.5333 | ×30 | **16.00** |
| NEG – No Hallucination | 95.0% | 0.9500 | ×10 | **9.50** |
| LAT – Speed | avg 3.70s | 0.5401 | ×10 | **5.40** |
| VRAM – GPU Memory | 0 MB | 1.0000 | ×10 | **10.00** |
| **TOTAL TMS** | | | | **70.9** |

---

## 🗂️ QUESTION-BY-QUESTION RESULTS

| ID | Domain & Query | RHR | SEC | NEG | Latency | Verdict |
| :-- | :--- | :---: | :---: | :---: | ---: | :--- |
| Q01 | [MAIN] What is a black hole? | ✅ | 1.00 |  | 10.7s | ✅ Pass |
| Q02 | [MAIN] Who coined the term black hole and when? | ✅ | 1.00 |  | 6.1s | ✅ Pass |
| Q03 | [MAIN] What is the Event Horizon of a black hole? | ✅ | 0.67 |  | 4.3s | ⚠️ Partial |
| Q04 | [MAIN] What is Hawking Radiation? | ✅ | 1.00 |  | 3.7s | ✅ Pass |
| Q05 | [MAIN] What is Sagittarius A star? | ❌ | 0.00 |  | 0.3s | ❌ Not retrieved |
| Q06 | [MAIN] What is the historical significance of Delhi? | ✅ | 0.00 |  | 4.9s | ❌ Failed SEC |
| Q07 | [MAIN] Who built the Red Fort and what city did they foun | ✅ | 1.00 |  | 4.7s | ✅ Pass |
| Q08 | [MAIN] When did the British shift India's capital to Delh | ✅ | 1.00 |  | 3.4s | ✅ Pass |
| Q09 | [MAIN] What is Navratri festival? | ✅ | 0.67 |  | 4.8s | ⚠️ Partial |
| Q10 | [MAIN] Who is Mahishasura in the Navratri legend? | ✅ | 1.00 |  | 5.3s | ✅ Pass |
| Q11 | [MAIN] What is RAG's role in the SIH 2025 chatbot? | ❌ | 0.00 |  | 0.4s | ❌ Not retrieved |
| Q12 | [MAIN] What caused dinosaur extinction 66 million years a | ✅ | 1.00 |  | 3.9s | ✅ Pass |
| Q13 | [MAIN] What is Robert Sternberg's Triangular Theory of Lo | ✅ | 1.00 |  | 4.6s | ✅ Pass |
| Q14 | [STRESS] What is the Mars Mission about? | ✅ | 0.33 |  ✅ | 4.6s | ⚠️ Partial |
| Q15 | [STRESS] What type of fuel does the Mars rocket use? | ✅ | 0.00 |  ✅ | 3.0s | ❌ Failed SEC |
| Q16 | [STRESS] What is the landing zone for the Mars mission? | ❌ | 0.00 |  ✅ | 0.3s | ❌ Not retrieved |
| Q17 | [STRESS] How long do you bake Apple Pie? | ✅ | 0.00 |  ❌HALL | 3.8s | ❌ HALLUCINATED |
| Q18 | [STRESS] What temperature to preheat oven for Apple Pie? | ✅ | 1.00 |  ✅ | 4.5s | ✅ Pass |
| Q19 | [STRESS] Which department had the highest profit in Q3 2025 | ❌ | 0.00 |  ✅ | 0.3s | ❌ Not retrieved |
| Q20 | [STRESS] Which department has the lowest margin in the Q3 2 | ❌ | 0.00 |  ✅ | 0.3s | ❌ Not retrieved |

---

## ⚠️ ROOT CAUSE ANALYSIS

- **Q05** (`What is Sagittarius A star?`): Retrieval below confidence — re-ranker rejected or chunk missing
- **Q06** (`What is the historical significance of D`): Generation model failed to extract relevant facts
- **Q11** (`What is RAG's role in the SIH 2025 chatb`): Retrieval below confidence — re-ranker rejected or chunk missing
- **Q15** (`What type of fuel does the Mars rocket u`): Generation model failed to extract relevant facts
- **Q16** (`What is the landing zone for the Mars mi`): Retrieval below confidence — re-ranker rejected or chunk missing
- **Q17** (`How long do you bake Apple Pie?`): Generation model blended wrong context into answer
- **Q19** (`Which department had the highest profit `): Retrieval below confidence — re-ranker rejected or chunk missing
- **Q20** (`Which department has the lowest margin i`): Retrieval below confidence — re-ranker rejected or chunk missing

---

## 🛠️ FULL SYSTEM SNAPSHOT

> Every component, model, config, and parameter as they existed during this test.

---

### 1. EMBEDDING MODEL
| Property | Value |
| :--- | :--- |
| Model Name | `paraphrase-xlm-r-multilingual-v1` |
| Library | sentence-transformers via langchain HuggingFaceEmbeddings |
| Dimensions | 768 |
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
| Confidence Threshold | 0.05 |
| Retrieval k (candidates) | 10 (top-3 after re-ranking) |
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
| Chunk Size | 500 characters |
| Chunk Overlap | 50 characters |
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
    ├─ paraphrase-xlm-r-multilingual-v1 → embed query (dim=768)
    ├─ ChromaDB.similarity_search(k=10) → top-10 chunks
    ├─ cross-encoder/ms-marco-MiniLM-L-6-v2 → re-rank → top-3
    │       └─ if score < 0.05 → "not confident"
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

*Archived 2026-02-22 11:51:53 — MBS v1.0*
