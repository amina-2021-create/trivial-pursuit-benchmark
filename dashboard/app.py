import streamlit as st
import pandas as pd
import plotly.express as px

from components.data import load_data


# =====================================================
# 1. CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Trivial Pursuit | Benchmark IA",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =====================================================
# 2. COULEURS
# =====================================================

BG = "#0B1020"
SIDEBAR = "#11182B"
CARD = "#151B32"
BORDER = "#293451"
TEXT = "#F1F5F9"
MUTED = "#94A3B8"

BLUE = "#38BDF8"
PURPLE = "#8B5CF6"
GREEN = "#34D399"
YELLOW = "#FBBF24"


# =====================================================
# 3. STYLE CSS
# =====================================================

st.markdown(f"""
<style>
.stApp {{
    background-color: {BG};
    color: {TEXT};
}}

.block-container {{
    padding-top: 2rem;
    padding-bottom: 2rem;
}}

h1, h2, h3 {{
    color: {TEXT} !important;
}}

[data-testid="stSidebar"] {{
    background-color: {SIDEBAR};
    border-right: 1px solid {BORDER};
}}

[data-testid="stMetric"] {{
    background-color: {CARD};
    padding: 18px;
    border-radius: 10px;
    border: 1px solid {BORDER};
}}

[data-testid="stMetricLabel"] {{
    color: {MUTED} !important;
}}

[data-testid="stMetricValue"] {{
    color: {TEXT} !important;
}}

[data-testid="stPlotlyChart"] {{
    background-color: {CARD};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 8px;
}}

hr {{
    border-color: {BORDER};
}}
</style>
""", unsafe_allow_html=True)


# =====================================================
# 4. CHARGEMENT DES DONNEES
# =====================================================

try:
    df = load_data()

except Exception as e:
    st.error(f"Erreur de chargement : {e}")
    st.stop()


required = [
    "source",
    "ai_model",
    "question",
    "ai_correct",
    "response_time",
    "category"
]

missing = [
    c for c in required if c not in df.columns
]

if missing:
    st.error(f"Colonnes manquantes : {missing}")
    st.stop()

df = df.copy()

df["ai_correct"] = pd.to_numeric(
    df["ai_correct"], errors="coerce"
)

df["response_time"] = pd.to_numeric(
    df["response_time"], errors="coerce"
)


# =====================================================
# 5. MENU LATERAL - SANS HTML PERSONNALISE
# =====================================================

st.sidebar.title("TRIVIAL PURSUIT")
st.sidebar.caption("TABLEAU DE BORD IA")

st.sidebar.divider()

st.sidebar.subheader("Navigation")

page = st.sidebar.radio(
    "Navigation",
    [
        "Vue générale",
        "Comparaison des modèles",
        "Analyse par catégorie",
        "Données"
    ],
    label_visibility="collapsed"
)

st.sidebar.divider()

st.sidebar.subheader("Filtres")

sources = sorted(
    df["source"].dropna().unique().tolist()
)

models = sorted(
    df["ai_model"].dropna().unique().tolist()
)

selected_sources = st.sidebar.multiselect(
    "Source",
    sources,
    default=sources
)

selected_models = st.sidebar.multiselect(
    "Modèle d'intelligence artificielle",
    models,
    default=models
)

st.sidebar.divider()

st.sidebar.caption(
    "Projet Data Engineering · 2026/2027"
)


# =====================================================
# 6. APPLICATION DES FILTRES
# =====================================================

filtered_df = df[
    df["source"].isin(selected_sources)
    & df["ai_model"].isin(selected_models)
].copy()

if filtered_df.empty:
    st.warning("Aucune donnée disponible avec ces filtres.")
    st.stop()


# =====================================================
# 7. CALCUL DES STATISTIQUES
# =====================================================

evaluated_df = filtered_df.dropna(
    subset=["ai_correct"]
)

total_questions = len(filtered_df)
total_evaluations = len(evaluated_df)

correct_answers = evaluated_df["ai_correct"].sum()

accuracy = (
    correct_answers / total_evaluations * 100
    if total_evaluations else 0
)

avg_response_time = filtered_df["response_time"].mean()

total_models = filtered_df["ai_model"].nunique()


