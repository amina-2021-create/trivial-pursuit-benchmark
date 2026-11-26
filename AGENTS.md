# AGENTS.md — Projet Jouons au Trivial Pursuit

## 1. Présentation du projet

Le projet consiste à réaliser un benchmark de modèles de langage (LLM) locaux à partir de questions de culture générale provenant de l'API Open Trivia Database (OpenTDB).

L'objectif est de comparer les performances des modèles selon plusieurs critères :
- Le taux de bonnes réponses.
- Les catégories de questions.
- Le niveau de difficulté.
- Le temps de réponse.
- La qualité des réponses générées.

Les résultats seront analysés et présentés sous forme de tableaux de bord.

## 2. Technologies utilisées

- Python 3
- Pandas
- PyArrow
- Requests
- Parquet
- Open Trivia Database (OpenTDB)
- LM Studio
- Qwen2-500M-Instruct
- Power BI
- Git et GitHub

## 3. Architecture du projet

Le projet utilise une architecture Medallion :

| Dossier | Rôle |
|---|---|
| `bronze/` | Données brutes extraites depuis OpenTDB |
| `silver/` | Données nettoyées et transformées |
| `gold/` | Résultats du benchmark et données finales |
| `src/` | Scripts Python |
| `logs/` | Journaux d'exécution et erreurs |
| `target/` | Rapports et fichiers exportés |

## 4. Fonctionnement du pipeline

Le pipeline de données comprend les étapes suivantes :

1. Extraction des questions depuis OpenTDB.
2. Stockage des données brutes dans Bronze.
3. Nettoyage et transformation des données dans Silver.
4. Préparation des questions et des propositions de réponses.
5. Interrogation des modèles LLM via l'API locale de LM Studio.
6. Récupération des réponses générées.
7. Calcul de la justesse des réponses et du temps de réponse.
8. Enregistrement des résultats dans Gold.
9. Analyse des performances et création du tableau de bord.

## 5. Structure des données

### Données Silver

Les données nettoyées contiennent :

- `type`
- `difficulty`
- `category`
- `question`
- `correct_answer`
- `incorrect_answers`

### Données Gold

Les résultats du benchmark doivent notamment contenir :

- `type`
- `difficulty`
- `category`
- `question`
- `correct_answer`
- `ai_answer`
- `ai_correct`
- `response_time`
- `model_name`
- `prompt_version`

## 6. Protocole de benchmark

Pour chaque question :

1. Récupérer la question et les propositions.
2. Mélanger les propositions de manière reproductible.
3. Construire un prompt adapté au type de question.
4. Envoyer la question au modèle sans lui transmettre la réponse correcte.
5. Mesurer le temps de réponse.
6. Récupérer la réponse générée.
7. Comparer la réponse avec la réponse correcte.
8. Enregistrer les résultats dans Gold.

Les tests doivent commencer sur un petit échantillon avant le traitement complet.

## 7. Contrôle technique et qualité des données

Chaque étape du pipeline doit faire l'objet de contrôles techniques.

### 7.1 Contrôle des données Bronze

- Vérifier que les fichiers JSON sont valides.
- Vérifier la présence des champs attendus.
- Contrôler le nombre de questions extraites.
- Vérifier l'absence de fichiers vides.
- Conserver les données brutes sans modification.

### 7.2 Contrôle des données Silver

- Vérifier les valeurs manquantes.
- Supprimer les questions vides ou invalides.
- Supprimer les doublons.
- Vérifier les catégories et les niveaux de difficulté.
- Vérifier la cohérence des réponses correctes et incorrectes.
- Contrôler le nombre de lignes après nettoyage.
- Vérifier la lecture des fichiers Parquet.

### 7.3 Contrôle du benchmark

- Vérifier la disponibilité du serveur LM Studio.
- Vérifier que le modèle demandé est bien chargé.
- Vérifier que chaque requête reçoit une réponse.
- Gérer les erreurs de connexion et les délais d'attente.
- Mesurer le temps de réponse de chaque question.
- Vérifier que la réponse correcte n'est jamais transmise au modèle.
- Contrôler la comparaison entre réponse IA et réponse attendue.
- Identifier les réponses manquantes ou les erreurs de génération.

