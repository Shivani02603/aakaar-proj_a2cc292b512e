import os
from typing import List
import openai

class EmbeddingClient:
    """Client for OpenAI text-embedding-3-small model."""
    def __init__(self):
        # Lazy initialization - key read when needed
        self._api_key = None
        self._client = None
        self.model = "text-embedding-3-small"
        self.dimension = 1536  # From spec

    def _ensure_client(self):
        if self._client is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            self._api_key = api_key
            self._client = openai.OpenAI(api_key=api_key)

    def embed_text(self, text: str) -> List[float]:
        """Embed a single text string."""
        self._ensure_client()
        response = self._client.embeddings.create(
            model=self.model,
            input=text,
            encoding_format="float"
        )
        return response.data[0].embedding

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed a batch of text strings."""
        self._ensure_client()
        response = self._client.embeddings.create(
            model=self.model,
            input=texts,
            encoding_format="float"
        )
        # Sort by index to maintain order
        sorted_data = sorted(response.data, key=lambda x: x.index)
        return [item.embedding for item in sorted_data]


def get_embedding(texts: List[str]) -> List[List[float]]:
    """Module-level function to get embeddings for a list of texts.
    
    Args:
        texts: List of text strings to embed
        
    Returns:
        List of embedding vectors (each vector is List[float])
    """
    client = EmbeddingClient()
    return client.embed_batch(texts)