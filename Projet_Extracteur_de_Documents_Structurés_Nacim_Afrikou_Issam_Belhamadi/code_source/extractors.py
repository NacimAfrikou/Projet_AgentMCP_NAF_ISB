"""Pipeline d'extraction de données depuis des fichiers via LLM multimodal."""

import base64
from pathlib import Path
from typing import Optional

from .llm_client import (
    detect_document_type_from_file,
    extract_invoice_from_file,
    extract_order_from_file,
)
from .models import ExtractedDocument, Invoice, Order


def _encode_file_to_base64(path: Path) -> str:
    """Encode un fichier en base64 pour l'envoyer au LLM."""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _get_mime_type(path: Path) -> str:
    """Détermine le type MIME du fichier basé sur son extension."""
    suffix = path.suffix.lower()
    mime_types = {
        ".pdf": "application/pdf",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    return mime_types.get(suffix, "application/octet-stream")


def extract_document(path: Path) -> ExtractedDocument:
    """Point d'entrée : détecte le type puis extrait via LLM multimodal.

    1. Encode le fichier en base64 (PDF, images...)
    2. Envoie au LLM multimodal (GPT-4 Vision) pour détection du type
    3. Extrait les champs avec le schéma Pydantic correspondant
    4. Retourne un objet Order ou Invoice validé automatiquement
    """
    # Encoder le fichier en base64
    base64_data = _encode_file_to_base64(path)
    mime_type = _get_mime_type(path)

    # Détecter le type de document via LLM vision
    doc_type = detect_document_type_from_file(base64_data, mime_type)

    # Extraire les données structurées selon le type
    if doc_type == "invoice":
        invoice: Invoice = extract_invoice_from_file(base64_data, mime_type, Invoice)
        invoice.source_file = str(path)
        return invoice

    order: Order = extract_order_from_file(base64_data, mime_type, Order)
    order.source_file = str(path)
    return order

