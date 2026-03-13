# TEST 66 — MBS_DOCKER_EXPANSION_V1
## MKRS Brain Snapshot

> **Date**: 2026-03-13 09:28:22
> **MBS Version**: 1.0
> **TMS Score**: **88.0 / 100**
> **Grade**: 🟢 GOOD — Solid, minor improvements possible

---

## 📊 SCORE BREAKDOWN

| Metric | Raw Value | Score | Weight | Points |
| :--- | :--- | :--- | :--- | :--- |
| RHR – Retrieval Hit Rate | 100.0% | 1.0000 | ×40 | **40.00** |
| SEC – Fact Accuracy | 84.2% | 0.8417 | ×30 | **25.25** |
| NEG – No Hallucination | 100.0% | 1.0000 | ×10 | **10.00** |
| LAT – Speed | avg 7.28s | 0.2748 | ×10 | **2.75** |
| VRAM – GPU Memory | 0 MB | 1.0000 | ×10 | **10.00** |
| **TOTAL TMS** | | | | **88.0** |

---

## 🗂️ QUESTION-BY-QUESTION RESULTS

| ID | Domain & Query | RHR | SEC | NEG | Latency | Verdict |
| :-- | :--- | :---: | :---: | :---: | ---: | :--- |
| Q01 | [MAIN] What is a black hole? | ✅ | 1.00 |  | 8.5s | ✅ Pass |
| Q02 | [MAIN] Who coined the term black hole and when? | ✅ | 1.00 |  | 5.5s | ✅ Pass |
| Q03 | [MAIN] What is the Event Horizon of a black hole? | ✅ | 1.00 |  | 7.6s | ✅ Pass |
| Q04 | [MAIN] What is Hawking Radiation? | ✅ | 1.00 |  | 6.8s | ✅ Pass |
| Q05 | [MAIN] What is Sagittarius A star? | ✅ | 1.00 |  | 7.7s | ✅ Pass |
| Q06 | [MAIN] What is the historical significance of Delhi? | ✅ | 1.00 |  | 8.9s | ✅ Pass |
| Q07 | [MAIN] Who built the Red Fort and what city did they foun | ✅ | 1.00 |  | 6.8s | ✅ Pass |
| Q08 | [MAIN] When did the British shift India's capital to Delh | ✅ | 0.50 |  | 5.9s | ⚠️ Partial |
| Q09 | [MAIN] What is Navratri festival? | ✅ | 1.00 |  | 7.7s | ✅ Pass |
| Q10 | [MAIN] Who is Mahishasura in the Navratri legend? | ✅ | 1.00 |  | 6.8s | ✅ Pass |
| Q11 | [MAIN] What is RAG's role in the SIH 2025 chatbot? | ✅ | 0.33 |  | 12.0s | ⚠️ Partial |
| Q12 | [MAIN] What caused dinosaur extinction 66 million years a | ✅ | 0.67 |  | 6.0s | ⚠️ Partial |
| Q13 | [MAIN] What is Robert Sternberg's Triangular Theory of Lo | ✅ | 1.00 |  | 10.1s | ✅ Pass |
| Q14 | [STRESS] What is the Mars Mission about? | ✅ | 0.33 |  ✅ | 7.6s | ⚠️ Partial |
| Q15 | [STRESS] What type of fuel does the Mars rocket use? | ✅ | 1.00 |  ✅ | 6.1s | ✅ Pass |
| Q16 | [STRESS] What is the landing zone for the Mars mission? | ✅ | 1.00 |  ✅ | 5.8s | ✅ Pass |
| Q17 | [STRESS] How long do you bake Apple Pie? | ✅ | 1.00 |  ✅ | 9.7s | ✅ Pass |
| Q18 | [STRESS] What temperature to preheat oven for Apple Pie? | ✅ | 1.00 |  ✅ | 5.6s | ✅ Pass |
| Q19 | [STRESS] Which department had the highest profit in Q3 2025 | ✅ | 0.50 |  ✅ | 9.3s | ⚠️ Partial |
| Q20 | [STRESS] Which department has the lowest margin in the Q3 2 | ✅ | 0.50 |  ✅ | 9.0s | ⚠️ Partial |
| Q21 | [MAIN] What is the difference between the docker run and  | ✅ | 1.00 |  | 6.0s | ✅ Pass |
| Q22 | [MAIN] What does the -a flag do when used with the docker | ✅ | 1.00 |  | 5.8s | ✅ Pass |
| Q23 | [MAIN] What is a Dockerfile and what is its primary purpo | ✅ | 1.00 |  | 6.5s | ✅ Pass |
| Q24 | [MAIN] How can you give a specific name to a container wh | ✅ | 1.00 |  | 5.4s | ✅ Pass |
| Q25 | [MAIN] What are the four main steps mentioned to work wit | ✅ | 1.00 |  | 6.1s | ✅ Pass |
| Q26 | [MAIN] Why are Docker volumes necessary for stateful appl | ✅ | 1.00 |  | 9.3s | ✅ Pass |
| Q27 | [MAIN] Where are Docker volumes usually stored on a Linux | ✅ | 1.00 |  | 5.5s | ✅ Pass |
| Q28 | [MAIN] What is the difference between Bind Mounts and Doc | ✅ | 0.67 |  | 5.6s | ⚠️ Partial |
| Q29 | [MAIN] What is Docker Compose and why is it useful for mu | ✅ | 0.50 |  | 7.3s | ⚠️ Partial |
| Q30 | [MAIN] How does Docker Compose differ from using the stan | ✅ | 0.25 |  | 7.8s | ⚠️ Partial |

---

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
| Model Name | `llama3.2:3b` |
| Pipeline Type | `unknown` |
| Device | CPU |
| Note | This is a summarization model, not an instruction-following LLM |

### 3. RE-RANKER
| Property | Value |
| :--- | :--- |
| Model Name | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| Confidence Threshold | 0.0 |
| Retrieval k (candidates) | 75 (top-3 after re-ranking) |
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

**13 PDFs indexed:**
  - `1759248623779-navratri.pdf`
  - `1765007523589-delhi_.pdf`
  - `1773373095022-Docker.pdf`
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
    ├─ ChromaDB.similarity_search(k=75) → top-75 chunks
    ├─ cross-encoder/ms-marco-MiniLM-L-6-v2 → re-rank → top-3
    │       └─ if score < 0.0 → "not confident"
    ├─ llama3.2:3b → generate answer
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

*Archived 2026-03-13 09:28:22 — MBS v1.0*
