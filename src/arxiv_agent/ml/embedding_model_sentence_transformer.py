from typing import List
import warnings
from sentence_transformers import SentenceTransformer
from src.arxiv_agent.ml.embedding_model_base import EmbeddingModel


class EmbeddingSentenceTransformer(EmbeddingModel):
    """Implementation of EmbeddingModel using SentenceTransformers."""

    def __init__(self, model_name: str = "malteos/scincl"):
        """
        Initialize the model.

        Args:
            model_name: Name of the SentenceTransformer model to use
        """
        self.model = SentenceTransformer(model_name)

    def encode(self, text: str) -> List[float]:
        """See parent class."""
        if not isinstance(text, str):
            warnings.warn(
                "encode() was called with a list of texts or some other input. For multiple texts, use "
                "encode_batch() instead.",
                UserWarning,
                stacklevel=2
            )
            raise TypeError("encode() expects singular str input!")

        text = [text]

        embeddings = self.model.encode(text)

        # Convert numpy arrays to lists
        embeddings = [emb.tolist() for emb in embeddings]

        return embeddings[0]

    def encode_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """See parent class."""
        all_embeddings = []

        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            embeddings = self.model.encode(batch)
            all_embeddings.extend([emb.tolist() for emb in embeddings])

        return all_embeddings