"""Générateur de quiz utilisant les LLM."""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..config import settings
from ..llm.client import LLMClient


class QuizGenerator:
    """Générateur de quiz à partir de documents."""

    # Templates de prompts pour la génération de quiz
    PROMPT_TEMPLATE = """Vous êtes un expert pédagogique spécialisé dans la création de quiz de formation.
À partir du contenu suivant, générez un quiz avec {num_questions} questions.

## Règles de génération:
1. Créez des questions variées (QCM et questions ouvertes)
2. Incluez des niveaux de difficulté différents (1-5)
3. Pour les QCM, créez {num_options} options avec exactement une bonne réponse
4. Fournissez des explications détaillées pour chaque réponse
5. Utilisez la taxonomie de Bloom pour varier les niveaux cognitifs

## Format de sortie (JSON):
{{
    "title": "Titre du quiz",
    "description": "Description du quiz",
    "questions": [
        {{
            "id": 1,
            "type": "qcm" ou "ouvert",
            "difficulty": 1-5,
            "question": "La question",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "La bonne option ou réponse",
            "explanation": "Explication détaillée"
        }}
    ]
}}

## Contenu:
{content}

## Instructions spécifiques:
- Générez exactement {num_questions} questions
- Mélangez les types de questions
- Assurez-vous que les questions couvrent l'ensemble du contenu
- Les questions doivent être en français
"""

    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialise le générateur de quiz.

        Args:
            model: Modèle LLM à utiliser (gpt-4o, claude-3-5-sonnet-latest, etc.)
            api_key: Clé API pour l'accès au LLM
        """
        self.model = model or settings.openai_model
        self.api_key = api_key or settings.openai_api_key
        self.client = LLMClient(api_key=self.api_key, model=self.model)

    def generate_quiz_from_text(
        self,
        text: str,
        num_questions: int = None,
        num_options: int = 4,
        difficulty: int = None,
        question_types: List[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Génère un quiz à partir d'un texte.

        Args:
            text: Le contenu à partir duquel générer le quiz
            num_questions: Nombre de questions à générer
            num_options: Nombre d'options pour les QCM
            difficulty: Difficulté cible (1-5)
            question_types: Types de questions souhaités ('qcm', 'ouvert')

        Returns:
            Dictionnaire contenant le quiz généré
        """
        num_questions = num_questions or settings.min_questions
        difficulty = difficulty or settings.default_difficulty
        question_types = question_types or ["qcm", "ouvert"]

        # Tronquer le texte si trop long
        max_tokens = 8000
        if len(text) > max_tokens:
            text = text[:max_tokens]

        prompt = self.PROMPT_TEMPLATE.format(
            content=text,
            num_questions=num_questions,
            num_options=num_options
        )

        # Appel au LLM pour générer le quiz
        response = self.client.generate(
            prompt=prompt,
            response_format={"type": "json_object"}
        )

        quiz = json.loads(response)

        # Ajouter des métadonnées
        quiz["metadata"] = {
            "generated_at": datetime.now().isoformat(),
            "model": self.model,
            "num_questions": num_questions,
            "difficulty": difficulty
        }

        return quiz

    def generate_quiz_from_sections(
        self,
        sections: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Génère un quiz à partir de sections parseées.

        Args:
            sections: Liste de sections avec titre et contenu

        Returns:
            Dictionnaire contenant le quiz généré
        """
        # Assembler le contenu des sections
        full_content = ""
        for section in sections:
            title = section.get("title", "Section")
            content = section.get("content", "")
            full_content += f"## {title}\n\n{content}\n\n"

        return self.generate_quiz_from_text(full_content, **kwargs)

    def export_quiz(
        self,
        quiz: Dict[str, Any],
        format: str = "json",
        output_path: str | Path = None,
        **kwargs
    ) -> str:
        """
        Exporte le quiz dans un format spécifique.

        Args:
            quiz: Le quiz à exporter
            format: Format de sortie (json, markdown, anki, quizlet)
            output_path: Chemin de sortie optionnel

        Returns:
            Chaîne de caractères avec le quiz formaté
        """
        output_path = Path(output_path or self.output_path)
        output_path.mkdir(parents=True, exist_ok=True)

        if format == "json":
            content = json.dumps(quiz, indent=2, ensure_ascii=False)
            filename = f"quiz_{quiz.get('title', 'default').replace(' ', '_')}.json"

        elif format == "markdown":
            content = self._export_markdown(quiz)
            filename = f"quiz_{quiz.get('title', 'default').replace(' ', '_')}.md"

        elif format == "anki":
            content = self._export_anki(quiz)
            filename = f"quiz_{quiz.get('title', 'default').replace(' ', '_')}.csv"

        elif format == "quizlet":
            content = self._export_quizlet(quiz)
            filename = f"quiz_{quiz.get('title', 'default').replace(' ', '_')}.txt"

        else:
            raise ValueError(f"Format inconnu: {format}")

        # Écrire le fichier
        full_path = output_path / filename
        full_path.write_text(content, encoding='utf-8')

        return str(full_path)

    def _export_markdown(self, quiz: Dict[str, Any]) -> str:
        """Exporte le quiz en Markdown."""
        lines = [f"# {quiz.get('title', 'Quiz')}", ""]
        if "description" in quiz:
            lines.append(f"{quiz['description']}\n")

        for i, question in enumerate(quiz.get("questions", []), 1):
            lines.append(f"## Question {i}")
            lines.append("")
            lines.append(f"**{question.get('question', '')}**")
            lines.append("")

            if question.get("type") == "qcm":
                for option in question.get("options", []):
                    lines.append(f"- {option}")
                lines.append("")
                lines.append(f"**Réponse correcte:** {question.get('correct_answer')}")
            else:
                lines.append(f"**Réponse:** {question.get('correct_answer')}")

            if question.get("explanation"):
                lines.append("")
                lines.append(f"**Explication:** {question['explanation']}")

            if question.get("difficulty"):
                lines.append("")
                lines.append(f"**Difficulté:** {question['difficulty']}/5")

            lines.append("")

        return "\n".join(lines)

    def _export_anki(self, quiz: Dict[str, Any]) -> str:
        """Exporte le quiz pour Anki (format CSV)."""
        lines = ["Question\tRéponse\tExplication\tDifficulté"]

        for question in quiz.get("questions", []):
            q = question.get("question", "").replace("\t", " ").replace("\n", " ")
            a = question.get("correct_answer", "").replace("\t", " ").replace("\n", " ")
            e = question.get("explanation", "").replace("\t", " ").replace("\n", " ")
            d = question.get("difficulty", 1)

            lines.append(f"{q}\t{a}\t{e}\t{d}")

        return "\n".join(lines)

    def _export_quizlet(self, quiz: Dict[str, Any]) -> str:
        """Exporte le quiz pour Quizlet (format texte)."""
        lines = [f"{quiz.get('title', 'Quiz')}", "=" * 50, ""]

        for question in quiz.get("questions", []):
            lines.append(f"Q: {question.get('question', '')}")
            lines.append(f"A: {question.get('correct_answer', '')}")
            lines.append("")

        return "\n".join(lines)
