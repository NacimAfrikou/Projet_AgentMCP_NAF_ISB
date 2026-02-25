## Projet NAF_ISB – Extracteur de Données Structurées

Ce projet est un **extracteur de données structurées** (sujet H5 du cours MSBNS3IN03 IA Générative).
Il vise à transformer des documents non structurés (par ex. factures, formulaires) en **données JSON** prêtes à être exploitées en data science.

### Objectifs

- **Reconnaître** différents types de documents (ex. facture, formulaire simple).
- **Extraire** les champs pertinents (ex. date, montant TTC, fournisseur, lignes de facture).
- **Valider et normaliser** les données extraites (formats de dates, numéros, montants).
- **Exporter** les résultats dans un format **JSON structuré** (et éventuellement CSV).

### Formats de fichiers supportés

L'application supporte maintenant plusieurs types de fichiers non structurés :

- **📄 PDF** - Documents PDF (via pdfplumber)
- **📝 Word** - Documents Microsoft Word (.docx)
- **📃 Texte** - Fichiers texte brut (.txt, .text)
- ** Excel** - Fichiers Excel (.xlsx, .xls)
- **📈 CSV** - Fichiers CSV

L'extraction de texte est automatiquement adaptée selon le type de fichier détecté.

### Installation

1. Se placer à la racine du dépôt cloné :

```bash
cd "c:\Users\Nacim\Projet IA Generative\Projet_AgentMCP_NAF_ISB"
```

2. Créer et activer un environnement virtuel (ex. Python 3.11) :

```bash
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Installer les dépendances du projet :

```bash
pip install --upgrade pip
pip install -r NAF_ISB/requirements.txt
```

### Utilisation rapide

Une fois l’environnement installé, vous pourrez lancer une première extraction (prototype) avec :

```bash
cd NAF_ISB
python -m src.main --input "data/input/mon_fichier.pdf" --output "data/output/resultat.json"
```

L'application accepte différents formats de fichiers (PDF, DOCX, TXT, images, Excel, CSV).

**Interface web Streamlit :**

Pour utiliser l'interface web interactive :

```bash
streamlit run app.py
```

Ou double-cliquez sur `run_app.bat` pour démarrer l'interface automatiquement.

### Structure du projet

```text
NAF_ISB/
|-- README.md
|-- requirements.txt
|-- .env.example
|-- .gitignore
|-- src/
|   |-- __init__.py
|   |-- main.py
|-- data/
|   |-- input/
|   |-- output/
|-- tests/
|-- docs/
|-- slides/
```

Les sous-dossiers `tests`, `docs` et `slides` seront remplis au fur et à mesure du développement.

