import uuid
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, VectorParams, PayloadSchemaType, PointStruct
from src.arxiv_agent.models.articles import Article
from src.database.database_client import DatabaseClient, SearchResult
from src.config.config_loader import ConfigurationLoader
from typing import List, Union, Sequence


class DatabaseClientQdrant(DatabaseClient):
    _instance = None
    _client: QdrantClient = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if self._client is None:
            conf = ConfigurationLoader().get_config()
            self.conf = conf
            self._client = QdrantClient(url=conf['database']['url'])
            self._ensure_collection()

    def _ensure_collection(self):
        if not self._client.collection_exists(self.conf['database']['collection']):
            print("Creating collection and indexes ...")

            self._client.create_collection(
                collection_name=self.conf['database']['collection'],
                vectors_config=VectorParams(
                    size=self.conf['database']['embedding_dimensions'],
                    distance=Distance.DOT
                )
            )

            # Create payload indexes
            for field, schema_type in [
                ("arxiv_id", PayloadSchemaType.TEXT),
                ("published", PayloadSchemaType.DATETIME),
                ("processed_at", PayloadSchemaType.DATETIME)
            ]:
                self._client.create_payload_index(
                    collection_name=self.conf['database']['collection'],
                    field_name=field,
                    field_schema=schema_type,
                )

    @staticmethod
    def _generate_point_id(arxiv_id: str) -> int:
        """Generate deterministic point ID from arxiv_id."""
        # Remove version from arxiv_id if present (e.g., '2501.09239v1' -> '2501.09239')
        base_id = arxiv_id.split('v')[0]

        # Convert the string to a number using a consistent method
        # Remove any dots and convert to integer
        numeric_id = int(base_id.replace('.', ''))

        # Ensure it's within int64 range for Qdrant
        return numeric_id % (2 ** 63)

    def insert(
            self,
            articles: Union[Article, Sequence[Article]],
            embeddings: Union[List[float], Sequence[List[float]]]
    ) -> None:
        """
        Insert one or more articles with their embeddings into Qdrant.

        Args:
            articles: Single Article or sequence of Articles
            embeddings: Single embedding vector or sequence of embedding vectors

        Raises:
            ValueError: If lengths of articles and embeddings don't match or if embeddings are empty
        """
        # Convert single inputs to lists
        if isinstance(articles, Article):
            articles = [articles]
            embeddings = [embeddings]

        if len(articles) != len(embeddings):
            raise ValueError(
                f"Number of articles ({len(articles)}) must match number of embeddings ({len(embeddings)})")

        if not articles:
            return

        points = [
            PointStruct(
                id=self._generate_point_id(article.arxiv_id),
                vector=embedding,
                payload=article.model_dump(mode='json')
            )
            for article, embedding in zip(articles, embeddings)
        ]

        self._client.upsert(
            collection_name=self.conf['database']['collection'],
            wait=True,
            points=points
        )

    def search(self, query_vector: List[float], limit: int = 10) -> List[SearchResult]:
        results = self._client.query_points(
            collection_name=self.conf['database']['collection'],
            query=query_vector,
            limit=limit,
            with_payload=True
        ).points

        return [SearchResult(article=Article(**hit.payload), score=hit.score) for hit in results]

    def get_by_id(self, arxiv_id: str) -> Article:
        results = self._client.scroll(
            collection_name=self.conf['database']['collection'],
            scroll_filter=models.Filter(
                must=[models.FieldCondition(key='arxiv_id', match=models.MatchValue(value=arxiv_id))]
            ),
            limit=1,
            with_payload=True
        )[0]

        return Article(**results[0].payload) if results else None

    def scroll(self, limit: int = 10) -> List[Article]:
        results = self._client.scroll(
            collection_name=self.conf['database']['collection'],
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )[0]

        return [Article(**point.payload) for point in results]

    def delete_collection(self) -> None:
        """Delete the current collection if it exists."""
        if self._client.collection_exists(self.conf['database']['collection']):
            self._client.delete_collection(
                collection_name=self.conf['database']['collection']
            )
            print(f"Collection {self.conf['database']['collection']} deleted.")
        else:
            print(f"Collection {self.conf['database']['collection']} does not exist.")
