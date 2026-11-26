# Dashboard – Trivial Pursuit Benchmark

## 1. Présentation

Le dashboard Trivial Pursuit Benchmark est une application interactive développée avec Streamlit. Il permet de visualiser et d'analyser les performances de différents modèles d'intelligence artificielle sur des questions de culture générale.

L'objectif est de comparer la précision des modèles, leurs temps de réponse et leurs performances selon les catégories de questions.

## 2. Technologies utilisées

- **Python** : langage de développement.
- **Streamlit** : création de l'interface interactive.
- **Pandas** : manipulation et analyse des données.
- **Plotly Express** : création des graphiques interactifs.

## 3. Design et interface

Le dashboard utilise un thème sombre personnalisé.

Les principales caractéristiques graphiques sont :

- Fond principal bleu nuit.
- Barre latérale sombre.
- Cartes statistiques personnalisées.
- Graphiques interactifs.
- Navigation latérale.
- Filtres dynamiques par source et par modèle IA.

## 4. Organisation du dashboard

Le dashboard est organisé en quatre pages principales.

### 4.1 Vue générale

Cette page présente une synthèse globale des performances.

**Indicateurs clés :**
- Nombre total de questions.
- Précision globale (Accuracy).
- Nombre d'évaluations.
- Temps moyen de réponse.
- Nombre de modèles testés.

**Visualisations :**
- Comparaison de la précision des modèles.
- Comparaison des temps moyens de réponse.
- Performance par catégorie.

### 4.2 Comparaison des modèles

Cette page permet de comparer les différents modèles d'intelligence artificielle.

**Indicateurs et visualisations :**
- Précision de chaque modèle.
- Temps moyen de réponse.
- Taux d'erreur.
- Tableau comparatif des performances.

Les résultats sont regroupés par source et par modèle.

### 4.3 Analyse par catégorie

Cette page étudie les performances des modèles selon les domaines de connaissance.

**Visualisations :**
- Précision par catégorie.
- Comparaison des modèles par catégorie.
- Classement des catégories selon leur précision moyenne.

**Indicateurs :**
- Catégorie la mieux maîtrisée.
- Catégorie la plus difficile.

### 4.4 Données

Cette page permet de consulter les données utilisées pour les évaluations.

**Fonctionnalités :**
- Affichage du nombre de lignes.
- Affichage du nombre de colonnes.
- Tableau interactif des évaluations.
- Téléchargement des résultats au format CSV.

## 5. Filtres interactifs

La barre latérale propose deux filtres :

- **Source** : sélection des sources de données.
- **Modèle d'intelligence artificielle** : sélection des modèles à analyser.

Les graphiques, les indicateurs et les tableaux sont actualisés selon les filtres sélectionnés.

## 6. Structure technique

Le code principal du dashboard est situé dans :

`dashboard/app.py`

Les données sont chargées à travers le module :

`components/data.py`

La fonction `load_data()` permet de récupérer les données utilisées par l'application.

## 7. Calcul des indicateurs

### Accuracy globale

L'accuracy représente le pourcentage de réponses correctes parmi les réponses évaluées.

Formule :

Accuracy = (Nombre de bonnes réponses / Nombre de réponses évaluées) × 100

### Taux d'erreur

Taux d'erreur = 100 - Accuracy

### Temps moyen de réponse

Le temps moyen est calculé à partir de la colonne `response_time`.

## 8. Lancement de l'application

Activer l'environnement virtuel :

```bash
source .venv/bin/activate
```

Lancer le dashboard :

```bash
streamlit run dashboard/app.py
```

## 9. Objectif final

Le dashboard permet de faciliter l'interprétation des résultats du benchmark, de comparer les modèles d'intelligence artificielle et d'identifier leurs points forts et leurs limites selon les catégories de questions.

Il constitue la partie visualisation et analyse du projet Data Engineering Trivial Pursuit Benchmark.