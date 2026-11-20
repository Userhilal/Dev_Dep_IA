# sentiment-app 1.0.0 — paquet Python

Classifie des avis en français avec TF-IDF et régression logistique. La commande `sentiment`
propose `predict`, `serve` (FastAPI) et `ui` (avec la dépendance optionnelle Streamlit).

## Construire le paquet

À la racine du dépôt :

```powershell
python src/make_demo.py
python src/train.py
New-Item -ItemType Directory sentiment_app\modele -Force | Out-Null
Copy-Item models\sentiment.joblib sentiment_app\modele\sentiment.joblib
python -m build
```

La roue `dist/sentiment_app-1.0.0-py3-none-any.whl` inclut alors le modèle et fonctionne
sur une machine neuve sans variable `SENTIMENT_MODELE`. Le modèle n'est **pas suivi par Git**.
L'option `SENTIMENT_MODELE` reste disponible pour charger volontairement un autre modèle.

## Installer et utiliser

```powershell
python -m pip install dist\sentiment_app-1.0.0-py3-none-any.whl
sentiment --version
sentiment predict "Livraison rapide, produit conforme, très satisfait"
sentiment serve
```

Pour l'interface : `pip install 'sentiment-app[ui]'` (ou les dépendances du dépôt) et `sentiment ui`.
API sécurisée : copier `.env.example` vers `.env`, définir les clés avec rôles `client` et `admin`,
puis utiliser `/v1/predict` avec l'en-tête `X-API-Key`. Les routes historiques restent
accessibles pour les anciens clients mais sont dépréciées.

## Limites

Le modèle de démonstration ne garantit pas de bonnes prédictions sur des avis réels. Les avis
incertains sont marqués `INDETERMINE` au seuil 0,60. Ne charger que des fichiers Joblib de
confiance. Le déploiement sur Internet nécessite un hébergement API séparé.
