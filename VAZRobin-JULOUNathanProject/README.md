# Revieweur de Code IA

## Description

Outil d'analyse de code automatique utilisant l'IA pour:
- Parser les diffs et Pull Requests
- Detecter les patterns problematiques
- Suggerer des ameliorations avec explications
- Verifier le respect des conventions
- Fournir un rapport structure et lisible

---

## Architecture Technique

```
VAZRobin-JULOUNathanProject/
├── src/
│   ├── __init__.py
│   ├── main.py              # Point d'entree CLI
│   ├── config.py            # Configuration
│   ├── parsers/             # Parsing de code/diffs
│   │   ├── __init__.py
│   │   ├── git_parser.py
│   │   └── diff_parser.py
│   ├── analyzers/           # Analyseurs de code
│   │   ├── __init__.py
│   │   ├── security_analyzer.py
│   │   ├── performance_analyzer.py
│   │   └── style_analyzer.py
│   ├── llm/                 # Integration LLM
│   │   ├── __init__.py
│   │   ├── openai_client.py
│   │   └── anthropic_client.py
│   └── reporters/           # Rapports
│       ├── __init__.py
│       ├── markdown_reporter.py
│       └── console_reporter.py
├── tests/                   # Tests unitaires
├── docs/                    # Documentation
├── slides/                  # Presentation
├── .env.example             # Template variables d'environnement
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Installation

### Pre-requis

- Python 3.10 ou superieur
- Git
- Une cle API OpenAI ou Anthropic

### Etapes

1. Cloner le depot:
```bash
git clone <votre-fork-url>
cd 2025-MSBNS3IN03-GenAI/VAZRobin-JULOUNathanProject
```

2. Creer un environnement virtuel:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Installer les dependances:
```bash
pip install -r requirements.txt
```

4. Configurer les variables d'environnement:
```bash
cp .env.example .env
# Editez .env avec vos cles API
```

---

## Utilisation

### Ligne de commande

Analyser un fichier:
```bash
python -m src.main analyze fichier.py
```

Analyser un diff:
```bash
python -m src.main review --diff HEAD~1..HEAD
```

Analyser une Pull Request:
```bash
python -m src.main review --pr 123
```

---

## Notebooks de Reference

Ce projet s'appuie sur les notebooks suivants du cours:

| Notebook | Description |
|----------|-------------|
| [GenAI/Vibe-Coding/Claude-Code-101.ipynb](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Vibe-Coding/Claude-Code-101.ipynb) | Assistance au code avec Claude |
| [GenAI/Texte/3_Structured_Outputs.ipynb](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/3_Structured_Outputs.ipynb) | Rapports de review structures |

---

## References Externes

- [CodeRabbit](https://coderabbit.ai/) - Review automatique de PR
- [Sourcery](https://sourcery.ai/) - Refactoring automatique
- [SonarQube](https://www.sonarsource.com/products/sonarqube/) - Analyse statique
- [GitHub Copilot PR Review](https://docs.github.com/en/copilot/using-github-copilot/code-review/using-copilot-code-review)

---

## Developpement

### Lancer les tests
```bash
pytest tests/
```

### Avec couverture
```bash
pytest --cov=src tests/
```

---

## Calendrier du Projet

| Etape | Date | Statut |
|-------|------|--------|
| Initialisation | 5 fevrier 2026 | En cours |
| Developpement core | A venir | |
| Tests et validation | A venir | |
| Documentation | A venir | |
| Soumission PR | 25 fevrier 2026 | |
| Soutenance | 27 fevrier 2026 | |

---

## License

Ce projet est soumis aux memes conditions que le depot parent.
