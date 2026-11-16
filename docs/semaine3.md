# Semaine 3 — API FastAPI

## 1. Pourquoi l'API refuse-t-elle de démarrer sans `models/sentiment.joblib` plutôt que de répondre 503 ?

Le modèle est une dépendance indispensable au fonctionnement du service. Au démarrage, la fonction de cycle de vie charge le classifieur avant que l'API accepte des requêtes. Si le fichier `models/sentiment.joblib` est absent, le chargement déclenche `FileNotFoundError` et le démarrage échoue. Ce comportement empêche le service d'annoncer qu'il est prêt alors qu'il ne peut effectuer aucune prédiction.

La réponse HTTP 503 correspond à un autre scénario : l'application est accessible, mais son classifieur n'est pas disponible dans l'état de l'application. Les tests d'intégration vérifient ces situations séparément.

## 2. Un texte vide est-il refusé deux fois, par Pydantic puis par `predict()` ?

Les deux validations sont complémentaires. Pydantic contrôle les requêtes HTTP à l'entrée de l'API et refuse les textes vides ou composés uniquement d'espaces avec une réponse HTTP 422 structurée. La validation dans `predict()` protège également le modèle lorsque la fonction est appelée directement, sans passer par FastAPI.

Le problème constaté initialement était l'incohérence de la forme du refus pour les textes contenant seulement des espaces. L'ajout d'un validateur dans le schéma a rendu le comportement HTTP cohérent. Les erreurs inattendues provenant du modèle sont désormais traitées comme des erreurs internes HTTP 500 sans exposer leur message technique dans la réponse.

## Contrôles réalisés

Les routes `/health` et `/predict` fonctionnent, le modèle se charge au démarrage et les tests couvrent les réponses 422, 503 et 500. Le lancement local de l'API a affiché `Application startup complete` et a confirmé le chargement du classifieur `tfidf-logreg`.
