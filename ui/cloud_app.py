"""Démonstration Streamlit Cloud autonome du modèle sentiment-app 1.0.1.

Cette entrée utilise le modèle embarqué dans la roue GitHub, sans API HTTP ni clé.
L'application locale historique reste ui/app.py et continue d'utiliser /v1.
"""

import sys
from importlib.metadata import PackageNotFoundError, distribution
from pathlib import Path

import pandas as pd
import streamlit as st

# Streamlit Cloud execute depuis la racine Git. Le dossier source sentiment_app/
# y est sans modele binaire et peut masquer le paquet reellement installe.
# Donner priorite au paquet de la roue dans site-packages.
possibles = [
    Path(p) for p in sys.path if p and "site-packages" in p
    and (Path(p) / "sentiment_app" / "modele" / "sentiment.joblib").is_file()
]
if not possibles:
    st.error("La roue autonome sentiment-app 1.0.1 est absente. Verifiez ui/requirements.txt.")
    st.stop()
site_packages = str(possibles[0])
if site_packages in sys.path:
    sys.path.remove(site_packages)
sys.path.insert(0, site_packages)

try:
    paquet = distribution("sentiment-app")
except PackageNotFoundError:
    st.error("Paquet sentiment-app absent de l'environnement Python.")
    st.stop()
if paquet.version != "1.0.1":
    st.error(f"Version attendue 1.0.1, version installee : {paquet.version}.")
    st.stop()

from sentiment_app import predict  # noqa: E402

SEUIL_ABSTENTION = 0.60
MAX_TEXTE = 2000
MAX_AVIS = 1000
VERDICTS = {
    "POSITIVE": "Avis positif",
    "NEGATIVE": "Avis négatif",
    "INDETERMINE": "À vérifier par un humain",
    "REFUS": "Texte refusé",
}


def analyser(texte: str) -> tuple[str, float | None]:
    """Applique le même seuil d'abstention que l'API locale."""
    if not isinstance(texte, str) or not texte.strip() or len(texte) > MAX_TEXTE:
        return "REFUS", None

    resultat = predict(texte)
    score = float(resultat["score"])
    etiquette = str(resultat["label"]).upper()
    if etiquette not in ("POSITIVE", "NEGATIVE"):
        raise ValueError("Étiquette du modèle inconnue")
    return ("INDETERMINE" if score < SEUIL_ABSTENTION else etiquette), score


st.set_page_config(page_title="Analyse de sentiment", page_icon="💬", layout="wide")
st.title("Analyse de sentiment des avis")
st.caption("Démonstration hébergée — modèle TF-IDF et régression logistique, sentiment-app 1.0.1")
st.info(
    "Le modèle est inclus dans le paquet Python : cette démonstration fonctionne "
    "sans serveur FastAPI. Une confiance inférieure à 60 % demande une vérification humaine."
)

onglet_avis, onglet_fichier = st.tabs(["Un avis", "Un fichier d'avis"])

with onglet_avis:
    texte = st.text_area("Avis client", placeholder="Ex. Livraison rapide, produit conforme, très satisfait")
    if st.button("Analyser", type="primary"):
        try:
            verdict, confiance = analyser(texte)
        except Exception:
            st.error("Impossible d'analyser l'avis. Réessayez ou contactez le responsable de la démonstration.")
        else:
            if verdict == "REFUS":
                st.warning("Saisissez un avis non vide de 2 000 caractères maximum.")
            else:
                colonne_1, colonne_2 = st.columns(2)
                colonne_1.metric("Verdict", VERDICTS[verdict])
                colonne_2.metric("Confiance", f"{confiance:.1%}")
                if verdict == "INDETERMINE":
                    st.warning("La confiance est sous le seuil : avis à vérifier par un humain.")

with onglet_fichier:
    st.write("Importez un CSV UTF-8 contenant une colonne **text** (maximum 1 000 avis).")
    fichier = st.file_uploader("Fichier CSV", type="csv")
    if fichier is not None:
        try:
            avis = pd.read_csv(fichier, encoding="utf-8-sig")
        except (UnicodeError, pd.errors.ParserError, ValueError):
            st.error("CSV illisible. Enregistrez le fichier au format CSV UTF-8.")
        else:
            if "text" not in avis.columns:
                st.error("La colonne obligatoire 'text' est absente.")
            elif avis.empty:
                st.warning("Le fichier ne contient aucun avis.")
            elif len(avis) > MAX_AVIS:
                st.error(f"Le fichier contient {len(avis)} lignes ; maximum {MAX_AVIS}.")
            else:
                try:
                    resultats = [analyser(t) for t in avis["text"].tolist()]
                except Exception:
                    st.error("Une erreur est survenue pendant l'analyse du fichier.")
                else:
                    table = avis.copy()
                    table["verdict"] = [VERDICTS[verdict] for verdict, _ in resultats]
                    table["confiance"] = [score for _, score in resultats]
                    st.dataframe(table, use_container_width=True)

                    categories = list(VERDICTS.values())
                    effectifs = table["verdict"].value_counts().reindex(categories, fill_value=0)
                    st.write("**Répartition des verdicts**")
                    st.bar_chart(effectifs)

                    bornes = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
                    tranches = pd.cut(
                        table["confiance"].dropna(), bins=bornes,
                        labels=["50–60 %", "60–70 %", "70–80 %", "80–90 %", "90–100 %"],
                        include_lowest=True,
                    )
                    compte_confiance = tranches.value_counts().sort_index()
                    st.write("**Distribution de la confiance**")
                    st.bar_chart(compte_confiance)
                    st.caption("Les avis refusés n'ont pas de score et sont exclus de l'histogramme.")
                    st.download_button(
                        "Télécharger les résultats CSV",
                        data=table.to_csv(index=False).encode("utf-8-sig"),
                        file_name="resultats_sentiment.csv", mime="text/csv",
                    )
