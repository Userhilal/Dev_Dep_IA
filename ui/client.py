"""Client HTTP Streamlit : /v1 avec clé ; ancien contrat conservé sans clé.

Renseigner API_KEYS et API_KEY dans .env pour utiliser réellement la version sécurisée.
"""

import os
from collections import Counter
from dataclasses import dataclass

import httpx
from dotenv import load_dotenv

load_dotenv()
API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")
API_KEY = os.environ.get("API_KEY", "")
VERDICTS = {
    "POSITIVE": "Avis positif",
    "NEGATIVE": "Avis négatif",
    "INDETERMINE": "Je ne sais pas : à faire vérifier par un humain",
}
INJOIGNABLE = "API injoignable : lancez d'abord uvicorn api.main:app"
REFUS = "Texte refusé : vide, fait d'espaces, ou de plus de 2000 caractères."
SANS_MODELE = "Modèle non chargé : python src/train.py, puis relancer l'API."
CLE = "Clé d'API absente, invalide ou rôle insuffisant. Vérifiez API_KEY dans .env."


@dataclass
class Reponse:
    ok: bool
    label: str | None = None
    score: float | None = None
    message: str = ""


def creer_session() -> httpx.Client:
    headers = {"X-API-Key": API_KEY} if API_KEY else {}
    return httpx.Client(base_url=API_URL, timeout=10, headers=headers)


def _code(r: httpx.Response) -> str:
    try:
        code = r.json()["erreur"]["code"]
        return str(code)
    except (ValueError, KeyError, TypeError):
        return ""


def sante(session: httpx.Client) -> Reponse:
    try:
        r = session.get("/v1/health" if API_KEY else "/health",
                        headers={"X-API-Key": API_KEY} if API_KEY else {})
    except httpx.TransportError:
        return Reponse(False, message=INJOIGNABLE)
    if r.status_code == 200:
        return Reponse(True, message=r.json()["model"])
    return Reponse(False, message=SANS_MODELE if r.status_code == 503
                   else f"Erreur de l'API ({r.status_code}).")


def predire(session: httpx.Client, texte: str) -> Reponse:
    try:
        r = session.post("/v1/predict" if API_KEY else "/predict", json={"text": texte},
                         headers={"X-API-Key": API_KEY} if API_KEY else {})
    except httpx.TransportError:
        return Reponse(False, message=INJOIGNABLE)
    if r.status_code == 200:
        corps = r.json()
        return Reponse(True, label=corps["label"], score=corps["score"])
    code = _code(r)
    if code == "ENTREE_INVALIDE" or r.status_code == 422:
        return Reponse(False, message=REFUS)
    if code in ("NON_AUTHENTIFIE", "ACCES_REFUSE") or r.status_code in (401, 403):
        return Reponse(False, message=CLE)
    if code == "MODELE_INDISPONIBLE" or r.status_code == 503:
        return Reponse(False, message=SANS_MODELE)
    return Reponse(False, message=f"Erreur interne de l'API ({r.status_code}).")


def predire_lot(session: httpx.Client, textes: list[str]) -> list[Reponse]:
    return [predire(session, texte) for texte in textes]


def resumer(reponses: list[Reponse]) -> dict[str, int]:
    compte = Counter(r.label if r.ok else "REFUS OU ERREUR" for r in reponses)
    return dict(sorted(compte.items()))