stats = (
    filtered_df
    .groupby(["source", "ai_model"])
    .agg(
        total_questions=("question", "count"),
        evaluated_questions=("ai_correct", "count"),
        correct_answers=("ai_correct", "sum"),
        avg_response_time=("response_time", "mean")
    )
    .reset_index()
)

stats["accuracy"] = (
    stats["correct_answers"]
    / stats["evaluated_questions"].replace(0, float("nan"))
    * 100
)

stats["error_rate"] = 100 - stats["accuracy"]


evaluated_categories = evaluated_df.dropna(
    subset=["category"]
)

category_stats = (
    evaluated_categories
    .groupby(["source", "ai_model", "category"])
    ["ai_correct"]
    .mean()
    .mul(100)
    .reset_index(name="accuracy")
)


# =====================================================
# 8. FONCTION GRAPHIQUES
# =====================================================

def apply_chart_style(fig):

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=CARD,
        plot_bgcolor=CARD,
        font=dict(
            color=TEXT,
            family="Arial"
        ),
        margin=dict(
            l=30,
            r=25,
            t=60,
            b=35
        ),
        legend_title_text="Source"
    )

    fig.update_xaxes(
        gridcolor=BORDER,
        zerolinecolor=BORDER
    )

    fig.update_yaxes(
        gridcolor=BORDER,
        zerolinecolor=BORDER
    )

    return fig


# =====================================================
# 9. EN-TETE COMMUN
# =====================================================

st.caption("TRIVIAL PURSUIT / BENCHMARK IA")


# =====================================================
# 10. PAGE VUE GENERALE
# =====================================================

if page == "Vue générale":

    st.title("Vue générale")

    st.caption(
        "Synthèse des performances des modèles "
        "d'intelligence artificielle."
    )

    st.divider()

    st.subheader("Indicateurs clés")

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Questions", f"{total_questions:,}")

    c2.metric("Précision globale", f"{accuracy:.2f}%")

    c3.metric("Évaluations", f"{total_evaluations:,}")

    c4.metric(
        "Temps moyen",
        f"{avg_response_time:.2f} s"
        if pd.notna(avg_response_time)
        else "N/A"
    )

    c5.metric("Modèles", total_models)

    st.divider()

    st.subheader("Comparaison des performances")

    col1, col2 = st.columns(2)

    with col1:

        fig = px.bar(
            stats,
            x="ai_model",
            y="accuracy",
            color="source",
            barmode="group",
            title="Précision des modèles (%)",
            color_discrete_sequence=[BLUE, PURPLE, GREEN]
        )

        fig.update_layout(
            yaxis_range=[0, 100],
            xaxis_title="Modèle",
            yaxis_title="Précision (%)"
        )

        st.plotly_chart(
            apply_chart_style(fig),
            use_container_width=True
        )

    with col2:

        fig = px.bar(
            stats,
            x="ai_model",
            y="avg_response_time",
            color="source",
            barmode="group",
            title="Temps moyen de réponse",
            color_discrete_sequence=[YELLOW, PURPLE, BLUE]
        )

        fig.update_layout(
            xaxis_title="Modèle",
            yaxis_title="Temps (secondes)"
        )

        st.plotly_chart(
            apply_chart_style(fig),
            use_container_width=True
        )

    st.divider()

    st.subheader("Performance par catégorie")

    if not category_stats.empty:

        fig = px.bar(
            category_stats,
            x="category",
            y="accuracy",
            color="ai_model",
            barmode="group",
            title="Précision par catégorie (%)",
            color_discrete_sequence=[BLUE, PURPLE, GREEN]
        )

        fig.update_layout(
            yaxis_range=[0, 100],
            xaxis_title="Catégorie",
            yaxis_title="Précision (%)"
        )

        st.plotly_chart(
            apply_chart_style(fig),
            use_container_width=True
        )

    else:
        st.info("Aucune donnée disponible pour les catégories.")


# =====================================================
# 11. PAGE COMPARAISON DES MODELES
# =====================================================

