"""Régression du guide V1.1 sans serveur ni installation distante."""

from sentiment_app import cli, predict


def test_import_public_et_compatibilite_ancien_kit():
    assert callable(predict)
    assert callable(predict.chemin_modele)


def test_option_json_au_debut_ou_a_la_fin(monkeypatch):
    valeurs = []
    monkeypatch.setattr(cli, "_direct", lambda texte, en_json: valeurs.append((texte, en_json)) or 0)
    assert cli.main(["--json", "un avis"]) == 0
    assert cli.main(["un avis", "--json"]) == 0
    assert valeurs == [(["un avis"], True), (["un avis"], True)]


def test_absence_texte_affiche_aide(capsys):
    assert cli.main([]) == 0
    assert "usage:" in capsys.readouterr().out.lower()


def test_texte_blanc_refuse_sans_trace(capsys):
    assert cli.main([" "]) == 2
    erreur = capsys.readouterr().err
    assert "erreur : texte vide" in erreur.lower()
    assert "Traceback" not in erreur

def test_ancien_import_predict_reste_un_module():
    """Le shim src/predict.py doit référencer le module, pas la fonction publique."""
    from importlib import import_module
    from types import ModuleType

    from sentiment_app.predict import charger_modele

    ancien = import_module("predict")
    assert isinstance(ancien, ModuleType)
    assert ancien.charger_modele is charger_modele
