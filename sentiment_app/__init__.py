"""sentiment-app : classer des avis en francais ; paquet autonome."""

from sentiment_app.predict import chemin_modele, predict

__version__ = "1.0.1"
__all__ = ["__version__", "predict"]

# Retrocompatibilite avec le test original TP6 : predict.chemin_modele().
# L'API recommande maintenant predict("texte") directement.
vars(predict)["chemin_modele"] = chemin_modele
