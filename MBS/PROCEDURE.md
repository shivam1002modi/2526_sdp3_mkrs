# MKRS Benchmark System (MBS) — Official Test Procedure v1.0
> **Purpose**: A permanent, versioned scorecard to objectively measure the "Brain" quality of MKRS
> after every upgrade, configuration change, or model swap.

---

## Part 1: What Is Being Tested?

The MBS tests the full **RAG Pipeline** as it runs in production:
- The **Embedding Model** (converts text to vectors for retrieval)
- The **Vector Database** (ChromaDB – stores and retrieves document chunks)
- The **Re-Ranker** (Cross-Encoder that scores result relevance)
- The **Generation Model** (the LLM that generates the final answer)

It does **NOT** test the network, the Rasa NLU, or the UI frontend.

---

## Part 2: Test Environment

The benchmark uses a **simulated environment** for clean, repeatable results.

| Component | Real System | MBS Simulation |
| :--- | :--- | :--- |
| Rasa Dispatcher | Sends JSON to frontend | `MockDispatcher` – captures response in memory |
| Rasa Tracker | Holds conversation state | `MockTracker` – injects query string directly |
| ChromaDB | Loaded once at startup | Same – loaded from `ai-service/documents/chroma_db` |
| Models | GPU/CPU | Same – uses whatever device is available |

---

## Part 3: The Test Suite (20 Questions)

Split: **65% Main KB** (13 questions) + **35% Stress Test** (7 questions from `stress_test.pdf`)

The stress_test.pdf contains:
- **Two side-by-side columns** (Space vs. Cooking) – tests column confusion
- **A financial data table** – tests structured data retrieval

### 3.1 Main Knowledge Base Questions (13)

| # | Query | Source PDF | Must-Find Keywords |
| :-- | :--- | :--- | :--- |
| Q01 | What is a black hole? | Black Holes Guide | gravity, escape, region |
| Q02 | Who coined the term black hole? | Black Holes Guide | wheeler, 1967 |
| Q03 | What is the Event Horizon? | Black Holes Guide | point, return, escape |
| Q04 | What is Hawking Radiation? | Black Holes Guide | hawking, radiation |
| Q05 | What is Sagittarius A*? | Black Holes Guide | milky, supermassive |
| Q06 | Historical significance of Delhi? | Delhi PDF | capital, mughal, sultanate |
| Q07 | Who built the Red Fort? | Delhi PDF | shah, jahan, shahjahanabad |
| Q08 | When did British shift capital to Delhi? | Delhi PDF | 1911, calcutta |
| Q09 | What is Navratri? | Navratri PDF | nine, durga, shakti |
| Q10 | Who is Mahishasura? | Navratri PDF | demon, mahishasura, durga |
| Q11 | What is RAG in SIH 2025? | SIH Blueprint | retrieval, augmented, pdf |
| Q12 | Dinosaur extinction cause? | Dinosaurs PDF | asteroid, extinct, impact |
| Q13 | Sternberg's theory of love? | Love PDF | triangular, intimacy, passion |

### 3.2 Stress Test Questions (7)

| # | Query | Must-Find Keywords | Adversarial Trap |
| :-- | :--- | :--- | :--- |
| Q14 | Mars Mission about? | mars, humanity, rocket | Must NOT say "apple pie" |
| Q15 | Mars rocket fuel? | liquid, hydrogen, fuel | Must NOT say "flour" |
| Q16 | Mars landing zone? | jezero, crater | Must NOT say "preheat" |
| Q17 | How long bake Apple Pie? | 45, golden | Must NOT say "mars" |
| Q18 | Apple Pie oven temp? | 375, degrees | Must NOT say "astronaut" |
| Q19 | Highest profit dept Q3 2025? | security, 400 | — |
| Q20 | Lowest margin dept? | logistics, margin | Must NOT say "security" |

---

## Part 4: Scoring Metrics

| Metric | Weight | Calculation |
| :--- | :--- | :--- |
| **RHR** – Retrieval Hit Rate | 40% | Did the correct source PDF appear in top-3 results? |
| **SEC** – Fact Accuracy | 30% | % of Must-Find Keywords in the answer |
| **NEG** – No Hallucination | 10% | Stress tests: 0 if trap word appears, 1 otherwise |
| **LAT** – Speed | 10% | `min(1, 2.0 / avg_latency_seconds)` |
| **VRAM** – GPU Efficiency | 10% | `min(1, 4096 / vram_mb)` |

### Formula
```
TMS = (avg_RHR × 40) + (avg_SEC × 30) + (avg_NEG × 10) + (lat_score × 10) + (vram_score × 10)
Max: 100
```

---

## Part 5: How to Run

```powershell
# Basic run (default name "BASELINE"):
.\ai-service\venv\Scripts\python.exe ai-service\eval_v1.py

# Named run (for upgrades):
.\ai-service\venv\Scripts\python.exe ai-service\eval_v1.py --name "After Phi-3 Upgrade"
```

### What happens automatically:
1. Scans all system components (models, configs, PDFs)
2. Loads the Brain and runs all 20 questions
3. Calculates TMS score
4. Creates `MBS/TEST_XX_<NAME>/` folder with:
   - `REPORT.md` — full human-readable report with system snapshot
   - `raw_scores.json` — machine-readable per-question data
5. Saves timestamped log to `MBS/LOGS/`
6. Updates `MBS/INDEX.md` with new test entry

---

## Part 6: Interpreting the Score

| TMS Range | Grade | Action |
| :--- | :--- | :--- |
| 0 – 40 | 🔴 CRITICAL | Rebuild vector store, check model |
| 41 – 60 | 🟡 WEAK | Upgrade Generation model |
| 61 – 75 | 🟠 MODERATE | Upgrade Embeddings + Re-ranker |
| 76 – 88 | 🟢 GOOD | Fine-tune or swap to BGE embeddings |
| 89 – 100 | 🏆 EXCELLENT | Maintain and monitor |

---

*MBS v1.0 — Established 2026-02-21*
