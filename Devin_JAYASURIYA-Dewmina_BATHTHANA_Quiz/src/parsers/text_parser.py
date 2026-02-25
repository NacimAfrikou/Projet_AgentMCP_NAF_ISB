"""Parseur pour les fichiers texte et markdown."""

from pathlib import Path
from typing import List, Dict, Any

from .base_parser import BaseParser


class TextParser(BaseParser):
    """Parseur pour les fichiers texte et markdown."""

    def __init__(self, file_path: str | Path, parse_markdown: bool = True):
        super().__init__(file_path)
        self.parse_markdown = parse_markdown

    def parse(self) -> List[Dict[str, Any]]:
        """Parse le texte et retourne une liste de sections."""
        if not self.validate():
            raise FileNotFoundError(f"Le fichier {self.file_path} n'existe pas.")

        content = self.file_path.read_text(encoding='utf-8')
        sections = []

        if self.parse_markdown:
            # Parser le markdown en sections
            current_section = None
            for line in content.split('\n'):
                if line.startswith('# '):
                    if current_section:
                        sections.append(current_section)
                    current_section = {
                        "title": line[2:].strip(),
                        "level": 1,
                        "content": "",
                        "text": line[2:].strip()
                    }
                elif line.startswith('## '):
                    if current_section:
                        sections.append(current_section)
                    current_section = {
                        "title": line[3:].strip(),
                        "level": 2,
                        "content": "",
                        "text": line[3:].strip()
                    }
                elif line.startswith('### '):
                    if current_section:
                        sections.append(current_section)
                    current_section = {
                        "title": line[4:].strip(),
                        "level": 3,
                        "content": "",
                        "text": line[4:].strip()
                    }
                else:
                    if current_section:
                        current_section["content"] += line + "\n"
                        current_section["text"] += line + "\n"
                    else:
                        sections.append({
                            "title": "Texte",
                            "level": 1,
                            "content": line + "\n",
                            "text": line + "\n"
                        })
        else:
            # Fichier texte simple
            sections.append({
                "title": "Contenu",
                "level": 1,
                "content": content,
                "text": content
            })

        return sections

    def extract_text(self) -> str:
        """Extract tout le texte du document."""
        if not self.validate():
            raise FileNotFoundError(f"Le fichier {self.file_path} n'existe pas.")

        return self.file_path.read_text(encoding='utf-8')
