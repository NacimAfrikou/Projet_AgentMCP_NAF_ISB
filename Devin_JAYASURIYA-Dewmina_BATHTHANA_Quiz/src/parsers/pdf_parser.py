"""Parseur pour les documents PDF."""

from pathlib import Path
from typing import List, Dict, Any
import PyPDF2

from .base_parser import BaseParser


class PdfParser(BaseParser):
    """Parseur pour les documents PDF."""

    def parse(self) -> List[Dict[str, Any]]:
        """Parse le PDF et retourne une liste de sections."""
        if not self.validate():
            raise FileNotFoundError(f"Le fichier {self.file_path} n'existe pas.")

        pages_content = []

        with open(self.file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(reader.pages, 1):
                text = page.extract_text() or ""
                pages_content.append({
                    "page": page_num,
                    "content": text,
                    "text": text
                })

        return pages_content

    def extract_text(self) -> str:
        """Extract tout le texte du document."""
        if not self.validate():
            raise FileNotFoundError(f"Le fichier {self.file_path} n'existe pas.")

        text = []

        with open(self.file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text() or ""
                text.append(page_text)

        return "\n".join(text)
