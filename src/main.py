"""
Point d'entrée principal de l'extracteur de données structurées.
Orchestre les différentes étapes: lecture, reconnaissance, extraction, validation, export.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional, Union

# Import des modules du package
from src.recognizer import recognize_document, get_available_document_types
from src.extractor import extract_all_data
from src.validator import InvoiceModel, FormModel, DocumentModel
from src.exporter import export_to_json, validate_json_output

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def read_file_content(filepath: str) -> str:
    """
    Lit le contenu d'un fichier (texte ou PDF).

    Args:
        filepath: Chemin du fichier

    Returns:
        Le texte extrait du fichier
    """
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"Fichier non trouvé: {filepath}")

    extension = path.suffix.lower()

    if extension in ['.txt', '.text']:
        # Fichier texte simple
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    elif extension in ['.pdf']:
        # Fichier PDF - essayer PyMuPDF ou pdfplumber
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(filepath)
            text = "".join([page.get_text() for page in doc])
            return text
        except ImportError:
            try:
                import pdfplumber
                with pdfplumber.open(filepath) as pdf:
                    text = "".join([page.extract_text() for page in pdf.pages])
                    return text
            except ImportError:
                raise ImportError(
                    "Pour lire des PDF, installer PyMuPDF ou pdfplumber: "
                    "pip install PyMuPDF pdfplumber"
                )
    else:
        # Fallback: essayer comme fichier texte
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()


def process_document(
    filepath: str,
    output_dir: str = "data/output",
    document_type: Optional[str] = None,
    confidence_threshold: float = 0.2
) -> Optional[DocumentModel]:
    """
    Traite un document complet: lecture -> reconnaissance -> extraction -> validation -> export.

    Args:
        filepath: Chemin du document à traiter
        output_dir: Dossier de sortie pour le JSON
        document_type: Type de document forcé (None = auto-détection)
        confidence_threshold: Seuil de confiance minimum pour l'auto-détection

    Returns:
        Instance de DocumentModel ou None en cas d'erreur
    """
    try:
        logger.info(f"Démarrage du traitement du fichier: {filepath}")

        # Étape 1: Lire le contenu
        text = read_file_content(filepath)
        if not text or len(text.strip()) == 0:
            logger.error("Le fichier est vide ou ne contient pas de texte lisible")
            return None

        logger.info(f"Contenu lu: {len(text)} caractères")

        # Étape 2: Reconnaître le type de document
        if document_type is None:
            detected_type, confidence = recognize_document(text)
            logger.info(f"Type détecté: {detected_type} (confiance: {confidence})")

            if confidence < confidence_threshold:
                logger.warning(
                    f"Confiance trop faible ({confidence} < {confidence_threshold}). "
                    f"Utiliser l'argument --type pour forcer le type."
                )
                return None
        else:
            detected_type = document_type
            confidence = 1.0
            logger.info(f"Type forcé: {detected_type}")

        # Étape 3: Extraire les données
        extracted_data = extract_all_data(text, detected_type)
        logger.info(f"Données extraites: {len(extracted_data)} champs")

        # Étape 4: Créer le modèle de validation approprié
        if detected_type == 'facture':
            model = InvoiceModel(**extracted_data)
        elif detected_type == 'formulaire':
            model = FormModel(**extracted_data)
        else:
            model = DocumentModel(
                document_type=detected_type,
                extracted_data=extracted_data,
                confidence_score=confidence
            )

        # Étape 5: Valider le modèle
        try:
            if detected_type == 'facture':
                validated = InvoiceModel(**model.model_dump())
            elif detected_type == 'formulaire':
                validated = FormModel(**model.model_dump())
            else:
                validated = model
        except Exception as e:
            logger.error(f"Validation échouée: {e}")
            return None

        # Étape 6: Exporter vers JSON
        result_dict = validated.model_dump()
        result_dict['document_type'] = detected_type
        result_dict['confidence_score'] = confidence

        filepath_out = export_to_json(
            result_dict,
            output_dir=output_dir,
            source_file=filepath
        )

        if filepath_out:
            logger.info(f"Résultat exporté vers: {filepath_out}")
            return validated
        else:
            logger.error("Échec de l'export JSON")
            return None

    except FileNotFoundError as e:
        logger.error(f"Fichier introuvable: {e}")
        return None
    except Exception as e:
        logger.error(f"Erreur lors du traitement: {e}")
        return None


def process_directory(
    input_dir: str,
    output_dir: str = "data/output",
    document_type: Optional[str] = None
) -> list:
    """
    Traite tous les fichiers d'un dossier.

    Args:
        input_dir: Dossier contenant les documents à traiter
        output_dir: Dossier de sortie pour les JSON
        document_type: Type de document forcé (None = auto-détection)

    Returns:
        Liste des résultats DocumentModel
    """
    path = Path(input_dir)
    if not path.exists():
        raise FileNotFoundError(f"Dossier introuvable: {input_dir}")

    results = []
    extensions = ['.txt', '.text', '.pdf']

    for filepath in path.iterdir():
        if filepath.suffix.lower() in extensions and filepath.is_file():
            logger.info(f"\n{'='*60}")
            logger.info(f"Traitement de: {filepath.name}")
            logger.info(f"{'='*60}")

            result = process_document(
                str(filepath),
                output_dir=output_dir,
                document_type=document_type
            )
            results.append(result)

    return results


def main():
    """Fonction principale pour l'interface CLI."""
    parser = argparse.ArgumentParser(
        description="Extracteur de Données Structurées - "
                    "Transforme des documents non structurés en données JSON."
    )

    parser.add_argument(
        '--input', '-i',
        type=str,
        required=True,
        help="Chemin du fichier ou dossier à traiter"
    )

    parser.add_argument(
        '--output', '-o',
        type=str,
        default="data/output",
        help="Dossier de sortie pour les JSON (par défaut: data/output)"
    )

    parser.add_argument(
        '--type', '-t',
        type=str,
        choices=get_available_document_types() + ['inconnu'],
        default=None,
        help="Type de document (détection automatique si non spécifié)"
    )

    parser.add_argument(
        '--directory', '-d',
        action='store_true',
        help="Traite tous les fichiers du dossier spécifié"
    )

    parser.add_argument(
        '--list-types',
        action='store_true',
        help="Affiche la liste des types de documents reconnus"
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help="Mode verbeux"
    )

    args = parser.parse_args()

    # Mode liste des types
    if args.list_types:
        print("Types de documents reconnus:")
        for t in get_available_document_types():
            print(f"  - {t}")
        sys.exit(0)

    # Configuration du niveau de logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Vérifier que le dossier de sortie existe
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)

    try:
        if args.directory:
            logger.info(f"Traitement du dossier: {args.input}")
            results = process_directory(
                args.input,
                output_dir=args.output,
                document_type=args.type
            )
            success_count = sum(1 for r in results if r is not None)
            logger.info(f"\nTraitement terminé: {success_count}/{len(results)} documents traités avec succès")
        else:
            logger.info(f"Traitement du fichier: {args.input}")
            result = process_document(
                args.input,
                output_dir=args.output,
                document_type=args.type
            )

            if result:
                logger.info("\nTraitement terminé avec succès!")
                print(f"\nRésultat JSON:")
                print(result.model_dump_json(indent=2))
            else:
                logger.error("\nTraitement échoué")
                sys.exit(1)

    except Exception as e:
        logger.error(f"Erreur fatale: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
