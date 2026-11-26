
from pathlib import Path
import duckdb

# Chemins des deux bases
PROJECT_DIR = Path(__file__).resolve().parents[2]

DB_AMINA = PROJECT_DIR / "gold" / "warehouse.duckdb"
DB_GHITA = PROJECT_DIR / "gold" / "warehouse-ghita.duckdb"


def load_data():

    # Vérifier les fichiers
    if not DB_AMINA.exists():
        raise FileNotFoundError(f"Base introuvable : {DB_AMINA}")

    if not DB_GHITA.exists():
        raise FileNotFoundError(f"Base introuvable : {DB_GHITA}")

    # Connexion à ta base principale
    con = duckdb.connect(str(DB_AMINA), read_only=True)

    try:
        # Connexion à la base de Ghita
        ghita_path = str(DB_GHITA).replace("'", "''")
        con.execute(
            f"ATTACH '{ghita_path}' AS ghita (READ_ONLY)"
        )

        query = """
        SELECT
            'Amina' AS source,
            ai_model,
            category,
            difficulty,
            type,
            question,
            correct_answer,
            ai_answer,
            ai_correct,
            answer_status,
            is_unanswered,
            response_time
        FROM main.mart_questions_detaillees

        UNION ALL

        SELECT
            'Ghita' AS source,
            ai_model,
            category,
            difficulty,
            type,
            question,
            correct_answer,
            ai_answer,
            ai_correct,
            answer_status,
            is_unanswered,
            response_time
        FROM ghita.main.mart_questions_detaillees
        """

        df = con.execute(query).df()

        return df

    finally:
        con.close()
