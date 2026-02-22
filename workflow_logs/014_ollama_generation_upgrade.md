# Workflow Log 014: Generation Layer Upgrade — Ollama Integration
**Date**: 2026-02-21
**Status**: 🟡 IN PROGRESS (Ollama Installed + Model Pulled, System Integration Pending)
**Agent**: The LLM Agent -1

## 0. Installation Log (2026-02-22 00:06 IST)

### Ollama Installed
*   **Installer**: `C:\Users\ASUS\Downloads\OllamaSetup.exe`
*   **Version**: `0.16.3`
*   **Status**: ✅ Installed and running as background service

### Model Pulled
*   **Tag**: `mashriram/sarvam-1:latest`
*   **Size**: 1.5 GB (GGUF quantized)
*   **ID**: `6443034ccda0`
*   **Pull Status**: ✅ Success (retry needed once due to connection abort)

### Live Test
*   **Prompt**: `"What is the capital of India? Answer in one sentence."`
*   **Response**: `भारत की राजधानी नई दिल्ली है।` ✅
*   **Observation**: Model responds in Hindi natively without translation layer.

### Config Updated
*   `actions.py` → `OLLAMA_MODEL` default changed from `"sarvam1"` to `"mashriram/sarvam-1"`

---

## 1. Problem Statement

The current generation model (`sshleifer/distilbart-cnn-12-6`) is a **summarization** model, NOT an instruction-following LLM. This causes:
*   Answers that are extracted/condensed snippets, not natural conversational responses.
*   No ability to reason, infer, or synthesize across multiple context chunks.
*   No native Indian language generation — answers are English-only, then translated.
*   The model loads directly into 4GB GPU VRAM via `transformers.pipeline`, competing with the Embedding model and Re-ranker for memory.

## 2. Solution: Ollama as Generation Service

Instead of loading the generation model inside `actions.py` (monolithic), we offload it to **Ollama** — a high-performance C++ inference engine that runs as a local HTTP service.

### Why Ollama?
| Feature | Old (distilbart in-process) | New (Ollama service) |
| :--- | :--- | :--- |
| Model Type | Summarization | Instruction-following LLM |
| Memory Mgmt | Crashes on OOM | Auto GPU/RAM split |
| Model Format | PyTorch (FP32/FP16) | GGUF (4-bit quantized) |
| Swap Models | Requires code change + restart | Change one config variable |
| Indian Lang | ❌ English only | ✅ Native Hindi, Tamil, Telugu, etc. |
| Startup Time | Slow (loads into Python) | Fast (pre-loaded C++ engine) |

---

## 3. Architecture

### 3.1 BEFORE (Current — Monolithic)

