

import os
import pandas as pd
import numpy as np

FICHIER_EXCEL = "data/BASE_SENEGAL2.xlsx"
FICHIER_BCEAO = "data/bceao_extrait.csv"
FICHIER_SORTIE = "data/banques_clean.csv"

GROUPES = {
    "SGBS": "Internationaux", "BICIS": "Internationaux",
    "CBAO": "Continentaux",   "CDS":   "Continentaux",
    "BHS":  "Locaux",         "CITIBANK": "Internationaux",
    "LBA":  "Locaux",         "BIS":   "Locaux",
    "ECOBANK": "Continentaux","ORABANK": "Continentaux",
    "BOA":  "Continentaux",   "BSIC":  "Continentaux",
    "BIMAO":"Locaux",         "BA-S":  "Continentaux",
    "BRM":  "Locaux",         "UBA":   "Internationaux",
    "FBNBANK": "Internationaux","CI":  "Locaux",
    "BNDE": "Locaux",         "NSIA":  "Continentaux",
    "BDK":  "Locaux",         "BGFI":  "Continentaux",
    "LBO":  "Locaux",         "CBI":   "Régionaux",
    "BAS":  "Continentaux",   "BCIM":  "Locaux",
    "CISA": "Locaux",         "BHS":   "Locaux",
}

COLONNES_NUM = [
    "bilan", "emploi", "ressources", "fonds_propres",
    "pnb", "resultat_net", "charges_exploit",
    "rbe", "cout_risque", "effectif", "agences",
    "interets_produits", "interets_charges",
    "total_actif",
]


def charger_base_excel():
    print("Chargement BASE_SENEGAL2...")
    df = pd.read_excel(FICHIER_EXCEL)

    df = df.rename(columns={
        "Sigle":                  "sigle",
        "Goupe_Bancaire":         "groupe",
        "ANNEE":                  "annee",
        "EMPLOI":                 "emploi",
        "BILAN":                  "bilan",
        "RESSOURCES":             "ressources",
        "FONDS.PROPRE":           "fonds_propres",
        "EFFECTIF":               "effectif",
        "AGENCE":                 "agences",
        "PRODUIT.NET.BANCAIRE":   "pnb",
        "RESULTAT.NET":           "resultat_net",
        "CHARGES.GENERALES.D'EXPLOITATION": "charges_exploit",
        "RESULTAT.BRUT.D'EXPLOITATION":     "rbe",
        "COÛT.DU.RISQUE":                   "cout_risque",
        "INTERETS.ET.PRODUITS.ASSIMILES":   "interets_produits",
        "NTERETS.ET.CHARGES.ASSIMILEES":    "interets_charges",
    })

    df["source"] = "BASE_SENEGAL2"
    return df


def charger_bceao():
    if not os.path.exists(FICHIER_BCEAO):
        print("Fichier BCEAO non trouvé — seule la base Excel sera utilisée")
        return pd.DataFrame()

    print("Chargement données BCEAO...")
    df = pd.read_csv(FICHIER_BCEAO)

    df["source"] = "BCEAO_2022"
    return df


def nettoyer(df):
    print("Nettoyage en cours...")

    # 1. Conversion numérique forcée
    for col in COLONNES_NUM:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["annee"] = pd.to_numeric(df["annee"], errors="coerce").astype("Int64")

    # 2. Suppression des lignes sans données utiles
    avant = len(df)
    df = df.dropna(subset=["sigle", "annee"])
    print(f"  Lignes sans sigle/année supprimées : {avant - len(df)}")

    # 3. Vérification des incohérences
    # Bilan négatif = incohérent pour une banque
    incoherents = df[df["bilan"] < 0] if "bilan" in df.columns else pd.DataFrame()
    if not incoherents.empty:
        print(f"  Bilans négatifs détectés ({len(incoherents)} lignes) → mis à NaN")
        df.loc[df["bilan"] < 0, "bilan"] = np.nan

    # Coefficient d'exploitation > 500% = aberrant
    if "coeff_exploit" in df.columns:
        df.loc[df["coeff_exploit"].abs() > 500, "coeff_exploit"] = np.nan

    # 4. Valeurs manquantes : on garde NaN pour les indicateurs financiers
    # (on ne remplace pas par 0 pour ne pas fausser les ratios)
    cols_presentes = [c for c in COLONNES_NUM if c in df.columns]
    taux_manquants = df[cols_presentes].isnull().mean() * 100
    cols_problematiques = taux_manquants[taux_manquants > 50].index.tolist()
    if cols_problematiques:
        print(f"  Colonnes avec > 50% de NaN : {cols_problematiques}")

    # 5. Standardisation des sigles
    df["sigle"] = df["sigle"].str.strip().str.upper()

    # 6. Ajout groupe si manquant
    if "groupe" not in df.columns:
        df["groupe"] = df["sigle"].map(GROUPES).fillna("Autres")
    else:
        df["groupe"] = df["groupe"].fillna(df["sigle"].map(GROUPES)).fillna("Autres")

    # 7. Suppression des doublons (même banque, même année, même source)
    avant = len(df)
    df = df.drop_duplicates(subset=["sigle", "annee", "source"], keep="first")
    print(f"  Doublons supprimés : {avant - len(df)}")

    return df


