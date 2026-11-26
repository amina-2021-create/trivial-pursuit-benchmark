
import json
import html
import re
from pathlib import Path

import pandas as pd

# Dossiers Bronze et Silver
BRONZE_DIR = Path("bronze")
SILVER_DIR = Path("silver")


def clean_text(value):
    """Décode les caractères HTML et nettoie les espaces."""

    if isinstance(value, str):
        value = html.unescape(value)
        value = re.sub(r"\s+", " ", value)
        return value.strip()

    return value


def clean_file(json_file):
    """Nettoie un fichier JSON et le transforme en Parquet."""

    print(f"\nTraitement de : {json_file.name}")

    # Lire le fichier JSON
    with open(json_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    questions = data.get("results", [])

    cleaned_questions = []
    seen = set()

    for question in questions:

        # Nettoyage des champs texte
        cleaned = {
            key: clean_text(value)
            if isinstance(value, str)
            else value
            for key, value in question.items()
        }

        # Vérifier les champs obligatoires
        if not cleaned.get("question") or not cleaned.get("correct_answer"):
            continue

        # Nettoyer les mauvaises réponses
        cleaned["incorrect_answers"] = [
            clean_text(answer)
            for answer in cleaned.get("incorrect_answers", [])
        ]

        # Uniformiser les champs
        cleaned["category"] = cleaned["category"].strip()
        cleaned["difficulty"] = cleaned["difficulty"].lower()
        cleaned["type"] = cleaned["type"].lower()

        # Supprimer les doublons dans ce fichier
        key = (
            cleaned["category"].casefold(),
            cleaned["question"].casefold(),
            cleaned["correct_answer"].casefold()
        )

        if key not in seen:
            seen.add(key)
            cleaned_questions.append(cleaned)

    # Convertir en DataFrame
    df = pd.DataFrame(cleaned_questions)

    # Créer le nom du fichier Parquet correspondant
    parquet_file = SILVER_DIR / f"{json_file.stem}.parquet"

    # Enregistrer en Parquet
    df.to_parquet(
        parquet_file,
        engine="pyarrow",
        index=False,
        compression="snappy"
    )

    print("Questions initiales :", len(questions))
    print("Questions conservées :", len(df))
    print("Fichier créé :", parquet_file)


def main():

    SILVER_DIR.mkdir(parents=True, exist_ok=True)

    # Traiter les fichiers JSON de Bronze
    json_files = sorted(BRONZE_DIR.glob("*.json"))

    if not json_files:
        print("Aucun fichier JSON trouvé dans Bronze.")
        return

    print("Nombre de fichiers JSON :", len(json_files))

    for json_file in json_files:
        clean_file(json_file)

    print("\nTransformation Bronze vers Silver terminée !")


if __name__ == "__main__":
    main()
