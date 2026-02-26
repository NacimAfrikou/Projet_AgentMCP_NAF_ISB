"""
Générateur de posts pour réseaux sociaux.

Utilise les Structured Outputs d'OpenAI (JSON Schema strict) combinés
avec Pydantic pour garantir la conformité des sorties.

Références :
- GenAI/Texte/3_Structured_Outputs.ipynb (Structured Outputs)
- GenAI/Texte/2_PromptEngineering.ipynb (Prompt Engineering)
"""

import os
import json
from typing import List, Optional

from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv

from .models import (
    PostContent,
    SocialMediaOutput,
    ABTestOutput,
    ABVariation,
    ABRecommendation,
    SingleVariationOutput,
    PostRequest,
    Platform,
    Tone,
    ContentType,
)
from .platforms import get_platform_config, PlatformConfig, PLATFORMS
from .utils import add_additional_properties_false


# ──────────────────────────────────────────────────────────────────────
# Classe principale
# ──────────────────────────────────────────────────────────────────────

class SocialMediaGenerator:
    """
    Générateur intelligent de posts pour réseaux sociaux.
    
    Utilise l'API OpenAI avec Structured Outputs pour générer
    du contenu adapté à chaque plateforme.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = None):
        """
        Initialise le générateur.
        
        Args:
            api_key: Clé API OpenAI (ou via OPENAI_API_KEY env var)
            model: Modèle OpenAI à utiliser (défaut: gpt-4o-mini)
        """
        # Charger .env depuis le dossier parent si présent
        load_dotenv()
        load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
        
        self.client = OpenAI(api_key=api_key) if api_key else OpenAI()
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def _call_structured(
        self,
        messages: list,
        output_model: type[BaseModel],
        schema_name: str = "output",
    ) -> BaseModel:
        """
        Appel OpenAI avec Structured Outputs et validation Pydantic.
        
        Args:
            messages: Messages pour l'API chat completions
            output_model: Classe Pydantic pour la validation
            schema_name: Nom du schéma JSON
            
        Returns:
            Instance validée du modèle Pydantic
        """
        schema = output_model.model_json_schema()
        schema = add_additional_properties_false(schema)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": schema_name,
                    "strict": True,
                    "schema": schema,
                },
            },
        )

        return output_model.model_validate_json(
            response.choices[0].message.content
        )

    # ──────────────────────────────────────────────────────────
    # Prompts système
    # ──────────────────────────────────────────────────────────

    def _build_system_prompt(self, platforms: List[str]) -> str:
        """Construit le prompt système avec les guidelines des plateformes."""
        platform_details = []
        for pname in platforms:
            config = get_platform_config(pname)
            platform_details.append(
                f"""
### {config.display_name}
- Longueur max : {config.max_characters} caractères
- Ton : {config.tone_guidelines}
- Format : {config.format_guidelines}
- Emojis : {config.emoji_usage}
- Hashtags recommandés : {config.recommended_hashtags} (max {config.max_hashtags})
- Image : {config.image_dimensions[0]}×{config.image_dimensions[1]}px (DALL-E size: {config.dalle_size})
- Astuces : {'; '.join(config.content_tips[:2])}
- CTA exemples : {'; '.join(config.cta_examples[:2])}
"""
            )

        return f"""Tu es un expert en marketing digital et community management.
Tu génères du contenu optimisé pour les réseaux sociaux, en adaptant le ton,
le format et la stratégie à chaque plateforme.

## Guidelines par plateforme
{''.join(platform_details)}

