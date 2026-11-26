
import os
import json
import time
import html
import re
import unicodedata
import requests

from pathlib import Path
from dotenv import load_dotenv

# ==================================================
# 1. CONFIGURATION
# ==================================================

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL")
API_KEY = os.getenv("API_KEY")

if not API_BASE_URL or not API_KEY:
    raise ValueError("Vérifie API_BASE_URL et API_KEY dans .env")

API_URL = API_BASE_URL.rstrip("/") + "/chat/completions"

MODEL_NAME = "Gemma-4-12b"

BRONZE_DIR = Path("bronze")

OUTPUT_FILE = BRONZE_DIR / "questions_avec_reponses_ia.json"

# None = toutes les questions
TEST_SIZE = None

PAUSE = 1

# Nombre de tentatives en cas d'erreur
MAX_RETRIES = 3

# ==================================================
# 2. NORMALISATION
# ==================================================

def normaliser(texte):

    texte = html.unescape(str(texte)).lower().strip()

    texte = unicodedata.normalize("NFD", texte)

    texte = "".join(
        c for c in texte
        if unicodedata.category(c) != "Mn"
    )

    texte = re.sub(r"[^\w\s]", " ", texte)

    return " ".join(texte.split())


# ==================================================
# 3. APPEL DE GEMMA
# ==================================================

def interroger_gemma(question, choix):

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
Answer this general knowledge question.

Question:
{html.unescape(str(question))}

Possible answers:
{choix}

