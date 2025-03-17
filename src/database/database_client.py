"""
Module for abstract baseclass database/vector store functionalities.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from src.arxiv_agent.models.articles import Article


@dataclass(frozen=True)
class SearchResult:
    """Search result and magic method implementations for list result ordering funtionality."""
    article: Article
    score: float

    def __lt__(self, other: 'SearchResult') -> bool:
        return self.score > other.score

    def __le__(self, other: 'SearchResult') -> bool:
        return self.score >= other.score

    def __gt__(self, other: 'SearchResult') -> bool:
        return self.score < other.score

    def __ge__(self, other: 'SearchResult') -> bool:
        return self.score <= other.score

class DatabaseClient(ABC):
    """Abstract base class for database / vector storage implementations."""

    @abstractmethod
    def get_instance(cls):
        """Get client instance."""
        pass

    @abstractmethod
    def insert(self, article: Article, embedding: List[float]) -> None:
        """Insert an article with its embedding."""
        pass

    @abstractmethod
    def vector_search(self, query_vector: List[float], limit: int = 3) -> List[SearchResult]:
        """Vector search of articles on basis of a vector.

        Args:
            query_vector: A vector, presumably created by embedding a source query.
            limit: How many results to return.

        Returns: A list of search results.
        """
        pass

    @abstractmethod
    def text_search(self, query: str, limit: int = 3) -> List[SearchResult]:
        """Vector search of articles on basis of a query.

        Args:
            query (str): A query to be used in the search.
            limit (int): How many results to return.

        Returns: List of search results.
        """
        pass

    @abstractmethod
    def get_by_id(self, arxiv_id: str) -> Optional[Article]:
        """Retrieve article by arxiv_id."""
        pass

    @abstractmethod
    def scroll(self, limit: int = 10) -> List[Article]:
        """Scroll through articles."""
        pass

    @abstractmethod
    def get_latest_import_date(self) -> datetime:
        """Get UTC datetime object corresponding to the day of the latest publish date in the collection."""
        pass