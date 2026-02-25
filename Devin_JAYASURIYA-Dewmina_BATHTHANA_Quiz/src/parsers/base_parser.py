"""Parser de base pour les documents."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any


class BaseParser(ABC):
    """Classe de base pour tous les parseurs de documents."""

    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)

    @abstractmethod
    def parse(self) -> List[Dict[str, Any]]:
        """Parse le document et retourne une liste de sections."""

    @abstractmethod
    def extract_text(self) -> str:
        """Extract tout le texte du document."""

    def validate(self) -> bool:
        """Vérifie que le fichier existe et est valide."""
        return self.file_path.exists()
