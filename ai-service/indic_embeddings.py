
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel
from typing import List
from langchain_core.embeddings import Embeddings

class IndicBERTEmbeddings(Embeddings):
    """
    Multilingual E5 Small wrapper. 
    Fast, light, and compatible with Transformers 4.x.
    """
    def __init__(self, model_name="intfloat/multilingual-e5-small", device=None):
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        print(f"Loading Embedding model: {model_name} on {self.device}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        self.model.eval()
        print("Embedding model loaded successfully.")

    def _mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[0]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    @torch.no_grad()
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # Required prefix for E5 models
        prefixed_texts = [f"passage: {t}" for t in texts]
        embeddings = []
        batch_size = 16
        for i in range(0, len(prefixed_texts), batch_size):
            batch = prefixed_texts[i:i + batch_size]
            encoded = self.tokenizer(batch, padding=True, truncation=True, max_length=512, return_tensors='pt').to(self.device)
            out = self.model(**encoded)
            embs = self._mean_pooling(out, encoded['attention_mask'])
            embs = F.normalize(embs, p=2, dim=1)
            embeddings.extend(embs.cpu().tolist())
        return embeddings

    @torch.no_grad()
    def embed_query(self, text: str) -> List[float]:
        # Required prefix for query
        prefixed_text = f"query: {text}"
        encoded = self.tokenizer([prefixed_text], padding=True, truncation=True, max_length=512, return_tensors='pt').to(self.device)
        out = self.model(**encoded)
        emb = self._mean_pooling(out, encoded['attention_mask'])
        emb = F.normalize(emb, p=2, dim=1)
        return emb.cpu().tolist()[0]
