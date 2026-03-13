
import sys
import os
sys.path.append(r'D:\MKRS\ai-service')
try:
    from indic_embeddings import IndicBERTEmbeddings
    print("Import successful")
    emb = IndicBERTEmbeddings(device='cpu')
    print("Initialization successful")
    res = emb.embed_query("Hello")
    print(f"Embedding successful, size: {len(res)}")
except Exception as e:
    import traceback
    traceback.print_exc()
