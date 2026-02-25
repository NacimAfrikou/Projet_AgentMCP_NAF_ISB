# Configuration pour le Générateur de Quiz
"""Module de configuration du générateur de quiz."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Configuration du générateur de quiz."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None

    # Modèles LLM
    openai_model: str = "gpt-4o"
    anthropic_model: str = "claude-3-5-sonnet-latest"
    embedding_model: str = "text-embedding-3-large"

    # Configuration de sortie
    output_language: str = "fr"
    default_difficulty: int = 1  # 1-5
    min_questions: int = 5
    max_questions: int = 20

    # Options de génération
    include_explanations: bool = True
    include_difficulty: bool = True
    shuffle_options: bool = True

    # Chemins
    document_path: str = "."
    output_path: str = "./output"


# Instance globale de configuration
settings = Settings()
