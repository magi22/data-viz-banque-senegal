
import os
import pandas as pd
from pymongo import MongoClient

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
FICHIER = "data/banques_clean.csv"


def charger_mongodb():
    if not os.path.exists(FICHIER):
        print(f"Fichier introuvable : {FICHIER}")
        print("Lancer d'abord scripts/nettoyage.py")
        return

    print("Connexion MongoDB...")
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.server_info()
    except Exception as e:
        print(f"Connexion impossible : {e}")
        return

    db = client["banques_senegal"]

    # Collection indicateurs
    df = pd.read_csv(FICHIER)
    if df.empty:
        print("Le fichier banques_clean.csv est vide.")
        return
    docs = df.where(pd.notnull(df), None).to_dict(orient="records")

    col = db["indicateurs"]
    col.drop()
    col.insert_many(docs)
    col.create_index([("sigle", 1), ("annee", 1)])

    print(f"{len(docs)} documents insérés dans MongoDB (collection 'indicateurs')")

    # Vérification rapide
    exemple = col.find_one({"sigle": "SGBS"}, {"_id": 0})
    print(f"Exemple SGBS : {exemple}")


if __name__ == "__main__":
    charger_mongodb()
