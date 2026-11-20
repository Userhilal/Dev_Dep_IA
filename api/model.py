
"""Raccord entre l'API FastAPI et le modèle TP2.

Le modèle est chargé une seule fois.
Un seuil d'abstention évite les prédictions trop incertaines.
"""

from typing import Literal, TypedDict

from sentiment_app.predict import charger_modele
from sentiment_app.predict import predict as _predict

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
    """Adaptateur du modèle sentiment_app pour FastAPI."""

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
