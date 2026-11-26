
import requests
import json
import time
import os
from datetime import datetime

# Adresse de l'API OpenTDB
API_URL = "https://opentdb.com/api.php"
TOKEN_URL = "https://opentdb.com/api_token.php"

# Dossiers de stockage
os.makedirs("bronze", exist_ok=True)

# Fichiers de sauvegarde
TOKEN_FILE = "bronze/opentdb_token.txt"
FINAL_FILE = "bronze/questions_completes.json"

# Pause obligatoire entre deux requêtes
PAUSE = 5.5


def get_token():
    """Récupère un jeton pour éviter les questions en double."""

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            token = f.read().strip()

        if token:
            return token

    response = requests.get(
        TOKEN_URL,
        params={"command": "request"},
        timeout=30
    )
    data = response.json()

    if data["response_code"] != 0:
        raise Exception("Impossible de récupérer le token.")

    token = data["token"]

    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        f.write(token)

    return token


def extract_questions():
    print("Début de l'extraction complète...")

    token = get_token()

    # Questions déjà enregistrées si on relance le script
    questions = []
    batch_number = 1

    existing_files = sorted([
        f for f in os.listdir("bronze")
        if f.startswith("batch_") and f.endswith(".json")
    ])

    for filename in existing_files:
        with open(os.path.join("bronze", filename),
                  "r", encoding="utf-8") as f:
            old_data = json.load(f)
            questions.extend(old_data.get("results", []))

    print("Questions déjà sauvegardées :", len(questions))

    # Identifiant pour éviter les doublons
    seen = {
        (q["category"], q["question"], q["correct_answer"])
        for q in questions
    }

    batch_number = len(existing_files) + 1

    while True:
        try:
            # Respect de la limite de l'API
            time.sleep(PAUSE)

            response = requests.get(
                API_URL,
                params={
                    "amount": 50,
                    "token": token
                },
                timeout=30
            )

            data = response.json()
            code = data.get("response_code")

            # Limite de requêtes atteinte
            if code == 5:
                print("Limite API atteinte. Nouvelle tentative...")
                time.sleep(PAUSE)
                continue

            # Token expiré ou invalide
            if code == 3:
                raise Exception(
                    "Token invalide ou expiré. "
                    "Supprime opentdb_token.txt puis relance."
                )

            # Plus de questions disponibles avec ce token
            if code in (1, 4):
                print("Fin de l'extraction : plus de questions disponibles.")
                break

            # Autre erreur
            if code != 0:
                raise Exception(f"Erreur API : code {code}")

            batch = data.get("results", [])

            if not batch:
                break

            # Sauvegarder chaque lot dans Bronze
            filename = f"batch_{batch_number:04d}.json"
            filepath = os.path.join("bronze", filename)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            # Ajouter uniquement les nouvelles questions
            new_count = 0

            for question in batch:
                key = (
                    question["category"],
                    question["question"],
                    question["correct_answer"]
                )

                if key not in seen:
                    seen.add(key)
                    questions.append(question)
                    new_count += 1

            print(
                f"Lot {batch_number} : "
                f"{len(batch)} reçues, "
                f"{new_count} nouvelles. "
                f"Total : {len(questions)}"
            )

            batch_number += 1

        except requests.exceptions.RequestException as error:
            print("Erreur réseau :", error)
            print("Nouvelle tentative dans 10 secondes...")
            time.sleep(10)

    # Sauvegarde finale
    with open(FINAL_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {
                "total_questions": len(questions),
                "extraction_date": datetime.now().isoformat(),
                "results": questions
            },
            f,
            ensure_ascii=False,
            indent=4
        )

    print("\nExtraction terminée !")
    print("Nombre de questions :", len(questions))
    print("Fichier final :", FINAL_FILE)


if __name__ == "__main__":
    extract_questions()