def calculer_ratios(df):
    print("Calcul des ratios financiers...")

    # ROA : rentabilité des actifs
    if "resultat_net" in df.columns and "bilan" in df.columns:
        df["roa"] = (df["resultat_net"] / df["bilan"] * 100).round(2)
        df.loc[df["roa"].abs() > 100, "roa"] = np.nan

    # Coefficient d'exploitation
    if "charges_exploit" in df.columns and "pnb" in df.columns:
        df["coeff_exploit"] = (df["charges_exploit"] / df["pnb"] * 100).round(2)
        df.loc[df["coeff_exploit"].abs() > 500, "coeff_exploit"] = np.nan

    # Taux de transformation
    if "emploi" in df.columns and "ressources" in df.columns:
        df["taux_transfo"] = (df["emploi"] / df["ressources"] * 100).round(2)
        df.loc[(df["taux_transfo"] <= 0) | (df["taux_transfo"] > 300), "taux_transfo"] = np.nan

    # Ratio de solvabilité simplifié : fonds propres / bilan
    if "fonds_propres" in df.columns and "bilan" in df.columns:
        df["solvabilite"] = (df["fonds_propres"] / df["bilan"] * 100).round(2)

    # Ratio de liquidité : ressources / bilan (part des actifs financés par dépôts clients)
    if "ressources" in df.columns and "bilan" in df.columns:
        df["liquidite"] = (df["ressources"] / df["bilan"] * 100).round(2)
        df.loc[(df["liquidite"] <= 0) | (df["liquidite"] > 200), "liquidite"] = np.nan

    return df


def score_positionnement(df):
    """
    Calcule un score global de positionnement pour chaque banque.
    Basé sur 4 critères normalisés : bilan, pnb, roa, solvabilité.
    """
    print("Calcul du score de positionnement...")

    criteres = ["bilan", "pnb", "roa", "solvabilite"]
    criteres_dispo = [c for c in criteres if c in df.columns]

    synthese = df.groupby("sigle")[criteres_dispo].mean()

    for col in criteres_dispo:
        mn, mx = synthese[col].min(), synthese[col].max()
        if mx > mn:
            synthese[f"{col}_score"] = ((synthese[col] - mn) / (mx - mn) * 100).round(1)
        else:
            synthese[f"{col}_score"] = 50.0

    score_cols = [f"{c}_score" for c in criteres_dispo]
    synthese["score_global"] = synthese[score_cols].mean(axis=1).round(1)
    synthese["classement"] = synthese["score_global"].rank(ascending=False).astype(int)

    return synthese[["score_global", "classement"]].reset_index()


def valider(df):
    print("\nValidation finale :")
    print(f"  Lignes    : {len(df)}")
    print(f"  Banques   : {df['sigle'].nunique()}")
    print(f"  Années    : {sorted(df['annee'].dropna().unique().tolist())}")
    print(f"  Colonnes  : {df.columns.tolist()}")
    print(f"  NaN bilan : {df['bilan'].isna().sum() if 'bilan' in df else 'N/A'}")
    print(f"  NaN pnb   : {df['pnb'].isna().sum() if 'pnb' in df else 'N/A'}")


if __name__ == "__main__":
    # 1. Chargement
    df_excel = charger_base_excel()
    df_bceao = charger_bceao()

    # 1b. Relier total_actif au bilan si bilan manquant
    if "total_actif" in df_excel.columns:
        df_excel["bilan"] = df_excel["bilan"].fillna(df_excel["total_actif"]) \
            if "bilan" in df_excel.columns else df_excel["total_actif"]

    if "total_actif" in df_bceao.columns and not df_bceao.empty:
        df_bceao["bilan"] = df_bceao["bilan"].fillna(df_bceao["total_actif"]) \
            if "bilan" in df_bceao.columns else df_bceao["total_actif"]

    # 2. Fusion
    if not df_bceao.empty:
        # On prend 2021-2022 depuis BCEAO pour compléter la base Excel (2015-2020)
        df_bceao_new = df_bceao[df_bceao["annee"].isin([2021, 2022])].copy()
        df = pd.concat([df_excel, df_bceao_new], ignore_index=True)
    else:
        df = df_excel.copy()

    # 3. Nettoyage
    df = nettoyer(df)

    # 4. Ratios
    df = calculer_ratios(df)

    # 5. Score de positionnement
    scores = score_positionnement(df)
    df = df.merge(scores, on="sigle", how="left")

    # 6. Validation
    valider(df)

    # 7. Sauvegarde — colonnes utiles uniquement
    cols_garder = [c for c in [
        "sigle", "groupe", "annee", "source",
        "bilan", "emploi", "ressources", "fonds_propres", "effectif", "agences",
        "pnb", "resultat_net", "charges_exploit", "rbe", "cout_risque",
        "interets_produits", "interets_charges",
        "roa", "coeff_exploit", "taux_transfo", "solvabilite", "liquidite",
        "score_global", "classement",
    ] if c in df.columns]
    df = df[cols_garder].sort_values(["annee", "sigle"]).reset_index(drop=True)
    df.to_csv(FICHIER_SORTIE, index=False)
    print(f"\nDonnées propres sauvegardées : {FICHIER_SORTIE}")
