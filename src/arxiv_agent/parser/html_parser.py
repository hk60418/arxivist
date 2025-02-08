# html_parser.py
from typing import Dict, Any
from bs4 import BeautifulSoup
from .base import ArxivBase, ParserException


class ArxivHTMLParser(ArxivBase):
    """Parser for HTML abstract pages from ArXiv."""

    BASE_HTML_URL = "https://arxiv.org/abs/"

    def extract_text(self, arxiv_id: str) -> Dict[str, Any]:
        """Extract text content from ArXiv's HTML abstract page."""
        url = f"{self.BASE_HTML_URL}{arxiv_id}"

        try:
            response = self._make_request(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            content = {
                'format': 'html',
                'success': False,
                'main_text': '',
                'metadata': {}
            }

            # Get title
            title_tag = soup.find('h1', class_='title')
            if title_tag:
                content['metadata']['title'] = title_tag.text.replace('Title:', '').strip()

            # Get authors
            authors_tag = soup.find('div', class_='authors')
            if authors_tag:
                content['metadata']['authors'] = [
                    auth.strip()
                    for auth in authors_tag.text.replace('Authors:', '').split(',')
                ]

            # Get abstract
            abstract_tag = soup.find('blockquote', class_='abstract')
            if abstract_tag:
                content['main_text'] = abstract_tag.text.replace('Abstract:', '').strip()

            # Get comments
            comments_tag = soup.find('td', class_='tablecell comments')
            if comments_tag:
                content['metadata']['comments'] = comments_tag.text.strip()

            # Get subjects
            subjects_tag = soup.find('td', class_='tablecell subjects')
            if subjects_tag:
                content['metadata']['subjects'] = [
                    subj.strip()
                    for subj in subjects_tag.text.split(';')
                ]

            content['success'] = bool(content['main_text'])
            return content

        except Exception as e:
            raise ParserException(f"Failed to parse HTML: {str(e)}")