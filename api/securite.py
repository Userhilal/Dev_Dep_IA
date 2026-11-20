"""Authentification et autorisation des routes /v1 (manuel, TP2)."""

import os
import secrets
from typing import Annotated, Callable, Literal, cast

from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader

Role = Literal["client", "admin"]
ROLES = {"client", "admin"}
LONGUEUR_MIN = 16
EN_TETE = APIKeyHeader(name="X-API-Key", auto_error=False)
NON_AUTHENTIFIE = {"WWW-Authenticate": "APIKey"}


def charger_cles(brut: str | None = None) -> dict[str, Role]:
    """Charge API_KEYS ; une configuration incorrecte interdit le démarrage."""
    brut = os.environ.get("API_KEYS", "") if brut is None else brut
    cles: dict[str, Role] = {}
    for entree in filter(None, (morceau.strip() for morceau in brut.split(","))):
        cle, separateur, role = entree.rpartition(":")
        if not separateur or role not in ROLES:
            raise ValueError(f"rôle inconnu dans API_KEYS : {role!r} (client ou admin attendu)")
        if len(cle) < LONGUEUR_MIN:
            raise ValueError(f"clé trop courte dans API_KEYS ({len(cle)} caractères, minimum 16)")
        cles[cle] = cast(Role, role)
    return cles


def identifier(cle: Annotated[str | None, Security(EN_TETE)]) -> Role:
    """401 en cas de clé absente/inconnue, même sans configuration de clés."""
    if not cle:
        raise HTTPException(401, "Clé d'API manquante : en-tête X-API-Key", headers=NON_AUTHENTIFIE)
    for connue, role in charger_cles().items():
        if secrets.compare_digest(cle.encode(), connue.encode()):
            return role
    raise HTTPException(401, "Clé d'API invalide", headers=NON_AUTHENTIFIE)


def exiger(*autorises: Role) -> Callable[..., Role]:
    """Fabrique la dépendance d'autorisation (403 si rôle insuffisant)."""

    def verifier(role: Annotated[Role, Depends(identifier)]) -> Role:
        if role not in autorises:
            raise HTTPException(403, f"Accès refusé au rôle « {role} »")
        return role

    return verifier
