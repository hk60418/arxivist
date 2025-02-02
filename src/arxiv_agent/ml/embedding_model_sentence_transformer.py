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
        """
        Encode a single text using SentenceTransformer. Will warn if attempting to encode multiple texts.
        For multiple texts, use encode_batch() instead.

        Args:
            text: Single text string to encode.

        Returns:
            For single text: List[float] representing the embedding
        """
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
        """
        Encode a large batch of texts efficiently.

        Args:
            texts: List of text strings to encode
            batch_size: Size of batches to process at once

        Returns:
            List of embedding vectors
        """
        all_embeddings = []

        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            embeddings = self.model.encode(batch)
            all_embeddings.extend([emb.tolist() for emb in embeddings])

        return all_embeddings