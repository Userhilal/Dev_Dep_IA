
# Fiche de cadrage : Analyse des avis en pharmacie

## Besoin en une phrase

Classer automatiquement les avis clients positifs et négatifs afin d'aider les pharmacies à identifier rapidement les problèmes de service et à améliorer leur réputation.

## Utilisateur final

Les propriétaires et les gérants de pharmacies au Canada utiliseront cet outil pour repérer les avis négatifs et prioriser les actions d'amélioration du service.

## Approche retenue

- [ ] Règles métier
- [x] Machine learning
- [ ] RAG
- [ ] Modèle génératif seul

## Justification

L'apprentissage supervisé est adapté à cette tâche. (a) Les 500 avis disponibles sont déjà étiquetés positifs ou négatifs par les propriétaires des pharmacies. (b) Les prédictions peuvent être vérifiées par un humain en relisant les avis. (d) Une erreur peut masquer une insatisfaction réelle ou déclencher une réaction inutile ; les cas ambigus seront donc contrôlés manuellement.

## Données nécessaires

Les données comprennent 500 avis de clients de pharmacies au Canada, étiquetés positifs ou négatifs sur une période de six mois. Ils portent notamment sur la qualité du service, les délais d'attente, l'amabilité du personnel et la disponibilité des médicaments.

## Métrique de succès

Le modèle devra viser un F1-score d'au moins 0,80 sur un jeu de test indépendant. Le rappel de la classe négative sera également mesuré afin de limiter les avis négatifs non détectés.

## Conséquence d'une erreur

Un avis négatif mal classé peut retarder la correction d'un problème réel, tandis qu'un avis positif classé négatif peut entraîner une réaction inutile. Les propriétaires vérifieront les prédictions incertaines avant de prendre une décision.

## Risques éthiques

Les avis peuvent contenir des noms ou des informations personnelles. Les données devront être anonymisées et les biais liés aux différences de rédaction ou de clientèle devront être surveillés.

## Approche écartée et pourquoi

Les heuristiques simples risquent de mal interpréter le sarcasme et les formulations nuancées. L'apprentissage non supervisé exploiterait moins directement les étiquettes déjà disponibles.
