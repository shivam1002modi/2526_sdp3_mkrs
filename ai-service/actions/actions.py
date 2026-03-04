# ai-service/actions/actions.py
# ══════════════════════════════════════════════════════════════════════════════
# MKRS Brain — ActionQueryDoc with Parent Document Retrieval (PDR)
# ══════════════════════════════════════════════════════════════════════════════
#
# PDR Flow:
#   1. RETRIEVE: Get top-15 CHILD chunks from ChromaDB (small, precise, 300 chars)
#   2. RE-RANK:  Cross-Encoder scores each child chunk → top-3
#   3. EXPAND:   Look up each child's parent_id in parent_store.json → get 1500-char context
#   4. DEDUPE:   If multiple children share the same parent, send the parent only once
#   5. GENERATE: Send expanded PARENT contexts to Sarvam-1 via Ollama
#
# Why this is better:
#   - Small chunks have better embedding similarity (more precise retrieval)
#   - Large contexts give the LLM enough detail to answer accurately
#   - Tables are kept atomic and enriched with surrounding text
# ══════════════════════════════════════════════════════════════════════════════

import os
import re
import time
import json
import requests
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from langchain_community.vectorstores import Chroma

from langdetect import detect, LangDetectException
from transformers import pipeline
# Import the CrossEncoder model for re-ranking
from sentence_transformers.cross_encoder import CrossEncoder
import torch
import traceback

# --- Configuration ---
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5001")
DB_FAISS_PATH = os.path.join(os.path.dirname(__file__), "..", "documents", "vectorstore")
TRANSLATION_MODEL_MAP = {
    'hi': 'Helsinki-NLP/opus-mt-en-hi',
}
# Disabled confidence threshold to ensure re-ranker always provides its best guess.
CONFIDENCE_THRESHOLD = 0.00

# --- Ollama Generation Service Configuration ---
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "120"))  # seconds

# --- Parent Store Path ---
PARENT_STORE_PATH = os.path.join(os.path.dirname(__file__), "..", "documents", "parent_store.json")


def clean_text(text: str) -> str:
    """
    Cleans up text extracted from a PDF by removing excessive whitespace and line breaks.
    """
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def is_translation_garbled(text: str) -> bool:
    """A simple heuristic to detect garbled or nonsensical translations."""
    if not text:
        return True
    if re.search(r'([A-Z]{2,})(\1{5,})', text, re.IGNORECASE):
        print("--- Gibberish Detected: Repetitive pattern found.")
        return True
    if text.strip().lower() in ['null', 'none', 'n/a', '']:
        return True
    return False


