"""
MKRS Benchmark System (MBS) - eval_v1.py
=========================================
ONE-COMMAND full benchmark: testing + scoring + logging + report generation.

Usage (from project root):
    .\ai-service\venv\Scripts\python.exe ai-service\eval_v1.py
    .\ai-service\venv\Scripts\python.exe ai-service\eval_v1.py --name "After Phi-3 Upgrade"

What happens automatically:
  1. Loads the Brain (all models + ChromaDB)
  2. Scans the system to capture exact model names, configs, and versions
  3. Runs 20 standardized questions (65% KB + 35% stress_test.pdf)
  4. Calculates TMS score (RHR, SEC, NEG, LAT, VRAM)
  5. Creates a new TEST_XX folder under MBS/
  6. Saves raw_scores.json + a full REPORT.md with every detail
  7. Updates MBS/INDEX.md with the new test entry
"""

import os
import sys
import time
import json
import argparse
import shutil
import re
import torch

# ── Path Setup ────────────────────────────────────────────────────────────────
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR    = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
MBS_DIR     = os.path.join(ROOT_DIR, "MBS")
MBS_LOG_DIR = os.path.join(MBS_DIR, "LOGS")
os.makedirs(MBS_LOG_DIR, exist_ok=True)

sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, os.path.join(SCRIPT_DIR, "actions"))

try:
    from actions import ActionQueryDoc
except Exception as e:
    print(f"[FATAL] Could not import ActionQueryDoc: {e}")
    sys.exit(1)


# ══════════════════════════════════════════════════════════════════════════════
# MOCK RASA OBJECTS
# ══════════════════════════════════════════════════════════════════════════════
class MockDispatcher:
    def __init__(self):
        self.messages = []
    def utter_message(self, **kwargs):
        self.messages.append(kwargs)
    def get_response(self):
        if not self.messages:
            return {"text": "", "sources": []}
        msg = self.messages[0]
        return msg.get("json_message", {"text": msg.get("text", ""), "sources": []})

class MockTracker:
    def __init__(self, text):
        self.latest_message = {"text": text}


