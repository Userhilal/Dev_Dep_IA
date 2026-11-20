/** Client navigateur de l'API /v1, avec interprétation des codes stables. */
export function messageErreur(code, statut) {
  const messages = {
    ENTREE_INVALIDE: "Avis refusé : texte vide ou trop long.",
    NON_AUTHENTIFIE: "Clé d'API absente ou incorrecte.",
    ACCES_REFUSE: "Cette clé ne possède pas le rôle requis.",
    MODELE_INDISPONIBLE: "Modèle indisponible.",
    ERREUR_INTERNE: "Erreur interne de l'API."
  };
  return messages[code] || `Erreur de l'API (HTTP ${statut}).`;
}

export async function classer({ adresse, cle, texte, fetcher = fetch }) {
  let reponse;
  try {
    reponse = await fetcher(`${adresse.replace(/\/$/, "")}/v1/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-API-Key": cle },
      body: JSON.stringify({ text: texte }),
    });
  } catch (_) {
    return { ok: false, message: "API injoignable ou requête bloquée (réseau/CORS)." };
  }
  let corps = {};
  try { corps = await reponse.json(); } catch (_) { /* corps inconnu */ }
  if (reponse.ok) {
    const verdict = corps.label === "INDETERMINE" ? "À vérifier par un humain" : corps.label;
    return { ok: true, message: `${verdict} — confiance ${(corps.score * 100).toFixed(0)} %` };
  }
  return { ok: false, message: messageErreur(corps?.erreur?.code, reponse.status) };
}

if (typeof document !== "undefined") {
  const formulaire = document.getElementById("analyse");
  const sortie = document.getElementById("resultat");
  formulaire?.addEventListener("submit", async (evenement) => {
    evenement.preventDefault();
    sortie.textContent = "Analyse en cours…";
    const resultat = await classer({
      adresse: document.getElementById("adresse").value.trim(),
      cle: document.getElementById("cle").value,
      texte: document.getElementById("avis").value,
    });
    sortie.textContent = resultat.message;
  });
}
