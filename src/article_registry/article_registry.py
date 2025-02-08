from pathlib import Path
import os
from src.arxiv_agent.models.articles import Article
from src.config.config_loader import ConfigurationLoader


class ArticleRegistry:
    def __init__(self, root_dir: str | Path = None):
        if not root_dir:
            root_dir = ConfigurationLoader().get_config()['articles']['download_location']
        self.root = Path(root_dir)
        self.by_id_dir = self.root / "by_id"
        self.by_category_dir = self.root / "by_category"

        # Fixed filenames
        self._article_filename = "article.json"

    def get_article_dir(self, arxiv_id: str) -> Path:
        """Get article directory using symlink lookup (fast)"""
        symlink_path = self.by_id_dir / arxiv_id
        if symlink_path.exists():
            return symlink_path.resolve()
        return None

    def create_article_dir(self, article: Article) -> Path:
        """Create article directory structure and symlink based on article's published date"""
        # Extract date components from article's published date
        year = str(article.published.year)
        month = f"{article.published.month:02d}"
        day = f"{article.published.day:02d}"

        # Create directory structure
        article_dir = self.root / year / month / day / article.arxiv_id
        article_dir.mkdir(parents=True, exist_ok=True)

        # Create symlink
        symlink_path = self.by_id_dir / article.arxiv_id
        self.by_id_dir.mkdir(exist_ok=True)

        # Create relative symlink
        if not symlink_path.exists():
            rel_path = os.path.relpath(article_dir, symlink_path.parent)
            symlink_path.symlink_to(rel_path)

        # Create category-based symlinks
        self.by_category_dir.mkdir(exist_ok=True)
        for category in article.categories:
            category_dir = self.by_category_dir / category
            category_dir.mkdir(exist_ok=True)

            category_symlink_path = category_dir / article.arxiv_id
            if not category_symlink_path.exists():
                rel_path = os.path.relpath(article_dir, category_symlink_path.parent)
                category_symlink_path.symlink_to(rel_path)

        return article_dir

    def get_paths(self, arxiv_id: str) -> dict[str, Path]:
        """Get all paths related to an article"""
        article_dir = self.get_article_dir(arxiv_id)
        if not article_dir:
            return None

        return {
            "dir": article_dir,
            "article": article_dir / self._article_filename
        }

    def list_articles(self,
                      year: int = None,
                      month: int = None,
                      day: int = None,
                      category: str = None) -> list[str]:
        """List arxiv IDs under specified directory level"""
        path = self.root

        # Build path based on provided hierarchy
        if year:
            path = path / str(year)
            if month:
                path = path / f"{month:02d}"
                if day:
                    path = path / f"{day:02d}"

        if not path.exists():
            return []

            # Get all arxiv ID directories at this level
        arxiv_ids = set()
        for root, dirs, _ in os.walk(path):
            # Only include directories that look like arxiv IDs
            arxiv_dirs = [d for d in dirs if self._is_arxiv_id(d)]
            arxiv_ids.update(arxiv_dirs)

        # If category filter is specified, intersect with category-specific articles
        if category:
            category_path = self.by_category_dir / category
            if not category_path.exists():
                return []

            category_ids = set(path.name for path in category_path.iterdir()
                               if path.is_symlink() and self._is_arxiv_id(path.name))
            arxiv_ids = arxiv_ids.intersection(category_ids)

        return list(arxiv_ids)

    @staticmethod
    def _is_arxiv_id(dirname: str) -> bool:
        """Basic check if directory name looks like an arxiv ID"""
        # This is a very basic check against possible year/month/day dirnames while being suspicious about if the
        # definition in https://info.arxiv.org/help/arxiv_identifier.html#new holds true
        return len(dirname) > 4 and any(c.isdigit() for c in dirname)


# Example usage:
if __name__ == "__main__":
    from datetime import datetime, timezone

    # Create sample Article instance
    article = Article(
        arxiv_id="2402.12345",
        title="Sample Paper",
        authors=["Author One", "Author Two"],
        published=datetime(2024, 2, 8, tzinfo=timezone.utc),
        abstract="Sample abstract",
        categories=["cs.AI"],
        format="pdf",
        sections=["Introduction"],
        main_text="Sample text",
        processed_at=datetime.now(timezone.utc)
    )

    registry = ArticleRegistry("/path/to/root")

    # Create directory for new paper using Article model
    articles_dir = registry.create_article_dir(article)

    # Get all paths for the paper
    paths = registry.get_paths(article.arxiv_id)
    if paths:
        print(f"Article PDF path: {paths['article']}")
        print(f"Embedding path: {paths['embedding']}")