# ══════════════════════════════════════════════════════════════════════════════
# TEST SUITE — 20 QUESTIONS (13 main + 7 stress)
# ══════════════════════════════════════════════════════════════════════════════
TEST_CASES = [
    # ── MAIN KNOWLEDGE BASE (13 questions, 65%) ──────────────────────────────
    {"id": "Q01", "query": "What is a black hole?",
     "source_pdf": "hole", "keywords": [["gravity", "gravitational"], ["escape", "pull"], ["region", "area", "space"]],
     "trap_word": None, "is_stress": False},
    {"id": "Q02", "query": "Who coined the term black hole and when?",
     "source_pdf": "hole", "keywords": [["wheeler", "john wheeler"], "1967"],
     "trap_word": None, "is_stress": False},
    {"id": "Q03", "query": "What is the Event Horizon of a black hole?",
     "source_pdf": "hole", "keywords": [["point", "boundary"], ["return", "no return"], ["escape", "light"]],
     "trap_word": None, "is_stress": False},
    {"id": "Q04", "query": "What is Hawking Radiation?",
     "source_pdf": "hole", "keywords": ["hawking", ["radiation", "radiates", "emission"]],
     "trap_word": None, "is_stress": False},
    {"id": "Q05", "query": "What is Sagittarius A star?",
     "source_pdf": "hole", "keywords": ["milky", "supermassive"],
     "trap_word": None, "is_stress": False},
    {"id": "Q06", "query": "What is the historical significance of Delhi?",
     "source_pdf": "delhi", "keywords": [["capital", "official seat"], ["mughal", "emperor"], ["sultanate", "dynasty"]],
     "trap_word": None, "is_stress": False},
    {"id": "Q07", "query": "Who built the Red Fort and what city did they found?",
     "source_pdf": "delhi", "keywords": [["shah", "emperor shah"], ["jahan", "shah jahan"], ["shahjahanabad", "shajahanabad", "delhi"]],
     "trap_word": None, "is_stress": False},
    {"id": "Q08", "query": "When did the British shift India's capital to Delhi?",
     "source_pdf": "delhi", "keywords": ["1911", ["calcutta", "kolkata"]],
     "trap_word": None, "is_stress": False},
    {"id": "Q09", "query": "What is Navratri festival?",
     "source_pdf": "navratri", "keywords": [["nine", "9 nights"], ["durga", "goddess"], ["shakti", "feminine"]],
     "trap_word": None, "is_stress": False},
    {"id": "Q10", "query": "Who is Mahishasura in the Navratri legend?",
     "source_pdf": "navratri", "keywords": [["demon", "demon bull"], ["mahishasura", "mahisasura"], ["durga", "shakti"]],
     "trap_word": None, "is_stress": False},
    {"id": "Q11", "query": "What is RAG's role in the SIH 2025 chatbot?",
     "source_pdf": "SIH_2025", "keywords": [["retrieval", "fetch"], ["augmented", "generation"], ["pdf", "documents", "files"]],
     "trap_word": None, "is_stress": False},
    {"id": "Q12", "query": "What caused dinosaur extinction 66 million years ago?",
     "source_pdf": "dinasours", "keywords": [["asteroid", "meteor"], ["extinct", "died out"], ["impact", "collision"]],
     "trap_word": None, "is_stress": False},
    {"id": "Q13", "query": "What is Robert Sternberg's Triangular Theory of Love?",
     "source_pdf": "love", "keywords": [["triangular", "triad"], ["intimacy", "bond"], ["passion", "romance"]],
     "trap_word": None, "is_stress": False},

    # ── STRESS TEST (7 questions, 35%) — stress_test.pdf ─────────────────────
    {"id": "Q14", "query": "What is the Mars Mission about?",
     "source_pdf": "stress_test", "keywords": ["mars", "humanity", "rocket"],
     "trap_word": "apple pie", "is_stress": True},
    {"id": "Q15", "query": "What type of fuel does the Mars rocket use?",
     "source_pdf": "stress_test", "keywords": ["liquid", "hydrogen", "fuel"],
     "trap_word": "flour", "is_stress": True},
    {"id": "Q16", "query": "What is the landing zone for the Mars mission?",
     "source_pdf": "stress_test", "keywords": ["jezero", "crater"],
     "trap_word": "preheat", "is_stress": True},
    {"id": "Q17", "query": "How long do you bake Apple Pie?",
     "source_pdf": "stress_test", "keywords": ["45", "golden"],
     "trap_word": "mars", "is_stress": True},
    {"id": "Q18", "query": "What temperature to preheat oven for Apple Pie?",
     "source_pdf": "stress_test", "keywords": ["375", "degrees"],
     "trap_word": "astronaut", "is_stress": True},
    {"id": "Q19", "query": "Which department had the highest profit in Q3 2025?",
     "source_pdf": "stress_test", "keywords": ["security", "400"],
     "trap_word": None, "is_stress": True},
    {"id": "Q20", "query": "Which department has the lowest margin in the Q3 2025 report?",
     "source_pdf": "stress_test", "keywords": ["logistics", "margin"],
     "trap_word": "security", "is_stress": True},
]


