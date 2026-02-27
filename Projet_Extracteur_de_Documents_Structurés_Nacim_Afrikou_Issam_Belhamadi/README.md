# 📄 Extracteur de Documents Structurés

**NAF_ISB** - Projet de traitement automatisé de documents commerciaux (factures, commandes) avec extraction structurée via IA générative (OpenAI GPT-4o-mini).

**Auteurs :** Nacim Afrikou & Issam Belhamadi
**Module :** MSBNS3IN03 - IA Générative
**Année :** 2026

---

## 🚀 Fonctionnalités

| Fonctionnalité | Description |
|----------------|-------------|
| 📄 **Multi-format** | Supporte PDF, Word, Excel, CSV, TXT et Images |
| 🤖 **Détection intelligente** | Identifie automatiquement le type de document (facture / commande) |
| 👁️ **GPT-4 Vision** | Extraction directe depuis des images (PNG, JPG, GIF, WEBP) sans OCR |
| 📦 **Structured Outputs** | JSON valides garanties via Pydantic & OpenAI strict mode |
| 🖥️ **3 interfaces** | CLI, Streamlit (Python), Flask (HTML/CSS/JS) |
| 📤 **Upload batch** | Traitement de plusieurs fichiers simultanément |
| 💾 **Export JSON** | Téléchargement individuel ou groupé |

---

## ⚡ Démarrage Rapide

### Prérequis

- Python 3.8+
- Compte OpenAI avec API Key valide

### 1. Installation

```bash
# Cloner le projet
cd Projet_Extracteur_de_Documents_Structurés_Nacim_Afrikou_Issam_Belhamadi

# Créer et activer l'environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configurer votre clé API OpenAI
cp .env.example .env
# Éditer .env avec votre OPENAI_API_KEY
```

### 2. Choix de l'interface

#### Option A : Interface Streamlit (Recommandé) 🎨

La plus simple et la plus rapide à mettre en œuvre :

```bash
# Double-cliquez sur le fichier :
run_streamlit.bat

# Ou manuellement :
streamlit run interface/app.py
```

**Disponible sur :** http://localhost:8501

#### Option B : Interface Web Flask 🌐

Version complète avec design moderne :

```bash
# Double-cliquez sur le fichier :
run_interface.bat

# Ou manuellement :
python interface/server.py
```

**Disponible sur :** http://localhost:5000

#### Option C : Ligne de commande 💻

Traitement automatisé en batch :

```bash
# Traiter tous les fichiers de data/input
python -m src.main

# Traiter un fichier spécifique
python -m src.main chemin/vers/fichier.pdf

# Traiter un dossier complet
python -m src.main chemin/vers/dossier
```

---

## 🏗️ Architecture

```
Projet_Extracteur_de_Documents_Structurés_Nacim_Afrikou_Issam_Belhamadi/
├── src/
│   ├── __init__.py
│   ├── main.py              # Point d'entrée CLI (typer/rich)
│   ├── models.py            # Modèles Pydantic (Order, Invoice)
│   ├── llm_client.py        # Client OpenAI + Structured Outputs + Vision
│   └── extractors.py        # Pipeline d'extraction multi-format
├── interface/
│   ├── app.py               # Interface Streamlit (Python pur)
│   ├── server.py            # Serveur Flask backend
│   ├── index.html           # Interface web HTML/CSS/JS
│   └── styles.css           # Styles CSS
├── data/
│   ├── input/               # Fichiers à traiter
│   └── output/              # Résultats JSON
├── docs/
│   └── schema_json.md       # Documentation des schémas
├── .env                     # Configuration API (à créer)
├── .env.example             # Template de configuration
├── requirements.txt         # Dépendances Python
├── run_streamlit.bat        # Script de lancement Streamlit
├── run_interface.bat        # Script de lancement Flask
└── README.md                # Documentation
```

---

## 📦 Support des Formats

| Type | Extensions | Méthode | Pipeline |
|------|-----------|---------|----------|
| 📄 PDF | `.pdf` | pdfplumber | Texte → LLM → JSON |
| 📝 Word | `.docx` | python-docx | Texte → LLM → JSON |
| 📃 Texte | `.txt`, `.text` | Lecture directe | Texte → LLM → JSON |
| 📊 Excel | `.xlsx`, `.xls` | pandas/openpyxl | Conversion CSV → LLM → JSON |
| 📈 CSV | `.csv` | pandas | Lecture directe → LLM → JSON |
| 🖼️ Images | `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp` | **GPT-4 Vision** | Base64 → Vision API → JSON |

---

## 🔄 Pipeline d'Extraction

### Pour les documents textuels (PDF, Word, TXT, Excel, CSV)

```
┌─────────────┐     ┌────────────────┐     ┌────────────────┐
│   Fichier   │────▶│ Extraction     │────▶│ Détection type │
│ (PDF/Word)  │     │ Texte          │     │ (LLM)          │
└─────────────┘     └────────────────┘     └────────────────┘
                                                      │
                                                      ▼
┌─────────────┐     ┌────────────────┐     ┌────────────────┐
│   Résultat  │◀────│ Extraction     │◀────│ Extraction     │
│   JSON      │     │ Structurée     │     │ Structurée     │
└─────────────┘     │ (LLM + Pydantic)│    │ (LLM + Pydantic)│
                    └────────────────┘     └────────────────┘
```

### Pour les images (GPT-4 Vision)

```
┌─────────────┐     ┌────────────────┐     ┌────────────────┐
│   Image     │────▶│ Encodage       │────▶│ GPT-4 Vision   │
│ (PNG/JPG)   │     │ Base64         │     │ + Structured   │
└─────────────┘     └────────────────┘     │ Outputs        │
                                           └────────────────┘
                                                    │
                                                    ▼
                                           ┌────────────────┐
                                           │   Résultat     │
                                           │   JSON         │
                                           └────────────────┘
```

