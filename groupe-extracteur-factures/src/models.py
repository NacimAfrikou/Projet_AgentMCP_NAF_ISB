from dataclasses import asdict, dataclass
from typing import Optional


@dataclass
class Invoice:
    """
    Représentation structurée d'une facture extraite.

    Tous les champs sont optionnels pour rester robustes face aux
    variations de format, mais le but est d'en remplir un maximum.
    """

    invoice_number: Optional[str] = None
    date: Optional[str] = None  # format ISO AAAA-MM-JJ si possible
    supplier: Optional[str] = None
    customer: Optional[str] = None
    currency: Optional[str] = "EUR"
    total_ht: Optional[float] = None
    tva: Optional[float] = None
    total_ttc: Optional[float] = None

    def to_dict(self) -> dict:
        """Convertit l'objet en dictionnaire sérialisable en JSON."""
        return asdict(self)
