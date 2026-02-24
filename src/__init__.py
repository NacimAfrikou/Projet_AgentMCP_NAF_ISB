"""
Extracteur de Données Structurées
Ce package fournit des outils pour transformer des documents non structurés en données JSON.
"""

from src.validator import InvoiceModel, FormModel, DocumentModel
from src.recognizer import recognize_document
from src.exporter import export_to_json

__version__ = "0.1.0"
__all__ = [
    "InvoiceModel",
    "FormModel",
    "DocumentModel",
    "recognize_document",
    "export_to_json",
]
