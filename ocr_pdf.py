

import os
import re
import pandas as pd
import pdfplumber
import pytesseract
from pdf2image import convert_from_path

PDF_BCEAO    = "data/rapport_bceao_2022.pdf"
FICHIER_SORTIE = "data/bceao_extrait.csv"

# Pages du rapport 2022 contenant les données Sénégal
PAGES_SENEGAL = range(266, 330)
ANNEES = [2020, 2021, 2022]


def extraire_nombres(ligne):
    """Extrait les valeurs numériques d'une ligne de texte."""
    tokens = re.findall(r"-?\d{1,3}(?:\s\d{3})*|\d+", ligne)
    valeurs = []
    for t in tokens:
        try:
            v = float(t.replace(" ", ""))
            if abs(v) < 1_000_000_000:
                valeurs.append(v)
        except ValueError:
            pass
    return valeurs


def extraire_via_texte(pdf_path):
    """
    Méthode 1 : extraction directe depuis un PDF avec texte natif.
    Fonctionne sur la majorité des rapports BCEAO.
    """
    records = []
    sigle = nom = type_page = None

    with pdfplumber.open(pdf_path) as pdf:
        for idx in PAGES_SENEGAL:
            if idx >= len(pdf.pages):
                break

            page = pdf.pages[idx]
            texte = page.extract_text()
            if not texte:
                continue

            lignes = [l.strip() for l in texte.split("\n") if l.strip()]

            # Détection de l'en-tête de page
            if len(lignes) >= 2 and "SENEGAL" in lignes[0].upper():
                sigle = lignes[1].strip()
                type_page = None
                for l in lignes:
                    if re.search(r"Bilans?\s+2020", l, re.I):
                        type_page = "bilan"
                        break
                    if re.search(r"R.sultat\s+2020", l, re.I):
                        type_page = "resultat"
                        break
                nom = next(
                    (l for l in lignes
                     if len(l) > 10 and l.upper() == l
                     and any(c.isalpha() for c in l)
                     and "SENEGAL" not in l and l != sigle),
                    None
                )

            if not sigle or not type_page:
                continue

            # Indicateurs à extraire
            mapping_bilan = {
                "caisse_bceao":       ["caisse, banque centrale"],
                "effets_publics":     ["effets publics"],
                "creances_clientele": ["créances sur la clientèle"],
                "total_actif":        ["total actif"],
            }
            mapping_resultat = {
                "interets_produits": ["intérêts et produits assimilés"],
                "interets_charges":  ["intérêts et charges assimilées"],
                "commissions_prod":  ["commissions (produits)"],
                "commissions_charg": ["commissions (charges)"],
                "pnb":               ["produit net bancaire"],
                "charges_exploit":   ["charges générales d'exploitation"],
                "rbe":               ["résultat brut d'exploitation"],
                "cout_risque":       ["coût du risque"],
                "resultat_net":      ["résultat net"],
            }

            mapping = mapping_bilan if type_page == "bilan" else mapping_resultat

            for ligne in lignes:
                ll = ligne.lower()
                vals = extraire_nombres(ligne)
                if not vals:
                    continue
                for indicateur, mots_cles in mapping.items():
                    if any(m in ll for m in mots_cles):
                        for i, annee in enumerate(ANNEES):
                            if i < len(vals):
                                records.append({
                                    "sigle": sigle,
                                    "nom": nom,
                                    "annee": annee,
                                    "indicateur": indicateur,
                                    "valeur": vals[i],
                                })
                        break

    return records


def extraire_via_ocr(pdf_path, pages=None):
    """
    Méthode 2 : OCR avec pytesseract sur les pages scannées.
    Utilisé quand pdfplumber ne trouve pas de texte (pages en image).
    """
    print(f"OCR sur {pdf_path}...")
    records = []

    try:
        images = convert_from_path(pdf_path, dpi=200)
    except Exception as e:
        print(f"Erreur conversion en images : {e}")
        return records

    pages_a_traiter = pages if pages else range(len(images))

    # Indicateurs ciblés par l'OCR
    indicateurs_ocr = {
        "pnb":            ["produit net bancaire"],
        "resultat_net":   ["résultat net"],
        "charges_exploit":["charges générales d'exploitation"],
        "total_actif":    ["total actif"],
    }

    for idx in pages_a_traiter:
        if idx >= len(images):
            break

        image = images[idx]
        image = image.convert("L")
        image = image.point(lambda x: 0 if x < 180 else 255, "1")

        texte = pytesseract.image_to_string(image, lang="fra", config="--psm 6")
        lignes = [l.strip() for l in texte.split("\n") if l.strip()]

        sigle = None
        for i, ligne in enumerate(lignes):
            if "SENEGAL" in ligne.upper() and i + 1 < len(lignes):
                sigle = lignes[i + 1].strip()

        if not sigle:
            continue

        for ligne in lignes:
            ll = ligne.lower()
            vals = extraire_nombres(ligne)
            if not vals:
                continue
            for indicateur, mots_cles in indicateurs_ocr.items():
                if any(m in ll for m in mots_cles):
                    for j, annee in enumerate(ANNEES):
                        if j < len(vals):
                            records.append({
                                "sigle": sigle,
                                "nom": None,
                                "annee": annee,
                                "indicateur": indicateur,
                                "valeur": vals[j],
                            })
                    break

    return records


def construire_dataframe(records):
    """Transforme la liste de records en DataFrame propre."""
    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)
    df = df.drop_duplicates(subset=["sigle", "annee", "indicateur"], keep="first")

    df_pivot = df.pivot_table(
        index=["sigle", "nom", "annee"],
        columns="indicateur",
        values="valeur",
        aggfunc="first"
    ).reset_index()
    df_pivot.columns.name = None

    # Harmonisation des sigles
    remap = {
        "B.A-S.": "BA-S", "B.A.-S.": "BA-S", "B.H.S.": "BHS",
        "B.I.S.": "BIS", "B.N.D.E": "BNDE", "B.R.M.": "BRM",
        "C.D.S.": "CDS", "U.B.A.": "UBA", "BOA-S": "BOA",
        "SGSN": "SGBS", "NSIA BANQUE": "NSIA", "CBI-SENEGAL": "CBI",
        "BGFI BANK": "BGFI",
    }
    df_pivot["sigle"] = df_pivot["sigle"].replace(remap)

    return df_pivot


def extraire_pdf(pdf_path):
    """
    Lance d'abord l'extraction texte.
    Si le résultat est vide, bascule sur l'OCR.
    """
    print(f"Traitement : {pdf_path}")

    records = extraire_via_texte(pdf_path)

    if not records:
        print("Texte non trouvé — passage en OCR...")
        records = extraire_via_ocr(pdf_path)

    return construire_dataframe(records)


if __name__ == "__main__":
    if not os.path.exists(PDF_BCEAO):
        print(f"PDF introuvable : {PDF_BCEAO}")
        print("Lancer d'abord scraping_bceao.py")
    else:
        df = extraire_pdf(PDF_BCEAO)
        if not df.empty:
            df.to_csv(FICHIER_SORTIE, index=False)
            print(f"\nExtraction terminée : {len(df)} lignes → {FICHIER_SORTIE}")
        else:
            print("Aucune donnée extraite.")
