import pytest
from datetime import datetime, timezone
from pathlib import Path
import os
from src.article_registry import ArticleRegistry
from src.arxiv_agent.models.articles import Article


@pytest.fixture
def sample_article():
    return Article(
        arxiv_id="2402.12345",
        title="Sample Paper",
        authors=["Author One", "Author Two"],
        published=datetime(2024, 2, 8, tzinfo=timezone.utc),
        abstract="Sample abstract",
        categories=["cs.AI", "cs.LG"],
        format="pdf",
        sections=["Introduction"],
        main_text="Sample text",
        processed_at=datetime.now(timezone.utc)
    )


@pytest.fixture
def registry(tmp_path):
    return ArticleRegistry(tmp_path)


def test_init(tmp_path):
    registry = ArticleRegistry(tmp_path)
    assert registry.root == tmp_path
    assert registry.by_id_dir == tmp_path / "by_id"
    assert registry.by_category_dir == tmp_path / "by_category"


def test_get_article_dir_nonexistent(registry):
    assert registry.get_article_dir("nonexistent") is None


def test_create_and_get_article_dir(registry, sample_article):
    # Create directory structure
    article_dir = registry.create_article_dir(sample_article)

    # Test main directory creation
    assert article_dir.exists()
    assert article_dir.is_dir()

    # Test directory structure matches published date
    expected_path = registry.root / "2024" / "02" / "08" / sample_article.arxiv_id
    assert article_dir == expected_path

    # Test by_id symlink
    id_symlink = registry.by_id_dir / sample_article.arxiv_id
    assert id_symlink.exists()
    assert id_symlink.is_symlink()
    assert id_symlink.resolve() == article_dir

    # Test category symlinks
    for category in sample_article.categories:
        category_symlink = registry.by_category_dir / category / sample_article.arxiv_id
        assert category_symlink.exists()
        assert category_symlink.is_symlink()
        assert category_symlink.resolve() == article_dir

    # Test get_article_dir retrieval
    retrieved_dir = registry.get_article_dir(sample_article.arxiv_id)
    assert retrieved_dir == article_dir


def test_get_paths(registry, sample_article):
    article_dir = registry.create_article_dir(sample_article)
    paths = registry.get_paths(sample_article.arxiv_id)

    assert paths["dir"] == article_dir
    assert paths["article"] == article_dir / "article.json"

    assert len(paths.keys()) == 2


def test_get_paths_nonexistent(registry):
    assert registry.get_paths("nonexistent") is None


@pytest.fixture
def populated_registry(registry):
    articles = [
        Article(
            arxiv_id=f"2402.{i:05d}",
            title=f"Paper {i}",
            authors=["Author"],
            published=datetime(2024, 2, i % 28 + 1, tzinfo=timezone.utc),
            abstract="Abstract",
            categories=["cs.AI"] + (["cs.LG"] if i % 2 == 0 else []),
            format="pdf",
            sections=["Introduction"],
            main_text="Text",
            processed_at=datetime.now(timezone.utc)
        ) for i in range(1, 6)
    ]

    for article in articles:
        registry.create_article_dir(article)

    return registry, articles


def test_list_articles_all(populated_registry):
    registry, articles = populated_registry
    arxiv_ids = registry.list_articles()
    assert len(arxiv_ids) == 5
    assert all(article.arxiv_id in arxiv_ids for article in articles)


def test_list_articles_by_date(populated_registry):
    registry, articles = populated_registry

    # Test by year
    assert len(registry.list_articles(year=2024)) == 5
    assert len(registry.list_articles(year=2023)) == 0

    # Test by year and month
    assert len(registry.list_articles(year=2024, month=2)) == 5
    assert len(registry.list_articles(year=2024, month=1)) == 0

    # Test by specific date
    day_1_articles = registry.list_articles(year=2024, month=2, day=2)
    assert len(day_1_articles) == 1
    assert any(article.arxiv_id in day_1_articles for article in articles)


def test_list_articles_by_category(populated_registry):
    registry, articles = populated_registry

    # Test cs.AI category (all articles)
    cs_ai_articles = registry.list_articles(category="cs.AI")
    assert len(cs_ai_articles) == 5

    # Test cs.LG category (every other article)
    cs_lg_articles = registry.list_articles(category="cs.LG")
    assert len(cs_lg_articles) == 2

    # Test nonexistent category
    assert len(registry.list_articles(category="nonexistent")) == 0


def test_list_articles_by_date_and_category(populated_registry):
    registry, _ = populated_registry

    # Test specific date with existing category
    articles = registry.list_articles(year=2024, month=2, day=2, category="cs.AI")
    assert len(articles) == 1

    # Test specific date with NO category
    articles = registry.list_articles(year=2024, month=2, day=2, category="cs.LG")
    assert len(articles) == 0

    # Test specific date with NO category
    articles = registry.list_articles(year=2024, month=2, day=2, category="cs.FE")
    assert len(articles) == 0

def test_is_arxiv_id():
    assert ArticleRegistry._is_arxiv_id("2402.12345")
    assert ArticleRegistry._is_arxiv_id("1234.56789")
    assert not ArticleRegistry._is_arxiv_id("2024")
    assert not ArticleRegistry._is_arxiv_id("02")
    assert not ArticleRegistry._is_arxiv_id("08")