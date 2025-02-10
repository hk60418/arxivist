# parser.py
import os
import json
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional
import logging
from .base import ArxivBase, ParserException
from .tex_parser import ArxivTexParser
from .pdf_parser import ArxivPDFParser
from .html_parser import ArxivHTMLParser

logger = logging.getLogger(__name__)


class ArxivParser:
    """Main interface for ArXiv paper parsing."""

    def __init__(self):
        self.tex_parser = ArxivTexParser()
        self.pdf_parser = ArxivPDFParser()
        self.html_parser = ArxivHTMLParser()

    def extract_paper_text(self, arxiv_id: str) -> Dict[str, Any]:
        """
        Try to extract paper text using parsers in order: TeX -> PDF -> HTML.
        Returns the first successful result.
        """
        result = None
        errors = []

        # Try TeX parser first
        try:
            result = self.tex_parser.extract_text(arxiv_id)
            if result['success']:
                logger.info(f"Successfully extracted TeX for {arxiv_id}")
                return result
        except ParserException as e:
            errors.append(f"TeX parsing failed: {str(e)}")

        # Try PDF parser next
        try:
            result = self.pdf_parser.extract_text(arxiv_id)
            if result['success']:
                logger.info(f"Successfully extracted PDF for {arxiv_id}")
                return result
        except ParserException as e:
            errors.append(f"PDF parsing failed: {str(e)}")

        # Finally, try HTML
        try:
            result = self.html_parser.extract_text(arxiv_id)
            if result['success']:
                logger.info(f"Successfully extracted HTML for {arxiv_id}")
                return result
        except ParserException as e:
            errors.append(f"HTML parsing failed: {str(e)}")

        # If all parsers fail, raise exception with all errors
        if not result or not result['success']:
            raise ParserException(f"All parsers failed for {arxiv_id}: {'; '.join(errors)}")

        return result

    def get_daily_papers(self, date: datetime, category: str) -> list:
        """Get list of papers published on a specific date."""
        return self.tex_parser.list_daily_papers(date, category)

    def save_papers(self, papers: list, output_dir: str) -> None:
        """Save extracted paper content to JSON files."""
        for paper in papers:
            try:
                # Extract text using available parsers
                content = self.extract_paper_text(paper['arxiv_id'])

                # Merge API metadata with extracted content
                paper_data = {**paper, **content}

                # Store processed_at
                paper_data['processed_at'] = datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
                paper_data['published'] = paper_data['published'].isoformat(timespec='seconds').replace('+00:00', 'Z')

                filename = "article.json"
                output_path = os.path.join(output_dir, filename)

                # Save as JSON
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(paper_data, f, ensure_ascii=False, indent=2)
                logger.info(f"Successfully saved: {filename}")

            except Exception as e:
                traceback.print_exc()
                logger.error(f"Error processing {paper['title']}: {str(e)}")

def main():
    """Example usage of the ArxivParser."""
    parser = ArxivParser()

    # Get today's AI papers
    today = datetime.now()
    category = 'cs.AI'
    output_dir = Path('arxiv_papers') / today.strftime('%Y-%m-%d') / category

    try:
        # Get paper list
        papers = parser.get_daily_papers(today, category)
        logger.info(f"Found {len(papers)} papers in {category} for {today.strftime('%Y-%m-%d')}")

        # Download and save papers
        parser.save_papers(papers, str(output_dir))

    except Exception as e:
        logger.error(f"Error during execution: {str(e)}")


if __name__ == "__main__":
    main()