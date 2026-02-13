
import os
import sys
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

print("Checking imports...")
import langchain
import faiss
import torch
import sentence_transformers
import spacy
print("Imports success.")

print("Downloading Sentence Transformer model (paraphrase-xlm-r-multilingual-v1)...")
from langchain_community.embeddings import HuggingFaceEmbeddings
try:
    embeddings = HuggingFaceEmbeddings(
        model_name="paraphrase-xlm-r-multilingual-v1"
    )
    print("Model downloaded successfully.")
except Exception as e:
    print(f"Failed to download model: {e}")
    sys.exit(1)

print("Setup verification complete.")
