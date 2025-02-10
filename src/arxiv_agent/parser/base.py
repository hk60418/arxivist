# base.py
from abc import ABC, abstractmethod
import requests
import xml.etree.ElementTree as ET
import time
import logging
from datetime import datetime
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ArxivBase(ABC):
    """Base class for ArXiv parsers with common functionality."""

    BASE_API_URL = "http://export.arxiv.org/api/query?"
    REQUEST_DELAY = 3  # ArXiv's rate limiting guidelines

    def __init__(self):
        self.last_request_time = 0

    def _respect_rate_limit(self):
        """Ensure we respect ArXiv's rate limiting guidelines."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.REQUEST_DELAY:
            time.sleep(self.REQUEST_DELAY - time_since_last_request)
        self.last_request_time = time.time()

    def _make_request(self, url: str) -> requests.Response:
        """Make a rate-limited request."""
        self._respect_rate_limit()
        response = requests.get(url)
        response.raise_for_status()
        return response

    def list_daily_papers(self, date: datetime, category: str) -> List[Dict[str, Any]]:
        """List all papers published on a specific date in a given category.

        Args:
            date (datetime): The date to search for papers
            category (str): The ArXiv category to search in

        Returns:
            List[Dict[str, Any]]: List of paper information dictionaries

        Raises:
            requests.exceptions.RequestException: If there's an error with the API request
            xml.etree.ElementTree.ParseError: If the response XML cannot be parsed
        """
        RESULTS_PER_REQUEST = 1000  # ArXiv's maximum allowed results per request
        date_str = date.strftime('%Y%m%d')
        base_query = f'cat:{category} AND submittedDate:[{date_str}0000 TO {date_str}2359]'

        start = 0
        all_papers = []
        total_results = None

        while True:
            query_params = {
                'search_query': base_query,
                'max_results': RESULTS_PER_REQUEST,
                'start': start,
                'sortBy': 'submittedDate',
                'sortOrder': 'ascending'
            }

            url = self.BASE_API_URL + "&".join(f"{k}={v}" for k, v in query_params.items())
            response = self._make_request(url)

            root = ET.fromstring(response.content)
            ns = {'atom': 'http://www.w3.org/2005/Atom',
                  'opensearch': 'http://a9.com/-/spec/opensearch/1.1/'}

            # Get total results count from opensearch namespace
            if total_results is None:
                total_results_elem = root.find('opensearch:totalResults', ns)
                total_results = int(total_results_elem.text) if total_results_elem is not None else 0
                logger.info(f"Total papers found for {date_str} in category {category}: {total_results}")

            # Parse entries
            for entry in root.findall('atom:entry', ns):
                paper_info = {
                    'arxiv_id': entry.find('atom:id', ns).text.split('/')[-1],
                    'title': entry.find('atom:title', ns).text.strip(),
                    'authors': [author.find('atom:name', ns).text for author in entry.findall('atom:author', ns)],
                    'published': entry.find('atom:published', ns).text,
                    'abstract': entry.find('atom:summary', ns).text.strip(),
                    'categories': [cat.get('term') for cat in entry.findall('atom:category', ns)]
                }
                all_papers.append(paper_info)

            # Check if we've got all results
            if len(all_papers) >= total_results:
                break

            start += RESULTS_PER_REQUEST
            logger.info(f"Fetched {len(all_papers)} papers so far, continuing pagination...")

        logger.info(f"Successfully retrieved {len(all_papers)} papers")
        return all_papers

    @abstractmethod
    def extract_text(self, arxiv_id: str) -> Dict[str, Any]:
        """Extract text content from paper source. Must be implemented by subclasses."""
        pass


class ParserException(Exception):
    """Custom exception for parser-related errors."""
    pass