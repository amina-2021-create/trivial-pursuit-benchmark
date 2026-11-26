
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.getenv("API_BASE_URL"),
    api_key=os.getenv("API_KEY")
)

try:
    models = client.models.list()

    print("Connexion réussie !")
    print("Modèles disponibles :")

    for model in models.data:
        print("-", model.id)

except Exception as e:
    print("Erreur de connexion :", e)