Instructions:
- Choose exactly one answer from the choices.
- Do not explain.
- Do not show your reasoning.
- Never ask a question.
- Always provide an answer.
- Return only the exact answer.
"""

    payload = {
        "model": MODEL_NAME,

        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a direct-answer quiz assistant. "
                    "Answer every question using the proposed choices. "
                    "Do not use extended reasoning. "
                    "Do not explain your reasoning. "
                    "Never ask the user a question. "
                    "Never return an empty answer. "
                    "Return only the selected answer."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        "temperature": 0,

        "max_tokens": 100,

        "stream": False,

        # Désactivation expérimentale du mode Thinking.
        # À conserver uniquement si le fournisseur le prend en charge.
        "reasoning_effort": "none"
    }

    debut = time.perf_counter()

    response = requests.post(
        API_URL,
        headers=headers,
        json=payload,
        timeout=180
    )

    response.raise_for_status()

    data = response.json()

    if not data.get("choices"):
        raise ValueError("Aucun résultat retourné par l'API")

    message = data["choices"][0]["message"]

    reponse_ia = message.get("content", "")

    # Gestion de certains formats de réponse
    if isinstance(reponse_ia, list):

        morceaux = []

        for part in reponse_ia:

            if isinstance(part, dict):
                morceaux.append(part.get("text", ""))

        reponse_ia = " ".join(morceaux)

    temps = round(time.perf_counter() - debut, 3)

    if not isinstance(reponse_ia, str) or not reponse_ia.strip():
        raise ValueError(
            f"Réponse vide. Finish reason : "
            f"{data['choices'][0].get('finish_reason')}"
        )

    return reponse_ia.strip(), temps


# ==================================================
# 4. VERIFICATION DE LA REPONSE
# ==================================================

def verifier_reponse(reponse_ia, bonne_reponse):

    return (
        normaliser(reponse_ia)
        == normaliser(bonne_reponse)
    )


# ==================================================
# 5. SAUVEGARDE BRONZE
# ==================================================

def sauvegarder(resultats):

    BRONZE_DIR.mkdir(parents=True, exist_ok=True)

    fichier_temp = OUTPUT_FILE.with_suffix(".tmp")

    with open(fichier_temp, "w", encoding="utf-8") as f:

        json.dump(
            resultats,
            f,
            ensure_ascii=False,
            indent=4
        )

    fichier_temp.replace(OUTPUT_FILE)


# ==================================================
# 6. LECTURE DES FICHIERS JSON
# ==================================================

print("\n========== BENCHMARK GEMMA ==========")

if not BRONZE_DIR.exists():
    raise FileNotFoundError("Le dossier Bronze n'existe pas.")

fichiers_json = sorted(
    fichier
    for fichier in BRONZE_DIR.glob("*.json")
    if fichier.name != OUTPUT_FILE.name
)

if not fichiers_json:
    raise FileNotFoundError(
        "Aucun fichier JSON trouvé dans Bronze."
    )

questions = []

for fichier in fichiers_json:

    print("\nLecture :", fichier.name)

    try:

        with open(fichier, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict):
            lot = data.get("results", [])

        elif isinstance(data, list):
            lot = data

        else:
            print("Format ignoré :", fichier.name)
            continue

        for question in lot:

            if not isinstance(question, dict):
                continue

            question = question.copy()

            question["source_file"] = fichier.name

            questions.append(question)

    except Exception as erreur:

        print("Erreur de lecture :", erreur)


print("\nTotal questions récupérées :", len(questions))


# ==================================================
# 7. SUPPRESSION DES DOUBLONS
# ==================================================

questions_uniques = []

questions_vues = set()

for question in questions:

    cle = normaliser(question.get("question", ""))

    if cle and cle not in questions_vues:

        questions_uniques.append(question)

        questions_vues.add(cle)


questions = questions_uniques

print("Questions uniques :", len(questions))


if TEST_SIZE is not None:

    questions = questions[:TEST_SIZE]


print("Questions à traiter :", len(questions))


# ==================================================
# 8. CHARGEMENT DES RESULTATS EXISTANTS
# ==================================================

if OUTPUT_FILE.exists():

    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:

        resultats = json.load(f)

else:

    resultats = []


questions_traitees = {

    normaliser(item.get("question", ""))

    for item in resultats

    if item.get("ai_answer") is not None
}


# ==================================================
# 9. ENVOI AUTOMATIQUE A GEMMA
# ==================================================

for index, item in enumerate(questions, start=1):

    question = item.get("question", "")

    bonne_reponse = item.get("correct_answer", "")

    cle = normaliser(question)

    if cle in questions_traitees:

        print(f"\n[{index}/{len(questions)}] Déjà traitée")

        continue

    print(f"\n========== QUESTION {index}/{len(questions)} ==========")

    print("Question :", question)

    if not question.strip() or not bonne_reponse:
        print("Question ignorée : question ou bonne réponse manquante")
        continue

    # Récupération des propositions
    choix = item.get("incorrect_answers", [])

    if not isinstance(choix, list):
        choix = []

    choix = [
        html.unescape(str(option))
        for option in choix
    ]

    bonne_reponse = html.unescape(str(bonne_reponse))

    # Ajouter la bonne réponse parmi les propositions
    if normaliser(bonne_reponse) not in {
        normaliser(option) for option in choix
    }:
        choix.append(bonne_reponse)

    # Mélanger les réponses pour éviter un biais de position
    import random
    random.shuffle(choix)

    texte_choix = "\n".join(
        f"- {option}"
        for option in choix
    )

    print("Envoi à Gemma...")

    succes = False

    for tentative in range(1, MAX_RETRIES + 1):

        try:

            ai_answer, response_time = interroger_gemma(
                question,
                texte_choix
            )

            ai_correct = verifier_reponse(
                ai_answer,
                bonne_reponse
            )

            print("Réponse Gemma :", ai_answer)

            print("Bonne réponse :", bonne_reponse)

            print("Correct :", ai_correct)

            print("Temps :", response_time, "secondes")

            resultat = item.copy()

            resultat["ai_answer"] = ai_answer

            resultat["ai_correct"] = bool(ai_correct)

            resultat["response_time"] = response_time

            resultat["ai_model"] = MODEL_NAME

            resultat["error"] = None

            succes = True

            break

        except Exception as erreur:

            print(
                f"Tentative {tentative}/{MAX_RETRIES} échouée :",
                erreur
            )

            if tentative < MAX_RETRIES:
                time.sleep(3 * tentative)

    # Si toutes les tentatives échouent
    if not succes:

        print("Échec définitif de cette question.")

        resultat = item.copy()

        resultat["ai_answer"] = None

        resultat["ai_correct"] = None

        resultat["response_time"] = None

        resultat["ai_model"] = MODEL_NAME

        resultat["error"] = "Échec après plusieurs tentatives"

    resultats.append(resultat)

    # Ajouter aux questions traitées uniquement si réponse obtenue
    if succes:
        questions_traitees.add(cle)

    # Sauvegarder après chaque question
    sauvegarder(resultats)

    print("Résultat sauvegardé dans Bronze.")

    time.sleep(PAUSE)


# ==================================================
# 10. BILAN FINAL
# ==================================================

reponses_valides = [

    r for r in resultats

    if r.get("ai_answer") is not None

]

correctes = sum(

    r.get("ai_correct") is True

    for r in reponses_valides

)

incorrectes = sum(

    r.get("ai_correct") is False

    for r in reponses_valides

)

sans_reponse = sum(

    r.get("ai_answer") is None

    for r in resultats

)


print("\n========================================")

print("          BILAN FINAL GEMMA")

print("========================================")

print("Modèle :", MODEL_NAME)

print("Questions enregistrées :", len(resultats))

print("Réponses obtenues :", len(reponses_valides))

print("Réponses correctes :", correctes)

print("Réponses incorrectes :", incorrectes)

print("Questions sans réponse :", sans_reponse)


if reponses_valides:

    accuracy = correctes / len(reponses_valides) * 100

    print("Accuracy :", round(accuracy, 2), "%")


print("\nRésultats sauvegardés dans :")

print(OUTPUT_FILE)

print("\nTraitement terminé !")
