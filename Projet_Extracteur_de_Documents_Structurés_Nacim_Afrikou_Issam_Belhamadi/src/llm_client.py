"""Client LLM (OpenAI) – Structured Outputs pour extraction de documents.

Utilise les Structured Outputs d'OpenAI (JSON Schema strict + Pydantic)
pour garantir des sorties JSON conformes aux modèles définis.
"""

import base64
import os
from pathlib import Path
from typing import Any, Dict, Type

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()

# Modèle OpenAI à utiliser
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def _get_client() -> OpenAI:
    """Retourne un client OpenAI configuré (clé API depuis .env)."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY manquant. Vérifiez votre fichier .env.")
    return OpenAI(api_key=api_key)


def _add_additional_properties_false(schema: dict) -> dict:
    """Ajoute récursivement additionalProperties: false (requis par OpenAI strict mode)."""
    if not isinstance(schema, dict):
        return schema

    if "$defs" in schema:
        for def_schema in schema["$defs"].values():
            _add_additional_properties_false(def_schema)

    if schema.get("type") == "object":
        schema["additionalProperties"] = False
        if "properties" in schema:
            schema["required"] = list(schema["properties"].keys())
            for prop_schema in schema["properties"].values():
                _add_additional_properties_false(prop_schema)

    if schema.get("type") == "array" and "items" in schema:
        _add_additional_properties_false(schema["items"])

    for key in ["anyOf", "allOf", "oneOf"]:
        if key in schema:
            for item in schema[key]:
                _add_additional_properties_false(item)

    return schema


def _extract_structured(prompt: str, model_class: Type[BaseModel], system_msg: str = "") -> BaseModel:
    """Extraction structurée via Structured Outputs (JSON Schema strict).

    Génère le schema depuis le modèle Pydantic, appelle l'API avec
    response_format strict, et valide la réponse avec model_validate_json().
    """
    client = _get_client()
    schema = model_class.model_json_schema()
    schema = _add_additional_properties_false(schema)

    if not system_msg:
        system_msg = "Tu es un assistant qui extrait des informations structurées. Réponds en JSON."

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": model_class.__name__.lower(),
                "strict": True,
                "schema": schema,
            },
        },
    )

    content = response.choices[0].message.content
    if content is None:
        raise RuntimeError("Réponse vide du modèle LLM.")

    return model_class.model_validate_json(content)


# --- Modèle interne pour la détection de type ---

class _DocumentTypeResult(BaseModel):
    """Résultat de la détection de type de document."""
    document_type: str = Field(description="Type : 'order' ou 'invoice'")


# --- Détection du type de document ---

def detect_document_type(text: str) -> str:
    """Identifie le type de document (order / invoice) via Structured Output."""
    system_msg = (
        "Tu es un assistant spécialisé dans la classification de documents commerciaux."
    )
    prompt = (
        "Analyse le texte ci-dessous et détermine le type de document.\n"
        "- 'order' si c'est un bon de commande (purchase order, order confirmation)\n"
        "- 'invoice' si c'est une facture (invoice, bill)\n\n"
        "Indices :\n"
        "- Un 'order' contient souvent : Order ID, Order Date, Shipped Date, Shipper\n"
        "- Une 'invoice' contient souvent : Invoice Number, Invoice Date, Due Date, Tax/TVA\n\n"
        f"Texte du document :\n{text}"
    )

    result = _extract_structured(prompt, _DocumentTypeResult, system_msg)
    doc_type = result.document_type.lower().strip()
    return doc_type if doc_type in ("order", "invoice") else "order"


# --- Extraction des champs d'une commande ---

def extract_order_with_llm(text: str, model_class: Type[BaseModel]) -> BaseModel:
    """Extrait les champs d'une commande via Structured Output."""
    system_msg = "Tu es un assistant qui extrait des informations de commandes depuis des documents PDF."
    prompt = (
        "À partir du texte de commande ci-dessous, extrais toutes les informations pertinentes :\n"
        "identifiants, dates, client, employé, transporteur, livraison, produits, total.\n\n"
        f"Texte du document :\n{text}"
    )
    return _extract_structured(prompt, model_class, system_msg)


# --- Extraction des champs d'une facture ---

