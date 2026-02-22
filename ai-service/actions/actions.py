# ai-service/actions/actions.py
import os
import re
import time
import json
import requests
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from langchain_community.embeddings import HuggingFaceEmbeddings
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
# Lowered to 0.02 for better RHR on difficult Stress Tests.
CONFIDENCE_THRESHOLD = 0.02

# --- Ollama Generation Service Configuration ---
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mashriram/sarvam-1")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "120"))  # seconds

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
            self.embeddings = HuggingFaceEmbeddings(
                model_name="paraphrase-xlm-r-multilingual-v1",
                model_kwargs={'device': self.device}
            )
        except Exception as e:
            print("FATAL: Could not initialize HuggingFaceEmbeddings model:", e)
            self.embeddings = None

        try:
            # DB Path
            # Fix NameError: Use relative path from actions.py to documents/chroma_db
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
        # Q01 was taking 19.6s (cold-start) vs ~4s (warm). This fixes that.
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
        print("ActionQueryDoc initialized successfully (Pro Mode — Ollama Generation).")

    def name(self) -> Text:
        return "action_query_doc"

    def generate_with_ollama(self, question: str, context: str) -> str:
        """
        Sends a structured RAG prompt to Ollama and returns the generated answer.
        Falls back to returning the raw context if Ollama is unavailable.
        """
        if not self.ollama_available:
            print("Ollama not available — returning raw context as answer.")
            return context

        # Structured RAG prompt optimized for FACT ACCURACY (SEC score)
        # KEY INSIGHT from 8 tests: the baseline model scored better SEC because
        # it quoted context verbatim. Sarvam-1 paraphrases and loses keywords.
        # Solution: force the model to QUOTE directly from the documents.
        # SUPER CONFIG: NO PREAMBLE + VERBATIM QUOTE (Targeting 72+ TMS)
        prompt = (
            "You are a document assistant that answers questions by DIRECTLY QUOTING "
            "from the provided context documents.\n\n"
            "RULES:\n"
            "1. NO PREAMBLE. Do NOT say 'Based on the context' or 'The document states'. Start the answer immediately.\n"
            "2. QUOTE VERBATIM. Use the EXACT words, names, dates, and numbers. Do NOT paraphrase.\n"
            "3. Include ALL technical details provided (like specific chemicals, years, and city names).\n"
            "4. Only use facts from the document relevant to the question.\n"
            "5. If the answer is not present, say exactly: 'The documents do not contain this information.'\n"
            "6. Max 3 sentences. Focus only on the direct answer.\n\n"
            f"CONTEXT:\n{context}\n\n"
            f"QUESTION: {question}\n\n"
            "ANSWER (verbatim quote, no preamble):"
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
                        "top_p": 0.8,
                        "num_predict": 350,
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
                    print("WARNING: Ollama returned empty response. Falling back to context.")
                    return context
            else:
                print(f"ERROR: Ollama returned HTTP {response.status_code}: {response.text[:200]}")
                return context
        except requests.exceptions.Timeout:
            print(f"ERROR: Ollama timed out after {OLLAMA_TIMEOUT}s. Returning raw context.")
            return context
        except requests.exceptions.ConnectionError:
            print("ERROR: Lost connection to Ollama. Returning raw context.")
            self.ollama_available = False  # Disable for subsequent requests
            return context
        except Exception as e:
            print(f"ERROR: Ollama generation failed: {e}")
            return context

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        raw_query = tracker.latest_message.get("text", "").strip()
        
        # --- Query Normalization ---
        temp_query = raw_query
        if temp_query.isupper() and len(temp_query) > 3:
            temp_query = temp_query.lower()
        
        # Strip leading articles which often confuse small context-matching models
        temp_query = re.sub(r'^(a|an|the)\s+', '', temp_query, flags=re.IGNORECASE).strip()
        
        original_query = temp_query

        print(f"\n--- New Request Received ---\nRaw Query: '{raw_query}'")
        if original_query != raw_query:
             print(f"Normalized to: '{original_query}'")

        if not self.db:
            dispatcher.utter_message(text="Sorry, the AI's knowledge base is currently unavailable. Please ask an administrator to check the system.")
            return []

        try:
            lang = detect(original_query) if original_query else 'en'
        except Exception:
            lang = 'en'
        print(f"Detected language: '{lang}'")

        # 1. RETRIEVE: k=12 (Final optimized depth)
        try:
            retrieved_docs = self.db.similarity_search(original_query, k=15)
        except Exception as e:
            print(f"ERROR: Document similarity_search failed: {e}")
            retrieved_docs = []

        if not retrieved_docs:
            dispatcher.utter_message(text="Sorry, I couldn't find any information related to your question.")
            return []

        # 2. RE-RANK: Use the Cross-Encoder for more accurate relevance scoring.
        if self.reranker:
            passages = [doc.page_content for doc in retrieved_docs]
            rerank_scores = self.reranker.predict([(original_query, passage) for passage in passages])
            scored_docs = list(zip(rerank_scores, retrieved_docs))
            scored_docs.sort(key=lambda x: x[0], reverse=True)
            
            top_score = scored_docs[0][0]
            if top_score < CONFIDENCE_THRESHOLD:
                dispatcher.utter_message(text="I found some documents, but I'm not confident they contain the right answer for your question.")
                return []
            
            print(f"Re-ranked top document score: {top_score:.4f}")
        else:
            # Fallback to simple similarity scores if reranker is missing
            scored_docs = [(1.0, doc) for doc in retrieved_docs]

        # 3. GENERATE: Create the answer using Ollama LLM (or fallback to raw text).
        
        # Build structured context: Label each chunk so the LLM knows which doc it's from.
        # This prevents "Context Bleed" (hallucinating facts from one doc into another).
        context_parts = []
        final_docs = []
        for i, (score, d) in enumerate(scored_docs[:3]): # top-3 for speed (latency is killing TMS)
            final_docs.append(d)
            metadata = getattr(d, "metadata", {})
            source_name = os.path.basename(str(metadata.get("source", "Unknown")))
            page_no = metadata.get("page", "?")
            
            content = clean_text(d.page_content)
            context_parts.append(f"### DOCUMENT {i+1}: {source_name} (Page {page_no})\n{content}")
            
        combined_context = "\n\n".join(context_parts)
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
        print("--- Response Sent to User ---")
        return []

