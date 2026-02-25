"""
Configuration des plateformes de réseaux sociaux.

Définit les contraintes, dimensions, formats et bonnes pratiques
pour chaque plateforme supportée (LinkedIn, Instagram, Twitter/X).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class PlatformConfig:
    """Configuration complète d'une plateforme de réseau social."""
    name: str
    display_name: str
    max_characters: int
    image_dimensions: Tuple[int, int]  # (largeur, hauteur)
    dalle_size: str  # Taille DALL-E 3 la plus proche
    max_hashtags: int
    recommended_hashtags: int
    tone_guidelines: str
    format_guidelines: str
    emoji_usage: str
    best_posting_times: List[Dict[str, str]]
    content_tips: List[str]
    cta_examples: List[str]


# ──────────────────────────────────────────────────────────────────────
# Configurations par plateforme
# ──────────────────────────────────────────────────────────────────────

LINKEDIN_CONFIG = PlatformConfig(
    name="linkedin",
    display_name="LinkedIn",
    max_characters=3000,
    image_dimensions=(1200, 627),
    dalle_size="1792x1024",  # Format paysage le plus proche
    max_hashtags=10,
    recommended_hashtags=5,
    tone_guidelines=(
        "Professionnel, inspirant et authentique. "
        "Privilégier le storytelling personnel et les insights métier. "
        "Utiliser la première personne. "
        "Structurer avec des sauts de ligne pour la lisibilité."
    ),
    format_guidelines=(
        "Commencer par une accroche forte sur la première ligne. "
        "Utiliser des sauts de ligne fréquents (1 idée par ligne). "
        "Inclure un CTA clair à la fin. "
        "Terminer avec les hashtags séparés."
    ),
    emoji_usage="Modéré (2-5 emojis max, professionnels : 🚀 💡 ✅ 📊 🎯)",
    best_posting_times=[
        {"jour": "Mardi", "heure": "08:00", "raison": "Pic d'activité professionnelle matinale"},
        {"jour": "Mercredi", "heure": "10:00", "raison": "Forte consultation en milieu de semaine"},
        {"jour": "Jeudi", "heure": "12:00", "raison": "Pause déjeuner, consultation mobile"},
    ],
    content_tips=[
        "Les posts avec une histoire personnelle obtiennent 3x plus d'engagement",
        "Les carrousels (PDF) génèrent 10x plus de portée que les posts texte",
        "Poser une question augmente les commentaires de 50%",
        "Les chiffres dans l'accroche captent l'attention",
    ],
    cta_examples=[
        "Qu'en pensez-vous ? Partagez votre expérience en commentaire 👇",
        "Si ce post vous a été utile, partagez-le avec votre réseau 🔄",
        "Suivez-moi pour plus de contenu sur ce sujet 🔔",
        "Quel est votre avis ? Je lis tous les commentaires 💬",
    ],
)

INSTAGRAM_CONFIG = PlatformConfig(
    name="instagram",
    display_name="Instagram",
    max_characters=2200,
    image_dimensions=(1080, 1080),
    dalle_size="1024x1024",  # Format carré natif
    max_hashtags=30,
    recommended_hashtags=15,
    tone_guidelines=(
        "Créatif, visuel et émotionnel. "
        "Miser sur l'esthétique et l'authenticité. "
        "Raconter une histoire derrière l'image. "
        "Ton conversationnel et proche de l'audience."
    ),
    format_guidelines=(
        "Le visuel est ROI : le texte accompagne l'image. "
        "Accroche captivante dans les 2 premières lignes (avant le 'Plus...'). "
        "Les hashtags peuvent être en commentaire ou en fin de caption. "
        "Utiliser le line break entre le texte et les hashtags."
    ),
    emoji_usage="Généreux (5-10 emojis, expressifs : ✨ 🔥 💫 🌟 ❤️ 🙌)",
    best_posting_times=[
        {"jour": "Lundi", "heure": "11:00", "raison": "Début de semaine, engagement élevé"},
        {"jour": "Mercredi", "heure": "14:00", "raison": "Pause après-midi, scrolling mobile"},
        {"jour": "Vendredi", "heure": "17:00", "raison": "Fin de semaine, mood détendu"},
    ],
    content_tips=[
        "Les Reels obtiennent 2x plus de portée que les posts statiques",
        "Les carrousels gardent l'attention 3x plus longtemps",
        "Répondre aux commentaires dans la première heure booste l'algo",
        "Les Stories avec sondages augmentent l'interaction de 40%",
    ],
    cta_examples=[
        "Double tap si tu es d'accord ❤️",
        "Tag quelqu'un qui a besoin de voir ça 👇",
        "Enregistre ce post pour plus tard 🔖",
        "Quel est ton favoris ? Dis-le en commentaire 💬",
    ],
)

