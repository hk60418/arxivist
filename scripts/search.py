# Query articles from project database
import sys
from src.arxiv_agent.ml.embedding_model_sentence_transformer import EmbeddingSentenceTransformer as EmbeddingModel
from src.database.database_client_qdrant import DatabaseClientQdrant as Client


def search_papers(query):
    db_client = Client.get_instance()
    embedding_model = EmbeddingModel()
    query_embedding = embedding_model.encode(query)
    return db_client.search(query_embedding, limit=3)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python search.py \"your query here\"")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    results = search_papers(query)

    for i in results:
        print(f"{i.score}, {i.article.title}")
    print()
