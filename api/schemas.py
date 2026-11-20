"""Contrats Pydantic, compatibles avec les routes historiques et /v1."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator

Label = Literal["POSITIVE", "NEGATIVE", "INDETERMINE"]


class PredictRequest(BaseModel):
    text: str = Field(
        ..., min_length=1, max_length=2000, description="Texte à classifier",
        examples=["Livraison rapide, produit conforme, très satisfait"],
    )

    @field_validator("text")
    @classmethod
    def valider_texte(cls, valeur: str) -> str:
        if not valeur.strip():
            raise ValueError("texte vide une fois les blancs retirés")
        return valeur


class PredictResponse(BaseModel):
    label: Label = Field(..., description="POSITIVE, NEGATIVE ou INDETERMINE")
    score: float = Field(..., ge=0, le=1)
    text: str = Field(..., description="Aperçu du texte (100 caractères)")


class HealthResponse(BaseModel):
    status: str
    model: str


class ErrorResponse(BaseModel):
    detail: str


class ChampInvalide(BaseModel):
    champ: str
    message: str


class DetailErreur(BaseModel):
    code: str
    message: str
    champs: list[ChampInvalide] = Field(default_factory=list)


class ErreurV1(BaseModel):
    erreur: DetailErreur