TWITTER_CONFIG = PlatformConfig(
    name="twitter",
    display_name="Twitter/X",
    max_characters=280,
    image_dimensions=(1600, 900),
    dalle_size="1792x1024",  # Format paysage le plus proche
    max_hashtags=3,
    recommended_hashtags=2,
    tone_guidelines=(
        "Concis, percutant et direct. "
        "Chaque mot compte. Écrire pour être partagé. "
        "Opinions fortes et prises de position. "
        "Utiliser l'humour avec parcimonie."
    ),
    format_guidelines=(
        "280 caractères MAX. Chaque caractère est précieux. "
        "Accroche immédiate (pas de préambule). "
        "Si besoin de développer, utiliser un thread (1/n). "
        "Hashtags intégrés dans le texte ou en fin de tweet."
    ),
    emoji_usage="Minimal (0-2 emojis, stratégiques : 🧵 📢 ⚡ 🔥)",
    best_posting_times=[
        {"jour": "Lundi", "heure": "09:00", "raison": "Les professionnels consultent en début de journée"},
        {"jour": "Mercredi", "heure": "12:00", "raison": "Pic de consultation pendant la pause"},
        {"jour": "Vendredi", "heure": "15:00", "raison": "Scrolling de fin de semaine"},
    ],
    content_tips=[
        "Les tweets avec images obtiennent 150% plus de retweets",
        "Les threads génèrent 10x plus d'impressions qu'un tweet unique",
        "Tweeter aux heures de bureau augmente la visibilité B2B",
        "Les citations et opinions fortes sont les plus partagées",
    ],
    cta_examples=[
        "RT si vous êtes d'accord 🔄",
        "Votre avis ? 👇",
        "Follow pour plus de contenu comme celui-ci",
        "Like + RT = 🔥",
    ],
)

# ──────────────────────────────────────────────────────────────────────
# Registry des plateformes
# ──────────────────────────────────────────────────────────────────────

PLATFORMS: Dict[str, PlatformConfig] = {
    "linkedin": LINKEDIN_CONFIG,
    "instagram": INSTAGRAM_CONFIG,
    "twitter": TWITTER_CONFIG,
}


def get_platform_config(platform: str) -> PlatformConfig:
    """
    Récupère la configuration d'une plateforme.
    
    Args:
        platform: Nom de la plateforme (linkedin, instagram, twitter)
        
    Returns:
        PlatformConfig correspondante
        
    Raises:
        ValueError: Si la plateforme n'est pas supportée
    """
    platform = platform.lower().strip()
    if platform not in PLATFORMS:
        raise ValueError(
            f"Plateforme '{platform}' non supportée. "
            f"Choix : {', '.join(PLATFORMS.keys())}"
        )
    return PLATFORMS[platform]


def get_all_platforms() -> List[str]:
    """Retourne la liste des plateformes supportées."""
    return list(PLATFORMS.keys())


def get_platform_summary() -> str:
    """Retourne un résumé formaté de toutes les plateformes."""
    lines = ["Plateformes supportées :\n"]
    for name, config in PLATFORMS.items():
        lines.append(
            f"  • {config.display_name} : "
            f"max {config.max_characters} car., "
            f"image {config.image_dimensions[0]}×{config.image_dimensions[1]}px, "
            f"{config.recommended_hashtags} hashtags recommandés"
        )
    return "\n".join(lines)
