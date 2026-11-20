"""Contrôles reconstitués À PARTIR DU MANUEL TP2 ; ce n'est PAS le kit officiel absent."""

import pytest
from fastapi.testclient import TestClient

from api import main
from api.securite import charger_cles

CLIENT_KEY = "client-secret-ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ADMIN_KEY = "admin-secret-ABCDEFGHIJKLMNOPQRSTUVWXYZ"


class FauxModele:
    model_name = "tfidf-logreg (TP2, modèles de démonstration)"

    def predict(self, texte):
        if texte == "ERREUR_INTERNE":
            raise RuntimeError("secret interne non publiable")
        if texte == "incertain":
            return {"label": "INDETERMINE", "score": 0.5162, "text": texte}
        return {"label": "POSITIVE", "score": 0.777, "text": texte[:100]}


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("API_KEYS", f"{CLIENT_KEY}:client,{ADMIN_KEY}:admin")
    monkeypatch.setattr(main, "load_model", FauxModele)
    with TestClient(main.app) as c:
        yield c


def avec_cle(cle=CLIENT_KEY):
    return {"X-API-Key": cle}


def test_api_v1_sante_publique(client):
    r = client.get("/v1/health")
    assert r.status_code == 200 and r.json()["status"] == "OK"


def test_api_v1_predictions(client):
    r = client.post("/v1/predict", headers=avec_cle(), json={"text": "Très bien"})
    assert r.status_code == 200 and r.json()["label"] == "POSITIVE"


def test_api_v1_indetermine(client):
    r = client.post("/v1/predict", headers=avec_cle(), json={"text": "incertain"})
    assert r.status_code == 200 and r.json()["label"] == "INDETERMINE"


def test_api_v1_cle_absente_401(client):
    r = client.post("/v1/predict", json={"text": "Bonjour"})
    assert r.status_code == 401 and r.json()["erreur"]["code"] == "NON_AUTHENTIFIE"
    assert "WWW-Authenticate" in r.headers


def test_api_v1_cle_invalide_401(client):
    r = client.post("/v1/predict", headers=avec_cle("mauvaise-cle"), json={"text": "Bonjour"})
    assert r.status_code == 401 and r.json()["erreur"]["code"] == "NON_AUTHENTIFIE"


def test_api_v1_role_client_refuse_admin(client):
    r = client.get("/v1/modele", headers=avec_cle())
    assert r.status_code == 403 and r.json()["erreur"]["code"] == "ACCES_REFUSE"


def test_api_v1_role_admin_autorise(client):
    r = client.get("/v1/modele", headers=avec_cle(ADMIN_KEY))
    assert r.status_code == 200 and r.json()["seuil_abstention"] == 0.60


def test_api_v1_role_admin_predict(client):
    r = client.post("/v1/predict", headers=avec_cle(ADMIN_KEY), json={"text": "Bonjour"})
    assert r.status_code == 200


@pytest.mark.parametrize("corps", [{"text": ""}, {"text": "  "}, {"text": "a" * 2001}, {}, {"text": 42}])
def test_api_v1_422_corps(client, corps):
    r = client.post("/v1/predict", headers=avec_cle(), json=corps)
    assert r.status_code == 422
    assert r.json()["erreur"]["code"] == "ENTREE_INVALIDE"
    assert r.json()["erreur"]["champs"]


def test_api_v1_422_json_invalide(client):
    r = client.post(
        "/v1/predict", headers={**avec_cle(), "Content-Type": "application/json"},
        content=b"pas du json"
    )
    assert r.status_code == 422 and r.json()["erreur"]["code"] == "ENTREE_INVALIDE"


def test_api_v1_erreur_interne_500(client):
    r = client.post("/v1/predict", headers=avec_cle(), json={"text": "ERREUR_INTERNE"})
    assert r.status_code == 500 and r.json()["erreur"]["code"] == "ERREUR_INTERNE"
    assert "secret interne" not in r.text