```
┌─────────────────────────────────────────────────────────────┐
│                     actions.py (Python)                      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │  Embedding    │  │  Re-Ranker   │  │  distilbart       │  │
│  │  paraphrase-  │  │  cross-enc.  │  │  (summarization)  │  │
│  │  xlm-r        │  │  ms-marco    │  │  GENERATION ❌    │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬──────────┘  │
│         │                 │                    │             │
│         ▼                 ▼                    ▼             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              ALL IN 4GB GPU VRAM 💥                   │   │
│  │         (Unstable, OOM risk, no room to grow)         │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 AFTER (Upgraded — Distributed)

```
┌──────────────────────────────────────┐    ┌──────────────────────────────┐
│         actions.py (Python)          │    │     Ollama Service (C++)     │
│                                      │    │     http://localhost:11434   │
│  ┌──────────────┐ ┌──────────────┐   │    │                              │
│  │  Embedding   │ │  Re-Ranker   │   │    │  ┌────────────────────────┐  │
│  │  paraphrase- │ │  cross-enc.  │   │    │  │  LLM Model (GGUF)     │  │
│  │  xlm-r       │ │  ms-marco    │   │    │  │  e.g. sarvam1 / gemma │  │
│  └──────┬───────┘ └──────┬───────┘   │    │  │  GENERATION ✅         │  │
│         │                │           │    │  └────────────────────────┘  │
│         ▼                ▼           │    │                              │
│  ┌────────────────────────────┐      │    │  ┌────────────────────────┐  │
│  │   GPU VRAM (~2.5GB used)  │      │    │  │   Smart Memory Mgmt   │  │
│  │   (Stable, room to grow)  │      │    │  │   GPU + System RAM    │  │
│  └────────────────────────────┘      │    │  │   (Auto-managed)      │  │
│                                      │    │  └────────────────────────┘  │
│  Step 3: GENERATE ──── HTTP POST ────┼───▶│                              │
│          (question + context)        │    │  Returns: natural answer     │
└──────────────────────────────────────┘    └──────────────────────────────┘
```

### 3.3 Data Flow (Per User Query)

```
User Query: "What is the history of Delhi?"
        │
        ▼
  ┌─── 1. RETRIEVE ───┐
  │ ChromaDB returns   │
  │ top-10 documents   │   (Embedding model — stays in actions.py)
  └────────┬───────────┘
           ▼
  ┌─── 2. RE-RANK ────┐
  │ Cross-Encoder      │
  │ scores & sorts     │   (Re-ranker — stays in actions.py)
  │ top-3 most relevant│
  └────────┬───────────┘
           ▼
  ┌─── 3. GENERATE ───┐
  │ POST to Ollama:    │
  │ {                  │
  │   model: "sarvam1",│   (NEW — delegated to Ollama service)
  │   prompt: "..."    │
  │ }                  │
  └────────┬───────────┘
           ▼
  ┌─── 4. TRANSLATE ──┐
  │ If lang != 'en',   │
  │ translate answer   │   (Translation — stays in actions.py)
  └────────┬───────────┘
           ▼
  ┌─── 5. RESPOND ────┐
  │ Send JSON payload  │
  │ to frontend        │   (Rasa dispatcher — stays in actions.py)
  └────────────────────┘
```

---

## 4. Before vs After — Full Query Flow

### 🔴 BEFORE — What happened when a user asked a question

```
User asks: "What is the history of Delhi?"
        │
        ▼
┌─── Step 1: SYSTEM STARTUP ──────────────────────────────────────────┐
│  actions.py loads ALL models into your 4GB GPU at once:             │
│                                                                      │
│  ① paraphrase-xlm-r (Embedding)        → ~1.0 GB GPU               │
│  ② cross-encoder/ms-marco (Re-ranker)   → ~0.3 GB GPU              │
│  ③ distilbart-cnn-12-6 (Summarizer)     → ~1.2 GB GPU  ← THIS ONE  │
│  ④ Helsinki-NLP translator (on demand)  → ~0.5 GB GPU              │
│                                                                      │
│  Total: ~3.0 GB locked in GPU at startup (out of 4GB)               │
│  ⚠️ Very tight. OOM risk if any model spikes.                       │
└──────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─── Step 2: RETRIEVE ────────────────────────────────────────────────┐
│  ChromaDB similarity_search(query, k=10)                            │
│  → Returns 10 document chunks                                       │
└──────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─── Step 3: RE-RANK ─────────────────────────────────────────────────┐
│  Cross-Encoder scores all 10 docs                                    │
│  → Picks top 3, checks confidence threshold                         │
└──────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─── Step 4: GENERATE (THE WEAK LINK) ────────────────────────────────┐
│                                                                      │
│  Model: distilbart-cnn-12-6 (SUMMARIZATION model)                   │
│                                                                      │
│  Input:  "Question: What is the history of Delhi?                    │
│           Context: <ONLY best 1 doc's text>                          │
│           Answer:"                                                   │
│                                                                      │
│  What it does: Tries to COMPRESS/SUMMARIZE the context               │
│  What it CANNOT do:                                                  │
│    ❌ Reason about the question                                      │
│    ❌ Synthesize across multiple chunks                               │
│    ❌ Generate natural conversational answers                         │
│    ❌ Understand Hindi questions                                      │
│    ❌ Answer in Hindi directly                                        │
│                                                                      │
│  Output: A choppy, extractive English summary                        │
│  Example: "Delhi is capital. Founded by. Mughal empire ruled."       │
└──────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─── Step 5: TRANSLATE (BAND-AID) ────────────────────────────────────┐
│  If user spoke Hindi → Load Helsinki-NLP translator into GPU         │
│  Translate the choppy English summary → Often garbled Hindi          │
│  ⚠️ Garbled because source text was already bad                     │
└──────────────────────────────────────────────────────────────────────┘
        │
        ▼
  💬 User gets: A robotic, choppy, often meaningless answer
