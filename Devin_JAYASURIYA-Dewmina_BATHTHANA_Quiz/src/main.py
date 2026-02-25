"""Point d'entrée CLI pour le Générateur de Quiz."""

import sys
import click
from pathlib import Path

from .config import settings
from .parsers.pdf_parser import PdfParser
from .parsers.docx_parser import DocxParser
from .parsers.pptx_parser import PptxParser
from .parsers.text_parser import TextParser
from .generators.quiz_generator import QuizGenerator


@click.group()
@click.version_option(version="1.0.0", prog_name="quiz-generator")
def cli():
    """Générateur de Quiz - Outil d'automatisation de création de quiz avec IA."""
    pass


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("-o", "--output", type=click.Path(), default="./output", help="Dossier de sortie")
@click.option("-f", "--format", type=click.Choice(["json", "markdown", "anki", "quizlet"]), default="json", help="Format de sortie")
@click.option("-n", "--num-questions", type=int, default=None, help="Nombre de questions")
@click.option("-t", "--question-type", type=click.Choice(["qcm", "ouvert", "mixed"]), default="mixed", help="Type de questions")
@click.option("-d", "--difficulty", type=click.Choice(["1", "2", "3", "4", "5"]), default=None, help="Difficulté cible (1-5)")
@click.option("--api-key", envvar="OPENAI_API_KEY", help="Clé API OpenAI")
def generate(file_path, output, format, num_questions, question_type, difficulty, api_key):
    """
    Génère un quiz à partir d'un document.

    FILE_PATH: Chemin vers le document (PDF, DOCX, PPTX, TXT, MD)
    """
    file_path = Path(file_path)
    output = Path(output)

    # Sélectionner le parser en fonction de l'extension
    extension = file_path.suffix.lower()

    parsers = {
        ".pdf": PdfParser,
        ".docx": DocxParser,
        ".pptx": PptxParser,
        ".txt": TextParser,
        ".md": TextParser,
    }

    if extension not in parsers:
        click.echo(f"Format de fichier non supporté: {extension}")
        click.echo("Formats supportés: PDF, DOCX, PPTX, TXT, MD")
        sys.exit(1)

    # Parse le document
    click.echo(f"Parsing du fichier: {file_path}")
    parser = parsers[extension](file_path)
    sections = parser.parse()
    click.echo(f"Nombre de sections trouvées: {len(sections)}")

    # Génère le quiz
    click.echo("Génération du quiz avec l'IA...")

    # Configurer le générateur
    generator = QuizGenerator(api_key=api_key)

    # Générer le quiz
    quiz = generator.generate_quiz_from_sections(
        sections,
        num_questions=num_questions,
        question_types=(
            ["qcm"] if question_type == "qcm"
            else ["ouvert"] if question_type == "ouvert"
            else ["qcm", "ouvert"]
        ),
        difficulty=int(difficulty) if difficulty else None
    )

    # Exporter le quiz
    output_path = generator.export_quiz(quiz, format=format, output_path=output)
    click.echo(f"Quiz généré avec succès: {output_path}")

    # Afficher un résumé
    click.echo(f"\nRésumé du quiz:")
    click.echo(f"  - Titre: {quiz.get('title', 'N/A')}")
    click.echo(f"  - Questions: {len(quiz.get('questions', []))}")
    click.echo(f"  - Format: {format}")


@cli.command()
def config():
    """Affiche la configuration actuelle."""
    click.echo("Configuration du Générateur de Quiz:")
    click.echo(f"  - Modèle: {settings.openai_model}")
    click.echo(f"  - Langue: {settings.output_language}")
    click.echo(f"  - Difficulté par défaut: {settings.default_difficulty}")
    click.echo(f"  - Nombre min de questions: {settings.min_questions}")
    click.echo(f"  - Nombre max de questions: {settings.max_questions}")


if __name__ == "__main__":
    cli()
