"""
Générateur de visuels pour posts réseaux sociaux via DALL-E 3.

Génère des images adaptées aux dimensions de chaque plateforme
en utilisant l'API OpenAI Images.

Référence : GenAI/Images/01-1-OpenAI-DALL-E-3.ipynb
"""

import os
import base64
import requests
from io import BytesIO
from typing import Optional, Tuple
from pathlib import Path

from openai import OpenAI
from dotenv import load_dotenv

from .platforms import get_platform_config


class ImageGenerator:
    """
    Générateur de visuels via DALL-E 3, optimisé pour les réseaux sociaux.
    
    Gère les dimensions spécifiques à chaque plateforme et propose
    des options de sauvegarde et d'affichage.
    """

    # Tailles DALL-E 3 supportées
    DALLE_SIZES = {
        "1024x1024": (1024, 1024),    # Carré (Instagram)
        "1792x1024": (1792, 1024),    # Paysage (LinkedIn, Twitter)
        "1024x1792": (1024, 1792),    # Portrait (Stories)
    }

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialise le générateur d'images.
        
        Args:
            api_key: Clé API OpenAI (ou via OPENAI_API_KEY env var)
        """
        load_dotenv()
        load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
        self.client = OpenAI(api_key=api_key) if api_key else OpenAI()

    def generate_image(
        self,
        prompt: str,
        platform: str = "linkedin",
        quality: str = "standard",
        style: str = "vivid",
        save_path: Optional[str] = None,
    ) -> dict:
        """
        Génère une image avec DALL-E 3 adaptée à une plateforme.
        
        Args:
            prompt: Description de l'image (en anglais pour de meilleurs résultats)
            platform: Plateforme cible (linkedin, instagram, twitter)
            quality: Qualité DALL-E 3 (standard, hd)
            style: Style DALL-E 3 (vivid, natural)
            save_path: Chemin pour sauvegarder l'image (optionnel)
            
        Returns:
            Dict avec url, revised_prompt, platform, size
        """
        config = get_platform_config(platform)
        dalle_size = config.dalle_size

        # Enrichir le prompt avec le contexte plateforme
        enhanced_prompt = self._enhance_prompt(prompt, platform, config)

        response = self.client.images.generate(
            model="dall-e-3",
            prompt=enhanced_prompt,
            size=dalle_size,
            quality=quality,
            style=style,
            n=1,
        )

        result = {
            "url": response.data[0].url,
            "revised_prompt": response.data[0].revised_prompt,
            "platform": platform,
            "size": dalle_size,
            "target_dimensions": f"{config.image_dimensions[0]}×{config.image_dimensions[1]}",
        }

        # Sauvegarder si un chemin est fourni
        if save_path:
            self._save_image_from_url(response.data[0].url, save_path)
            result["saved_to"] = save_path

        return result

    def generate_for_all_platforms(
        self,
        prompt: str,
        save_dir: Optional[str] = None,
        quality: str = "standard",
        style: str = "vivid",
    ) -> dict:
        """
        Génère des visuels adaptés pour les 3 plateformes.
        
        Args:
            prompt: Description de l'image de base
            save_dir: Dossier de sauvegarde (optionnel)
            quality: Qualité DALL-E 3
            style: Style DALL-E 3
            
        Returns:
            Dict avec un résultat par plateforme
        """
        results = {}
        for platform in ["linkedin", "instagram", "twitter"]:
            save_path = None
            if save_dir:
                os.makedirs(save_dir, exist_ok=True)
                save_path = os.path.join(save_dir, f"post_{platform}.png")

            results[platform] = self.generate_image(
                prompt=prompt,
                platform=platform,
                quality=quality,
                style=style,
                save_path=save_path,
            )
        return results

    def _enhance_prompt(
        self, prompt: str, platform: str, config
    ) -> str:
        """
        Enrichit le prompt DALL-E avec des directives spécifiques à la plateforme.
        
        Args:
            prompt: Prompt original
            platform: Nom de la plateforme
            config: Configuration de la plateforme
            
        Returns:
            Prompt enrichi
        """
        platform_hints = {
            "linkedin": (
                "Professional, corporate style. Clean and modern design. "
                "Suitable for business social media. "
                "No text or watermarks in the image. "
                "High contrast, professional color palette."
            ),
            "instagram": (
                "Eye-catching, vibrant and aesthetic. Instagram-worthy composition. "
                "Bold colors, strong visual impact. "
                "No text or watermarks. "
                "Square composition optimized for mobile viewing."
            ),
            "twitter": (
                "Bold, attention-grabbing visual. Clean composition. "
                "Works well as a wide banner format. "
                "No text or watermarks. Simple yet impactful. "
                "Optimized for fast scrolling consumption."
            ),
        }

        hint = platform_hints.get(platform, "")
        return f"{prompt}. {hint}"

    def _save_image_from_url(self, url: str, save_path: str) -> None:
        """Télécharge et sauvegarde une image depuis une URL."""
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(response.content)

    @staticmethod
    def display_image_from_url(url: str):
        """
        Affiche une image depuis une URL dans un notebook Jupyter.
        
        Args:
            url: URL de l'image à afficher
        """
        try:
            from IPython.display import display, Image as IPImage
            response = requests.get(url, timeout=30)
            display(IPImage(data=response.content))
        except ImportError:
            print(f"Affichage notebook indisponible. URL : {url}")

    @staticmethod
    def get_platform_image_info() -> str:
        """Retourne un résumé des dimensions d'images par plateforme."""
        from .platforms import PLATFORMS
        lines = ["Dimensions d'images par plateforme :\n"]
        for name, config in PLATFORMS.items():
            lines.append(
                f"  • {config.display_name} : "
                f"{config.image_dimensions[0]}×{config.image_dimensions[1]}px "
                f"(DALL-E: {config.dalle_size})"
            )
        return "\n".join(lines)