```

### 🟢 AFTER — What happens now with Ollama

```
User asks: "What is the history of Delhi?"
        │
        ▼
┌─── Step 1: SYSTEM STARTUP ──────────────────────────────────────────┐
│  actions.py loads FEWER models into GPU:                             │
│                                                                      │
│  ① paraphrase-xlm-r (Embedding)        → ~1.0 GB GPU               │
│  ② cross-encoder/ms-marco (Re-ranker)   → ~0.3 GB GPU              │
│  ③ ❌ distilbart REMOVED (saves ~1.2 GB!)                           │
│  ④ Helsinki-NLP translator (on demand)  → ~0.5 GB GPU              │
│                                                                      │
│  Total: ~1.3 GB in GPU at startup (saved 1.2 GB!)                   │
│  ✅ Plenty of room. Stable.                                         │
│                                                                      │
│  Meanwhile, Ollama runs SEPARATELY as its own service:               │
│  ┌──────────────────────────────────────────────┐                    │
│  │  Ollama (C++ engine) @ localhost:11434        │                   │
│  │  mashriram/sarvam-1 (2B, 1.5GB, GGUF)        │                   │
│  │  Manages its own GPU/RAM split automatically  │                   │
│  └──────────────────────────────────────────────┘                    │
└──────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─── Step 2: RETRIEVE (Same as before) ───────────────────────────────┐
│  ChromaDB similarity_search(query, k=10)                            │
│  → Returns 10 document chunks                                       │
└──────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─── Step 3: RE-RANK (Same as before) ────────────────────────────────┐
│  Cross-Encoder scores all 10 docs                                    │
│  → Picks top 3, checks confidence threshold                         │
└──────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─── Step 4: GENERATE (THE UPGRADE) ──────────────────────────────────┐
│                                                                      │
│  Model: Sarvam-1 (INSTRUCTION-FOLLOWING LLM, 10 Indian languages)   │
│  Engine: Ollama (separate process, smart memory management)          │
│                                                                      │
│  Input: HTTP POST to localhost:11434/api/generate                    │
│  {                                                                   │
│    "You are a helpful document assistant.                             │
│     Answer based ONLY on the provided context.                       │
│     Context: <ALL top-3 docs combined>      ← MORE context!         │
│     Question: What is the history of Delhi?                          │
│     Answer:"                                                         │
│  }                                                                   │
│                                                                      │
│  What it CAN do:                                                     │
│    ✅ Reason about the question                                      │
│    ✅ Synthesize across all 3 document chunks                        │
│    ✅ Generate natural, conversational answers                       │
│    ✅ Understand Hindi/English/Hinglish questions                    │
│    ✅ Answer in Hindi DIRECTLY (no translation needed!)              │
│                                                                      │
│  Output: A natural, coherent answer                                  │
│  Example: "Delhi has a rich history spanning several centuries.       │
│   Founded as Indraprastha, it later became the seat of the           │
│   Mughal Empire under Shah Jahan, who built the Red Fort..."         │
└──────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─── Step 5: TRANSLATE (STILL THERE, but less needed) ────────────────┐
│  If user spoke Hindi → Sarvam may already answer in Hindi!           │
│  Translation layer still exists as safety net                        │
│  But quality is MUCH better because source text is coherent          │
└──────────────────────────────────────────────────────────────────────┘
        │
        ▼
  💬 User gets: A natural, intelligent, well-formed answer
