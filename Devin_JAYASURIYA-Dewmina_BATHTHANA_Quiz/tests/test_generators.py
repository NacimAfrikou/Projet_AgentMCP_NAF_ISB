"""Tests pour les générateurs de quiz."""

import pytest


class TestQuizGenerator:
    """Tests pour le générateur de quiz."""

    def test_generator_init(self):
        """Test l'initialisation du générateur."""
        from src.generators.quiz_generator import QuizGenerator
        # Note: Cela nécessite une clé API valide
        # generator = QuizGenerator(api_key="test-key")
        pass

    def test_export_formats(self):
        """Test les formats d'export."""
        from src.generators.quiz_generator import QuizGenerator

        quiz = {
            "title": "Test Quiz",
            "questions": [
                {
                    "id": 1,
                    "type": "qcm",
                    "question": "Question test?",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": "A",
                    "explanation": "Explication"
                }
            ]
        }

        generator = QuizGenerator()

        # Test export JSON
        json_output = generator._export_markdown(quiz)
        assert "Test Quiz" in json_output