### 7.4 Contrôle des résultats Gold

- Vérifier le nombre de questions traitées.
- Vérifier l'absence de doublons.
- Contrôler les types des colonnes.
- Vérifier que les temps de réponse sont positifs.
- Vérifier que `ai_correct` contient des valeurs cohérentes.
- Contrôler les résultats avant leur utilisation dans Power BI.

### 7.5 Tests techniques

Avant chaque exécution complète :

- Effectuer un test sur un petit échantillon.
- Vérifier les connexions API.
- Tester les fonctions de nettoyage et de comparaison.
- Vérifier les fichiers générés.
- Consulter les logs en cas d'erreur.
- Documenter les anomalies rencontrées.

## 8. Mise en page et conventions de développement

### 8.1 Organisation du code

- Utiliser des noms de fichiers et de variables explicites.
- Séparer les fonctions selon leurs responsabilités.
- Éviter de regrouper tout le traitement dans un seul script.
- Ajouter des commentaires pour expliquer les traitements importants.
- Utiliser des fonctions réutilisables.
- Respecter une indentation de 4 espaces.
- Utiliser des noms de variables en `snake_case`.
- Ajouter des docstrings aux fonctions principales.

### 8.2 Présentation des fichiers

- Utiliser des titres et des sections clairs.
- Organiser les scripts avec des blocs logiques.
- Conserver une structure homogène entre les fichiers.
- Éviter les lignes de code inutilement longues.
- Utiliser des messages d'exécution compréhensibles.
- Ajouter des commentaires uniquement lorsqu'ils apportent une information utile.

### 8.3 Présentation des résultats

Les résultats doivent être faciles à lire et à analyser.

Les tableaux doivent notamment présenter :
- Le nom du modèle.
- Le nombre de questions testées.
- Le nombre de bonnes réponses.
- Le taux de réussite.
- Le temps moyen de réponse.
- Les résultats par catégorie.
- Les résultats par difficulté.

### 8.4 Mise en page du tableau de bord Power BI

Le tableau de bord doit respecter les principes suivants :

- Présentation claire et professionnelle.
- Titres explicites pour chaque visualisation.
- Couleurs cohérentes entre les pages.
- Indicateurs KPI visibles.
- Axes et légendes lisibles.
- Filtres par modèle, catégorie et difficulté.
- Comparaison facile entre les modèles.
- Affichage des taux en pourcentage.
- Affichage des temps de réponse en secondes.

## 9. Indicateurs d'analyse

Les principaux indicateurs à calculer sont :

- Nombre total de questions.
- Nombre de réponses correctes.
- Nombre de réponses incorrectes.
- Taux de réussite global.
- Temps moyen de réponse.
- Taux de réussite par catégorie.
- Taux de réussite par difficulté.
- Temps moyen par modèle.
- Comparaison des performances entre modèles.

## 10. Règles à respecter par les agents IA

Tout agent IA intervenant sur ce projet doit :

- Respecter l'architecture Bronze, Silver et Gold.
- Ne pas supprimer les données sources.
- Ne pas inventer de résultats.
- Ne jamais communiquer la réponse correcte au modèle interrogé.
- Respecter les conventions de nommage.
- Produire du code lisible, commenté et structuré.
- Vérifier les résultats avant de modifier les fichiers existants.
- Signaler les erreurs et les limites techniques.
- Documenter les modifications importantes.
- Préserver la reproductibilité des expériences.

## 11. Livrables attendus

Les livrables du projet comprennent :

- Les données brutes Bronze.
- Les données nettoyées Silver.
- Les résultats enrichis Gold.
- Les scripts Python d'extraction, de nettoyage et de benchmark.
- Les logs d'exécution.
- Le tableau de bord Power BI.
- La documentation technique.
- Le dépôt GitHub contenant le projet.

## 12. Objectif final

Produire un benchmark reproductible permettant d'évaluer et de comparer plusieurs modèles de langage locaux sur un ensemble de questions de culture générale, en analysant leur précision, leur comportement selon les catégories et les difficultés, ainsi que leur temps de réponse.