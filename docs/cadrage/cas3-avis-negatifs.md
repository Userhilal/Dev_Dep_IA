# Fiche de cadrage : Priorisation des avis négatifs

## Besoin en une phrase

Classer les avis négatifs des clients afin d'identifier les problèmes les plus urgents et d'améliorer la satisfaction client.

## Utilisateur final

Le responsable du service client et l'équipe de support utilisent l'outil pour repérer les réclamations prioritaires et organiser leur traitement.

## Approche retenue

- [ ] Règles métier
- [x] Machine learning
- [ ] RAG
- [ ] Modèle génératif seul

## Justification

Le machine learning est adapté à la classification d'avis clients. (a) Des avis historiques étiquetés permettent d'entraîner le modèle. (b) Les prédictions peuvent être évaluées sur un jeu de test et vérifiées par un humain. (c) Le classement de nombreux avis peut être réalisé à faible coût après l'entraînement.

## Données nécessaires

Les données comprennent les textes des avis clients et, si possible, leurs catégories ou niveaux de priorité. Elles doivent être anonymisées et vérifiées avant l'entraînement.

## Métrique de succès

Le modèle devra atteindre un F1-score d'au moins 0,80 sur un jeu de test indépendant. Le rappel des avis urgents sera aussi mesuré afin de limiter les réclamations prioritaires manquées.

## Conséquence d'une erreur

Une réclamation importante peut être retardée ou un avis non urgent peut être traité en priorité. Un responsable vérifiera les cas urgents ou incertains avant toute décision importante.

## Risques éthiques

Les avis peuvent contenir des noms, des coordonnées ou des informations sensibles. Les données doivent être anonymisées et les résultats contrôlés pour limiter les biais.

## Approche écartée et pourquoi

Les règles métier seules risquent de manquer les formulations variées. Un modèle génératif seul peut produire des résultats variables et entraîner des coûts supplémentaires.
