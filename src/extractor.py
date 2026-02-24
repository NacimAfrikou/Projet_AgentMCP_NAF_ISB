"""
Module d'extraction des données des documents.
Utilise des expressions régulières pour identifier et extraire les champs.
"""

import re
from typing import Optional, Dict, Any
from datetime import datetime


# Constantes pour les motifs regex
class RegexPatterns:
    """Motifs regex pour l'extraction des données."""

    # Numéro de facture
    INVOICE_NUMBER = [
        r'(?:Facture\s+N|N|NUMÉRO\s+DE\s+FACTURE)\s*[°N]?\s*[:\-]?\s*([A-Z0-9\-/]+)',
        r'(?:Invoice(?:\s+No| Number)?)\s*[:\-]?\s*([A-Z0-9\-/]+)',
    ]

    # Date (différents formats)
    DATE = [
        r'(\d{4})[-/\.](\d{2})[-/\.](\d{2})',  # YYYY-MM-DD ou YYYY/MM/DD
        r'(\d{2})[-/\.](\d{2})[-/\.](\d{4})',  # DD-MM-YYYY ou DD/MM/YYYY
        r'(\d{2})[-/\.](\d{4})',  # MM/YYYY
    ]

    # Montants
    TOTAL_AMOUNT = [
        r'(?:Total\s+TTC|Montant\s+total|Montant\s+à\s+payer)\s*[:\-]?\s*([\d\s,\.]+)\s*(?:€|EUR)?',
        r'(?:Total\s+TTC|Montant\s+total|Montant\s+à\s+payer)\s*[:\-]?\s*([\d\.]+)',
        r'TOTAL\s+TTC\s*[:\-]?\s*([\d\s,\.]+)',
    ]

    SUBTOTAL = [
        r'(?:Sous\-)?total\s+HT\s*[:\-]?\s*([\d\s,\.]+)\s*(?:€|EUR)?',
        r'SOUS\-TOTAL\s+HT\s*[:\-]?\s*([\d\s,\.]+)',
    ]

    TAX_AMOUNT = [
        r'(?:Montant\s+)?TVA\s*[:\-]?\s*([\d\s,\.]+)\s*(?:€|EUR)?',
        r'TAXE\s+SUR\s+LA\s+VALEUR\s+AJOUTÉE\s*[:\-]?\s*([\d\s,\.]+)',
    ]

    TVA_NUMBER = [
        r'(?:Numéro\s+)?TVA(?:\s+intracommunautaire)?\s*[:\-]?\s*([A-Z]{2}[A-Z0-9\s]+)',
        r'SIRET\s*[:\-]?\s*([\d\s]+)',
        r'SIREN\s*[:\-]?\s*([\d\s]+)',
    ]

    # Client
    CLIENT_NAME = [
        r'(?:Nom\s+du\s+client|Client| destinataire)\s*[:\-]?\s*([A-Z][a-zA-Z\u00C0-\u017F\s]+)',
        r'(?:From|Bill\s+to)\s*[:\-]?\s*([A-Z][a-zA-Z\s]+)',
    ]

    CLIENT_ADDRESS = [
        r'(?:Adresse\s+du\s+client|Adresse|Adresse postale)\s*[:\-]?\s*(.+?)(?=\n|$)',
    ]

    # Email
    EMAIL = [
        r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
    ]

    # Téléphone
    PHONE = [
        r'(?:Tél(?:éphone)?|Mobile|Numéro\s+de\s+téléphone)\s*[:\-]?\s*([\d\s]+)',
        r'\+?\d{1,3}[\s\.]?\d{2}[\s\.]?\d{2}[\s\.]?\d{2}[\s\.]?\d{2}',
    ]

    # Prénom et Nom
    FIRST_NAME = [
        r'(?:Prénom|First\s+name)\s*[:\-]?\s*([A-Z][a-zA-ZàâçéèêëîïôûùýÿæœxcçÀÂÇÉÈÊËÎÏÔÛÙÝŸÆŒXCÇ\-]+)',
    ]

    LAST_NAME = [
        r'(?:Nom|Last\s+name|Nom\s+de\s+famille)\s*[:\-]?\s*([A-Z][a-zA-ZàâçéèêëîïôûùýÿæœxcçÀÂÇÉÈÊËÎÏÔÛÙÝŸÆŒXCÇ\-]+)',
    ]

    # Date de naissance
    BIRTH_DATE = [
        r'(?:Date\s+de\s+naissance|Né\s+le)\s*[:\-]?\s*(\d{2}[-/\.]\d{2}[-/\.]\d{4})',
    ]

    # Profession
    PROFESSION = [
        r'(?:Profession|Poste|Fonction)\s*[:\-]?\s*([a-zA-Z\u00C0-\u017F\s]+)',
    ]

    # Ville et Code postal
    CITY = [
        r'(?:Ville|Localité)\s*[:\-]?\s*([A-Z][a-zA-Z\u00C0-\u017F\s]+)',
    ]

    POSTAL_CODE = [
        r'(?:Code\s+postal|CP)\s*[:\-]?\s*(\d{5})',
    ]


