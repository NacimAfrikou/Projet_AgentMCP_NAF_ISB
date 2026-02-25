"""Tests pour les parseurs de documents."""

import pytest
from pathlib import Path

# Tests simulés car nous n'avons pas de fichiers réels
class TestBaseParser:
    """Tests pour le parser de base."""

    def test_parser_init(self):
        """Test l'initialisation du parser."""
        from src.parsers.base_parser import BaseParser

        class DummyParser(BaseParser):
            def parse(self):
                return []
            def extract_text(self):
                return ""

        parser = DummyParser("test.txt")
        assert parser.file_path == Path("test.txt")


class TestDocxParser:
    """Tests pour le parser DOCX."""

    def test_docx_parser_init(self):
        """Test l'initialisation du parser DOCX."""
        from src.parsers.docx_parser import DocxParser
        parser = DocxParser("test.docx")
        assert parser.file_path == Path("test.docx")


class TestPdfParser:
    """Tests pour le parser PDF."""

    def test_pdf_parser_init(self):
        """Test l'initialisation du parser PDF."""
        from src.parsers.pdf_parser import PdfParser
        parser = PdfParser("test.pdf")
        assert parser.file_path == Path("test.pdf")


class TestTextParser:
    """Tests pour le parser de texte."""

    def test_text_parser_init(self):
        """Test l'initialisation du parser de texte."""
        from src.parsers.text_parser import TextParser
        parser = TextParser("test.txt")
        assert parser.file_path == Path("test.txt")

    def test_text_parser_markdown(self):
        """Test le parsing de markdown."""
        from src.parsers.text_parser import TextParser
        parser = TextParser("test.md", parse_markdown=True)
        assert parser.parse_markdown is True
