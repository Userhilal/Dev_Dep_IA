"""Six contrôles RECONSTITUÉS d'après pages 52-54 du manuel, PAS ceux du kit absent.

Ils doivent tourner dans un environnement neuf où la roue a été installée.
"""

import importlib.metadata
import importlib.resources
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

spec = importlib.util.find_spec("sentiment_app")
if not os.environ.get("VERIFICATION_LIVRABLE") and (
    spec is None or "site-packages" not in str(spec.origin)
):
    pytest.skip("paquet non installé : lancer scripts/verifier_livrable.py",
                allow_module_level=True)

import sentiment_app  # noqa: E402
from sentiment_app.predict import predict  # noqa: E402

# Utilise le chemin absolu pour vérifier la commande installée hors du dépôt.
COMMANDE = Path(sys.executable).parent / ("sentiment.exe" if sys.platform == "win32" else "sentiment")


def test_importe_depuis_le_paquet_installe():
    assert "site-packages" in str(Path(sentiment_app.__file__).resolve())


def test_version_1_0_0():
    assert sentiment_app.__version__ == "1.0.0"
    assert importlib.metadata.version("sentiment-app") == "1.0.0"


def test_modele_est_dans_la_roue():
    fichier = importlib.resources.files("sentiment_app").joinpath("modele/sentiment.joblib")
    assert fichier.is_file()


def test_import_predict_fonctionne_hors_du_depot():
    assert predict("Livraison rapide, produit conforme, très satisfait")["label"] == "positive"


def test_commande_installee():
    assert COMMANDE.is_file()
    r = subprocess.run([str(COMMANDE), "--version"], capture_output=True, text=True, check=False)
    assert r.returncode == 0 and "1.0.0" in r.stdout


def test_commande_predict_installee():
    r = subprocess.run([str(COMMANDE), "predict", "Livraison rapide, produit conforme, très satisfait"],
                       capture_output=True, text=True, check=False)
    assert r.returncode == 0
    assert json.loads(r.stdout)["label"] == "POSITIVE"
