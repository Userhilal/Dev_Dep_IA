# Semaine 4 — Tests approfondis et qualité

## 1. Couverture

Le premier rapport local affichait **90 %** de couverture pour `api/` : 79 instructions mesurées, dont 8 non couvertes. Les lignes manquantes correspondaient notamment au refus HTTP 503 en l'absence de classifieur, à la gestion d'une erreur inattendue HTTP 500 et au bloc de lancement direct de l'application.

Les tests d'intégration ajoutés exercent le démarrage réel, l'absence du modèle, le retrait du classifieur et deux pannes internes (`RuntimeError` et `ValueError`). Une `ValueError` interne était initialement transformée en HTTP 422 ; ce traitement a été corrigé pour renvoyer HTTP 500 sans divulguer le message interne.

La dernière mesure transmise est de **96,63 %** : 89 instructions mesurées, 3 non couvertes. Le rapport indique deux lignes non couvertes dans `api/main.py` (bloc de lancement direct) et une dans `api/model.py` (branche d'étiquette inconnue). Aucune exclusion manuelle de lignes n'a été déclarée dans la commande utilisée.

Commande de contrôle :

```powershell
python -m pytest -q --cov=api --cov-report=term-missing --cov-fail-under=95
```

Résultat final observé : **92 passed, 4 xfailed**, un avertissement de dépréciation et une couverture supérieure au seuil de 95 %.

## 2. Défauts identifiés et corrections

| Symptôme | Vérification | Correction |
| --- | --- | --- |
| Les textes composés d'espaces produisaient un refus HTTP 422 sous une forme différente | Tests aux limites et tests de propriétés | Validation des textes blancs au niveau du schéma Pydantic |
| Une panne interne `ValueError` était renvoyée au client comme HTTP 422 | `test_panne_interne_500[value-error]` | Traitement des exceptions internes en HTTP 500 avec message générique |
| Le comportement sans classifieur n'était pas exercé | Tests d'intégration | Contrôle de HTTP 503 pour `/health` et `/predict` |
| Les prédictions incertaines étaient forcées en positif ou négatif | Courbe des seuils et prédiction sur texte inventé | Ajout du verdict `INDETERMINE` sous le seuil de 0,60 |
| Les contrats de prédiction étaient insuffisamment typés | Vérification du contrat de sortie | Ajout de `TypedDict`, de `Literal` et d'une correspondance explicite des étiquettes |

## 3. Seuil d'abstention

Les mesures suivantes proviennent du jeu de test de **58 avis** :

| Seuil | Avis traités automatiquement | Part traitée | Exactitude sur les avis traités | Erreurs | Avis vers vérification humaine |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0,50 | 58 | 100 % | 0,879 | 7 | 0 |
| 0,60 | 42 | 72 % | 0,952 | 2 | 16 |
| 0,65 | 41 | 71 % | 0,976 | 1 | 17 |
| 0,70 | 37 | 64 % | 1,000 | 0 | 21 |

Le **seuil retenu est 0,60**. Il permet de traiter automatiquement 42 avis sur 58, tout en faisant passer les erreurs observées de 7 à 2 parmi les réponses automatiques. **16 avis sur 58**, soit environ 28 %, sont transmis à une vérification humaine. L'exactitude de 95,2 % s'applique uniquement aux 42 avis acceptés, et non à la totalité du jeu.

## 4. Jeu d'or

Le jeu d'or contient **20 avis**, avec les résultats observés suivants :

| Résultat | Nombre | Part des 20 avis |
| --- | ---: | ---: |
| Prédiction correcte | 5 | 25 % |
| Abstention | 11 | 55 % |
| Erreur franche déclarée | 4 | 20 % |

Les quatre erreurs franches sont conservées et documentées avec `xfail(strict=True)`. Leur présence est visible dans les résultats : les tests réussissent sans masquer les limites du modèle.

Ce bilan est moins favorable que celui du jeu de test de 58 avis : l'abstention atteint **55 %** et quatre des neuf réponses automatiques restent incorrectes. La performance est donc fortement dépendante des exemples évalués et ne doit pas être résumée au seul pourcentage de couverture des tests.

## 5. Outils statiques et qualité

Les premières vérifications locales ont révélé **13 remarques Ruff** (7 corrigées automatiquement, 6 restées à corriger). Les problèmes restants concernaient notamment l'ordre des imports, les appels à `zip()` sans `strict=True` et le nom ambigu `l` dans les tests. Après correction, Ruff affiche `All checks passed!`.

Mypy ne signalait pas d'erreur lors du contrôle initial ; cela ne démontrait pas que le contrat de prédiction était suffisamment précis. Après l'ajout de types explicites, Mypy affiche `Success: no issues found in 4 source files`. Les contrôles `pre-commit` Ruff et Mypy passent également.

Les outils statiques n'avaient pas signalé les défauts fonctionnels des réponses HTTP ou le mauvais comportement sur des prédictions incertaines : ce sont les tests ciblés et les mesures qui les ont révélés.

## Points restant à confirmer

Le bon fonctionnement de la CI distante doit être vérifié pour le dernier commit. L'indépendance du jeu d'or vis-à-vis des données d'entraînement et les contributions aux exemples doivent également être confirmées dans les sources du projet.