def test_api_v1_modele_absent_503(client, monkeypatch):
    monkeypatch.setattr(main.app.state, "classifier", None)
    r = client.get("/v1/health")
    assert r.status_code == 503 and r.json()["erreur"]["code"] == "MODELE_INDISPONIBLE"


def test_api_v1_route_inconnue(client):
    r = client.get("/v1/inconnu")
    assert r.status_code == 404 and r.json()["erreur"]["code"] == "INTROUVABLE"


def test_api_v1_methode_invalide(client):
    r = client.get("/v1/predict")
    assert r.status_code == 405 and r.json()["erreur"]["code"] == "METHODE_NON_AUTORISEE"


def test_api_historique_conserve(client):
    r = client.post("/predict", json={"text": "Bonjour"})
    assert r.status_code == 200 and r.headers["deprecation"] == "true"


def test_api_historique_erreur_conserve(client):
    r = client.post("/predict", json={"text": ""})
    assert r.status_code == 422 and isinstance(r.json()["detail"], list)


def test_api_v1_cors_autorise_5500(client):
    r = client.options("/v1/predict", headers={
        "Origin": "http://localhost:5500", "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "x-api-key,content-type",
    })
    assert r.status_code == 200
    assert r.headers["access-control-allow-origin"] == "http://localhost:5500"


def test_api_v1_cors_rejette_autre_port(client):
    r = client.options("/v1/predict", headers={
        "Origin": "http://localhost:5600", "Access-Control-Request-Method": "POST",
    })
    assert r.status_code == 400


@pytest.mark.parametrize("brut", ["abc:client", "abcdef1234567890:autre", "abcdef1234567890", ":admin"])
def test_api_cles_configuration_refusee(brut):
    with pytest.raises(ValueError):
        charger_cles(brut)


def test_api_cles_configuration_vide():
    assert charger_cles("") == {}


def test_api_cles_configuration_ok():
    assert charger_cles(f"{CLIENT_KEY}:client,{ADMIN_KEY}:admin,") == {
        CLIENT_KEY: "client", ADMIN_KEY: "admin"
    }


def test_api_v1_metriques_reelles(client):
    r = client.get("/v1/modele", headers=avec_cle(ADMIN_KEY))
    assert isinstance(r.json()["metriques"], dict)


def test_api_v1_metriques_presentes(client, monkeypatch, tmp_path):
    from api import v1

    donnees = tmp_path / "models" / "metrics.json"
    donnees.parent.mkdir()
    donnees.write_text('{"f1_macro":0.879}', encoding="utf-8")
    monkeypatch.setattr(v1, "__file__", str(tmp_path / "api" / "v1.py"))
    r = client.get("/v1/modele", headers=avec_cle(ADMIN_KEY))
    assert r.json()["metriques"]["f1_macro"] == 0.879


def test_api_v1_metriques_illisibles(client, monkeypatch, tmp_path):
    from api import v1

    donnees = tmp_path / "models" / "metrics.json"
    donnees.parent.mkdir()
    donnees.write_text("pas du json", encoding="utf-8")
    monkeypatch.setattr(v1, "__file__", str(tmp_path / "api" / "v1.py"))
    r = client.get("/v1/modele", headers=avec_cle(ADMIN_KEY))
    assert r.status_code == 200 and r.json()["metriques"] == {}


def test_api_historique_route_inconnue(client):
    r = client.get("/route-inconnue")
    assert r.status_code == 404 and r.json()["detail"] == "Not Found"


def test_api_v1_sans_cles_configurees(monkeypatch):
    monkeypatch.setenv("API_KEYS", "")
    monkeypatch.setattr(main, "load_model", FauxModele)
    with TestClient(main.app) as client:
        r = client.post("/v1/predict", json={"text": "Bonjour"}, headers=avec_cle())
        assert r.status_code == 401
        assert client.get("/v1/health").status_code == 200
