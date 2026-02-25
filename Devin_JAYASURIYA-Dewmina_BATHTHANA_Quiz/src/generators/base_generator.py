"""Générateur de base pour les quiz."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path


class BaseGenerator(ABC):
    """Classe de base pour tous les générateurs de quiz."""

    def __init__(self, output_path: str | Path = "./output"):
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def generate_quiz(self, content: str | List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """Génère un quiz à partir du contenu fourni."""

    @abstractmethod
    def export_quiz(self, quiz: Dict[str, Any], format: str = "json", **kwargs) -> str:
        """Exporte le quiz dans un format spécifique."""

    def validate_quiz(self, quiz: Dict[str, Any]) -> bool:
        """Valide la structure du quiz."""
        required_fields = ["title", "questions"]
        return all(field in quiz for field in required_fields)
