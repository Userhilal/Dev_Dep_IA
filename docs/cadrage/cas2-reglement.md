# Fiche de cadrage : Analyse des commentaires sur le règlement immobilier

## Besoin en une phrase

Classer les commentaires des résidents afin d'identifier les problèmes d'application du règlement et d'aider le syndic à organiser leur traitement.

## Utilisateur final

Le syndic et le comité d'administration utilisent l'outil pour repérer les plaintes récurrentes et prioriser les actions nécessaires.

## Approche retenue

- [ ] Règles métier
- [x] Machine learning
- [ ] RAG
- [ ] Modèle génératif seul

## Justification

L'apprentissage supervisé est adapté à cette tâche. (a) Les 1 200 commentaires historiques sont déjà étiquetés par le comité. (b) Les prédictions peuvent être vérifiées en relisant les commentaires. (c) Le classement automatique réduit le temps de traitement sans nécessiter un appel coûteux à un modèle génératif pour chaque commentaire.

## Données nécessaires

Les données comprennent les 1 200 commentaires collectés sur deux ans et leurs étiquettes positives ou négatives. Les données doivent être nettoyées, anonymisées et séparées en ensembles d'entraînement et de test.

## Métrique de succès

Le modèle devra atteindre un F1-score d'au moins 0,80 sur un jeu de test indépendant. Le rappel de la classe négative sera également suivi pour limiter les plaintes importantes manquées.

## Conséquence d'une erreur

Une plainte peut être ignorée ou classée à tort comme négative. Le syndic vérifiera les commentaires ambigus et les cas prioritaires avant de décider des mesures à prendre.

## Risques éthiques

Les commentaires peuvent contenir des informations personnelles ou des accusations visant des résidents. L'accès doit être limité et les résultats ne doivent pas servir à sanctionner automatiquement une personne.

## Approche écartée et pourquoi

Les heuristiques simples risquent de mal interpréter les formulations nuancées. L'apprentissage non supervisé ne profite pas directement des étiquettes déjà disponibles.
