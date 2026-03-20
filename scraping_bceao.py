"""
Télécharge le rapport BCEAO (bilans et comptes de résultat) depuis le site officiel.
Sauvegarde le premier PDF pertinent trouvé sous data/rapport_bceao_2022.pdf.
URL source : https://www.bceao.int/fr/publications/bilans-et-comptes-de-resultat
"""

import os
import requests
from bs4 import BeautifulSoup

URL_BCEAO = "https://www.bceao.int/fr/publications/bilans-et-comptes-de-resultat-des-banques-etablissements-financiers-et-compagnies"
DOSSIER       = "data"
NOM_FICHIER   = "rapport_bceao_2022.pdf"


def telecharger_rapport():
    os.makedirs(DOSSIER, exist_ok=True)
    chemin = os.path.join(DOSSIER, NOM_FICHIER)

    if os.path.exists(chemin):
        print(f"Déjà présent : {chemin}")
        return chemin

    headers = {"User-Agent": "Mozilla/5.0"}

    print("Connexion au site BCEAO...")
    try:
        reponse = requests.get(URL_BCEAO, headers=headers, timeout=15)
        reponse.raise_for_status()
    except requests.RequestException as e:
        print(f"Erreur de connexion : {e}")
        return None

    soup = BeautifulSoup(reponse.text, "html.parser")

    # Récupérer les liens PDF (uniquement les vrais .pdf, sans doublons)
    liens_pdf = []
    for tag in soup.find_all("a", href=True):
        href = tag["href"]
        if href.lower().endswith(".pdf"):
            if not href.startswith("http"):
                href = "https://www.bceao.int" + href
            liens_pdf.append(href)

    liens_pdf = list(dict.fromkeys(liens_pdf))
    print(f"{len(liens_pdf)} PDF(s) trouvé(s)")

    if not liens_pdf:
        print("Aucun lien PDF trouvé.")
        return None

    # Télécharger le premier PDF pertinent
    for lien in liens_pdf:
        try:
            r = requests.get(lien, headers=headers, timeout=30)
            r.raise_for_status()
            with open(chemin, "wb") as f:
                f.write(r.content)
            print(f"Téléchargé : {chemin}")
            return chemin
        except Exception as e:
            print(f"Erreur sur {lien} : {e}")
            continue

    print("Aucun PDF n'a pu être téléchargé.")
    return None


if __name__ == "__main__":
    resultat = telecharger_rapport()
    if resultat:
        print(f"\nRapport disponible : {resultat}")
    else:
        print("\nÉchec du téléchargement.")
