# Fiche de recette du paquet — guide V1.1, version 1.0.1

À renseigner avec les **résultats réellement obtenus** par la personne qui joue
le client, depuis un dossier vide hors du dépôt Git. Ne pas remplir à l'avance.

| Contrôle | Vérification | Commande / preuve | Obtenu | Conforme ? |
| --- | --- | --- | --- | --- |
| C1 | Python >= 3.11 | `python --version` | À renseigner | À renseigner |
| C2 | Installer la roue depuis la Release | `pip install URL-roue-v1.0.1` | À renseigner | À renseigner |
| C3 | Dépendances | `pip check` | À renseigner | À renseigner |
| C4 | Version | `sentiment --version` | À renseigner | À renseigner |
| C5 | Avis positif | `sentiment "Livraison rapide, très satisfait"` | À renseigner | À renseigner |
| C6 | JSON négatif | `sentiment --json "Produit cassé, à fuir"` | À renseigner | À renseigner |
| C7 | Import Python | `from sentiment_app import predict; predict("Produit conforme")` | À renseigner | À renseigner |
| C8 | Texte blanc | `sentiment " "` et `$LASTEXITCODE` | À renseigner | À renseigner |
| C9 | README suffisant | Note des questions posées par le client, s'il y en a | À renseigner | À renseigner |
| C10 | Désinstallation | `pip uninstall -y sentiment-app`, `sentiment` introuvable | À renseigner | À renseigner |

Méthode Git depuis un tag : non validée sans artefact de modèle lors de la
construction. Le manuel demande de ne **pas** versionner le `.joblib` dans Git.
Ce contrôle doit être traité séparément et ne doit pas être marqué « conforme »
sans essai réel.
