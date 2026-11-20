# Semaine 6 : le paquet, notes du binôme

> Trois questions, quelques phrases chacune. Répondez avec ce que vous avez observé.

## 1. Pourquoi le modèle n'est-il pas dans la roue ? Comment le paquet le trouve-t-il ?

Nous avons remplacé les imports utilisant sys.path par des imports directs depuis sentiment_app.predict. Cette organisation rend le code plus propre et permet d'utiliser le paquet après son installation, même en dehors du dépôt Git.

## 2. Qu'est-ce qui a changé dans api/model.py quand predict() est entré dans le paquet, et pourquoi est-ce mieux ?

Nous avons remplacé les imports utilisant sys.path par des imports directs depuis sentiment_app.predict. Cette organisation rend le code plus propre et permet d'utiliser le paquet après son installation, même en dehors du dépôt Git.

## 3. La roue installée hors du dépôt : qu'a-t-il fallu lui fournir, et pourquoi scikit-learn est-il épinglé dans pyproject.toml ?

La roue déclare ses dépendances, mais ne contient pas le modèle entraîné. Pour réaliser une prédiction depuis un environnement indépendant, il faut fournir un modèle compatible via SENTIMENT_MODELE. La version de scikit-learn est épinglée en 1.5.* afin de réduire les risques d'incompatibilité avec le modèle sauvegardé.
