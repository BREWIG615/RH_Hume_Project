"""
Embedding Client

Abstraction for embedding generation (OpenAI or local BGE).
"""

from abc import ABC, abstractmethod
from typing import Optional
import logging
import os

logger = logging.getLogger(__name__)


class BaseEmbeddingClient(ABC):
    """Base class for embedding clients."""
    
    @property
    @abstractmethod
    def dimensions(self) -> int:
        pass
    
    @abstractmethod
    def embed(self, text: str) -> list[float]:
        pass
    
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(t) for t in texts]


class OpenAIEmbeddingClient(BaseEmbeddingClient):
    """OpenAI embedding client."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "text-embedding-3-small"):
        from openai import OpenAI
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = model
        self.client = OpenAI(api_key=self.api_key)
        self._dimensions = 1536
    
    @property
    def dimensions(self) -> int:
        return self._dimensions
    
    def embed(self, text: str) -> list[float]:
        response = self.client.embeddings.create(input=text, model=self.model)
        return response.data[0].embedding
    
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(input=texts, model=self.model)
        return [d.embedding for d in response.data]


class LocalEmbeddingClient(BaseEmbeddingClient):
    """Local embedding client using sentence-transformers (BGE)."""
    
    def __init__(self, model: str = "BAAI/bge-large-en-v1.5"):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model)
        self._dimensions = self.model.get_sentence_embedding_dimension()
    
    @property
    def dimensions(self) -> int:
        return self._dimensions
    
    def embed(self, text: str) -> list[float]:
        return self.model.encode(text).tolist()
    
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts).tolist()


def get_embedding_client(provider: str = "openai", **kwargs) -> BaseEmbeddingClient:
    """Factory function for embedding clients."""
    if provider == "openai":
        return OpenAIEmbeddingClient(**kwargs)
    elif provider == "local":
        return LocalEmbeddingClient(**kwargs)
    else:
        raise ValueError(f"Unknown embedding provider: {provider}")
