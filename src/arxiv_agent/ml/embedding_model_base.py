from abc import ABC, abstractmethod
from typing import List, Union


class EmbeddingModel(ABC):
    """Abstract base class for embedding models."""

    @abstractmethod
    def encode(self, texts: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """
        Encode text into embeddings.

        Args:
            texts: Single text string or list of text strings to encode

        Returns:
            List of embeddings. For single text input, returns single embedding vector.
            For list input, returns list of embedding vectors.
        """
        pass

    @abstractmethod
    def encode_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Encode a large batch of texts efficiently.

        Args:
            texts: List of text strings to encode
            batch_size: Size of batches to process at once

        Returns:
            List of embedding vectors
        """
        pass
