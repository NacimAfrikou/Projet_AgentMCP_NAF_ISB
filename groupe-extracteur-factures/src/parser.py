import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import pdfplumber

from .models import Invoice


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Lit un fichier PDF et renvoie tout le texte concaténé.

    Hypothèse : les factures sont des PDF « texte » (pas besoin d'OCR).
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF introuvable : {pdf_path}")

    pages_text: list[str] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            pages_text.append(text)

    return "\n".join(pages_text)


def _normalize_amount(raw: Optional[str]) -> Optional[float]:
    if not raw:
        return None
    # Supprime les espaces (y compris insécables) et remplace les virgules par des points
    cleaned = raw.replace("\xa0", " ").replace(" ", "").replace(",", ".")
    match = re.search(r"[-+]?\d*\.?\d+(?:e[-+]?\d+)?", cleaned)
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def _normalize_date(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None

    raw = raw.strip()
    patterns = [
        ("%d/%m/%Y", r"\d{1,2}/\d{1,2}/\d{4}"),
        ("%d-%m-%Y", r"\d{1,2}-\d{1,2}-\d{4}"),
        ("%Y-%m-%d", r"\d{4}-\d{2}-\d{2}"),
        ("%d/%m/%y", r"\d{1,2}/\d{1,2}/\d{2}"),
        ("%d-%m-%y", r"\d{1,2}-\d{1,2}-\d{2}"),
    ]

    for fmt, pattern in patterns:
        m = re.search(pattern, raw)
        if m:
            try:
                dt = datetime.strptime(m.group(0), fmt)
                return dt.date().isoformat()
            except ValueError:
                continue
    return None


def _search_first(pattern: str, text: str, flags: int = 0) -> Optional[str]:
    m = re.search(pattern, text, flags)
    if not m:
        return None
    if m.lastindex:
        return m.group(1).strip()
    return m.group(0).strip()


def parse_invoice_text(text: str) -> Invoice:
    """
    Parse le texte brut d'une facture et renvoie un objet Invoice.

    Les regex sont volontairement simples pour rester pédagogiques.
    Vous pourrez les affiner en fonction de vos vrais exemples.
    """
    # Numéro de facture (ex: "Facture n° 2025-001")
    invoice_number = _search_first(
        r"Facture\s*(?:n°|no|numéro)?\s*[:\-]?\s*([A-Z0-9\-\/]+)",
        text,
        flags=re.IGNORECASE,
    )

    # Date (prend la première date trouvée)
    date_raw = _search_first(
        r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}|\d{4}-\d{2}-\d{2})",
        text,
    )
    date_iso = _normalize_date(date_raw)

    # Fournisseur : on prend la première ligne non vide
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    supplier = lines[0] if lines else None

    # Client : on cherche une ligne commençant par "Client" ou "Destinataire"
    customer = None
    for line in lines:
        m_client = re.match(r"(Client|Destinataire)\s*[:\-]?\s*(.+)", line, flags=re.IGNORECASE)
        if m_client:
            customer = m_client.group(2).strip()
            break

    # Montants : cherche les labels classiques
    total_ht_raw = _search_first(r"Total\s+HT\s*[:\-]?\s*([\d\s.,]+)", text, flags=re.IGNORECASE)
    tva_raw = _search_first(r"(?:TVA|T\.V\.A\.)\s*[:\-]?\s*([\d\s.,]+)", text, flags=re.IGNORECASE)
    total_ttc_raw = _search_first(
        r"Total\s+TTC\s*[:\-]?\s*([\d\s.,]+)", text, flags=re.IGNORECASE
    )

    total_ht = _normalize_amount(total_ht_raw)
    tva = _normalize_amount(tva_raw)
    total_ttc = _normalize_amount(total_ttc_raw)

    return Invoice(
        invoice_number=invoice_number,
        date=date_iso,
        supplier=supplier,
        customer=customer,
        currency="EUR",
        total_ht=total_ht,
        tva=tva,
        total_ttc=total_ttc,
    )


__all__ = ["extract_text_from_pdf", "parse_invoice_text"]
