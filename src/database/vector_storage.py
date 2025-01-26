from abc import ABC, abstractmethod
from typing import List, Optional
from src.arxiv_agent.models.articles import Article


class VectorStore(ABC):
    """Abstract base class for vector storage implementations."""

    @abstractmethod
    def insert(self, article: Article, embedding: List[float]) -> None:
        """Insert an article with its embedding."""
        pass

    @abstractmethod
    def search(self, query_vector: List[float], limit: int = 10) -> List[Article]:
        """Search articles by vector similarity."""
        pass

    @abstractmethod
    def get_by_id(self, arxiv_id: str) -> Optional[Article]:
        """Retrieve article by arxiv_id."""
        pass

    @abstractmethod
    def scroll(self, limit: int = 10) -> List[Article]:
        """Scroll through articles."""
        pass