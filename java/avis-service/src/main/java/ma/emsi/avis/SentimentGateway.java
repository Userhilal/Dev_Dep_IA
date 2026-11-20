package ma.emsi.avis;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.Map;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.HttpStatusCode;
import org.springframework.stereotype.Service;

@Service
public class SentimentGateway {
    private final String url;
    private final String cle;
    private final ObjectMapper json;
    private final HttpClient client;

    public SentimentGateway(@Value("${sentiment.api.url:http://127.0.0.1:8000}") String url,
                            @Value("${sentiment.api.key:}") String cle,
                            ObjectMapper json) {
        this.url = url.replaceAll("/+$", "") + "/v1/predict";
        this.cle = cle;
        this.json = json;
        this.client = HttpClient.newBuilder()
                .version(HttpClient.Version.HTTP_1_1)
                .connectTimeout(Duration.ofSeconds(3))
                .build();
    }

    public AnalyseResponse analyser(String texte) {
        if (texte == null || texte.isBlank() || texte.length() > 2000) {
            throw new ErreurService(HttpStatus.UNPROCESSABLE_ENTITY, "ENTREE_INVALIDE",
                    "Le texte doit contenir entre 1 et 2000 caracteres non blancs.");
        }

        final String corps;
        try {
            corps = json.writeValueAsString(Map.of("text", texte));
        } catch (JsonProcessingException e) {
            throw new ErreurService(HttpStatus.BAD_GATEWAY, "ENCODAGE_INVALIDE",
                    "Impossible de preparer la requete JSON.");
        }

        HttpRequest.Builder constructeur = HttpRequest.newBuilder(URI.create(url))
                .version(HttpClient.Version.HTTP_1_1) // requis pour l'essai reel du manuel
                .timeout(Duration.ofSeconds(5))
                .header("Content-Type", "application/json; charset=utf-8")
                .POST(HttpRequest.BodyPublishers.ofString(corps, StandardCharsets.UTF_8));
        if (!cle.isBlank()) {
            constructeur.header("X-API-Key", cle);
        }

        final HttpResponse<String> reponse;
        try {
            reponse = client.send(constructeur.build(),
                    HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8));
        } catch (IOException e) {
            throw new ErreurService(HttpStatus.SERVICE_UNAVAILABLE, "API_INJOIGNABLE",
                    "API Python injoignable : verifiez http://127.0.0.1:8000.");
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new ErreurService(HttpStatus.SERVICE_UNAVAILABLE, "API_INJOIGNABLE",
                    "Appel a l'API Python interrompu.");
        }

        if (reponse.statusCode() != 200) {
            int statut = reponse.statusCode();
            if (statut < 400 || statut > 599) {
                throw new ErreurService(HttpStatus.BAD_GATEWAY, "API_REPONSE_INVALIDE",
                        "Statut inattendu de l'API Python.");
            }
            String code = "API_HTTP_" + statut;
            try {
                JsonNode erreur = json.readTree(reponse.body()).path("erreur").path("code");
                if (erreur.isTextual() && !erreur.asText().isBlank()) {
                    code = erreur.asText();
                }
            } catch (JsonProcessingException e) {
                // Corps distant illisible : garder le code HTTP stable.
            }
            throw new ErreurService(HttpStatusCode.valueOf(statut), code,
                    "L'API Python a refuse la requete (HTTP " + statut + ").");
        }

        try {
            JsonNode resultat = json.readTree(reponse.body());
            String verdict = resultat.path("label").asText();
            JsonNode score = resultat.path("score");
            if (!(verdict.equals("POSITIVE") || verdict.equals("NEGATIVE")
                    || verdict.equals("INDETERMINE"))
                    || !score.isNumber() || score.asDouble() < 0 || score.asDouble() > 1) {
                throw new ErreurService(HttpStatus.BAD_GATEWAY, "API_REPONSE_INVALIDE",
                        "Format de prediction inattendu.");
            }
            return new AnalyseResponse(verdict, score.asDouble(), verdict.equals("INDETERMINE"));
        } catch (JsonProcessingException e) {
            throw new ErreurService(HttpStatus.BAD_GATEWAY, "API_REPONSE_INVALIDE",
                    "Reponse JSON illisible.");
        }
    }
}
