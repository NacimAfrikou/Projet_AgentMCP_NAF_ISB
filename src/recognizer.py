"""
Module d'identification du type de document.
Basé sur la détection de mots-clés spécifiques à chaque type de document.
"""

from typing import Optional


# Constantes pour les mots-clés par type de document
KEYWORDS_BY_TYPE = {
    "facture": [
        "facture", "facture n", "facture numero", "facture n°", "facture #",
        "total ttc", "total ttc:", "montant total", "tva",
        "numéro de facture", "référence facture", "bon de commande",
        "conditions de paiement", "mode de paiement", "échéance",
        "tvaa déduisible", "taxe sur la valeur ajoutée"
    ],
    "devis": [
        "devis", "devi n", "devi numero", "devi n°", "devi #",
        "validation devis", "valider ce devis", "validez notre devis",
        "prix total", "tarif", "notre devis", "proposition commerciale",
        "validité de l'offre", "délais d'exécution"
    ],
    "formulaire": [
        "formulaire", "inscription", "dossier", "candidature",
        "nom complet", "prénom", "nom de famille",
        "adresse e-mail", "adresse email", "email",
        "téléphone", "telephone", "numéro de téléphone",
        "date de naissance", "lieu de naissance",
        "profession", "entreprise", "société"
    ],
    "reçu": [
        "reçu", "recu", "reçu de paiement", "recu de paiement",
        "versement", "paiement reçu", "montant payé",
        "date de paiement", "remise reçu"
    ],
    "contrat": [
        "contrat", "convention", "accord", "entente",
        "entre les parties", "les signataires", "ci-dessous signé",
        "durée du contrat", "résiliation", "pénalités"
    ]
}


def count_keywords(text: str, keywords: list) -> int:
    """
    Compte le nombre de mots-clés présents dans le texte (insensible à la casse).

    Args:
        text: Le texte à analyser
        keywords: Liste des mots-clés à rechercher

    Returns:
        Le nombre de mots-clés trouvés
    """
    text_lower = text.lower()
    count = 0
    for keyword in keywords:
        if keyword.lower() in text_lower:
            count += 1
    return count


def recognize_document(text: str) -> tuple[str, float]:
    """
    Identify le type de document basé sur les mots-clés présents.

    Args:
        text: Le texte du document à analyser

    Returns:
        Tuple (type_document, score_confiance) où score_confiance est entre 0 et 1
    """
    best_type = "inconnu"
    best_score = 0.0

    for doc_type, keywords in KEYWORDS_BY_TYPE.items():
        score = count_keywords(text, keywords)
        # Normaliser le score par rapport au nombre de mots-clés
        normalized_score = score / len(keywords)

        if normalized_score > best_score:
            best_score = normalized_score
            best_type = doc_type

    # Ajuster le seuil de confiance minime
    if best_score < 0.1:
        best_type = "inconnu"
        best_score = 0.0

    return best_type, round(best_score, 2)


def is_document_type(text: str, target_type: str) -> bool:
    """
    Vérifie si le texte correspond à un type de document spécifique.

    Args:
        text: Le texte à analyser
        target_type: Le type cible à vérifier

    Returns:
        True si le type correspond, False sinon
    """
    detected_type, score = recognize_document(text)
    return detected_type == target_type and score > 0.2


def get_available_document_types() -> list[str]:
    """
    Retourne la liste des types de documents reconnus.
    """
    return list(KEYWORDS_BY_TYPE.keys())
