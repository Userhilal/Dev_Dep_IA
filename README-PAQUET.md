# sentiment-app 1.0.1 — paquet Python

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

La roue `dist/sentiment_app-1.0.1-py3-none-any.whl` inclut alors le modèle et fonctionne
sur une machine neuve sans variable `SENTIMENT_MODELE`. Le modèle n'est **pas suivi par Git**.
L'option `SENTIMENT_MODELE` reste disponible pour charger volontairement un autre modèle.

## Installer et utiliser

```powershell
python -m pip install dist\sentiment_app-1.0.1-py3-none-any.whl
sentiment --version
sentiment "Livraison rapide, produit conforme, très satisfait"
sentiment --json "Colis abîmé, service client injoignable"
python -c "from sentiment_app import predict; print(predict('Produit conforme'))"
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

## Essai sans les sources du dépôt

Installer depuis la Release GitHub (de préférence dans un environnement virtuel neuf) :

```powershell
python -m pip install https://github.com/Userhilal/Dev_Dep_IA/releases/download/v1.0.1/sentiment_app-1.0.1-py3-none-any.whl
sentiment --version
sentiment --json "Colis abîmé, service client injoignable"
python -m pip check
```

**Limite de la méthode Git (`pip install git+...@v1.0.1`)** : le modèle n'est
pas enregistré dans Git pour respecter le manuel. Un paquet reconstruit directement
depuis le tag Git ne peut donc pas embarquer le modèle sans étape spécifique de
production de cet artefact ; utiliser la roue publiée dans la Release.
Le guide `TESTER-LA-ROUE.md` liste aussi une fiche de recette C1-C10.
