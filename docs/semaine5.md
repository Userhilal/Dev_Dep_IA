# Semaine 5 — Interface Streamlit

## 1. Pourquoi l'interface n'importe-t-elle jamais `predict()` ni le fichier `.joblib` ?

L'interface présente les résultats et communique avec le service au moyen de requêtes HTTP ; elle n'exécute pas directement le modèle. Le module `ui/client.py` contacte les routes `/health` et `/predict`, puis traduit les réponses en messages lisibles. Le chargement du modèle et le choix du verdict restent dans l'API.

Cette séparation permet de réentraîner ou de remplacer le modèle sans changer le code de la page, tant que le contrat HTTP est conservé. Elle rend également possible l'utilisation de l'API par d'autres clients.

## 2. Que montre l'interface quand le modèle hésite, et pourquoi est-ce mieux qu'un verdict forcé ?

Lorsque le score est inférieur au seuil de 0,60, l'API renvoie `INDETERMINE`. L'interface traduit cette valeur par « Je ne sais pas : à faire vérifier par un humain », affiche le score et un message indiquant qu'une vérification humaine est nécessaire.

Pour le texte `xqzvb wlkptr grombu`, la prédiction contrôlée renvoie `INDETERMINE` avec un score de **0,5162**, affiché approximativement comme **52 %**. L'abstention évite de transformer une confiance insuffisante en avis positif ou négatif potentiellement trompeur.

## 3. Que voit l'utilisateur quand l'API tombe ? Combien d'avis du fichier CSV partent vers un humain ?

Lorsque la connexion à l'API échoue, le client est conçu pour afficher « API injoignable » au lieu de provoquer une erreur Python dans la page. Un texte refusé provoque un avertissement spécifique, et un classifieur indisponible renvoie un message de modèle non chargé. Ces cas sont couverts par les tests automatiques ; les manipulations manuelles correspondantes restent à confirmer.

Le fichier `data/avis_exemple.csv` fourni contient **6 avis**. Le nombre effectivement classé `INDETERMINE` lors de l'import dans l'interface **n'a pas encore été communiqué par une exécution manuelle**. Il reste à ouvrir l'onglet « Un fichier d'avis », importer le CSV, relever le récapitulatif et vérifier le téléchargement de `resultats.csv`.

## Vérifications déjà effectuées

L'interface Streamlit s'est ouverte sur le port 8501 avec FastAPI accessible sur le port 8000. L'affichage « API prête » a été constaté et les deux onglets « Un avis » et « Un fichier d'avis » sont présents. La suite globale, après installation de l'interface, a affiché **92 passed, 4 xfailed** avec **96,63 %** de couverture API. Le contrôle automatique ne remplace pas les derniers essais manuels.