class ActionQueryDoc(Action):
    def __init__(self):
        super().__init__()
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"--- Using device: {self.device.upper()} ---")

        try:
            from indic_embeddings import IndicBERTEmbeddings
            print("Loading IndicBERT-v3-1B Embeddings...")
            self.embeddings = IndicBERTEmbeddings(device=self.device)
        except Exception as e:
            print("FATAL: Could not initialize IndicBERTEmbeddings:", e)
            self.embeddings = None

        try:
            # DB Path
            chroma_path = os.path.join(os.path.dirname(__file__), "..", "documents", "chroma_db")

            if os.path.exists(chroma_path):
                print(f"Loading ChromaDB from: {chroma_path}")
                self.db = Chroma(persist_directory=chroma_path, embedding_function=self.embeddings)
                print("Vector store loaded successfully.")
            else:
                print("WARNING: Vector store not found. The bot cannot answer document questions until it's retrained.")
                self.db = None
        except Exception as e:
            print("FATAL: Failed to load ChromaDB:", e)
            traceback.print_exc()
            self.db = None

        # ── Load Parent Store (PDR) ───────────────────────────────────────
        self.parent_store = {}
        try:
            if os.path.exists(PARENT_STORE_PATH):
                with open(PARENT_STORE_PATH, "r", encoding="utf-8") as f:
                    self.parent_store = json.load(f)
                print(f"✅ Parent store loaded: {len(self.parent_store)} parent contexts available (PDR active)")
            else:
                print("⚠️ WARNING: parent_store.json not found. PDR disabled — using raw child chunks.")
        except Exception as e:
            print(f"WARNING: Could not load parent store: {e}. PDR disabled.")

        # Initialize a Cross-Encoder for re-ranking search results
        try:
            print("Loading local Re-ranking model (Cross-Encoder)...")
            self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', device=self.device)
            print("Re-ranking model loaded successfully.")
        except Exception as e:
            print(f"WARNING: Could not load local Re-ranking model: {e}.")
            self.reranker = None

        # --- Ollama Connection Check ---
        self.ollama_available = False
        try:
            print(f"Checking Ollama service at {OLLAMA_URL}...")
            health_check = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
            if health_check.status_code == 200:
                models = health_check.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                print(f"Ollama is running. Available models: {model_names}")
                if any(OLLAMA_MODEL in name for name in model_names):
                    self.ollama_available = True
                    print(f"✅ Ollama model '{OLLAMA_MODEL}' is ready for generation.")
                else:
                    print(f"⚠️ WARNING: Model '{OLLAMA_MODEL}' not found in Ollama. "
                          f"Available: {model_names}. Run: ollama pull {OLLAMA_MODEL}")
            else:
                print(f"WARNING: Ollama returned status {health_check.status_code}.")
        except requests.exceptions.ConnectionError:
            print(f"⚠️ WARNING: Ollama is NOT running at {OLLAMA_URL}. "
                  f"Generation will fall back to raw text retrieval. "
                  f"Install Ollama: https://ollama.com/download/windows")
        except Exception as e:
            print(f"WARNING: Ollama health check failed: {e}")

        # --- Ollama Warmup: Pre-load model into memory to eliminate cold-start ---
        if self.ollama_available:
            try:
                print("Warming up Ollama model (pre-loading into memory)...")
                warmup_resp = requests.post(
                    f"{OLLAMA_URL}/api/generate",
                    json={"model": OLLAMA_MODEL, "prompt": "Hi", "stream": False,
                          "options": {"num_predict": 1}},
                    timeout=60
                )
                if warmup_resp.status_code == 200:
                    print("✅ Ollama model warmed up — ready for fast inference.")
                else:
                    print(f"WARNING: Ollama warmup returned {warmup_resp.status_code}")
            except Exception as e:
                print(f"WARNING: Ollama warmup failed: {e}")

        self.translator_cache = {}
        pdr_status = "ACTIVE" if self.parent_store else "DISABLED"
        print(f"ActionQueryDoc initialized successfully (PDR Mode: {pdr_status}).")

    def name(self) -> Text:
        return "action_query_doc"

    def _expand_to_parent(self, child_doc):
        """
        PDR Expansion: Given a child chunk, look up its parent context.
        Returns the parent text if found, otherwise the child's own text.
        """
        parent_id = child_doc.metadata.get("parent_id", "")
        if parent_id and parent_id in self.parent_store:
            return self.parent_store[parent_id]
        # Fallback: return the child content as-is
        return child_doc.page_content

    def generate_with_ollama(self, question: str, context: str) -> str:
        """
        Sends a structured RAG prompt to Ollama and returns the generated answer.
        Falls back to returning the raw context if Ollama is unavailable.
        """
        if not self.ollama_available:
            print("Ollama not available — returning raw context as answer.")
            return context

        # Structured RAG prompt optimized for FACT ACCURACY (SEC score)
        # ULTRA CONFIG: MAXIMUM DETAIL EXTRACTION
        prompt = (
            "You are a document assistant that answers questions by extracting and quoting "
            "from the provided context documents.\n\n"
            "RULES:\n"
            "1. NO PREAMBLE. Start the answer immediately.\n"
            "2. DATA ACCURACY. Use EXACT words, names, dates, and technical figures. If a table is present, look up the values requested.\n"
            "3. BE COMPREHENSIVE. Include all relevant facts found in the context provided.\n"
            "4. Only use provided documents to answer the question.\n"
            "5. BE HELPFUL. If the answer is partially available, provide the available portion accurately. "
            "Only say 'The documents do not contain this information.' if there is absolutely no relevant context at all.\n"
            "6. Max 5 sentences. Focus on high-density information.\n\n"
            f"CONTEXT:\n{context}\n\n"
            f"QUESTION: {question}\n\n"
            "ANSWER (accurate, comprehensive, start immediately):"
        )

        try:
            response = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "keep_alive": "10m",
                    "options": {
                        "temperature": 0.0,
                        "top_p": 0.9,
                        "num_predict": 500,
                        "repeat_penalty": 1.05,
                    }
                },
                timeout=OLLAMA_TIMEOUT
            )
            if response.status_code == 200:
                result = response.json()
                answer = result.get("response", "").strip()
                if answer:
                    print(f"Ollama generated answer ({len(answer)} chars): '{answer[:100]}...'")
                    return answer
                else:
                    return context
            else:
                return context
        except Exception:
            return context

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        raw_query = tracker.latest_message.get("text", "").strip()

        # --- Query Normalization ---
        temp_query = raw_query
        if temp_query.isupper() and len(temp_query) > 3:
            temp_query = temp_query.lower()

        temp_query = re.sub(r'^(a|an|the)\s+', '', temp_query, flags=re.IGNORECASE).strip()
        original_query = temp_query

        print(f"\n--- New Request Received (PDR Mode - RECORD BREAKER) ---\nQuery: '{original_query}'")

        if not self.db:
            return []

        try:
            lang = detect(original_query) if original_query else 'en'
        except Exception:
            lang = 'en'

        # ══════════════════════════════════════════════════════════════════
        # STEP 1: RETRIEVE — Get top-50 CHILD chunks (Balanced Precision)
        # ══════════════════════════════════════════════════════════════════
        try:
            retrieved_docs = self.db.similarity_search(original_query, k=50)
        except Exception:
            retrieved_docs = []

        if not retrieved_docs:
            return []

        # ══════════════════════════════════════════════════════════════════
        # STEP 2: RE-RANK — Cross-Encoder scores each child chunk
        # ══════════════════════════════════════════════════════════════════
        if self.reranker:
            # OPTIMIZATION: Only re-rank top-25 instead of full k=50 to save CPU cycles
            top_candidates = retrieved_docs[:25]
            passages = [doc.page_content for doc in top_candidates]
            rerank_scores = self.reranker.predict([(original_query, passage) for passage in passages])
            scored_docs = list(zip(rerank_scores, top_candidates))
            scored_docs.sort(key=lambda x: x[0], reverse=True)
            print(f"Re-ranked top child chunk score: {scored_docs[0][0]:.4f}")
        else:
            scored_docs = [(1.0, doc) for doc in retrieved_docs]

        # ══════════════════════════════════════════════════════════════════
        # STEP 3: EXPAND — PDR: Look up parent contexts for top candidates
        # ══════════════════════════════════════════════════════════════════
        context_parts = []
        final_docs = []
        seen_parent_ids = set()

        for score, child_doc in scored_docs[:15]:  # Consider top-15 children
            metadata = getattr(child_doc, "metadata", {})
            parent_id = metadata.get("parent_id", "")
            source_name = os.path.basename(str(metadata.get("source", "Unknown")))
            page_no = metadata.get("page", "?")

            if parent_id and parent_id in seen_parent_ids:
                continue
            if parent_id:
                seen_parent_ids.add(parent_id)

            if self.parent_store and parent_id in self.parent_store:
                expanded_text = self.parent_store[parent_id]
            else:
                expanded_text = child_doc.page_content

            content = clean_text(expanded_text)
            context_parts.append(f"### DOCUMENT {len(context_parts)+1}: {source_name} (Page {page_no})\n{content}")
            final_docs.append(child_doc)

            if len(context_parts) >= 5:  # Record Breaker Context Limit
                break

        # ══════════════════════════════════════════════════════════════════
        # STEP 4: GENERATE — Send expanded context to Ollama
        # ══════════════════════════════════════════════════════════════════
        combined_context = "\n\n".join(context_parts)
        print(f"Total context sent to LLM: {len(combined_context)} chars "
              f"(from {len(context_parts)} unique parents)")
        english_answer = self.generate_with_ollama(original_query, combined_context)

        sources = []
        for i, doc in enumerate(final_docs):
            metadata = getattr(doc, "metadata", {})
            source_filename = metadata.get("source", "Unknown")
            page_no = metadata.get("page", "?")
            sources.append({
                "source": os.path.basename(str(source_filename)),
                "page": page_no,
                "rank": i + 1,
            })
        print(f"DEBUG: Top source retrieved: {sources[0] if sources else 'N/A'}")

        final_answer = english_answer
        if lang in TRANSLATION_MODEL_MAP:
            try:
                model_name = TRANSLATION_MODEL_MAP[lang]
                if lang not in self.translator_cache:
                    print(f"Loading translator for '{lang}': {model_name}")
                    device_id = 0 if self.device == 'cuda' else -1
                    self.translator_cache[lang] = pipeline('translation', model=model_name, device=device_id)

                translator = self.translator_cache[lang]
                translated_output = translator(final_answer)
                translated_text = translated_output[0].get('translation_text')
                if translated_text and not is_translation_garbled(translated_text):
                    final_answer = translated_text
                    print(f"Translated Answer: '{final_answer[:100]}...'")
                else:
                    print("WARN: Translation appears garbled. Falling back to English.")
            except Exception as e:
                print("ERROR: Translation failed:", e)

        sources_info = []
        for src in sources:
            pdf_name = os.path.basename(src["source"])
            page_number = src.get("page", 1)
            sources_info.append({
                "title": pdf_name,
                "page": page_number,
                "url": f"{BACKEND_URL}/api/documents/{pdf_name}#page={page_number}"
            })

        answer_payload = {
            "text": final_answer,
            "sources": sources_info
        }

        dispatcher.utter_message(json_message=answer_payload)
        print("--- Response Sent to User (PDR Mode) ---")
        return []