## Règles générales
- Chaque post doit être UNIQUE et adapté à sa plateforme (pas de copier-coller)
- Les hashtags doivent être pertinents et mélanger popularité et niche
- Les prompts d'image doivent être en ANGLAIS, détaillés et adaptés à DALL-E 3
- Les créneaux de publication sont basés sur le fuseau horaire Europe/Paris
- Le texte du post doit respecter la longueur max de la plateforme
- Toujours inclure un CTA (Call To Action) adapté
- Les emojis doivent être utilisés selon les guidelines de chaque plateforme
"""

    def _build_user_prompt(self, request: PostRequest) -> str:
        """Construit le prompt utilisateur à partir de la requête."""
        platforms_str = ", ".join(p.value for p in request.platforms)
        
        prompt = f"""Génère des posts optimisés pour les plateformes suivantes : {platforms_str}

## Détails de la demande
- **Sujet** : {request.topic}
- **Ton souhaité** : {request.tone.value}
- **Type de contenu** : {request.content_type.value}
- **Audience cible** : {request.target_audience}
- **Langue** : {request.language}
"""
        if request.key_message:
            prompt += f"- **Message clé** : {request.key_message}\n"
        if request.brand_name:
            prompt += f"- **Marque/Entreprise** : {request.brand_name}\n"

        prompt += """
## Instructions
1. Crée un post UNIQUE et optimisé pour CHAQUE plateforme demandée
2. Adapte le ton, la longueur et le format à chaque plateforme
3. Génère des hashtags pertinents (mix popularité + niche)
4. Propose un prompt d'image DALL-E 3 optimisé (en anglais) pour chaque post
5. Recommande les 3 meilleurs créneaux de publication
6. Ajoute un CTA adapté à chaque plateforme
"""
        return prompt

    # ──────────────────────────────────────────────────────────
    # Méthodes publiques
    # ──────────────────────────────────────────────────────────

    def generate_posts(self, request: PostRequest) -> SocialMediaOutput:
        """
        Génère des posts pour toutes les plateformes demandées.
        
        Args:
            request: Requête de génération (PostRequest)
            
        Returns:
            SocialMediaOutput avec les posts pour chaque plateforme
        """
        platforms = [p.value for p in request.platforms]
        system_prompt = self._build_system_prompt(platforms)
        user_prompt = self._build_user_prompt(request)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        return self._call_structured(
            messages=messages,
            output_model=SocialMediaOutput,
            schema_name="social_media_output",
        )

    def generate_post_simple(
        self,
        topic: str,
        platform: str = "linkedin",
        tone: str = "professionnel",
    ) -> SocialMediaOutput:
        """
        Génère un post pour une seule plateforme (API simplifiée).
        
        Args:
            topic: Sujet du post
            platform: Plateforme cible
            tone: Ton souhaité
            
        Returns:
            SocialMediaOutput avec un seul post
        """
        request = PostRequest(
            topic=topic,
            platforms=[Platform(platform)],
            tone=Tone(tone),
        )
        return self.generate_posts(request)

    def _generate_single_variation(
        self,
        topic: str,
        platform: str,
        tone: str,
        content_type: str,
        target_audience: str,
        version_letter: str,
        strategy: str,
    ) -> ABVariation:
        """
        Génère UNE SEULE variation via un appel API dédié.
        Retourne une ABVariation complète.
        """
        config = get_platform_config(platform)
        system_prompt = self._build_system_prompt([platform])
        system_prompt += f"""
## Génération d'une variation de test A/B
Tu dois générer UN SEUL post complet en suivant la stratégie imposée.
Stratégie à suivre : {strategy}
Le post doit être un contenu complet, prêt à être publié sur {config.display_name}.
"""

        user_prompt = f"""Génère un post {config.display_name} en suivant la stratégie : {strategy}.

- **Sujet** : {topic}
- **Ton** : {tone}
- **Type de contenu** : {content_type}
- **Audience** : {target_audience}

