# C3 - Créateur de Posts Réseaux Sociaux

**Difficulté : 2/5**

Outil intelligent de génération de contenus (textes + visuels) optimisés pour les principales plateformes de réseaux sociaux : **LinkedIn**, **Instagram** et **Twitter/X**.

---

## Description

Ce projet implémente un pipeline complet de création de posts pour réseaux sociaux, exploitant l'IA générative pour :

1. **Adapter le ton et le format** selon la plateforme cible (professionnel sur LinkedIn, visuel sur Instagram, concis sur Twitter/X)
2. **Générer des visuels** aux dimensions appropriées via DALL-E 3
3. **Suggérer des hashtags** pertinents et des **moments de publication** optimaux
4. **Créer des variations A/B** pour tester différentes approches de contenu

---

## Architecture

```
groupe-social-media-creator/
├── README.md                          # Ce fichier
├── requirements.txt                   # Dépendances Python
├── .env.example                       # Template de configuration
├── src/
│   ├── __init__.py                    # Package principal
│   ├── models.py                      # Modèles Pydantic (Structured Outputs)
│   ├── platforms.py                   # Configuration des plateformes
│   ├── generator.py                   # Générateur de posts (texte)
│   ├── image_generator.py            # Générateur de visuels (DALL-E 3)
│   └── utils.py                       # Fonctions utilitaires
├── notebooks/
│   └── social_media_creator.ipynb    # Notebook de démonstration principal
└── examples/
    └── sample_output/                 # Exemples de sorties générées
```

---

## Technologies Utilisées

| Technologie | Usage | Référence |
|-------------|-------|-----------|
| **OpenAI GPT** | Génération de texte structuré | [API OpenAI](https://platform.openai.com/docs/) |
| **OpenAI DALL-E 3** | Génération de visuels | [DALL-E 3 Guide](https://platform.openai.com/docs/guides/images) |
| **Pydantic** | Structured Outputs & validation | [Pydantic Docs](https://docs.pydantic.dev/) |
| **Python 3.10+** | Langage principal | - |
| **Pillow (PIL)** | Traitement d'images | [Pillow Docs](https://pillow.readthedocs.io/) |

---

## Notebooks de Référence (CoursIA)

| Notebook | Description |
|----------|-------------|
| [`GenAI/Images/01-1-OpenAI-DALL-E-3.ipynb`](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Images/01-1-OpenAI-DALL-E-3.ipynb) | Génération de visuels avec DALL-E 3 |
| [`GenAI/Texte/3_Structured_Outputs.ipynb`](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/3_Structured_Outputs.ipynb) | Structuration du contenu avec JSON Schema |
| [`GenAI/Texte/1_OpenAI_Intro.ipynb`](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/1_OpenAI_Intro.ipynb) | Introduction à l'API OpenAI |
| [`GenAI/Texte/2_PromptEngineering.ipynb`](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/2_PromptEngineering.ipynb) | Techniques de prompt engineering |

---

## Références Externes

- [Buffer](https://buffer.com/) — Exemple d'outil de planification de posts
- [Canva AI](https://www.canva.com/ai-image-generator/) — Génération de visuels pour réseaux sociaux
- [Hootsuite Best Times to Post](https://www.hootsuite.com/resources/best-time-to-post-on-social-media) — Données sur les meilleurs moments de publication
- [OpenAI Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs) — Documentation officielle

---

## Installation

### 1. Prérequis

- Python 3.10 ou supérieur
- Clé API OpenAI avec accès GPT-4o et DALL-E 3

### 2. Installation des dépendances

```bash
cd groupe-social-media-creator
pip install -r requirements.txt
```

### 3. Configuration

```bash
cp .env.example .env
# Éditer .env avec votre clé API OpenAI
```

### 4. Utilisation

#### Via le notebook (recommandé)

Ouvrir `notebooks/social_media_creator.ipynb` dans VS Code ou Jupyter et exécuter les cellules.

#### Via Python

```python
from src.generator import SocialMediaGenerator

generator = SocialMediaGenerator()

# Générer un post pour LinkedIn
result = generator.generate_post(
    topic="Lancement de notre nouvelle fonctionnalité IA",
    platform="linkedin",
    tone="professionnel",
    generate_image=True
)

print(result.text)
print(result.hashtags)
print(result.best_posting_time)
```

---

## Fonctionnalités Détaillées

### 1. Adaptation Multi-Plateforme

| Plateforme | Ton | Longueur Max | Format Image | Spécificités |
|------------|-----|-------------|--------------|--------------|
| **LinkedIn** | Professionnel, inspirant | 3000 car. | 1200×627 px | Storytelling, CTA, emojis modérés |
| **Instagram** | Créatif, engageant | 2200 car. | 1080×1080 px | Visuel dominant, hashtags (max 30) |
| **Twitter/X** | Concis, percutant | 280 car. | 1600×900 px | Threads possibles, hashtags (2-3) |

### 2. Génération de Visuels (DALL-E 3)

- Visuels adaptés aux dimensions de chaque plateforme
- Styles cohérents avec l'identité visuelle
- Prompts optimisés pour chaque type de contenu

### 3. Suggestions Intelligentes

- **Hashtags** : Génération contextuelle + tendances par plateforme
- **Timing** : Recommandations basées sur les données d'engagement par plateforme et fuseau horaire
- **CTA** : Appels à l'action adaptés au type de contenu

### 4. Variations A/B

- Génération de 2+ versions pour chaque post
- Variation du ton, de l'accroche, et du CTA
- Scoring comparatif pour aider au choix

---

## Livrables

- [x] Code source Python complet (`src/`)
- [x] Notebook de démonstration interactif (`notebooks/`)
- [x] README documenté (ce fichier)
- [x] Modèles Pydantic pour Structured Outputs
- [x] Génération de visuels DALL-E 3
- [x] Système de hashtags et timing
- [x] Variations A/B

---

## Date de Soutenance

**27 février 2026**

---

## Licence

Voir la licence du repository principal.
