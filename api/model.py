
"""Raccord entre l'API FastAPI et le modèle TP2.

Le modèle est chargé une seule fois.
Un seuil d'abstention évite les prédictions trop incertaines.
"""

import sys
from pathlib import Path
from typing import Literal, TypedDict

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))

from predict import charger_modele  # noqa: E402
from predict import predict as _predict  # noqa: E402

SEUIL_ABSTENTION = 0.60

EtiquetteAPI = Literal[
    "POSITIVE",
    "NEGATIVE",
    "INDETERMINE",
]

ETIQUETTES: dict[str, Literal["POSITIVE", "NEGATIVE"]] = {
    "positive": "POSITIVE",
    "negative": "NEGATIVE",
}


class PredictionAPI(TypedDict):
    """Structure de sortie du classifieur API."""

    label: EtiquetteAPI
    score: float
    text: str


class SentimentClassifier:
    """Adaptateur du modèle TP2 pour FastAPI."""

    model_name = "tfidf-logreg (TP2, models/sentiment.joblib)"

    def __init__(self) -> None:
        """Charge et vérifie les étiquettes du modèle."""

        pipeline = charger_modele()

        etiquettes_modele = {
            str(etiquette)
            for etiquette in pipeline.classes_
        }

        if etiquettes_modele != set(ETIQUETTES):
            raise ValueError(
                "Étiquettes inconnues dans le modèle : "
                f"{sorted(etiquettes_modele)}"
            )

    def predict(self, text: str) -> PredictionAPI:
        """Prédit le sentiment ou retourne INDETERMINE."""

        resultat = _predict(text)
        score = resultat["score"]

        if score < SEUIL_ABSTENTION:
            label: EtiquetteAPI = "INDETERMINE"
        else:
            label = ETIQUETTES[resultat["label"]]

        return {
            "label": label,
            "score": score,
            "text": text[:100],
        }


def load_model() -> SentimentClassifier:
    """Retourne un classifieur prêt à servir les prédictions."""

    return SentimentClassifier()