Crée un post COMPLET optimisé pour {config.display_name}, avec hashtags, timing, image prompt, etc.
Estime le score d'engagement de cette variation (élevé, moyen, ou faible).
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        single = self._call_structured(
            messages=messages,
            output_model=SingleVariationOutput,
            schema_name="single_variation",
        )

        return ABVariation(
            version=version_letter,
            post=single.post,
            strategie=single.strategie,
            score_estime=single.score_estime,
        )

    def generate_ab_variations(
        self,
        topic: str,
        platform: str = "linkedin",
        num_variations: int = 2,
        tone: str = "professionnel",
        content_type: str = "annonce",
        target_audience: str = "professionnels",
    ) -> ABTestOutput:
        """
        Génère des variations A/B d'un post pour une plateforme.

        Chaque variation est générée par un appel API séparé pour
        garantir exactement N variations distinctes.
        
        Args:
            topic: Sujet du post
            platform: Plateforme cible
            num_variations: Nombre de variations (2-4)
            tone: Ton souhaité
            content_type: Type de contenu
            target_audience: Audience cible
            
        Returns:
            ABTestOutput avec les variations et recommandations
        """
        strategies = [
            ("A", "Approche émotionnelle / storytelling"),
            ("B", "Approche factuelle / données chiffrées"),
            ("C", "Approche question / engagement direct"),
            ("D", "Approche humour / créativité"),
        ]

        # ── Étape 1 : générer chaque variation séparément ──
        variations = []
        for letter, strategy in strategies[:num_variations]:
            print(f"  ⏳ Génération de la variation {letter} ({strategy})...")
            var = self._generate_single_variation(
                topic=topic,
                platform=platform,
                tone=tone,
                content_type=content_type,
                target_audience=target_audience,
                version_letter=letter,
                strategy=strategy,
            )
            variations.append(var)
            print(f"  ✅ Variation {letter} générée")

        # ── Étape 2 : obtenir la recommandation ──
        print("  ⏳ Génération de la recommandation...")
        variations_summary = "\n".join(
            f"- Variation {v.version} : stratégie={v.strategie}, "
            f"score={v.score_estime}, longueur={v.post.longueur_caracteres} car., "
            f"hashtags={len(v.post.hashtags)}, accroche=\"{v.post.accroche}\""
            for v in variations
        )

        reco_messages = [
            {"role": "system", "content": (
                "Tu es un expert en marketing digital. "
                "Compare les variations A/B suivantes et donne ta recommandation."
            )},
            {"role": "user", "content": (
                f"Voici les variations générées pour un post {platform} sur "
                f"\"{topic}\" (audience: {target_audience}) :\n\n"
                f"{variations_summary}\n\n"
                f"Quelle variation recommandes-tu et pourquoi ? "
                f"Liste aussi les critères d'évaluation que tu as utilisés."
            )},
        ]

        reco = self._call_structured(
            messages=reco_messages,
            output_model=ABRecommendation,
            schema_name="ab_recommendation",
        )
        print("  ✅ Recommandation générée")

        return ABTestOutput(
            plateforme=platform,
            sujet=topic,
            variations=variations,
            recommandation=reco.recommandation,
            criteres_evaluation=reco.criteres_evaluation,
        )

    def generate_all_platforms(
        self,
        topic: str,
        tone: str = "professionnel",
        content_type: str = "annonce",
        target_audience: str = "professionnels",
        key_message: str = "",
        brand_name: str = "",
    ) -> SocialMediaOutput:
        """
        Génère un post pour TOUTES les plateformes (LinkedIn, Instagram, Twitter).
        
        Args:
            topic: Sujet du post
            tone: Ton souhaité
            content_type: Type de contenu
            target_audience: Audience cible
            key_message: Message clé optionnel
            brand_name: Nom de marque optionnel
            
        Returns:
            SocialMediaOutput avec les 3 posts
        """
        request = PostRequest(
            topic=topic,
            platforms=[Platform.LINKEDIN, Platform.INSTAGRAM, Platform.TWITTER],
            tone=Tone(tone),
            content_type=ContentType(content_type),
            target_audience=target_audience,
            key_message=key_message,
            brand_name=brand_name,
        )
        return self.generate_posts(request)