def extract_with_patterns(text: str, patterns: list[str]) -> Optional[str]:
    """
    Extrait une valeur à partir du texte en utilisant une liste de motifs regex.

    Args:
        text: Le texte à analyser
        patterns: Liste de motifs regex à essayer

    Returns:
        La valeur extraite ou None si rien n'est trouvé
    """
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            value = match.group(1).strip()
            # Nettoyer la valeur
            value = re.sub(r'\s+', ' ', value)
            return value
    return None


def normalize_date(date_str: Optional[str]) -> Optional[str]:
    """
    Normalise une date au format YYYY-MM-DD.

    Args:
        date_str: La date à normaliser

    Returns:
        La date formatée ou None
    """
    if not date_str:
        return None

    # Essayer différents formats
    formats = [
        '%Y-%m-%d',
        '%d/%m/%Y',
        '%d-%m-%Y',
        '%m/%d/%Y',
        '%Y/%m/%d',
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue

    return None


def normalize_amount(amount_str: Optional[str]) -> Optional[float]:
    """
    Normalise un montant en float (gère les virgules et espaces).

    Args:
        amount_str: Le montant à normaliser

    Returns:
        Le montant en float ou None
    """
    if not amount_str:
        return None

    try:
        # Nettoyer la chaîne
        cleaned = amount_str.replace(',', '.').replace(' ', '').replace('€', '').strip()
        return round(float(cleaned), 2)
    except (ValueError, TypeError):
        return None


def extract_invoice_data(text: str) -> Dict[str, Any]:
    """
    Extrait les données spécifiques à une facture.

    Args:
        text: Le texte du document

    Returns:
        Dictionnaire des données extraites
    """
    data = {}

    # Numéro de facture - chercher spécifiquement le numéro après "FACTURE N°" ou "N°"
    invoice_patterns = [
        r'(?:FACTURE\s+N°|N°)\s*[:\-]?\s*([A-Z0-9\-/]+)',
        r'(?:facture\s+n|N)\s*[:\-]?\s*([A-Z0-9\-/]+)',
        r'(?:Invoice\s+No|Number)\s*[:\-]?\s*([A-Z0-9\-/]+)',
    ]
    data['invoice_number'] = extract_with_patterns(text, invoice_patterns)

    # Date - chercher spécifiquement après "Date:" ou "Date :"
    date_patterns = [
        r'(?:Date\s*:|Date\s*[:])\s*(\d{2}[-/]\d{2}[-/]\d{4})',
        r'(\d{4})[-/](\d{2})[-/](\d{2})',  # YYYY-MM-DD
        r'(\d{2})[-/](\d{2})[-/](\d{4})',  # DD-MM-YYYY
    ]
    date_str = extract_with_patterns(text, date_patterns)
    data['date'] = normalize_date(date_str)

    # Dates supplémentaires (due date)
    due_patterns = [
        r'(?:Date\s+d?é?é?cheance|Echéance|Paiement\s+du)\s*[:\-]?\s*(\d{2}[-/\.]\d{2}[-/\.]\d{4})',
    ]
    due_date_str = extract_with_patterns(text, due_patterns)
    data['due_date'] = normalize_date(due_date_str)

    # Montants
    total_str = extract_with_patterns(text, RegexPatterns.TOTAL_AMOUNT)
    data['total_amount'] = normalize_amount(total_str)

    subtotal_str = extract_with_patterns(text, RegexPatterns.SUBTOTAL)
    data['subtotal'] = normalize_amount(subtotal_str)

    tax_str = extract_with_patterns(text, RegexPatterns.TAX_AMOUNT)
    data['tax_amount'] = normalize_amount(tax_str)

    # Numéro de TVA - chercher spécifiquement après "Numéro de TVA:" ou "TVA:"
    tva_patterns = [
        r'(?:Numéro\s+)?TVA(?:\s+intracommunautaire)?\s*[:]\s*([A-Z]{2}[A-Z0-9]+)',
        r'SIRET\s*[:]\s*([\d\s]+)',
        r'SIREN\s*[:]\s*([\d\s]+)',
    ]
    tva_str = extract_with_patterns(text, tva_patterns)
    if tva_str:
        # Extraire seulement le numéro de TVA propre (ex: FR1234567890123)
        # Le format français est FR + 11 caractères (lettres ou chiffres)
        tva_match = re.search(r'(FR[A-Z0-9]{11})', tva_str)
        if tva_match:
            data['tva_number'] = tva_match.group(1)
        else:
            # Fallback: enlever les espaces et chercher un numéro FR
            cleaned = tva_str.replace(' ', '')
            tva_match = re.search(r'FR[A-Z0-9]{11}', cleaned)
            if tva_match:
                data['tva_number'] = tva_match.group(0)

    # Client - chercher spécifiquement après "Client:" ou "Client :"
    client_patterns = [
        r'(?:Client|Destinataire)\s*[:]\s*([A-Z][a-zA-Z\u00C0-\u017F\s]+?)(?=\n|$)',
        r'(?:Client|Destinataire)\s*[:]\s*([A-Z][a-zA-Z\u00C0-\u017F\s]+?)\s*\n',
    ]
    client_name = extract_with_patterns(text, client_patterns)
    if client_name:
        data['client_name'] = client_name.strip()
    data['client_address'] = extract_with_patterns(text, RegexPatterns.CLIENT_ADDRESS)

    return data


def extract_form_data(text: str) -> Dict[str, Any]:
    """
    Extrait les données spécifiques à un formulaire.

    Args:
        text: Le texte du document

    Returns:
        Dictionnaire des données extraites
    """
    data = {}

    # Nom et Prénom
    data['last_name'] = extract_with_patterns(text, RegexPatterns.LAST_NAME)
    data['first_name'] = extract_with_patterns(text, RegexPatterns.FIRST_NAME)

    # Email
    email = extract_with_patterns(text, RegexPatterns.EMAIL)
    if email:
        data['email'] = email.lower().strip()

    # Téléphone
    phone = extract_with_patterns(text, RegexPatterns.PHONE)
    if phone:
        # Nettoyer le numéro (garder seulement les chiffres et le +)
        phone = re.sub(r'[^\d+]', '', phone.strip())
        if phone:
            data['phone'] = phone

    # Date de naissance
    birth_str = extract_with_patterns(text, RegexPatterns.BIRTH_DATE)
    data['birth_date'] = normalize_date(birth_str)

    # Adresse complète
    address_lines = []
    address_patterns = [
        r'(?:Adresse|Adresse postale)\s*[:\-]?\s*(.+?)(?=\n(?:Ville|Code postal|CP|Profession|Email|Téléphone|$))',
    ]
    for pattern in address_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            address_lines.append(match.group(1).strip())

    if address_lines:
        data['address'] = ' '.join(address_lines)

    # Ville
    data['city'] = extract_with_patterns(text, RegexPatterns.CITY)

    # Code postal
    postal = extract_with_patterns(text, RegexPatterns.POSTAL_CODE)
    if postal:
        data['postal_code'] = postal

    # Profession
    data['profession'] = extract_with_patterns(text, RegexPatterns.PROFESSION)

    return data


def extract_all_data(text: str, document_type: str) -> Dict[str, Any]:
    """
    Extrait toutes les données possibles du document.

    Args:
        text: Le texte du document
        document_type: Le type de document (facture, formulaire, etc.)

    Returns:
        Dictionnaire des données extraites
    """
    data = {}

    if document_type == 'facture':
        data.update(extract_invoice_data(text))
    elif document_type == 'formulaire':
        data.update(extract_form_data(text))

    # Extraire les données communes à plusieurs types
    if not data.get('email'):
        email = extract_with_patterns(text, RegexPatterns.EMAIL)
        if email:
            data['email'] = email.lower().strip()

    if not data.get('client_name') and not data.get('last_name'):
        name = extract_with_patterns(text, RegexPatterns.CLIENT_NAME)
        if name:
            # Essayer de séparer nom et prénom
            parts = name.split()
            if len(parts) >= 2:
                data['last_name'] = parts[0]
                data['first_name'] = ' '.join(parts[1:])
            else:
                data['client_name'] = name

    return data