def extract_invoice_with_llm(text: str, model_class: Type[BaseModel]) -> BaseModel:
    """Extrait les champs d'une facture via Structured Output."""
    system_msg = "Tu es un assistant qui extrait des informations de factures depuis des documents PDF."
    prompt = (
        "À partir du texte de facture ci-dessous, extrais toutes les informations pertinentes :\n"
        "numéro, dates, vendeur, acheteur, articles, montants, conditions de paiement.\n\n"
        f"Texte du document :\n{text}"
    )
    return _extract_structured(prompt, model_class, system_msg)


# --- Extraction depuis images via GPT-4 Vision ---

def _encode_image_to_base64(image_path: Path) -> str:
    """Encode une image en base64 pour l'API Vision."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def _get_image_mime_type(image_path: Path) -> str:
    """Retourne le type MIME de l'image selon son extension."""
    suffix = image_path.suffix.lower()
    mime_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }
    return mime_types.get(suffix, 'image/jpeg')


def _extract_structured_from_image(image_path: Path, model_class: Type[BaseModel], system_msg: str, user_prompt: str) -> BaseModel:
    """Extraction structurée depuis une image via GPT-4 Vision + Structured Outputs.
    
    Encode l'image en base64, l'envoie à GPT-4 Vision avec le prompt,
    et retourne le résultat validé selon le modèle Pydantic.
    """
    client = _get_client()
    schema = model_class.model_json_schema()
    schema = _add_additional_properties_false(schema)

    # Encoder l'image
    base64_image = _encode_image_to_base64(image_path)
    mime_type = _get_image_mime_type(image_path)

    # Utiliser gpt-4o ou gpt-4o-mini (supportent vision + structured outputs)
    vision_model = os.getenv("OPENAI_VISION_MODEL", "gpt-4o-mini")

    response = client.chat.completions.create(
        model=vision_model,
        messages=[
            {"role": "system", "content": system_msg},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        temperature=0.0,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": model_class.__name__.lower(),
                "strict": True,
                "schema": schema,
            },
        },
    )

    content = response.choices[0].message.content
    if content is None:
        raise RuntimeError("Réponse vide du modèle LLM Vision.")

    return model_class.model_validate_json(content)


def detect_document_type_from_image(image_path: Path) -> str:
    """Identifie le type de document (order / invoice) depuis une image via GPT-4 Vision."""
    system_msg = "Tu es un assistant spécialisé dans la classification de documents commerciaux."
    prompt = (
        "Analyse l'image du document ci-dessous et détermine le type de document.\n"
        "- 'order' si c'est un bon de commande (purchase order, order confirmation)\n"
        "- 'invoice' si c'est une facture (invoice, bill)\n\n"
        "Indices :\n"
        "- Un 'order' contient souvent : Order ID, Order Date, Shipped Date, Shipper\n"
        "- Une 'invoice' contient souvent : Invoice Number, Invoice Date, Due Date, Tax/TVA"
    )

    result = _extract_structured_from_image(image_path, _DocumentTypeResult, system_msg, prompt)
    doc_type = result.document_type.lower().strip()
    return doc_type if doc_type in ("order", "invoice") else "order"


def extract_order_from_image(image_path: Path, model_class: Type[BaseModel]) -> BaseModel:
    """Extrait les champs d'une commande depuis une image via GPT-4 Vision."""
    system_msg = "Tu es un assistant qui extrait des informations de commandes depuis des images de documents."
    prompt = (
        "À partir de l'image de commande ci-dessous, extrais toutes les informations pertinentes :\n"
        "identifiants, dates, client, employé, transporteur, livraison, produits, total."
    )
    return _extract_structured_from_image(image_path, model_class, system_msg, prompt)


def extract_invoice_from_image(image_path: Path, model_class: Type[BaseModel]) -> BaseModel:
    """Extrait les champs d'une facture depuis une image via GPT-4 Vision."""
    system_msg = "Tu es un assistant qui extrait des informations de factures depuis des images de documents."
    prompt = (
        "À partir de l'image de facture ci-dessous, extrais toutes les informations pertinentes :\n"
        "numéro, dates, vendeur, acheteur, articles, montants, conditions de paiement."
    )
    return _extract_structured_from_image(image_path, model_class, system_msg, prompt)

