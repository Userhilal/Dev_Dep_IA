# Journal des versions

## [1.0.0] - 2026-11-20 — Manuel Volume 1

- API `/v1` protégée par des clés et des rôles `client`/`admin` ; erreurs stables et CORS contrôlé.
- Client web HTML/JavaScript et client Streamlit compatible avec `/v1`.
- Roue Python incluant le modèle, installable hors du dépôt ; commande `sentiment`.
- Compatibilité conservée avec les routes historiques `/health` et `/predict`.
- **Limites :** les kits originaux `kit-tp2.zip`, kit TP3 et kit TP4 du nouveau manuel
  n'ont pas été fournis ; leurs tests et le vérificateur officiels ne sont pas disponibles.
  Les preuves cloud et service Java complémentaire ne sont pas effectués.

## 0.6.0 (TP6) : le paquet

- Installation : paquet Python et commande `sentiment` (`predict`, `serve`, `ui`).
- Développement : prédiction dans `sentiment_app` ; variable `SENTIMENT_MODELE`.
- CI : construction et vérification de la roue en dehors du dépôt.

## 0.5.0 (TP5) : l'interface

- Streamlit : avis individuel, fichier CSV, visualisations des verdicts et de la confiance.

## 0.4.0 (TP4) : tests et qualité

- Contrat d'entrée, abstention, jeu d'or, intégration, Ruff, mypy et CI.

## 0.3.0 (TP3) : l'API

- FastAPI : `/health`, `/predict`, contrat Pydantic.

## 0.2.0 (TP2) : le modèle

- TF-IDF et régression logistique, métriques versionnées, modèle reconstituable.

## 0.1.0 (TP1) : le cadrage

- Environnement Python 3.11, dépôt, fiches de cadrage.
