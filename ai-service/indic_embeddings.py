import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel
from typing import List
from langchain_core.embeddings import Embeddings

class IndicBERTEmbeddings(Embeddings):
    """
    Custom LangChain wrapper for ai4bharat/IndicBERT-v3-1B.
    Uses Mean Pooling and L2 Normalization for high-quality semantic embeddings.
    """
    def __init__(self, model_name="ai4bharat/IndicBERT-v3-1B", device=None):
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        print(f"Loading IndicBERT model: {model_name} on {self.device}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        self.model = AutoModel.from_pretrained(model_name, trust_remote_code=True).to(self.device)
        self.model.eval()
        print("IndicBERT loaded successfully.")

    def _mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[0]  # First element of model_output contains all token embeddings
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    @torch.no_grad()
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents."""
        embeddings = []
        # Batch processing to avoid OOM
        batch_size = 8
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            encoded_input = self.tokenizer(batch_texts, padding=True, truncation=True, max_length=512, return_tensors='pt').to(self.device)
            model_output = self.model(**encoded_input)
            sentence_embeddings = self._mean_pooling(model_output, encoded_input['attention_mask'])
            sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)
            embeddings.extend(sentence_embeddings.cpu().tolist())
        return embeddings

    @torch.no_grad()
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query."""
        encoded_input = self.tokenizer([text], padding=True, truncation=True, max_length=512, return_tensors='pt').to(self.device)
        model_output = self.model(**encoded_input)
        sentence_embeddings = self._mean_pooling(model_output, encoded_input['attention_mask'])
        sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)
        return sentence_embeddings.cpu().tolist()[0]
