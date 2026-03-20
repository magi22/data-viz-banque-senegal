# Positionnement des Banques au Sénégal — Dashboard Interactif

Projet de data visualisation sur le secteur bancaire sénégalais.

## Structure du projet

```
projet_banques/
├── app.py                  : Application Flask principale (orchestre Flask + Dash)
├── dashboard.py            : Dashboard Dash interactif (secteur bancaire)
├── scraping_bceao.py       : Téléchargement du rapport PDF BCEAO
├── ocr_pdf.py              : Extraction des tableaux PDF (pdfplumber + pytesseract)
├── nettoyage.py            : Nettoyage et fusion des données
├── mongodb_loader.py       : Chargement dans MongoDB
├── test_donnees.py         : Tests unitaires (pytest)
├── requirements.txt
├── README.md
└── data/
    ├── BASE_SENEGAL2.xlsx
    └── rapport_bceao_2022.pdf
```

## Sources de données

- **BASE_SENEGAL2.xlsx** : données 2015–2020, 24 banques sénégalaises
- **rapport_bceao_2022.pdf** : rapport BCEAO (bilans et comptes de résultat), données 2020–2022

## Installation

```bash
pip install -r requirements.txt
```

Installer aussi Tesseract OCR :
- Windows : https://github.com/UB-Mannheim/tesseract/wiki
- Linux : `sudo apt install tesseract-ocr`
- Mac : `brew install tesseract`

## Lancement

```bash
# 1 - télécharger le rapport PDF BCEAO
python scraping_bceao.py

# 2 - extraire les données du PDF
python ocr_pdf.py

# 3 - nettoyer et fusionner les données
python nettoyage.py

# 4 - charger dans MongoDB
python mongodb_loader.py

# 5 - lancer l'application
python app.py
```

## Tests

```bash
python -m pytest test_donnees.py -v
```

## MongoDB

L'application se connecte à MongoDB en local par défaut (`mongodb://localhost:27017/`).
Pour utiliser MongoDB Atlas, modifier la variable `MONGO_URI` dans `mongodb_loader.py`.

## Déploiement

Le projet est prêt pour Render ou Railway :
- Ajouter la variable d'environnement `MONGO_URI`
- Le fichier `requirements.txt` inclut toutes les dépendances

## Pipeline complet

```
BASE_SENEGAL2.xlsx ──┐
                      ├─→ nettoyage.py ─→ banques_clean.csv ─→ mongodb_loader.py ─→ MongoDB ─→ app.py
rapport_bceao_2022.pdf ─→ ocr_pdf.py ─→ bceao_extrait.csv ──┘
```
