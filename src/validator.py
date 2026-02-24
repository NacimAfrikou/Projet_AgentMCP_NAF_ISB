"""
Modèles Pydantic pour la validation des données extraites des documents.
"""

from datetime import date
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
import re


class InvoiceModel(BaseModel):
    """
    Modèle pour les factures.
    """
    document_type: str = Field(default="facture", description="Type de document")

    invoice_number: Optional[str] = Field(default=None, description="Numéro de facture")
    date: Optional[str] = Field(default=None, description="Date de la facture (YYYY-MM-DD)")
    due_date: Optional[str] = Field(default=None, description="Date d'échéance (YYYY-MM-DD)")

    client_name: Optional[str] = Field(default=None, description="Nom du client")
    client_address: Optional[str] = Field(default=None, description="Adresse du client")
    tva_number: Optional[str] = Field(default=None, description="Numéro de TVA du client")

    total_amount: Optional[float] = Field(default=None, description="Montant total TTC")
    subtotal: Optional[float] = Field(default=None, description="Sous-total HT")
    tax_amount: Optional[float] = Field(default=None, description="Montant de la TVA")
    tax_rate: Optional[float] = Field(default=None, description="Taux de TVA appliqué")

    items: Optional[list] = Field(default=None, description="Liste des lignes de facturation")

    @field_validator('date')
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # Accepter plusieurs formats et normaliser en YYYY-MM-DD
        patterns = [
            r'(\d{4})-(\d{2})-(\d{2})',  # YYYY-MM-DD
            r'(\d{2})/(\d{2})/(\d{4})',  # DD/MM/YYYY
            r'(\d{2})-(\d{2})-(\d{4})',  # DD-MM-YYYY
        ]
        for pattern in patterns:
            match = re.match(pattern, v)
            if match:
                groups = match.groups()
                if len(groups[0]) == 4:
                    return f"{groups[0]}-{groups[1]}-{groups[2]}"
                else:
                    return f"{groups[2]}-{groups[1]}-{groups[0]}"
        raise ValueError(f"Format de date invalide: {v}")

    @field_validator('total_amount', 'subtotal', 'tax_amount', 'tax_rate')
    @classmethod
    def validate_amounts(cls, v: Optional[float]) -> Optional[float]:
        if v is None:
            return v
        if v < 0:
            raise ValueError(f"Le montant ne peut pas être négatif: {v}")
        return round(v, 2)


class FormModel(BaseModel):
    """
    Modèle pour les formulaires d'inscription.
    """
    document_type: str = Field(default="formulaire", description="Type de document")

    first_name: Optional[str] = Field(default=None, description="Prénom")
    last_name: Optional[str] = Field(default=None, description="Nom")
    email: Optional[str] = Field(default=None, description="Adresse email")
    phone: Optional[str] = Field(default=None, description="Numéro de téléphone")

    birth_date: Optional[str] = Field(default=None, description="Date de naissance (YYYY-MM-DD)")
    address: Optional[str] = Field(default=None, description="Adresse postale")
    city: Optional[str] = Field(default=None, description="Ville")
    postal_code: Optional[str] = Field(default=None, description="Code postal")
    country: Optional[str] = Field(default=None, description="Pays")

    profession: Optional[str] = Field(default=None, description="Profession")
    company: Optional[str] = Field(default=None, description="Nom de l'entreprise")

    comments: Optional[str] = Field(default=None, description="Commentaires supplémentaires")

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError(f"Format d'email invalide: {v}")
        return v.lower()

    @field_validator('birth_date')
    @classmethod
    def validate_birth_date_format(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # Accepter plusieurs formats et normaliser en YYYY-MM-DD
        patterns = [
            r'(\d{4})-(\d{2})-(\d{2})',
            r'(\d{2})/(\d{2})/(\d{4})',
            r'(\d{2})-(\d{2})-(\d{4})',
        ]
        for pattern in patterns:
            match = re.match(pattern, v)
            if match:
                groups = match.groups()
                if len(groups[0]) == 4:
                    return f"{groups[0]}-{groups[1]}-{groups[2]}"
                else:
                    return f"{groups[2]}-{groups[1]}-{groups[0]}"
        raise ValueError(f"Format de date invalide: {v}")


class DocumentModel(BaseModel):
    """
    Modèle de sortie pour tous les types de documents.
    """
    document_type: str = Field(description="Type de document détecté")
    extracted_data: Dict[str, Any] = Field(description="Données extraites du document")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Score de confiance de l'extraction")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Métadonnées de l'extraction")
