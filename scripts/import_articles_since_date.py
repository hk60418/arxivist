# Script to process papers published since given date
import json
import os.path
import sys
from datetime import datetime, timedelta, timezone
from src.article_registry import ArticleRegistry
from src.config.config_loader import ConfigurationLoader
from src.arxiv_agent.ml.embedding_model_sentence_transformer import EmbeddingSentenceTransformer as EmbeddingModel
from src.arxiv_agent.models.articles import Article
from src.arxiv_agent.parser.parser import ArxivParser
from src.database.database_client_qdrant import DatabaseClientQdrant as DatabaseClient


def import_articles_since_date(date_and_time: datetime = None):
    conf = ConfigurationLoader().get_config()
    parser = ArxivParser()
    article_registry = ArticleRegistry()
    model = EmbeddingModel()
    db_client = DatabaseClient.get_instance()
    while date_and_time < datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0):
        print(f"Processing {str(date_and_time)} ...")
        article_dicts = []
        try:
            for category in conf['articles']['categories']:
                print(f"Processing {category} ...")
                article_dicts.extend(parser.get_daily_papers(date_and_time, category))

            # Clean up duplicates from overlapping categories
            ids = set()
            cleaned = []
            for article_dict in article_dicts:
                if article_dict['arxiv_id'] not in ids:
                    ids.add(article_dict['arxiv_id'])
                    cleaned.append(article_dict)
            article_dicts = cleaned

            for article_dict in article_dicts:
                try:
                    pass
                    article_directory = article_registry.create_article_dir_from_dict(article_dict)
                    parser.save_papers([article_dict], str(article_directory))
                    with open(os.path.join(article_directory, 'article.json')) as f:
                        data = json.load(f)
                    article = Article(**data)
                    embedding = model.encode(article.abstract)
                    result = db_client.insert([article], [embedding])
                    print(f"Inserted paper {article_dict['arxiv_id']} with op_info: {result}")
                except Exception as e:
                    print(f"Failed to process {article_dict['arxiv_id']}. Exception: {str(e)}")
                    continue

            date_and_time = date_and_time + timedelta(days=1)
        except Exception as e:
            print(f"Failed process batch {str(date_and_time)}. Exception: {str(e)}")
            date_and_time = date_and_time + timedelta(days=1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python import_articles_from_date.py YYYY-MM-DD")
        sys.exit(1)
    try:
        start = datetime.strptime(sys.argv[1], "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD.")
        sys.exit(1)
    import_articles_since_date(start)
