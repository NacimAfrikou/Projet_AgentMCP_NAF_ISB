## Extracteur de Données Structurées pour Factures PDF

Ce projet fait partie du cours **MSBNS3IN03 - Intelligence Artificielle Générative**.

Objectif : développer un petit outil qui lit des **factures PDF simples** et extrait
des informations structurées (numéro de facture, date, montants, etc.) au format **JSON**,
sans utiliser d’API externes (pas de clé OpenAI / Azure).

### Fonctionnalités prévues

- Lecture de factures PDF (texte clairement extractible, pas de cas OCR complexe).
- Extraction par règles (regex, heuristiques simples) des champs principaux.
- Validation et normalisation des données (dates, montants).
- Export en JSON avec un schéma fixe.

### Installation rapide

Depuis la racine du dépôt (où se trouve ce dossier) :

```bash
cd groupe-extracteur-factures
python -m venv .venv
.\.venv\Scripts\activate  # sous Windows PowerShell
pip install -r requirements.txt
```

### Utilisation (prévisionnelle)

```bash
python -m src.cli --input samples/facture_exemple.pdf --output output.json
```

Ce README sera complété au fur et à mesure avec :
- la description détaillée de l’architecture,
- les exemples d’entrée / sortie,
- et les instructions de démonstration.

