# pdf_parser.py
import io
from typing import Dict, Any
import pdfminer
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
from .base import ArxivBase, ParserException


class ArxivPDFParser(ArxivBase):
    """Parser for PDF files from ArXiv."""

    BASE_PDF_URL = "https://arxiv.org/pdf/"

    def extract_text(self, arxiv_id: str) -> Dict[str, Any]:
        """Download and extract text content from PDF."""
        url = f"{self.BASE_PDF_URL}{arxiv_id}.pdf"

        try:
            response = self._make_request(url)

            # Set up PDF parsing parameters
            laparams = LAParams(
                line_margin=0.5,
                word_margin=0.1,
                char_margin=2.0,
                boxes_flow=0.5,
                detect_vertical=True
            )

            # Extract text from PDF
            output_string = io.StringIO()
            with io.BytesIO(response.content) as pdf_file:
                extract_text_to_fp(pdf_file, output_string, laparams=laparams)

            text = output_string.getvalue()

            # Basic structure detection
            lines = text.split('\n')
            content = {
                'format': 'pdf',
                'main_text': text,
                'sections': [],
                'success': True
            }

            # Try to identify section headers (basic heuristic)
            for i, line in enumerate(lines):
                line = line.strip()
                if (line.isupper() or
                        line.startswith(('1.', '2.', '3.', '4.', '5.')) or
                        line.lower().startswith(('introduction', 'background', 'method',
                                                 'conclusion', 'discussion', 'results'))):
                    content['sections'].append(line)

            return content

        except Exception as e:
            raise ParserException(f"Failed to parse PDF: {str(e)}")