```

### 📊 Side-by-Side Summary

| Aspect | 🔴 Before | 🟢 After |
| :--- | :--- | :--- |
| **Generation Model** | `distilbart-cnn-12-6` (summarizer) | `mashriram/sarvam-1` (instruction LLM) |
| **Model Size** | ~1.2 GB (FP16 in Python) | ~1.5 GB (GGUF in Ollama) |
| **Loaded Where** | Inside `actions.py` (shares GPU) | Separate Ollama process (own memory) |
| **GPU Usage by Python** | ~3.0 GB (tight!) | ~1.3 GB (comfortable!) |
| **Context Sent** | Best 1 document only | All top-3 documents combined |
| **Answer Quality** | Choppy extractive summary | Natural conversational response |
| **Hindi Support** | ❌ English only → then translates | ✅ Native Hindi generation |
| **Can Reason?** | ❌ No | ✅ Yes |
| **Crash Risk** | ⚠️ High (OOM) | ✅ Low (Ollama auto-manages memory) |
| **Swap Models** | Rewrite Python code | Change 1 env variable |

---

## 5. Priority Model List (for Ollama)

| Priority | Model | Params | VRAM Needed (Q4) | Indian Langs | Ollama Tag |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 🥇 P1 | Sarvam-1 | 2B | ~1.5 GB | 10 languages | `mashriram/sarvam-1` |
| 🥈 P2 | Gemma 2 | 2B | ~1.5 GB | Multilingual | `gemma2:2b` |
| 🥉 P3 | Airavata | 7B | ~4.0 GB | Hindi-focused | Custom GGUF |
| P4 | Navarasa 2.0 | 2B | ~1.5 GB | 15 languages | Custom GGUF |
| P5 | Nemotron-Hindi | 4B | ~2.5 GB | Hindi | Custom GGUF |

---

## 6. Code Changes

### 6.1 What Changed in `actions.py`
*   **REMOVED**: `self.summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6", ...)` — frees ~1.2 GB GPU.
*   **ADDED**: `import requests` and `import json` for HTTP calls to Ollama.
*   **ADDED**: `OLLAMA_URL`, `OLLAMA_MODEL`, `OLLAMA_TIMEOUT` config constants (all env-configurable).
*   **ADDED**: `generate_with_ollama()` method — sends a structured RAG prompt to Ollama and returns a natural language answer.
*   **MODIFIED**: Step 3 (GENERATE) in the `run()` method now calls `generate_with_ollama()` instead of `self.summarizer()`.
*   **IMPROVED**: Now sends ALL top-3 document chunks as combined context (was only best-1 before).
*   **ADDED**: Startup health check — checks if Ollama is running and if the configured model is available.
*   **ADDED**: Graceful fallback — if Ollama is unreachable at any point, falls back to returning raw retrieved text (no crash).

