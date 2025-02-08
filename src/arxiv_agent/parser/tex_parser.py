# tex_parser.py
import re
import io
import tarfile
from typing import Dict, Any
from .base import ArxivBase, ParserException


class ArxivTexParser(ArxivBase):
    """Parser for TeX source files from ArXiv."""

    BASE_TEX_URL = "https://arxiv.org/e-print/"

    def extract_text(self, arxiv_id: str) -> Dict[str, Any]:
        """Download and extract text content from TeX source files."""
        url = f"{self.BASE_TEX_URL}{arxiv_id}"

        try:
            response = self._make_request(url)
            tar = tarfile.open(fileobj=io.BytesIO(response.content), mode="r:*")

            content = {
                'format': 'tex',
                'sections': [],
                'figures': [],
                'equations': [],
                'bibliography': [],
                'main_text': '',
                'success': False
            }

            # Find main tex file
            main_tex = None
            for member in tar.getmembers():
                if member.name.endswith('.tex'):
                    f = tar.extractfile(member)
                    if f:
                        tex_content = f.read().decode('utf-8', errors='ignore')
                        if '\\documentclass' in tex_content:
                            main_tex = tex_content
                            break

            if not main_tex:
                raise ParserException("No main TeX file found")

            # Extract sections
            content['sections'] = re.findall(
                r'\\(?:section|subsection|subsubsection)\{([^}]+)\}',
                main_tex
            )

            # Extract figures
            content['figures'] = re.findall(
                r'\\caption\{([^}]+)\}',
                main_tex
            )

            # Extract equations
            content['equations'] = re.findall(
                r'\\begin\{equation\*?\}(.*?)\\end\{equation\*?\}',
                main_tex,
                re.DOTALL
            )

            # Extract bibliography
            content['bibliography'] = re.findall(
                r'\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}(.*?)(?=\\bibitem|\n\n|$)',
                main_tex,
                re.DOTALL
            )

            # Clean and extract main text
            content['main_text'] = self._clean_tex(main_tex)
            content['success'] = True

            tar.close()
            return content

        except Exception as e:
            raise ParserException(f"Failed to parse TeX: {str(e)}")

    def _clean_tex(self, text: str) -> str:
        """Clean TeX commands and formatting from text."""
        # Remove comments
        text = re.sub(r'%.*$', '', text, flags=re.MULTILINE)

        # Remove common LaTeX commands
        text = re.sub(r'\\[a-zA-Z]+(?:\[.*?\])?(?:\{.*?\})?', '', text)

        # Remove math environments
        text = re.sub(r'\\begin\{equation\*?\}.*?\\end\{equation\*?\}', '', text, flags=re.DOTALL)
        text = re.sub(r'\$\$.*?\$\$', '', text, flags=re.DOTALL)
        text = re.sub(r'\$.*?\$', '', text)

        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()