# ══════════════════════════════════════════════════════════════════════════════
# SYSTEM SCANNER — auto-detects all component configs
# ══════════════════════════════════════════════════════════════════════════════
def scan_system_snapshot():
    """Reads the actual source files to capture the exact state of every component."""
    snapshot = {}

    # 1. Embedding Model
    if os.path.exists(os.path.join(SCRIPT_DIR, "indic_embeddings.py")):
        snapshot["embedding_model"] = "ai4bharat/IndicBERT-v3-1B"
        snapshot["embedding_library"] = "Custom Wrapper (Transformers + Mean Pooling)"
        snapshot["embedding_dims"] = 1024
    else:
        snapshot["embedding_model"] = "paraphrase-xlm-r-multilingual-v1"
        snapshot["embedding_library"] = "sentence-transformers via langchain HuggingFaceEmbeddings"
        snapshot["embedding_dims"] = 768

    # 2. Generation Model — parse from actions.py
    actions_path = os.path.join(SCRIPT_DIR, "actions", "actions.py")
    gen_model = "unknown"
    gen_pipeline = "unknown"
    reranker_model = "unknown"
    confidence_threshold = 0.1
    retrieval_k = 10
    translation_models = {}

    if os.path.exists(actions_path):
        with open(actions_path, "r", encoding="utf-8") as f:
            actions_src = f.read()

        # Generation model
        m = re.search(r'OLLAMA_MODEL\s*=\s*os\.getenv\(.*?,\s*"([^"]+)"', actions_src)
        if m: gen_model = m.group(1)
        
        m = re.search(r'pipeline\("summarization",\s*model="([^"]+)"', actions_src)
        if m: gen_model = m.group(1)
        m = re.search(r'pipeline\("([^"]+)"', actions_src)
        if m: gen_pipeline = m.group(1)

        # Re-ranker
        m = re.search(r"CrossEncoder\('([^']+)'", actions_src)
        if m: reranker_model = m.group(1)

        # Confidence threshold
        m = re.search(r'CONFIDENCE_THRESHOLD\s*=\s*([\d.]+)', actions_src)
        if m: confidence_threshold = float(m.group(1))

        # Retrieval k
        m = re.search(r'similarity_search\(.*?k=(\d+)', actions_src)
        if m: retrieval_k = int(m.group(1))

        # Translation models
        tm = re.findall(r"'(\w+)':\s*'([^']+)'", actions_src)
        for lang, model in tm:
            if 'Helsinki' in model or 'opus' in model:
                translation_models[lang] = model

    snapshot["generation_model"] = gen_model
    snapshot["generation_pipeline"] = gen_pipeline
    snapshot["reranker_model"] = reranker_model
    snapshot["confidence_threshold"] = confidence_threshold
    snapshot["retrieval_k"] = retrieval_k
    snapshot["translation_models"] = translation_models

    # 3. Chunker config — parse from smart_chunker.py
    chunker_path = os.path.join(SCRIPT_DIR, "smart_chunker.py")
    chunk_size = 500
    chunk_overlap = 50
    if os.path.exists(chunker_path):
        with open(chunker_path, "r", encoding="utf-8") as f:
            csrc = f.read()
        m = re.search(r'chunk_size=(\d+)', csrc)
        if m: chunk_size = int(m.group(1))
        m = re.search(r'chunk_overlap=(\d+)', csrc)
        if m: chunk_overlap = int(m.group(1))

    snapshot["chunk_size"] = chunk_size
    snapshot["chunk_overlap"] = chunk_overlap

    # 4. Ingestion method — parse from smart_ingest.py
    ingest_path = os.path.join(SCRIPT_DIR, "smart_ingest.py")
    ingest_method = "SmartIngest V4 (Hybrid)"
    if os.path.exists(ingest_path):
        with open(ingest_path, "r", encoding="utf-8") as f:
            isrc = f.read()
        m = re.search(r'ingestion_method.*?["\']([^"\']+)["\']', isrc)
        if m: ingest_method = m.group(1)
        # Also check for class name
        m2 = re.search(r'class\s+(\w+)', isrc)
        if m2: ingest_method = f"{m2.group(1)} ({ingest_method})"

    snapshot["ingestion_method"] = ingest_method

    # 5. Rasa config — parse from config.yml
    rasa_cfg_path = os.path.join(SCRIPT_DIR, "config.yml")
    nlu_model = "unknown"
    if os.path.exists(rasa_cfg_path):
        with open(rasa_cfg_path, "r", encoding="utf-8") as f:
            cfg = f.read()
        m = re.search(r'model_weights:\s*"([^"]+)"', cfg)
        if m: nlu_model = m.group(1)

    snapshot["nlu_model"] = nlu_model

    # 6. Vector store
    chroma_path = os.path.join(SCRIPT_DIR, "documents", "chroma_db")
    snapshot["vector_store"] = "ChromaDB"
    snapshot["vector_store_path"] = chroma_path
    snapshot["vector_store_exists"] = os.path.exists(chroma_path)

    # 7. PDF count
    pdfs_path = os.path.join(SCRIPT_DIR, "documents", "pdfs")
    if os.path.exists(pdfs_path):
        pdf_files = [f for f in os.listdir(pdfs_path) if f.lower().endswith('.pdf')]
        snapshot["pdf_count"] = len(pdf_files)
        snapshot["pdf_files"] = pdf_files
    else:
        snapshot["pdf_count"] = 0
        snapshot["pdf_files"] = []

    # 8. Device
    snapshot["device"] = "CUDA (GPU)" if torch.cuda.is_available() else "CPU"
    if torch.cuda.is_available():
        snapshot["gpu_name"] = torch.cuda.get_device_name(0)
    else:
        snapshot["gpu_name"] = "N/A (CPU fallback)"

    return snapshot