### 6.2 Environment
*   **Ollama must be running** before starting the Rasa Action Server.
*   Default: `http://localhost:11434` (Ollama's default port).
*   Model must be pre-pulled: `ollama pull mashriram/sarvam-1`.

---

## 7. Setup Steps (Completed)

### Step 1: Install Ollama ✅
```bash
# Downloaded from https://ollama.com/download/windows
# Ran OllamaSetup.exe → installed v0.16.3
```

### Step 2: Pull a Model ✅
```bash
ollama pull mashriram/sarvam-1
# Downloaded 1.5 GB successfully (1 retry needed)
```

### Step 3: Verify Ollama is Running ✅
```bash
ollama list
# Output: mashriram/sarvam-1:latest  6443034ccda0  1.5 GB

ollama run mashriram/sarvam-1 "What is the capital of India?"
# Output: भारत की राजधानी नई दिल्ली है।
```

### Step 4: Restart the System 🟡 PENDING
```bash
# Restart start_system.bat
# The updated actions.py will now connect to Ollama for generation
```

---

## 8. Rollback Plan
If Ollama causes issues:
*   Set `OLLAMA_URL = ""` (empty string) in `actions.py`.
*   The code will fall back to returning raw retrieved text (no summarization, but no crash either).
*   The old `distilbart` code has been removed but can be restored from git history.

---

## 9. Prompt Tuning for SEC (Fact Accuracy) — 2026-02-22 00:56 IST

### Problem Diagnosis
Test 02 showed SEC (Fact Accuracy) at **40%**. Root cause analysis of failing questions:

| Q | Expected | Model Said | Problem |
| :-- | :--- | :--- | :--- |
| Q02 | **Wheeler, 1967** | "Stephen Hawking" | Wrong person — model guessed instead of extracting |
| Q07 | **Shah Jahan, Shahjahanabad** | "the british raj." | Too short — 3 words, no facts extracted |
| Q10 | **demon, Mahishasura** | "defeated goddess Durga" | Factually inverted |
| Q12 | **asteroid, impact** | "went extinct" | Too vague — missed the cause |
| Q17 | **45, golden** | "approximately two hours" | Fabricated number — context says 45 min |

### Root Cause
The original prompt was too vague: `"Answer the user's question based ONLY on the provided context."`
This gave the LLM freedom to paraphrase loosely, abstract away specific facts, and even fabricate details.

### Fix Applied
**Prompt changes:**
*   Added explicit RULES section with 6 constraints
*   Rule 1: "Include specific names, dates, numbers, and places from the context"
*   Rule 2: "Do NOT paraphrase loosely — stay close to the original wording"
*   Rule 3: "If the context mentions a specific person, year, or measurement, you MUST include it"
*   Rule 6: "Keep the answer concise but fact-complete (2-4 sentences)"
*   Added suffix: "ANSWER (include all relevant facts, names, dates, and numbers from the context):"

**Parameter changes:**
*   `temperature`: 0.3 → **0.1** (more deterministic, less creative)
*   `top_p`: 0.9 → **0.85** (tighter token selection)
*   `num_predict`: 300 → **400** (room for fact-complete answers)

### A/B Test Results (Manual)
| Question | Old Prompt | New Prompt |
| :--- | :--- | :--- |
| "Who coined term black hole?" | ❌ "Stephen Hawking" | ✅ **"John Archibald Wheeler...1967"** |
| "How long bake Apple Pie?" | ❌ "approximately two hours" | ✅ **"45 minutes or until golden brown"** |

### MBS Test 03 Results (2026-02-22 01:02 IST)
*   TMS: 68.42 | SEC: 39.2% | NEG: 95%
*   Prompt improved Q01 (+0.67), Q10 (+0.67), Q12 (+0.67)
*   But regressed Q06 (-0.67), Q08 (-0.50), Q18 (-1.00 hallucinated)
*   Root cause: remaining failures are RETRIEVAL problems, not generation

---

## 10. Score Progression

| Test | TMS | SEC | NEG | Change |
| :--- | :---: | :---: | :---: | :--- |
| Test 01 | 68.2 | -- | -- | distilbart summarizer |
| Test 02 | 68.93 | 40.0% | 100% | Sarvam-1 via Ollama |
| Test 03 | 68.42 | 39.2% | 95% | Prompt tuned for facts |

---

## 11. Next Steps
- [x] Install Ollama + Pull mashriram/sarvam-1
- [x] Update actions.py with Ollama integration
- [x] Run MBS Test 02 (TMS: 68.93)
- [x] Prompt tuning for SEC + Run MBS Test 03 (TMS: 68.42)
- [ ] Fix retrieval layer (chunking/re-ranking is the bottleneck)
- [ ] Investigate stress_test.pdf multi-topic chunk confusion
- [ ] Lower re-ranker threshold for Q05, Q11, Q16, Q19, Q20
