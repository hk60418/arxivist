# src/arxiv_parser/models/articles.py
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class Article(BaseModel):
   """
   ArXiv Paper model representing academic papers with their metadata and content.
   This collection stores extracted and processed papers from ArXiv including their
   structure, content and metadata. Used for paper analysis, search, and content extraction.

   Fields:
   - arxiv_id: ArXiv identifier (e.g. "2412.02957v1")
   - title: Full title of the paper
   - authors: List of author names in order of appearance
   - published: UTC timestamp of paper publication on ArXiv
   - abstract: Full abstract text
   - categories: ArXiv categories (e.g. "cs.LG", "cs.AI")
   - format: Original format of the paper (e.g. "tex", "pdf")
   - sections: List of main section headings in the paper
   - main_text: Extracted main text content
   - figures: List of extracted figures (empty in current version)
   - equations: List of extracted equations (empty in current version)
   - bibliography: List of references (empty in current version)
   - processed_at: UTC timestamp of processing the paper in the app

   Indexes:
   - arxiv_id (unique)
   - categories (multikey, not doable with Qdrant?)
   - published (for time-based queries)
   - processed_at (for time-based queries relative to user time)

   Example:
   {
       "arxiv_id": "2412.02957v1",
       "title": "3D Interaction Geometric Pre-training for Molecular Relational Learning",
       "authors": ["Namkyeong Lee", "Yunhak Oh"],
       "published": "2024-12-04T02:05:55Z",
       "abstract": "Molecular Relational Learning (MRL) is a rapidly growing field...",
       "categories": ["cs.LG", "cs.AI"],
       "format": "tex",
       "sections": ["Introduction", "Method", "Results"],
       "main_text": "Molecular Relational Learning (MRL) is...",
       "processed_at": "2024-01-17T10:30:00Z"
   }
   """
   arxiv_id: str
   title: str
   authors: List[str]
   published: datetime
   abstract: str
   categories: List[str]
   format: str
   sections: List[str]
   main_text: str
   figures: Optional[List[str]] = None
   equations: Optional[List[str]] = None
   bibliography: Optional[List[List[str]]] = None
   processed_at: datetime
