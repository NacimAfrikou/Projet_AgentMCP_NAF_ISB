# Client LLM pour le Générateur de Quiz
"""Module de communication avec les API LLM (OpenAI, Anthropic)."""

from typing import Optional, Dict, Any, List
from pathlib import Path
import os

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


__all__ = ["LLMClient"]


class LLMClient:
    """Client unifié pour les API LLM."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        provider: str = "openai"
    ):
        """
        Initialise le client LLM.

        Args:
            api_key: Clé API pour l'accès au LLM
            model: Modèle à utiliser
            provider: Fournisseur ("openai" ou "anthropic")
        """
        self.provider = provider
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")

        if provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError("Le package 'openai' n'est pas installé.")
            if not self.api_key:
                raise ValueError("Une clé API OpenAI est requise.")
            self.client = OpenAI(api_key=self.api_key)

        elif provider == "anthropic":
            if not ANTHROPIC_AVAILABLE:
                raise ImportError("Le package 'anthropic' n'est pas installé.")
            if not self.api_key:
                raise ValueError("Une clé API Anthropic est requise.")
            self.client = anthropic.Anthropic(api_key=self.api_key)

        else:
            raise ValueError(f"Provider inconnu: {provider}")

    def generate(
        self,
        prompt: str,
        response_format: Optional[Dict[str, Any]] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Génère du texte à partir d'un prompt.

        Args:
            prompt: Le prompt à envoyer au modèle
            response_format: Format de réponse attendu (ex: {"type": "json_object"})
            max_tokens: Nombre maximal de tokens à générer
            temperature: Température pour la génération

        Returns:
            Texte généré par le modèle
        """
        if self.provider == "openai":
            return self._generate_openai(prompt, response_format, max_tokens, temperature)
        else:
            return self._generate_anthropic(prompt, max_tokens, temperature)

    def _generate_openai(
        self,
        prompt: str,
        response_format: Optional[Dict[str, Any]] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7
    ) -> str:
        """Génère du texte avec OpenAI."""
        messages = [
            {"role": "system", "content": "Vous êtes un assistant expert et précis."},
            {"role": "user", "content": prompt}
        ]

        params = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        if response_format:
            params["response_format"] = response_format

        response = self.client.chat.completions.create(**params)
        return response.choices[0].message.content

    def _generate_anthropic(
        self,
        prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.7
    ) -> str:
        """Génère du texte avec Anthropic."""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text

    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Génère des embeddings pour une liste de textes.

        Args:
            texts: Liste de textes à embedding

        Returns:
            Liste de vecteurs d'embedding
        """
        if self.provider == "openai":
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            return [data.embedding for data in response.data]
        else:
            # Anthropic ne fournit pas d'embedding natif
            raise NotImplementedError(
                "Les embeddings ne sont pas supportés par l'API Anthropic."
            )
