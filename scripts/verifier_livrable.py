#!/usr/bin/env python
"""Vérificateur RECONSTITUÉ d'après pages 51-54 du manuel.

Attention : ce fichier N'EST PAS le vérificateur officiel du kit absent.
Bilan CONFORME signifie conformité aux critères vérifiés ici, pas certification enseignant.
"""

import os
import subprocess
import sys
import tempfile
import venv
import zipfile
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
VERSION = "1.0.0"
ROUE = RACINE / "dist" / f"sentiment_app-{VERSION}-py3-none-any.whl"
ARCHIVE = RACINE / "dist" / f"sentiment_app-{VERSION}.tar.gz"
RAPPORT = RACINE / "docs" / "livrable-tp4.txt"
LIGNES: list[str] = []
ERREURS = 0


def noter(ok: bool, message: str, details: str = "") -> bool:
    global ERREURS
    ligne = f"[{'OK' if ok else 'ÉCHEC'}] {message}" + (f" — {details}" if details else "")
    print(ligne)
    LIGNES.append(ligne)
    if not ok:
        ERREURS += 1
    return ok


def terminer() -> int:
    bilan = "Bilan : CONFORME" if ERREURS == 0 else f"Bilan : NON CONFORME ({ERREURS} échec(s))"
    print(bilan)
    LIGNES.append(bilan)
    RAPPORT.parent.mkdir(exist_ok=True)
    RAPPORT.write_text("\n".join(LIGNES) + "\n", encoding="utf-8")
    print(f"Rapport : {RAPPORT.relative_to(RACINE)}")
    return 0 if ERREURS == 0 else 1


def lancer(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "VERIFICATION_LIVRABLE": "1"}
    env.pop("SENTIMENT_MODELE", None)
    return subprocess.run(args, cwd=cwd, env=env, capture_output=True,
                          text=True, encoding="utf-8", errors="replace", check=False)


def main() -> int:
    if not noter(ROUE.is_file(), f"roue présente : {ROUE.name}"):
        return terminer()
    noter(ARCHIVE.is_file(), f"distribution source présente : {ARCHIVE.name}")
    extras = [p.name for p in (RACINE / "dist").iterdir()
              if p.is_file() and p.name not in {ROUE.name, ARCHIVE.name}]
    noter(not extras, "aucun autre fichier dans dist/", ", ".join(extras))
    with zipfile.ZipFile(ROUE) as z:
        noms = z.namelist()
        noter("sentiment_app/modele/sentiment.joblib" in noms, "modèle embarqué dans la roue")
        entry = [x for x in noms if x.endswith(".dist-info/entry_points.txt")]
        entree = z.read(entry[0]).decode() if entry else ""
        noter("sentiment = sentiment_app.cli:main" in entree, "commande sentiment déclarée")
        noter(not any("tests/" in x or x.startswith("tests/") for x in noms),
              "pas de tests dans la roue")
    changelog = (RACINE / "CHANGELOG.md").read_text(encoding="utf-8")
    noter("[1.0.0]" in changelog, "CHANGELOG décrit la version [1.0.0]")
    tag = lancer(["git", "tag", "--points-at", "HEAD"], RACINE)
    noter(tag.returncode == 0 and "v1.0.0" in tag.stdout.splitlines(),
          "étiquette Git sur le dernier commit : v1.0.0")
    if ERREURS:
        return terminer()
    with tempfile.TemporaryDirectory(prefix="verif-manuel-") as tmp:
        dossier = Path(tmp)
        venv.create(dossier / "env", with_pip=True)
        binaires = dossier / "env" / ("Scripts" if sys.platform == "win32" else "bin")
        python = binaires / ("python.exe" if sys.platform == "win32" else "python")
        commande = binaires / ("sentiment.exe" if sys.platform == "win32" else "sentiment")
        install = lancer([str(python), "-m", "pip", "install", "-q", str(ROUE), "pytest"], dossier)
        if not noter(install.returncode == 0, "installation de la roue dans un environnement neuf",
                     (install.stderr.strip().splitlines() or [""])[-1] if install.returncode else ""):
            return terminer()
        tests = lancer([str(python), "-m", "pytest", "-q", "-p", "no:cacheprovider",
                        str(RACINE / "tests" / "test_paquet.py")], dossier)
        bilan = (tests.stdout.strip().splitlines() or [""])[-1]
        noter(tests.returncode == 0 and "skipped" not in bilan,
              "six contrôles RECONSTITUÉS sur le paquet installé", bilan)
        cmd = lancer([str(commande), "predict", "Produit cassé et service injoignable, à fuir"], dossier)
        noter(cmd.returncode == 0 and '"label": "NEGATIVE"' in cmd.stdout,
              "commande installée : prédiction hors du dépôt", cmd.stdout.strip())
    return terminer()


if __name__ == "__main__":
    raise SystemExit(main())