# ══════════════════════════════════════════════════════════════════════════════
# DETERMINE NEXT TEST NUMBER
# ══════════════════════════════════════════════════════════════════════════════
def get_next_test_number():
    """Scans MBS/ for TEST_XX folders and returns next number."""
    existing = []
    if os.path.exists(MBS_DIR):
        for name in os.listdir(MBS_DIR):
            m = re.match(r"TEST_(\d+)", name)
            if m:
                existing.append(int(m.group(1)))
    return max(existing, default=0) + 1


# ══════════════════════════════════════════════════════════════════════════════
# REPORT GENERATOR
# ══════════════════════════════════════════════════════════════════════════════
def generate_report(test_num, test_name, summary, snapshot, results):
    """Generates the full REPORT.md content."""

    ts = summary["timestamp"]
    tms = summary["tms_score"]
    bd = summary["breakdown"]

    # Grade
    grade_label = "UNKNOWN"
    for threshold, label in [(89, "EXCELLENT"), (76, "GOOD"), (61, "MODERATE"), (41, "WEAK"), (0, "CRITICAL")]:
        if tms >= threshold:
            grade_label = label
            break

    grade_icons = {
        "EXCELLENT": "🏆 EXCELLENT — State-of-the-art",
        "GOOD": "🟢 GOOD — Solid, minor improvements possible",
        "MODERATE": "🟠 MODERATE — Working but unreliable",
        "WEAK": "🟡 WEAK — Failing most questions",
        "CRITICAL": "🔴 CRITICAL — Barely functional"
    }

    # Per-question table rows
    q_rows = ""
    failures = []
    for r in results:
        rhr_icon = "✅" if r["rhr"] else "❌"
        neg_icon = ""
        if r["is_stress"] and r.get("neg", 1) == 0:
            neg_icon = " ❌HALL"
        elif r["is_stress"]:
            neg_icon = " ✅"

        if r["sec"] >= 0.99:
            verdict = "✅ Pass"
        elif r["rhr"] == 0:
            verdict = "❌ Not retrieved"
            failures.append(f"**{r['id']}** (`{r['query'][:40]}`): Retrieval below confidence — re-ranker rejected or chunk missing")
        elif r.get("neg", 1) == 0:
            verdict = "❌ HALLUCINATED"
            failures.append(f"**{r['id']}** (`{r['query'][:40]}`): Generation model blended wrong context into answer")
        elif r["sec"] > 0:
            verdict = "⚠️ Partial"
        else:
            verdict = "❌ Failed SEC"
            failures.append(f"**{r['id']}** (`{r['query'][:40]}`): Generation model failed to extract relevant facts")

        tag = "[STRESS]" if r["is_stress"] else "[MAIN]"
        q_rows += f"| {r['id']} | {tag} {r['query'][:50]} | {rhr_icon} | {r['sec']:.2f} | {neg_icon} | {r['latency']:.1f}s | {verdict} |\n"

    # Failure analysis
    failure_section = ""
    if failures:
        failure_section = "## ⚠️ ROOT CAUSE ANALYSIS\n\n"
        for f in failures:
            failure_section += f"- {f}\n"
        failure_section += "\n"

    # Translation models list
    trans_list = ""
    if snapshot.get("translation_models"):
        for lang, model in snapshot["translation_models"].items():
            trans_list += f"  - `{lang}` → `{model}`\n"
    else:
        trans_list = "  - None detected\n"

    # PDF list
    pdf_list = ""
    for pdf in snapshot.get("pdf_files", []):
        pdf_list += f"  - `{pdf}`\n"

    report = f"""# TEST {test_num:02d} — {test_name}
## MKRS Brain Snapshot

> **Date**: {ts}
> **MBS Version**: 1.0
> **TMS Score**: **{tms} / 100**
> **Grade**: {grade_icons.get(grade_label, grade_label)}

---

## 📊 SCORE BREAKDOWN

| Metric | Raw Value | Score | Weight | Points |
| :--- | :--- | :--- | :--- | :--- |
| RHR – Retrieval Hit Rate | {bd['avg_rhr']*100:.1f}% | {bd['avg_rhr']:.4f} | ×40 | **{bd['avg_rhr']*40:.2f}** |
| SEC – Fact Accuracy | {bd['avg_sec']*100:.1f}% | {bd['avg_sec']:.4f} | ×30 | **{bd['avg_sec']*30:.2f}** |
| NEG – No Hallucination | {bd['avg_neg']*100:.1f}% | {bd['avg_neg']:.4f} | ×10 | **{bd['avg_neg']*10:.2f}** |
| LAT – Speed | avg {bd['avg_latency_s']:.2f}s | {bd['lat_score']:.4f} | ×10 | **{bd['lat_score']*10:.2f}** |
| VRAM – GPU Memory | {bd['vram_mb']:.0f} MB | {bd['vram_score']:.4f} | ×10 | **{bd['vram_score']*10:.2f}** |
| **TOTAL TMS** | | | | **{tms}** |

---

## 🗂️ QUESTION-BY-QUESTION RESULTS

| ID | Domain & Query | RHR | SEC | NEG | Latency | Verdict |
| :-- | :--- | :---: | :---: | :---: | ---: | :--- |
{q_rows}
---

{failure_section}---

## 🛠️ FULL SYSTEM SNAPSHOT

> Every component, model, config, and parameter as they existed during this test.

---

### 1. EMBEDDING MODEL
| Property | Value |
| :--- | :--- |
| Model Name | `{snapshot['embedding_model']}` |
| Library | {snapshot['embedding_library']} |
| Dimensions | {snapshot['embedding_dims']} |
| Device | {snapshot['device']} |

### 2. GENERATION MODEL (LLM)
| Property | Value |
| :--- | :--- |
| Model Name | `{snapshot['generation_model']}` |
| Pipeline Type | `{snapshot['generation_pipeline']}` |
| Device | {snapshot['device']} |
| Note | This is a summarization model, not an instruction-following LLM |

### 3. RE-RANKER
| Property | Value |
| :--- | :--- |
| Model Name | `{snapshot['reranker_model']}` |
| Confidence Threshold | {snapshot['confidence_threshold']} |
| Retrieval k (candidates) | {snapshot['retrieval_k']} (top-3 after re-ranking) |
| Device | {snapshot['device']} |

### 4. TRANSLATION LAYER
{trans_list}

### 5. INGESTION ENGINE
| Property | Value |
| :--- | :--- |
| Method | `{snapshot['ingestion_method']}` |
| Library | pdfplumber |
| Features | Layout-aware reading, Y/X histogram column detection, table masking, header/footer artifact removal |

### 6. CHUNKING ENGINE
| Property | Value |
| :--- | :--- |
| Chunk Size | {snapshot['chunk_size']} characters |
| Chunk Overlap | {snapshot['chunk_overlap']} characters |
| Table Handling | Regex-based atomic preservation (unsplit) |
| Splitter | RecursiveCharacterTextSplitter |

### 7. VECTOR STORE
| Property | Value |
| :--- | :--- |
| Type | {snapshot['vector_store']} |
| Path | `{snapshot['vector_store_path']}` |
| Exists | {snapshot['vector_store_exists']} |

### 8. RASA NLU
| Property | Value |
| :--- | :--- |
| NLU Feature Model | `{snapshot['nlu_model']}` |
| Pipeline | WhitespaceTokenizer → CountVectors → LanguageModelFeaturizer → DIETClassifier |

### 9. COMPUTE DEVICE
| Property | Value |
| :--- | :--- |
| Device | {snapshot['device']} |
| GPU | {snapshot['gpu_name']} |

---

## 📄 KNOWLEDGE BASE

**{snapshot['pdf_count']} PDFs indexed:**
{pdf_list}
---

## 🔗 DATA FLOW (End-to-End)

```
[User Query]
    ↓
[Rasa NLU :5005] → intent detection ({snapshot['nlu_model']})
    ↓
[Rasa Actions :5055] → ActionQueryDoc.run()
    ├─ langdetect → detect language
    ├─ {snapshot['embedding_model']} → embed query (dim={snapshot['embedding_dims']})
    ├─ ChromaDB.similarity_search(k={snapshot['retrieval_k']}) → top-{snapshot['retrieval_k']} chunks
    ├─ {snapshot['reranker_model']} → re-rank → top-3
    │       └─ if score < {snapshot['confidence_threshold']} → "not confident"
    ├─ {snapshot['generation_model']} → generate answer
    └─ Translation (if needed)
    ↓
[JSON {{text, sources[]}}] → Backend :5001 → Frontend :3000
```

---

## 📁 FILES IN THIS TEST FOLDER

| File | Description |
| :--- | :--- |
| `REPORT.md` | This document — full system snapshot and results |
| `raw_scores.json` | Machine-readable per-question data |

---

*Archived {ts} — MBS v1.0*
"""
    return report


