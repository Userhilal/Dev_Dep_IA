
"""Tests aux limites du contrat d'entrée — TP4."""

import json
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

MODELE = Path(__file__).resolve().parents[1] / "models" / "sentiment.joblib"

pytestmark = pytest.mark.skipif(
    not MODELE.exists(),
    reason="Modèle absent : python src/train.py",
)


@pytest.fixture(scope="module")
def client():
    from fastapi.testclient import TestClient

    from api.main import app

    with TestClient(app) as c:
        yield c


def en_json(valeur: object) -> bytes:
    return json.dumps(valeur).encode("utf-8")


# Huit cas aux frontières du contrat
CAS = [
    pytest.param(en_json({"text": ""}), 422, id="texte-vide"),
    pytest.param(en_json({"text": "   "}), 422, id="espaces"),
    pytest.param(en_json({"text": "a"}), 200, id="un-caractere"),
    pytest.param(en_json({"text": "a" * 2000}), 200, id="2000-caracteres"),
    pytest.param(en_json({"text": "a" * 2001}), 422, id="2001-caracteres"),
    pytest.param(en_json({}), 422, id="champ-absent"),
    pytest.param(en_json({"text": 42}), 422, id="type-invalide"),
    pytest.param(b"pas du json", 422, id="json-invalide"),
]


@pytest.mark.parametrize("corps, code_attendu", CAS)
def test_frontieres_du_contrat(client, corps, code_attendu):
    reponse = client.post(
        "/predict",
        content=corps,
        headers={"Content-Type": "application/json"},
    )

    assert reponse.status_code == code_attendu

    if code_attendu == 422:
        detail = reponse.json()["detail"]
        assert isinstance(detail, list)

        for erreur in detail:
            assert {"loc", "msg", "type"} <= erreur.keys()


# Propriété 1 : textes valides
@given(
    st.text(
        alphabet=st.characters(blacklist_categories=("Cs",)),
        min_size=1,
        max_size=2000,
    ).filter(lambda texte: bool(texte.strip()))
)
@settings(max_examples=30, deadline=None)
def test_propriete_texte_valide(client, texte):
    reponse = client.post("/predict", json={"text": texte})

    assert reponse.status_code == 200

    resultat = reponse.json()
    assert resultat["label"] in {"POSITIVE", "NEGATIVE", "INDETERMINE"}
    assert 0 <= resultat["score"] <= 1


# Propriété 2 : textes constitués uniquement de blancs
@given(
    st.text(
        alphabet=st.sampled_from(
            [" ", "\t", "\n", "\r", "\v", "\f", "\u0085", "\u00a0"]
        ),
        min_size=1,
        max_size=2000,
    )
)
@settings(max_examples=30, deadline=None)
def test_propriete_texte_blanc(client, texte):
    reponse = client.post("/predict", json={"text": texte})

    assert reponse.status_code == 422
    assert isinstance(reponse.json()["detail"], list)
