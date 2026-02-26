"""
Modèles Pydantic pour la génération structurée de posts réseaux sociaux.

Utilise les Structured Outputs d'OpenAI pour garantir la conformité
des sorties JSON au schéma défini.

Référence : GenAI/Texte/3_Structured_Outputs.ipynb
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


# ──────────────────────────────────────────────────────────────────────
# Enums pour contraindre les valeurs
# ──────────────────────────────────────────────────────────────────────

class Platform(str, Enum):
    """Plateformes de réseaux sociaux supportées."""
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"


class Tone(str, Enum):
    """Tons disponibles pour la génération de contenu."""
    PROFESSIONNEL = "professionnel"
    CREATIF = "créatif"
    HUMORISTIQUE = "humoristique"
    INSPIRANT = "inspirant"
    INFORMATIF = "informatif"
    ENGAGEANT = "engageant"


class ContentType(str, Enum):
    """Types de contenu supportés."""
    ANNONCE = "annonce"
    PROMOTION = "promotion"
    EDUCATIF = "éducatif"
    STORYTELLING = "storytelling"
    EVENEMENT = "événement"
    TEMOIGNAGE = "témoignage"
    ACTUALITE = "actualité"


# ──────────────────────────────────────────────────────────────────────
# Modèles de sortie structurés
# ──────────────────────────────────────────────────────────────────────

class Hashtag(BaseModel):
    """Un hashtag avec son score de pertinence."""
    tag: str = Field(description="Le hashtag sans le #")
    relevance: str = Field(
        description="Pertinence: haute, moyenne, basse"
    )


class PostingTimeSlot(BaseModel):
    """Créneau de publication recommandé."""
    jour: str = Field(description="Jour de la semaine recommandé")
    heure: str = Field(description="Heure recommandée (format HH:MM)")
    raison: str = Field(description="Raison de cette recommandation")
    score_engagement: str = Field(
        description="Score d'engagement estimé: excellent, bon, moyen"
    )


class ImagePrompt(BaseModel):
    """Prompt optimisé pour la génération d'image DALL-E 3."""
    prompt_en: str = Field(
        description="Prompt en anglais optimisé pour DALL-E 3"
    )
    style: str = Field(
        description="Style visuel : photographique, illustration, minimaliste, corporate, artistique"
    )
    couleurs_dominantes: List[str] = Field(
        description="Couleurs dominantes suggérées pour le visuel"
    )
    elements_cles: List[str] = Field(
        description="Éléments visuels clés à inclure"
    )


class PostContent(BaseModel):
    """Contenu d'un post pour une plateforme donnée."""
    plateforme: str = Field(description="Plateforme cible: linkedin, instagram, twitter")
    texte: str = Field(description="Texte complet du post adapté à la plateforme")
    accroche: str = Field(description="Première ligne accrocheuse du post")
    call_to_action: str = Field(description="Appel à l'action en fin de post")
    hashtags: List[Hashtag] = Field(description="Liste de hashtags recommandés")
    emojis_utilises: List[str] = Field(description="Emojis utilisés dans le post")
    longueur_caracteres: int = Field(description="Nombre de caractères du texte")
    image_prompt: ImagePrompt = Field(description="Prompt pour générer le visuel associé")
    timing: List[PostingTimeSlot] = Field(
        description="Créneaux de publication recommandés (top 3)"
    )


class ABVariation(BaseModel):
    """Une variation A/B d'un post."""
    version: str = Field(description="Identifiant de la version: A, B, C, etc.")
    post: PostContent = Field(description="Contenu du post pour cette variation")
    strategie: str = Field(
        description="Stratégie de cette variation (ex: accroche émotionnelle, données chiffrées, question, etc.)"
    )
    score_estime: str = Field(
        description="Score d'engagement estimé: élevé, moyen, faible"
    )


class SocialMediaOutput(BaseModel):
    """Sortie complète du générateur de posts multi-plateformes."""
    sujet: str = Field(description="Sujet/thématique du post")
    objectif: str = Field(description="Objectif du post (notoriété, engagement, conversion, etc.)")
    posts: List[PostContent] = Field(
        description="Posts générés pour chaque plateforme demandée"
    )
    conseil_global: str = Field(
        description="Conseil stratégique global pour cette campagne"
    )


class SingleVariationOutput(BaseModel):
    """Sortie pour la génération d'une seule variation A/B."""
    post: PostContent = Field(description="Contenu du post pour cette variation")
    strategie: str = Field(
        description="Stratégie utilisée (ex: storytelling, données chiffrées, question, humour)"
    )
    score_estime: str = Field(
        description="Score d'engagement estimé: élevé, moyen, faible"
    )


class ABRecommendation(BaseModel):
    """Recommandation finale après comparaison des variations A/B."""
    recommandation: str = Field(
        description="Recommandation détaillée sur la meilleure variation et pourquoi"
    )
    criteres_evaluation: List[str] = Field(
        description="Critères utilisés pour évaluer les variations"
    )


class ABTestOutput(BaseModel):
    """Sortie d'un test A/B pour une plateforme donnée."""
    plateforme: str = Field(description="Plateforme cible du test A/B")
    sujet: str = Field(description="Sujet du post")
    variations: List[ABVariation] = Field(
        description="Variations A/B générées (minimum 2)"
    )
    recommandation: str = Field(
        description="Recommandation sur la meilleure variation et pourquoi"
    )
    criteres_evaluation: List[str] = Field(
        description="Critères utilisés pour évaluer les variations"
    )


# ──────────────────────────────────────────────────────────────────────
# Modèle d'entrée utilisateur
# ──────────────────────────────────────────────────────────────────────

class PostRequest(BaseModel):
    """Requête utilisateur pour générer un post."""
    topic: str = Field(description="Sujet ou thème du post")
    platforms: List[Platform] = Field(
        default=[Platform.LINKEDIN, Platform.INSTAGRAM, Platform.TWITTER],
        description="Plateformes cibles"
    )
    tone: Tone = Field(
        default=Tone.PROFESSIONNEL,
        description="Ton souhaité"
    )
    content_type: ContentType = Field(
        default=ContentType.ANNONCE,
        description="Type de contenu"
    )
    target_audience: str = Field(
        default="professionnels",
        description="Audience cible"
    )
    key_message: str = Field(
        default="",
        description="Message clé à transmettre"
    )
    brand_name: str = Field(
        default="",
        description="Nom de la marque/entreprise"
    )
    language: str = Field(
        default="français",
        description="Langue du contenu"
    )
    generate_ab_variations: bool = Field(
        default=False,
        description="Générer des variations A/B"
    )
    num_variations: int = Field(
        default=2,
        description="Nombre de variations A/B (2-4)"
    )