# ══════════════════════════════════════════════════════════════════════════════
# INDEX UPDATER
# ══════════════════════════════════════════════════════════════════════════════
def update_index(test_num, test_name, tms, date_str):
    """Creates or updates MBS/INDEX.md with the new test entry."""

    index_path = os.path.join(MBS_DIR, "INDEX.md")

    # Build entry line
    folder = f"TEST_{test_num:02d}_{test_name.upper().replace(' ', '_')}"
    entry = f"| [{folder}](./{folder}/REPORT.md) | **{tms}** | {date_str} | {test_name} |"

    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Append before the last line that starts with ---
        # Find the table end marker
        if entry not in content:
            content = content.rstrip() + "\n" + entry + "\n"
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(content)
    else:
        content = f"""# MBS — MKRS Benchmark System Index

This folder contains all official benchmark runs for the MKRS AI Brain.

## How to Run a New Test

```powershell
# From the project root (optionally pass a test name):
.\\ai-service\\venv\\Scripts\\python.exe ai-service\\eval_v1.py
.\\ai-service\\venv\\Scripts\\python.exe ai-service\\eval_v1.py --name "After Phi-3 Upgrade"
```

---

## Test History

| Test | TMS Score | Date | What Changed |
| :--- | :---: | :--- | :--- |
{entry}

---

## Scoring Reference

| TMS Range | Grade |
| :--- | :--- |
| 89 - 100 | EXCELLENT |
| 76 - 88 | GOOD |
| 61 - 75 | MODERATE |
| 41 - 60 | WEAK |
| 0 - 40 | CRITICAL |

See [PROCEDURE.md](./PROCEDURE.md) for full scoring rules.
"""
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(content)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN BENCHMARK RUNNER
# ══════════════════════════════════════════════════════════════════════════════
def run_benchmark(test_name="BASELINE"):
    print("=" * 60)
    print("  MKRS Benchmark System (MBS) v1.0")
    print(f"  Test Name: {test_name}")
    print(f"  Run at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # ── 0. Scan system snapshot ───────────────────────────────────────────────
    print("\n[SCAN] Scanning system components...")
    snapshot = scan_system_snapshot()
    print(f"  Device: {snapshot['device']}")
    print(f"  Embedding: {snapshot['embedding_model']}")
    print(f"  Generation: {snapshot['generation_model']}")
    print(f"  Re-ranker: {snapshot['reranker_model']}")
    print(f"  PDFs: {snapshot['pdf_count']}")

    # Reset VRAM tracker
    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()

    # ── 1. Load the Brain ─────────────────────────────────────────────────────
    print("\n[INIT] Loading Brain (all models + ChromaDB)...")
    t_init = time.time()
    brain = ActionQueryDoc()
    init_time = time.time() - t_init
    print(f"[INIT] Brain loaded in {init_time:.2f}s\n")

    # ── 2. Run all 20 questions ───────────────────────────────────────────────
    results = []
    total_latency = 0.0

    for tc in TEST_CASES:
        qid = tc["id"]
        query = tc["query"]
        tag = "[STRESS]" if tc["is_stress"] else "[MAIN]  "

        dispatcher = MockDispatcher()
        tracker    = MockTracker(query)

        t0 = time.time()
        brain.run(dispatcher, tracker, {})
        latency = time.time() - t0
        total_latency += latency

        response = dispatcher.get_response()
        answer   = response.get("text", "").lower()
        sources  = response.get("sources", [])

        # RHR
        rhr = 1 if any(tc["source_pdf"].lower() in s.get("title", "").lower() for s in sources) else 0
        # SEC (Improved: Synonym-Aware Keyword Matching)
        kws_found = []
        for kw in tc["keywords"]:
            if isinstance(kw, str):
                if kw.lower() in answer:
                    kws_found.append(kw)
            elif isinstance(kw, list):
                # If any synonym in the list matches, consider it found
                if any(syn.lower() in answer for syn in kw):
                    kws_found.append(kw[0]) # Use first as head keyword
        sec = len(kws_found) / len(tc["keywords"]) if tc["keywords"] else 1.0
        # NEG
        neg = 1
        if tc["trap_word"] and tc["trap_word"].lower() in answer:
            neg = 0

        results.append({
            "id": qid, "query": query, "is_stress": tc["is_stress"],
            "rhr": rhr, "sec": round(sec, 3), "neg": neg,
            "latency": round(latency, 3),
            "answer_preview": answer[:150].replace("\n", " "),
            "keywords_found": kws_found,
            "keywords_expected": tc["keywords"],
            "sources_found": [s.get("title", "?") for s in sources[:3]],
        })

        status = "[RHR_OK]" if rhr else "[RHR_FAIL]"
        trap_info = f" | TRAP:{'HALLUCINATION' if neg == 0 else 'OK'}" if tc["is_stress"] else ""
        
        # Determine simple tag
        tag = "GOOD" if rhr == 1 and sec >= 0.7 else ("WARN" if rhr == 1 else "FAIL")
        
        try:
            print(f"  {tag} {qid} [{status} | SEC:{sec:.2f} | {latency:.2f}s{trap_info}]  '{query[:55]}'")
        except Exception:
            print(f"  {qid} SEC:{sec:.2f} | RHR:{rhr}")

    # ── 3. Calculate aggregate scores ─────────────────────────────────────────
    avg_rhr = sum(r["rhr"] for r in results) / len(results)
    avg_sec = sum(r["sec"] for r in results) / len(results)
    avg_neg = sum(r["neg"] for r in results) / len(results)
    avg_lat = total_latency / len(results)

    vram_mb = 0
    if torch.cuda.is_available():
        vram_mb = torch.cuda.max_memory_allocated() / (1024 * 1024)

    lat_score  = min(1.0, 2.0 / avg_lat) if avg_lat > 0 else 1.0
    vram_score = min(1.0, 4096.0 / vram_mb) if vram_mb > 0 else 1.0

    tms = round((avg_rhr * 40) + (avg_sec * 30) + (avg_neg * 10) + (lat_score * 10) + (vram_score * 10), 2)

    # ── Print summary ─────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"  MKRS BRAIN SCORE (TMS): {tms} / 100")
    print("=" * 60)
    print(f"  |-- RHR  (Retrieval Hit):     {avg_rhr*100:.1f}%  x40 = {avg_rhr*40:.1f}")
    print(f"  |-- SEC  (Fact Accuracy):     {avg_sec*100:.1f}%  x30 = {avg_sec*30:.1f}")
    print(f"  |-- NEG  (No Hallucination):  {avg_neg*100:.1f}%  x10 = {avg_neg*10:.1f}")
    print(f"  |-- LAT  (Speed, {avg_lat:.2f}s avg): {lat_score:.2f}  x10 = {lat_score*10:.1f}")
    print(f"  \\-- VRAM ({vram_mb:.0f} MB):           {vram_score:.2f}  x10 = {vram_score*10:.1f}")
    print("=" * 60)

    # Grade
    for threshold, label in [(89, "EXCELLENT (🏆)"), (76, "GOOD (🟢)"), (61, "MODERATE (🟠)"), (41, "WEAK (🟡)"), (0, "CRITICAL (🔴)")]:
        if tms >= threshold:
            # Strip emojis for terminal print but keep for report
            clean_label = label.split(' (')[0]
            print(f"  Grade: {clean_label}")
            break

    # ── 4. Build summary dict ─────────────────────────────────────────────────
    timestamp_str = time.strftime("%Y%m%d_%H%M%S")
    date_str = time.strftime("%Y-%m-%d")
    summary = {
        "mbs_version": "1.0",
        "test_name": test_name,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "tms_score": tms,
        "breakdown": {
            "avg_rhr": round(avg_rhr, 4), "avg_sec": round(avg_sec, 4),
            "avg_neg": round(avg_neg, 4), "avg_latency_s": round(avg_lat, 3),
            "vram_mb": round(vram_mb, 2), "lat_score": round(lat_score, 4),
            "vram_score": round(vram_score, 4),
        },
        "system_snapshot": snapshot,
        "per_question": results
    }

    # ── 5. Determine test number & create folder ──────────────────────────────
    test_num = get_next_test_number()
    safe_name = test_name.upper().replace(" ", "_").replace("/", "_")[:30]
    folder_name = f"TEST_{test_num:02d}_{safe_name}"
    test_dir = os.path.join(MBS_DIR, folder_name)
    os.makedirs(test_dir, exist_ok=True)

    # Save raw_scores.json
    raw_path = os.path.join(test_dir, "raw_scores.json")
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4, ensure_ascii=False)

    # Save REPORT.md
    report_path = os.path.join(test_dir, "REPORT.md")
    report_content = generate_report(test_num, test_name, summary, snapshot, results)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    # Also save to LOGS (timestamped + latest)
    log_path = os.path.join(MBS_LOG_DIR, f"benchmark_{timestamp_str}.json")
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4, ensure_ascii=False)
    latest_path = os.path.join(MBS_LOG_DIR, "latest_result.json")
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4, ensure_ascii=False)

    # Update INDEX.md
    update_index(test_num, test_name, tms, date_str)

    print(f"\n  📁 Test folder created: MBS/{folder_name}/")
    print(f"     ├── REPORT.md")
    print(f"     └── raw_scores.json")
    print(f"  📋 Index updated:      MBS/INDEX.md")
    print(f"  📊 Log saved:          MBS/LOGS/benchmark_{timestamp_str}.json")
    print()


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MKRS Benchmark System (MBS)")
    parser.add_argument("--name", type=str, default="BASELINE",
                        help="Name for this test run (e.g. 'After Phi-3 Upgrade')")
    args = parser.parse_args()
    run_benchmark(test_name=args.name)
