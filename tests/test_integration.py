
"""Tests d'intégration de l'API — TP4, T26."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import app

MODELE = (
    Path(__file__).resolve().parents[1]
    / "models"
    / "sentiment.joblib"
)

pytestmark = pytest.mark.skipif(
    not MODELE.exists(),
    reason="Modèle absent : python src/train.py",
)


def test_demarrage_reel_charge_le_modele():
    """L'API charge le modèle au démarrage."""
    with TestClient(app) as client:
        reponse = client.get("/health")

    assert reponse.status_code == 200
    assert "TP2" in reponse.json()["model"]


def test_demarrage_sans_modele(monkeypatch, tmp_path):
    """L'API refuse de démarrer si le modèle est absent."""
    import predict as module_predict
    from predict import charger_modele

    charger_modele.cache_clear()

    try:
        with monkeypatch.context() as patch:
            patch.setattr(
                module_predict,
                "MODELE",
                tmp_path / "modele-absent.joblib",
            )

            with pytest.raises(FileNotFoundError):
                with TestClient(app):
                    pass
    finally:
        charger_modele.cache_clear()


def test_modele_non_charge_503(monkeypatch):
    """Les routes refusent les demandes sans modèle chargé."""
    with TestClient(app) as client:
        monkeypatch.setattr(
            app.state,
            "classifier",
            None,
        )

        health = client.get("/health")
        prediction = client.post(
            "/predict",
            json={"text": "Très bon produit"},
        )

        assert health.status_code == 503
        assert prediction.status_code == 503


@pytest.mark.parametrize(
    "type_erreur",
    [RuntimeError, ValueError],
    ids=["runtime-error", "value-error"],
)
def test_panne_interne_500(monkeypatch, type_erreur):
    """Une panne du modèle répond 500 sans exposer ses détails."""
    with TestClient(app) as client:

        def prediction_en_panne(_texte):
            raise type_erreur("bug interne")

        monkeypatch.setattr(
            app.state.classifier,
            "predict",
            prediction_en_panne,
        )

        reponse = client.post(
            "/predict",
            json={"text": "Très bon produit"},
        )

        assert reponse.status_code == 500
        assert reponse.json()["detail"] == (
            "Erreur interne du serveur"
        )
        assert "bug interne" not in reponse.text
