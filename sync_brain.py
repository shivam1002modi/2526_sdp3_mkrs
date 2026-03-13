import os
import sys
import subprocess
import json

# ══════════════════════════════════════════════════════════════════════════════
# SYNC_BRAIN.PY — MKRS "Self-Healing" System Sync
# ══════════════════════════════════════════════════════════════════════════════
# This script ensures that the AI Brain is always synchronized with the code.
# Run this after any git revert, pull, or branch switch.

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
AI_SERVICE_DIR = os.path.join(ROOT_DIR, "ai-service")
VENV_PYTHON = os.path.join(AI_SERVICE_DIR, "venv", "Scripts", "python.exe")
DB_PATH = os.path.join(AI_SERVICE_DIR, "documents", "chroma_db")
PARENT_STORE = os.path.join(AI_SERVICE_DIR, "documents", "parent_store.json")

def print_banner(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def check_env():
    print("[1/3] Checking Environment Compatibility...")
    try:
        import transformers
        from packaging import version
        if version.parse(transformers.__version__) < version.parse("4.40.0"):
            print(f"⚠️  OUTDATED: transformers {transformers.__version__}. Need 4.40.0+")
            return False
        print(f"✅  Environment OK (transformers {transformers.__version__})")
        return True
    except ImportError:
        print("❌  Environment Missing! Please run setup_system.bat")
        return False

def check_brain_data():
    print("[2/3] Checking Brain Data Integrity...")
    
    db_exists = os.path.exists(os.path.join(DB_PATH, "chroma.sqlite3"))
    store_exists = os.path.exists(PARENT_STORE)
    
    if not db_exists or not store_exists:
        print("⚠️  DATA MISSING: ChromaDB or Parent Store not found.")
        return False

    # Check if DB has entries (quick check via python)
    try:
        # We run a small subprocess to avoid importing heavy libs in the main check
        cmd = [VENV_PYTHON, "-c", "from langchain_community.vectorstores import Chroma; import sys; sys.path.append(r'" + AI_SERVICE_DIR + "'); from indic_embeddings import IndicBERTEmbeddings; db = Chroma(persist_directory=r'" + DB_PATH + "', embedding_function=IndicBERTEmbeddings()); print(db._collection.count())"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        count = int(result.stdout.strip().split('\n')[-1])
        if count == 0:
            print("⚠️  EMPTY BRAIN: Vector database has 0 documents.")
            return False
        print(f"✅  Brain Data OK ({count} documents found)")
        return True
    except Exception as e:
        print(f"⚠️  SYSTEM ERROR: Could not read database: {e}")
        return False

def rebuild_brain():
    print_banner("REBUILDING BRAIN (RAG PIPELINE)")
    print("This will re-index all PDFs using IndicBERT-v3-1B. Please wait...")
    pipeline_path = os.path.join(AI_SERVICE_DIR, "rag_pipeline.py")
    subprocess.run([VENV_PYTHON, pipeline_path])

if __name__ == "__main__":
    print_banner("MKRS AUTO-SYNC & REPAIR")
    
    env_ok = check_env()
    data_ok = check_brain_data() if env_ok else False
    
    if not env_ok:
        print("\n❌  ACTION REQUIRED: Run 'pip install --upgrade transformers' or 'setup_system.bat'")
    
    if env_ok and not data_ok:
        print("\n🔄  TRIGGERING AUTO-REPAIR...")
        rebuild_brain()
        print("\n✅  AUTO-REPAIR COMPLETE.")
    elif env_ok and data_ok:
        print("\n💎  SYSTEM IS PERFECT. No action needed.")
    
    print_banner("READY TO START")
