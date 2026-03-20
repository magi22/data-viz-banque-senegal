"""
Tests unitaires simples pour vérifier l'intégrité des données.
Lancement : python -m pytest tests/test_donnees.py -v
"""

import os
import sys
import pytest
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


# ─────────────────────────────────────────────
# FIXTURE : chargement des données de test
# ─────────────────────────────────────────────
@pytest.fixture
def df():
    chemin = "data/banques_clean.csv"
    if os.path.exists(chemin):
        return pd.read_csv(chemin)
    # Fallback : lire l'Excel brut
    df = pd.read_excel("data/BASE_SENEGAL2.xlsx")
    df = df.rename(columns={
        "Sigle": "sigle", "Goupe_Bancaire": "groupe",
        "ANNEE": "annee", "BILAN": "bilan",
        "PRODUIT.NET.BANCAIRE": "pnb", "RESULTAT.NET": "resultat_net",
        "EMPLOI": "emploi", "RESSOURCES": "ressources",
        "FONDS.PROPRE": "fonds_propres",
    })
    return df


# ─────────────────────────────────────────────
# TESTS
# ─────────────────────────────────────────────

def test_chargement(df):
    """Le dataset doit se charger et contenir des données."""
    assert df is not None
    assert len(df) > 0


def test_colonnes_obligatoires(df):
    """Les colonnes essentielles doivent être présentes."""
    colonnes_requises = ["sigle", "annee", "bilan"]
    for col in colonnes_requises:
        assert col in df.columns, f"Colonne manquante : {col}"


def test_aucune_ligne_sans_sigle(df):
    """Chaque ligne doit avoir un identifiant de banque."""
    assert df["sigle"].isna().sum() == 0


def test_annees_valides(df):
    """Les années doivent être dans la plage 2015-2022."""
    annees = df["annee"].dropna().unique()
    for annee in annees:
        assert 2015 <= int(annee) <= 2022, f"Année hors plage : {annee}"


def test_bilan_positif(df):
    """Le bilan d'une banque doit être positif."""
    bilans_negatifs = df[df["bilan"] < 0] if "bilan" in df.columns else pd.DataFrame()
    assert len(bilans_negatifs) == 0, f"{len(bilans_negatifs)} bilans négatifs détectés"


def test_nombre_banques(df):
    """Le dataset doit contenir au moins 10 banques distinctes."""
    nb = df["sigle"].nunique()
    assert nb >= 10, f"Seulement {nb} banques — attendu au moins 10"


def test_pas_de_doublons(df):
    """Pas de doublon (même banque, même année, même source)."""
    cols = ["sigle", "annee"]
    if "source" in df.columns:
        cols.append("source")
    doublons = df.duplicated(subset=cols).sum()
    assert doublons == 0, f"{doublons} lignes dupliquées détectées"


def test_calcul_roa(df):
    """Le ROA calculé doit être cohérent avec résultat_net / bilan."""
    if "roa" not in df.columns or "resultat_net" not in df.columns or "bilan" not in df.columns:
        pytest.skip("Colonnes roa/resultat_net/bilan non disponibles")

    mask = df["bilan"].notna() & df["resultat_net"].notna() & df["bilan"] > 0
    roa_calcule = (df.loc[mask, "resultat_net"] / df.loc[mask, "bilan"] * 100).round(2)
    roa_stocke = df.loc[mask, "roa"].round(2)

    differences = (roa_calcule - roa_stocke).abs()
    assert differences.max() < 0.1, "Le ROA stocké ne correspond pas au calcul attendu"


def test_taux_complet_pnb(df):
    """Le PNB doit être renseigné pour au moins 60% des lignes banques."""
    if "pnb" not in df.columns:
        pytest.skip("Colonne pnb non disponible")
    taux = df["pnb"].notna().mean()
    assert taux >= 0.6, f"Taux de remplissage PNB trop faible : {taux:.0%}"


