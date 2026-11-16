# Semaine 2 — Entraînement et évaluation

## Données et modèle

L'entraînement vérifié utilise le jeu de démonstration de 290 avis en français, répartis en 145 avis positifs et 145 avis négatifs. Le modèle est une chaîne TF-IDF associée à une régression logistique. Les prédictions sont exposées par `src/predict.py` et le modèle entraîné est enregistré localement dans `models/sentiment.joblib`.

L'évaluation fournie ici concerne **le jeu de démonstration**. Aucun résultat d'entraînement sur Allociné n'a été confirmé dans les exécutions examinées.

## Résultats mesurés

Le jeu de test contient 58 avis, soit 29 avis par classe :

| Mesure | Résultat |
| --- | ---: |
| Accuracy | 0,879 |
| F1 macro | 0,879 |
| Précision macro | 0,883 |
| Rappel macro | 0,879 |
| F1 de la classe négative | 0,885 |
| F1 de la classe positive | 0,873 |
| Erreurs de classification | 7 / 58 |

Matrice de confusion (lignes : vérités ; colonnes : prédictions) :

| Vérité / prédiction | Négative | Positive |
| --- | ---: | ---: |
| Négative | 27 | 2 |
| Positive | 5 | 24 |

Le modèle classe incorrectement deux avis négatifs comme positifs et cinq avis positifs comme négatifs.

## Analyse des erreurs

Trois exemples examinés montrent une difficulté à traiter les retournements de sens dans les avis mitigés : un avis qui commence par un reproche puis se termine par une appréciation positive peut être classé négatif, et inversement. La représentation TF-IDF identifie les termes présents, mais représente difficilement l'ordre des propositions et des expressions comme « sauf que » ou « ensuite ».

Une amélioration possible serait d'utiliser davantage de données représentatives des négations et des avis mitigés, puis de comparer le modèle avec une approche sensible au contexte. Ces améliorations restent des pistes, pas des résultats mesurés.

## Reproductibilité

Commandes utilisées :

```powershell
python src/train.py
python src/evaluate.py
python -m pytest -q
```

Le fichier `models/metrics.json` doit être conservé dans le dépôt Git pour documenter l'évaluation ; le fichier entraîné `models/sentiment.joblib` reste local et est régénéré par la commande d'entraînement.
