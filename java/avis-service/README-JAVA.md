# Java Spring Boot — activité complémentaire du manuel V1.1

**Statut : reconstruction pédagogique du service Java, PAS le kit TP 2 du professeur.**
Le kit original `java/avis-service` n'était pas présent dans le dépôt consulté.
Les cinq tests JUnit ci-dessous ont été écrits pour cette reconstruction et ne sont
pas les tests officiels du kit.

## Contrat (manuel, pages 51–52)

- Java **21** et Maven (3.6.3 ou plus récent), Spring Boot **3.5.16**.
- Java : `POST http://localhost:8081/avis/analyse`, JSON `{"texte":"un avis"}`.
- Python : `POST http://127.0.0.1:8000/v1/predict`, JSON `{"text":"un avis"}` ;
  clé `X-API-Key` prise de `SENTIMENT_API_KEY`.
- Résultat Java : `{"verdict":"POSITIVE|NEGATIVE|INDETERMINE","confiance":0.7,"aVerifier":false}`.
- Si Python est arrêté : **503** avec `{"erreur":{"code":"API_INJOIGNABLE",...}}`.
- Le client Java force **HTTP/1.1** (important pour l'essai réel du manuel).
- Ne jamais enregistrer une clé d'API dans Git ni la publier dans les captures.

## 1. Prérequis, depuis PowerShell à la racine du projet

```powershell
java -version
mvn -version
```

## 2. Terminal 1 : démarrer l'API Python

Le fichier `.env` existant dans la racine doit fournir `API_KEYS=...` et `API_KEY=...`.

```powershell
cd "$HOME\Desktop\5IADO\Dev_Dep\sentiment-app\sentiment-app"
.\.venv\Scripts\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

Vérifier depuis un deuxième terminal :

```powershell
Invoke-RestMethod http://127.0.0.1:8000/v1/health
```

## 3. Terminal 2 : tester et démarrer Java

Depuis la racine du même dépôt :

```powershell
cd "$HOME\Desktop\5IADO\Dev_Dep\sentiment-app\sentiment-app"
mvn -f java/avis-service/pom.xml clean package
```

Résultat à obtenir : `Tests run: 5, Failures: 0, Errors: 0` et `BUILD SUCCESS`.

Pour lancer le JAR, la clé client doit être celle de `API_KEY=` de `.env` :

```powershell
$env:SENTIMENT_API_URL = 'http://127.0.0.1:8000'
$env:SENTIMENT_API_KEY = (Get-Content .env | Where-Object { $_ -match '^API_KEY=' } | Select-Object -First 1) -replace '^API_KEY=', ''
if (-not $env:SENTIMENT_API_KEY) { throw 'Cle API_KEY absente de .env' }
java -jar java/avis-service/target/avis-service-1.0.0.jar
```

Ne copiez pas la vraie clé dans le README ni dans vos captures.

## 4. Terminal 3 : test d'intégration réel

```powershell
$corps = @{ texte = 'Livraison rapide mais produit décevant' } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri 'http://localhost:8081/avis/analyse' `
  -ContentType 'application/json; charset=utf-8' -Body ([Text.Encoding]::UTF8.GetBytes($corps))
```

La réponse précise dépend du modèle réellement chargé par Python ; le manuel
mentionne `INDETERMINE`, confiance 0,559, `aVerifier: true`.

**Pour tester l'échec réseau :** arrêtez Python avec Ctrl+C dans le terminal 1,
puis relancez l'appel depuis le terminal 3. Attendu : HTTP 503, code
`API_INJOIGNABLE`. Sous PowerShell, `Invoke-RestMethod` signale une exception
pour HTTP 503 ; inspectez son statut et son corps pour la preuve.

## Ne pas confondre avec Streamlit Cloud

La démo Streamlit Cloud utilise directement le modèle de la roue. Son adresse
`*.streamlit.app` **n'est pas une adresse d'API FastAPI `/v1/predict`** et ne
peut pas remplacer `SENTIMENT_API_URL`.

## Vérifications de publication

Avant un commit éventuel :

```powershell
git add java/avis-service
 git diff --cached --check
 git diff --cached --name-only
```

Les secrets dans `.env` et la modification locale `tests/test_client.py`
ne doivent jamais être ajoutés au commit.
