"""API FastAPI : routes historiques conservées, routes /v1 sécurisées."""

import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from api.model import load_model
from api.schemas import HealthResponse, PredictRequest, PredictResponse
from api.securite import charger_cles
from api.v1 import router as router_v1

load_dotenv()  # variables du terminal prioritaires ; fichier .env ignoré par Git
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("sentiment_api")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Démarrage de l'API...")
    nb_cles = len(charger_cles())  # échoue immédiatement si API_KEYS est mal formé
    if nb_cles == 0:
        logger.warning("Aucune clé API_KEYS : les routes /v1 protégées répondront 401")
    app.state.classifier = load_model()
    logger.info("Modèle chargé : %s ; %d clé(s)", app.state.classifier.model_name, nb_cles)
    yield
    logger.info("Arrêt de l'API")


app = FastAPI(
    title="Sentiment Analysis API",
    description="Classification d'avis : API versionnée /v1 avec clé X-API-Key",
    version="1.2.0",
    lifespan=lifespan,
)

origines = os.environ.get(
    "CORS_ORIGINS", "http://localhost:5500,http://127.0.0.1:5500,http://localhost:8501"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in origines.split(",") if x.strip()],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-API-Key"],
)

CODES = {
    400: "REQUETE_INVALIDE",
    401: "NON_AUTHENTIFIE",
    403: "ACCES_REFUSE",
    404: "INTROUVABLE",
    405: "METHODE_NON_AUTORISEE",
    422: "ENTREE_INVALIDE",
    500: "ERREUR_INTERNE",
    503: "MODELE_INDISPONIBLE",
}


def _erreur_v1(statut: int, message: str, champs: list[dict[str, str]] | None = None,
               en_tetes: dict[str, str] | None = None) -> JSONResponse:
    corps = {"erreur": {"code": CODES.get(statut, f"HTTP_{statut}"),
                       "message": message, "champs": champs or []}}
    return JSONResponse(corps, status_code=statut, headers=en_tetes)


@app.exception_handler(StarletteHTTPException)
async def erreur_http(request: Request, exc: StarletteHTTPException) -> Response:
    if request.url.path.startswith("/v1"):
        return _erreur_v1(exc.status_code, str(exc.detail), en_tetes=getattr(exc, "headers", None))
    return await http_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def erreur_validation(request: Request, exc: RequestValidationError) -> Response:
    if request.url.path.startswith("/v1"):
        champs = [{"champ": ".".join(str(x) for x in e["loc"]), "message": e["msg"]}
                  for e in exc.errors()]
        return _erreur_v1(422, "Entrée refusée par le contrat de l'API", champs)
    return await request_validation_exception_handler(request, exc)


app.include_router(router_v1)


def _classifier():
    clf = getattr(app.state, "classifier", None)
    if clf is None:
        raise HTTPException(503, "Modèle non chargé")
    return clf


@app.get("/", summary="Accueil")
async def root():
    return {"message": "Sentiment Analysis API", "docs": "/docs", "health": "/health"}


@app.get("/health", response_model=HealthResponse, summary="Santé historique", deprecated=True)
async def health_check():
    return {"status": "OK", "model": _classifier().model_name}


@app.post("/predict", response_model=PredictResponse, summary="Route historique",
          deprecated=True)
async def predict(request: PredictRequest, response: Response):
    response.headers["deprecation"] = "true"
    response.headers["link"] = '</v1/predict>; rel="successor-version"'
    clf = _classifier()
    try:
        resultat = clf.predict(request.text)
    except Exception:
        logger.exception("Erreur lors de la prédiction")
        raise HTTPException(500, "Erreur interne du serveur") from None
    logger.info("predict -> %s (%.2f)", resultat["label"], resultat["score"])
    return resultat


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000)
