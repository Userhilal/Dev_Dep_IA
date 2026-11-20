# sentiment-app : dépôt du binôme

## Installer le paquet distribué (v1.0.1)

Python 3.11 minimum. Pour un nouvel utilisateur, créer un environnement virtuel
puis installer **la roue GitHub Release** ; le modèle est déjà inclus.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install https://github.com/Userhilal/Dev_Dep_IA/releases/download/v1.0.1/sentiment_app-1.0.1-py3-none-any.whl
sentiment --version
sentiment "Livraison rapide, très satisfait"
sentiment --json "Produit cassé, à fuir"
python -c "from sentiment_app import predict; print(predict('Produit conforme'))"
python -m pip check
```

Pour les erreurs : `sentiment " "` (code 2), `sentiment` (aide).
Anciennes commandes conservées : `sentiment predict`, `sentiment serve`,
`sentiment ui`. Consulter [README-PAQUET.md](README-PAQUET.md) pour le détail.


Application fil rouge du cours *Développement et déploiement d'applications intelligentes*.
Ce dépôt grandit chaque semaine ; la semaine 1 met en place le cadrage et l'environnement.

## Installation (3 commandes)

```bash
python -m venv .venv
source .venv/bin/activate        # Windows PowerShell : .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Vérifier son installation

```bash
python scripts/check_setup.py    # diagnostic lisible : versions, dossiers, Git
pytest -q                        # mêmes vérifications sous forme de tests
```

La démarche complète de test, étape par étape, est dans `TESTS.md`.

## Structure

```text
sentiment-app/
├── README.md
├── TP1-ENONCE.md    # énoncé du TP de la semaine 1
├── TESTS.md         # démarche à suivre pour le test
├── requirements.txt
├── .gitignore
├── data/            # jeux de données (versionnés par DVC à partir de la semaine 7)
├── models/          # modèles entraînés (jamais dans Git)
├── app/             # API FastAPI (semaine 3)
├── ui/              # Streamlit (semaine 5)
├── tests/           # pytest (semaine 1 : tests d'environnement)
├── scripts/         # utilitaires (check_setup, nouveau cas de cadrage)
└── docs/cadrage/    # fiches de cadrage du TP1
```

## Membres du binôme

| Rôle | Nom | Identifiant GitHub | Travail de la semaine 1 |
| --- | --- | --- | --- |
| Membre A | HILAL HIND| [@userhilal] | |
| Membre B | [Nom 2] | [@login] | |
