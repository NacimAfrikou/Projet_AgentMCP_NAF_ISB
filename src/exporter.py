"""
Module d'export des données vers JSON.
Gère la sauvegarde des résultats structurés.
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from src.validator import DocumentModel


def create_output_directory(output_dir: str) -> Path:
    """
    Crée le dossier de sortie s'il n'existe pas.

    Args:
        output_dir: Chemin du dossier de sortie

    Returns:
        Path objet représentant le dossier
    """
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def generate_filename(document_type: str, source_file: str) -> str:
    """
    Génère un nom de fichier unique pour le JSON exporté.

    Args:
        document_type: Type de document
        source_file: Nom du fichier source

    Returns:
        Nom de fichier unique (ex: facture_abc123_20240115.json)
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    extraction_id = uuid.uuid4().hex[:8]
    clean_source = Path(source_file).stem.replace(' ', '_')

    return f"{document_type}_{clean_source}_{extraction_id}_{timestamp}.json"


def export_to_json(
    data: Dict[str, Any],
    output_dir: str = "data/output",
    filename: Optional[str] = None,
    source_file: str = "unknown",
    indent: int = 2
) -> Optional[str]:
    """
    Exporte les données structurées vers un fichier JSON.

    Args:
        data: Dictionnaire des données à exporter
        output_dir: Dossier de sortie (par défaut: data/output)
        filename: Nom du fichier (généré automatiquement si None)
        source_file: Nom du fichier source pour la trace
        indent: Indentation JSON (par défaut: 2)

    Returns:
        Chemin complet du fichier créé, ou None en cas d'erreur
    """
    try:
        # Créer le dossier de sortie
        output_path = create_output_directory(output_dir)

        # Générer le nom de fichier si nécessaire
        if not filename:
            document_type = data.get('document_type', 'document')
            filename = generate_filename(document_type, source_file)

        # Compléter les métadonnées
        if 'metadata' not in data:
            data['metadata'] = {}

        data['metadata']['source_file'] = source_file
        data['metadata']['extraction_id'] = filename.replace('.json', '')
        data['metadata']['extraction_date'] = datetime.now().isoformat()

        # Créer le chemin complet
        filepath = output_path / filename

        # Écrire le fichier JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)

        return str(filepath)

    except Exception as e:
        print(f"Erreur lors de l'export JSON: {e}")
        return None


def export_with_model(
    model: DocumentModel,
    output_dir: str = "data/output",
    filename: Optional[str] = None,
    source_file: str = "unknown",
    indent: int = 2
) -> Optional[str]:
    """
    Exporte un modèle Pydantic vers JSON.

    Args:
        model: Instance de DocumentModel
        output_dir: Dossier de sortie
        filename: Nom du fichier (généré automatiquement si None)
        source_file: Nom du fichier source
        indent: Indentation JSON

    Returns:
        Chemin complet du fichier créé
    """
    data = model.model_dump()
    return export_to_json(data, output_dir, filename, source_file, indent)


def validate_json_output(filepath: str) -> bool:
    """
    Vérifie qu'un fichier JSON est valide.

    Args:
        filepath: Chemin du fichier à vérifier

    Returns:
        True si le fichier est un JSON valide
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            json.load(f)
        return True
    except (json.JSONDecodeError, FileNotFoundError):
        return False


def get_exported_files(output_dir: str = "data/output") -> list:
    """
    Liste les fichiers JSON exportés.

    Args:
        output_dir: Dossier de sortie

    Returns:
        Liste des chemins de fichiers JSON
    """
    path = Path(output_dir)
    if not path.exists():
        return []

    return [str(f) for f in path.glob('*.json')]


def clear_output_directory(output_dir: str = "data/output") -> int:
    """
    Supprime tous les fichiers JSON du dossier de sortie.

    Args:
        output_dir: Dossier de sortie

    Returns:
        Nombre de fichiers supprimés
    """
    path = Path(output_dir)
    if not path.exists():
        return 0

    count = 0
    for f in path.glob('*.json'):
        try:
            f.unlink()
            count += 1
        except OSError:
            pass

    return count