elif page == "Comparaison des modèles":

    st.title("Comparaison des modèles")

    st.caption(
        "Analyse comparative de la précision "
        "et de la rapidité."
    )

    st.divider()

    st.subheader("Précision des modèles")

    fig = px.bar(
        stats,
        x="ai_model",
        y="accuracy",
        color="source",
        barmode="group",
        text_auto=".2f",
        color_discrete_sequence=[BLUE, PURPLE, GREEN]
    )

    fig.update_layout(
        yaxis_range=[0, 100],
        xaxis_title="Modèle",
        yaxis_title="Précision (%)"
    )

    st.plotly_chart(
        apply_chart_style(fig),
        use_container_width=True
    )

    st.divider()

    st.subheader("Temps de réponse")

    fig = px.bar(
        stats,
        x="ai_model",
        y="avg_response_time",
        color="source",
        barmode="group",
        text_auto=".2f",
        color_discrete_sequence=[YELLOW, PURPLE, BLUE]
    )

    fig.update_layout(
        xaxis_title="Modèle",
        yaxis_title="Temps moyen (secondes)"
    )

    st.plotly_chart(
        apply_chart_style(fig),
        use_container_width=True
    )

    st.divider()

    st.subheader("Tableau comparatif")

    comparison = stats[
        [
            "source",
            "ai_model",
            "total_questions",
            "accuracy",
            "error_rate",
            "avg_response_time"
        ]
    ].copy()

    comparison.columns = [
        "Source",
        "Modèle",
        "Questions",
        "Précision (%)",
        "Taux d'erreur (%)",
        "Temps moyen (s)"
    ]

    st.dataframe(
        comparison.style.format({
            "Précision (%)": "{:.2f}",
            "Taux d'erreur (%)": "{:.2f}",
            "Temps moyen (s)": "{:.2f}"
        }),
        use_container_width=True,
        hide_index=True
    )


# =====================================================
# 12. PAGE ANALYSE PAR CATEGORIE
# =====================================================

elif page == "Analyse par catégorie":

    st.title("Analyse par catégorie")

    st.caption(
        "Étude des performances selon les domaines "
        "de connaissance."
    )

    st.divider()

    if not category_stats.empty:

        st.subheader("Précision par catégorie")

        fig = px.bar(
            category_stats,
            x="category",
            y="accuracy",
            color="ai_model",
            barmode="group",
            color_discrete_sequence=[BLUE, PURPLE, GREEN]
        )

        fig.update_layout(
            yaxis_range=[0, 100],
            xaxis_title="Catégorie",
            yaxis_title="Précision (%)"
        )

        st.plotly_chart(
            apply_chart_style(fig),
            use_container_width=True
        )

        st.divider()

        st.subheader("Classement des catégories")

        ranking = (
            category_stats
            .groupby("category")["accuracy"]
            .mean()
            .sort_values(ascending=False)
            .reset_index()
        )

        ranking.columns = [
            "Catégorie",
            "Précision moyenne (%)"
        ]

        st.dataframe(
            ranking.style.format({
                "Précision moyenne (%)": "{:.2f}"
            }),
            use_container_width=True,
            hide_index=True
        )

        if not ranking.empty:

            c1, c2 = st.columns(2)

            c1.metric(
                "Catégorie la mieux maîtrisée",
                ranking.iloc[0]["Catégorie"],
                f"{ranking.iloc[0]['Précision moyenne (%)']:.2f}%"
            )

            c2.metric(
                "Catégorie la plus difficile",
                ranking.iloc[-1]["Catégorie"],
                f"{ranking.iloc[-1]['Précision moyenne (%)']:.2f}%"
            )

    else:
        st.info("Aucune donnée disponible pour les catégories.")


# =====================================================
# 13. PAGE DONNEES
# =====================================================

elif page == "Données":

    st.title("Données")

    st.caption(
        "Consultation des données utilisées "
        "pour les évaluations."
    )

    st.divider()

    c1, c2 = st.columns(2)

    c1.metric(
        "Nombre de lignes",
        len(filtered_df)
    )

    c2.metric(
        "Nombre de colonnes",
        len(filtered_df.columns)
    )

    st.divider()

    st.subheader("Tableau des évaluations")

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

    csv = filtered_df.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        "Télécharger les données CSV",
        data=csv,
        file_name="trivial_pursuit_benchmark.csv",
        mime="text/csv"
    )


# =====================================================
# 14. PIED DE PAGE
# =====================================================

st.divider()

st.caption(
    "Trivial Pursuit | Benchmark IA | "
    "Projet Data Engineering 2026/2027"
)