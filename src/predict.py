
#!/usr/bin/env python
"""Prédiction unitaire du modèle de sentiment (TP2)."""

import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal, TypedDict, cast

import joblib

MODELE = Path(__file__).resolve().parents[1] / "models" / "sentiment.joblib"

EtiquetteTP2 = Literal["positive", "negative"]


class PredictionTP2(TypedDict):
    """Structure de la prédiction retournée par le modèle TP2."""

    label: EtiquetteTP2
    score: float


@lru_cache(maxsize=1)
def charger_modele() -> Any:
    """Charge le modèle une seule fois par processus."""
    if not MODELE.exists():
        raise FileNotFoundError(
            "models/sentiment.joblib absent : "
            "lancez python src/train.py"
        )

    return joblib.load(MODELE)


def predict(texte: str) -> PredictionTP2:
    """Prédit un sentiment positif ou négatif."""

    if not isinstance(texte, str) or not texte.strip():
        raise ValueError("texte vide")

    pipeline = charger_modele()

    etiquette_brute = str(pipeline.predict([texte])[0])

    if etiquette_brute not in ("positive", "negative"):
        raise ValueError(
            f"Étiquette inconnue : {etiquette_brute}"
        )

    etiquette = cast(EtiquetteTP2, etiquette_brute)

    score = float(pipeline.predict_proba([texte]).max())

    return {
        "label": etiquette,
        "score": round(score, 4),
    }


def main() -> int:
    """Permet une prédiction depuis le terminal."""

    if len(sys.argv) < 2:
        print(__doc__)
        return 2

    texte = " ".join(sys.argv[1:])
    resultat = predict(texte)

    print(
        f"{resultat['label']} "
        f"(confiance {resultat['score']:.0%})"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
