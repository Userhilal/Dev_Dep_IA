"""Commande `sentiment` : API/Streamlit (kit TP6) et usage direct (manuel TP4).

- sentiment --version
- sentiment predict "Livraison rapide"      (résultat API JSON)
- sentiment "Livraison rapide" --json        (résultat brut du modèle, manuel)
- sentiment serve
- sentiment ui
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

from sentiment_app import __version__


def _predire(args: argparse.Namespace) -> int:
    """Ancienne commande du kit TP6 : applique le seuil d'abstention de l'API."""
    from api.model import load_model

    try:
        classifieur = load_model()
    except FileNotFoundError as erreur:
        print(erreur, file=sys.stderr)
        return 1
    print(json.dumps(classifieur.predict(" ".join(args.texte)), ensure_ascii=False))
    return 0


def _direct(texte: list[str], en_json: bool) -> int:
    """Commande TP4 du manuel : sentiment TEXTE [--json]."""
    from sentiment_app.predict import predict

    try:
        resultat = predict(" ".join(texte))
    except (ValueError, FileNotFoundError) as erreur:
        print(f"erreur : {erreur}", file=sys.stderr)
        return 2
    if en_json:
        print(json.dumps(resultat, ensure_ascii=False))
    else:
        print(f"{resultat['label']} (confiance {resultat['score']:.0%})")
    return 0


def _servir(args: argparse.Namespace) -> int:
    import uvicorn

    uvicorn.run("api.main:app", host=args.host, port=args.port)
    return 0


def _interface(args: argparse.Namespace) -> int:
    try:
        import streamlit  # noqa: F401
    except ImportError:
        print('Streamlit absent : pip install "sentiment-app[ui]"', file=sys.stderr)
        return 1
    page = Path(__file__).resolve().parents[1] / "ui" / "app.py"
    return subprocess.call([sys.executable, "-m", "streamlit", "run", str(page)])


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] not in ("predict", "serve", "ui") and (
        argv[0] == "--json" or not argv[0].startswith("-")
    ):
        en_json = "--json" in argv
        texte = [mot for mot in argv if mot != "--json"]
        return _direct(texte, en_json)

    parser = argparse.ArgumentParser(prog="sentiment", description="Analyse de sentiment d'avis clients.")
    parser.add_argument("--version", action="version", version=f"sentiment-app {__version__}")
    commandes = parser.add_subparsers(dest="commande", required=True)

    predire = commandes.add_parser("predict", help="classe un avis avec le seuil (JSON)")
    predire.add_argument("texte", nargs="+", help="l'avis à analyser")
    predire.set_defaults(fonction=_predire)

    servir = commandes.add_parser("serve", help="lance l'API")
    servir.add_argument("--host", default="127.0.0.1")
    servir.add_argument("--port", type=int, default=8000)
    servir.set_defaults(fonction=_servir)

    interface = commandes.add_parser("ui", help="lance Streamlit (l'API doit tourner)")
    interface.set_defaults(fonction=_interface)

    if not argv:
        parser.print_help()
        return 0

    args = parser.parse_args(argv)
    return int(args.fonction(args))
