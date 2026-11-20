#!/usr/bin/env python
"""Prédiction unitaire : modèle externe ou modèle embarqué dans la roue (TP4 du manuel)."""

import os
import sys
from functools import lru_cache
from importlib.resources import files
from pathlib import Path
from typing import Any, Literal, TypedDict, cast

import joblib

RACINE = Path(__file__).resolve().parents[1]


def chemin_modele() -> Path:
    """Chemin extérieur configurable ; conserve la compatibilité avec le kit TP6."""
    return Path(os.environ.get("SENTIMENT_MODELE") or RACINE / "models" / "sentiment.joblib")


MODELE = chemin_modele()
EtiquetteTP2 = Literal["positive", "negative"]


class PredictionTP2(TypedDict):
    label: EtiquetteTP2
    score: float


@lru_cache(maxsize=1)
def charger_modele() -> Any:
    """Préfère SENTIMENT_MODELE, puis le modèle local, puis le modèle inclus dans la roue."""
    if MODELE.is_file():
        return joblib.load(MODELE)
    if os.environ.get("SENTIMENT_MODELE") or MODELE != chemin_modele():
        raise FileNotFoundError(f"modèle introuvable : {MODELE}")
    ressource = files("sentiment_app").joinpath("modele/sentiment.joblib")
    if ressource.is_file():
        with ressource.open("rb") as fichier:
            return joblib.load(fichier)
    raise FileNotFoundError(
        "Aucun modèle trouvé : lancez python src/train.py ou indiquez SENTIMENT_MODELE. "
        "Pour construire la roue complète, copiez models/sentiment.joblib dans "
        "sentiment_app/modele/ avant python -m build."
    )


def predict(texte: str) -> PredictionTP2:
    if not isinstance(texte, str) or not texte.strip():
        raise ValueError("texte vide")
    pipeline = charger_modele()
    etiquette_brute = str(pipeline.predict([texte])[0])
    if etiquette_brute not in ("positive", "negative"):
        raise ValueError(f"Étiquette inconnue : {etiquette_brute}")
    etiquette = cast(EtiquetteTP2, etiquette_brute)
    score = float(pipeline.predict_proba([texte]).max())
    return {"label": etiquette, "score": round(score, 4)}


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    resultat = predict(" ".join(sys.argv[1:]))
    print(f"{resultat['label']} (confiance {resultat['score']:.0%})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