---

## 📋 Modèles de Données

### Order (Commande)

```json
{
  "source_file": "order_10999.pdf",
  "document_type": "order",
  "order_id": "10999",
  "order_date": "2018-04-03",
  "shipped_date": "2018-04-10",
  "customer_id": "OTTIK",
  "customer_name": "Ottilies Käseladen",
  "employee_name": "Nancy Davolio",
  "shipper_name": "Speedy Express",
  "shipping": {
    "ship_name": "Ottilies Käseladen",
    "ship_address": "Mehrheimerstr. 369",
    "ship_city": "Köln",
    "ship_postal_code": "50739",
    "ship_country": "Germany"
  },
  "products": [
    {
      "description": "Queso Cabrales",
      "quantity": 15,
      "unit_price": 21.0,
      "line_total": 315.0
    }
  ],
  "total_price": 1261.0,
  "currency": "USD"
}
```

### Invoice (Facture)

```json
{
  "source_file": "facture_001.pdf",
  "document_type": "invoice",
  "invoice_number": "FAC-2024-001",
  "invoice_date": "2024-01-15",
  "due_date": "2024-02-15",
  "seller": {
    "name": "Entreprise ABC",
    "address": "123 Rue Exemple",
    "city": "Paris",
    "postal_code": "75001",
    "country": "France"
  },
  "seller_tax_id": "FR123456789",
  "buyer": {
    "name": "Client XYZ",
    "address": "456 Avenue Test",
    "city": "Lyon",
    "postal_code": "69001",
    "country": "France"
  },
  "items": [
    {
      "description": "Prestation de service",
      "quantity": 1,
      "unit_price": 1500.0,
      "tax_rate": 20.0,
      "line_total": 1500.0
    }
  ],
  "subtotal": 1500.0,
  "tax_amount": 300.0,
  "total": 1800.0,
  "currency": "EUR",
  "payment_terms": "30 jours"
}
```

---

## 🔧 Configuration

### Fichier `.env`

Créez un fichier `.env` à la racine du projet :

```env
# OpenAI API Configuration
OPENAI_API_KEY=sk-votre_clé_api_ici
OPENAI_MODEL=gpt-4o-mini
OPENAI_VISION_MODEL=gpt-4o-mini
```

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `OPENAI_API_KEY` | Clé API OpenAI | **Requis** |
| `OPENAI_MODEL` | Modèle pour extraction texte | `gpt-4o-mini` |
| `OPENAI_VISION_MODEL` | Modèle pour Vision | `gpt-4o-mini` |

---

## 📊 Dépendances

| Package | Version | Usage |
|---------|---------|-------|
| `openai` | >=4.0 | API OpenAI (GPT-4o-mini, Vision) |
| `pydantic` | >=2.0 | Modèles et validation JSON |
| `pdfplumber` | latest | Extraction texte PDF |
| `python-docx` | latest | Fichiers Word |
| `pandas` | latest | Excel/CSV |
| `openpyxl` | latest | Support Excel |
| `python-dotenv` | latest | Variables d'environnement |
| `streamlit` | latest | Interface Streamlit |
| `flask` | latest | Serveur Flask |
| `flask-cors` | latest | Support CORS |

---

## 💡 Utilisation Avancée

### Traitement par lots (CLI)

```bash
# Placer vos fichiers dans data/input/
# Puis exécuter :
python -m src.main
```

### Intégration en Python

```python
from pathlib import Path
from src.extractors import extract_document
from src.models import Invoice, Order

# Extraire d'un fichier
document = extract_document(Path("facture.pdf"))

if isinstance(document, Invoice):
    print(f"Facture: {document.invoice_number} - {document.total} {document.currency}")
elif isinstance(document, Order):
    print(f"Commande: {document.order_id} - {document.total_price} {document.currency}")

# Obtenir le JSON brut
json_data = document.model_dump(mode="json")
```

### Appel API (Flask)

```python
import requests

url = "http://localhost:5000/extract"
files = {"file": open("facture.pdf", "rb")}
response = requests.post(url, files=files)
data = response.json()
```

---

## 🐛 Dépannage

| Erreur | Solution |
|--------|----------|
| `OPENAI_API_KEY manquant` | Vérifiez que `.env` existe et contient votre clé |
| `Module not found` | Installez les dépendances : `pip install -r requirements.txt` |
| `Serveur Flask non disponible` | Vérifiez le port 5000 (ou modifiez dans `server.py`) |
| `Image trop grande` | Réduisez la taille de l'image (< 20MB recommandé) |
| `Extraction peu précise` | Utilisez des images de qualité (min 800x600) |

---

## 🎯 Points Forts du Projet

1. **GPT-4 Vision intégré** : Pas besoin d'OCR externe pour les images
2. **Structured Outputs** : JSON 100% valides, jamais de parsing errors
3. **Pydantic validation** : Typage fort et vérification automatique
4. **Multi-interface** : CLI, Streamlit et Flask pour tous les usages
5. **Support multi-format** : PDF, Word, Excel, CSV, TXT et Images

---

## 📝 Licence

MIT License - Voir le fichier [LICENSE](LICENSE)

---

## 👥 Auteurs

- **Nacim Afrikou** - Développement & Architecture
- **Issam Belhamadi** - Interface & Tests

---

## 🙏 Remerciements

- OpenAI pour l'API GPT-4o-mini et GPT-4 Vision avec Structured Outputs
- Streamlit pour le framework d'interface Python
- La communauté Python pour les bibliothèques utilisées

---

**NB :** Ce projet est développé dans le cadre du module MSBNS3IN03 - IA Générative (2026).
