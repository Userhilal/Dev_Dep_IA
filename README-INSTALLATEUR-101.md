# Installateur Windows sentiment-app 1.0.1 — kit de reconstruction

Ce kit de 4 fichiers est **une reconstruction adaptée à la roue v1.0.1**, pas le kit officiel de l'enseignant. L'installateur Windows final **n'est pas inclus** : il se construit sur votre ordinateur Windows. Le setup.exe dépassera probablement 10 Mo (souvent >60 Mo) et ne convient pas au formulaire déjà rempli.

## Prérequis

- Windows 10/11 x64.
- L'environnement `.venv` ayant construit le modèle, avec **Python 3.11.9** actif.
- La roue `dist/sentiment_app-1.0.1-py3-none-any.whl` contenant `sentiment_app/modele/sentiment.joblib`.
- Inno Setup 6.3+ : `winget install --id JRSoftware.InnoSetup --exact` (uniquement pour la compilation finale).
- Accès Internet lors de la construction : récupération de Python embarqué depuis python.org et des dépendances binaires depuis PyPI.

## Placer les fichiers

Décompresser ce ZIP à la **racine** du projet `sentiment-app` de façon à obtenir :

```
sentiment-app/
  dist/sentiment_app-1.0.1-py3-none-any.whl
  installateur/
    build_installateur.ps1
    sentiment.iss
    sentiment.cmd
    LISEZMOI.txt
```

Ne pas écraser le code ou les modèles existants.

## Construire (PowerShell)

```powershell
cd "$HOME\Desktop\5IADO\Dev_Dep\sentiment-app\sentiment-app"
.\.venv\Scripts\Activate.ps1
python --version
winget install --id JRSoftware.InnoSetup --exact
powershell -ExecutionPolicy Bypass -File .\installateur\build_installateur.ps1
```

Le script : (1) contrôle Python et le modèle dans la roue, (2) gèle les versions de l'environnement, (3) télécharge Python 3.11.9 embarqué, (4) récupère les roues Windows binaires nécessaires, (5) assemble `installateur/build/app`, (6) vérifie `sentiment --version`, le JSON et l'import Python, (7) compile avec Inno Setup.

Pour une **préparation sans Inno Setup**, ajouter `-SansCompilation`. Cela ne génère aucun setup.exe.

## Sortie attendue

`installateur/Output/sentiment-app-1.0.1-setup.exe`

**Non validé à ce stade** : le script doit s'exécuter sur Windows ; les vérifications statiques ne remplacent pas les tests réels. Corriger d'abord toute erreur de construction.

## Essais sur un compte utilisateur Windows distinct / Windows Sandbox

1. Sans Python préinstallé, double-cliquer sur le setup.exe et installer pour l'utilisateur courant.
2. Dans un nouveau terminal, `where.exe python` (idéalement absent) puis `sentiment --version` : doit montrer `sentiment-app 1.0.1`.
3. `sentiment "Livraison rapide, tres satisfait"` et `sentiment --json "Produit casse et service injoignable"` : verdict et confiance.
4. `sentiment " "` puis `$LASTEXITCODE` en PowerShell : texte vide et code `2`.
5. Tester le raccourci Démarrer.
6. Désinstaller depuis Paramètres > Applications, puis ouvrir un nouveau terminal et vérifier que `Get-Command sentiment -ErrorAction SilentlyContinue` ne trouve rien.

Si l'installateur n'est pas signé, Windows peut afficher un avertissement SmartScreen. Ne distribuez pas le fichier avant inspection et essais. Conserver le SHA-256 obtenu à la compilation.

## Git

Ne versionnez pas les fichiers temporaires ou l'installateur dans le dépôt. Ajoutez seulement :

```
installateur/build/
installateur/Output/
```

à `.gitignore`, puis versionnez le code source de `installateur/` après les tests. Ne stagez pas `tests/test_client.py`.

## Remarque technique

Le script vérifie le modèle embarqué, impose Python 3.11.9 et contraint les paquets téléchargés par les versions présentes dans le venv. L'utilisateur final n'a pas besoin d'Internet. L'installateur est pour Windows x64 uniquement et n'est pas la même chose que la roue Python ou l'interface Streamlit Cloud.

## Correctif PowerShell — 20 novembre 2026

Le premier kit interrompait la construction lors du test `python -c` car Windows PowerShell 5.1 supprimait les guillemets internes de `predict("Produit conforme")`. Le test import a été remplacé par `print(callable(predict))`, sans guillemets internes ; la prédiction réelle est déjà testée juste avant via `sentiment.cmd --json`.

Si le premier kit a déjà préparé `installateur/build/app`, vous pouvez **conserver ce dossier** et compiler directement le fichier `.iss` avec Inno Setup après vérification du test corrigé. Le correctif ne demande pas de retélécharger les dépendances.
