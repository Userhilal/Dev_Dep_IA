# Journal des versions

Le numéro de version suit les TP : 0.N.0 à la fin du TP N. Chaque version publiée porte une étiquette Git `v0.N.0`.

## 0.6.0 (TP6) : le paquet

- Installation : l'application est distribuée sous forme de paquet Python
  avec une commande sentiment (predict, serve, ui).
- Développement : predict.py est intégré au paquet sentiment_app.
  L'API importe directement le paquet, sans modifier sys.path.
  Le modèle peut être fourni avec la variable SENTIMENT_MODELE.
- Intégration continue : le workflow inclut la construction de la roue
  et sa vérification dans un environnement indépendant.
## 0.5.0 (TP5) : l'interface

- Page Streamlit : un avis, ou un fichier d'avis ; le client HTTP traduit chaque réponse de l'API.

## 0.4.0 (TP4) : tests et qualité

- Contrat d'entrée testé, abstention `INDETERMINE`, jeu d'or, tests d'intégration, contrat typé, ruff, mypy, pre-commit.

## 0.3.0 (TP3) : l'API

- FastAPI : `/health`, `/predict`, contrat Pydantic ; la CI entraîne le modèle avant les tests.

## 0.2.0 (TP2) : le modèle

- TF-IDF et régression logistique ; les métriques sont versionnées, le modèle ne l'est pas.

## 0.1.0 (TP1) : le cadrage

- Environnement Python 3.11, structure du dépôt, trois fiches de cadrage, dépôt GitHub à deux auteurs.
