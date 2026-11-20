package ma.emsi.avis;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

/** Cinq tests JUnit RECONSTITUES, pas le kit original du professeur. */
class AvisServiceTest {
    private HttpServer python;
    private MockMvc mvc;
    private final ObjectMapper json = new ObjectMapper();

    @BeforeEach
    void preparer() throws IOException {
        python = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
        python.createContext("/v1/predict", echange -> {
            String texte;
            try {
                JsonNode corps = json.readTree(echange.getRequestBody());
                texte = corps.path("text").asText();
            } catch (Exception e) {
                echange.sendResponseHeaders(400, -1);
                echange.close();
                return;
            }
            String cle = echange.getRequestHeaders().getFirst("X-API-Key");
            int statut;
            String corps;
            if (cle == null || cle.isBlank()) {
                statut = 401;
                corps = "{\"erreur\":{\"code\":\"NON_AUTHENTIFIE\",\"message\":\"Cle absente\",\"champs\":[]}}";
            } else if ("mitige".equals(texte)) {
                statut = 200;
                corps = "{\"label\":\"INDETERMINE\",\"score\":0.559,\"text\":\"mitige\"}";
            } else {
                statut = 200;
                corps = "{\"label\":\"POSITIVE\",\"score\":0.777,\"text\":\"bon\"}";
            }
            if (!"HTTP/1.1".equals(echange.getProtocol())) {
                statut = 505;
                corps = "{}";
            }
            byte[] octets = corps.getBytes(StandardCharsets.UTF_8);
            echange.getResponseHeaders().set("Content-Type", "application/json");
            echange.sendResponseHeaders(statut, octets.length);
            try (var flux = echange.getResponseBody()) {
                flux.write(octets);
            }
        });
        python.start();
        mvc = creerMvc("cle-de-test-longue-et-valide");
    }

    private MockMvc creerMvc(String cle) {
        String url = "http://127.0.0.1:" + python.getAddress().getPort();
        SentimentGateway passerelle = new SentimentGateway(url, cle, json);
        return MockMvcBuilders.standaloneSetup(new AvisController(passerelle))
                .setControllerAdvice(new GestionErreurs()).build();
    }

    @AfterEach
    void nettoyer() {
        if (python != null) {
            python.stop(0);
        }
    }

    @Test
    void reponsePositive() throws Exception {
        mvc.perform(post("/avis/analyse").contentType(MediaType.APPLICATION_JSON)
                        .content("{\"texte\":\"bon\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.verdict").value("POSITIVE"))
                .andExpect(jsonPath("$.confiance").value(0.777))
                .andExpect(jsonPath("$.aVerifier").value(false));
    }

    @Test
    void abstentionDemandeVerification() throws Exception {
        mvc.perform(post("/avis/analyse").contentType(MediaType.APPLICATION_JSON)
                        .content("{\"texte\":\"mitige\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.verdict").value("INDETERMINE"))
                .andExpect(jsonPath("$.confiance").value(0.559))
                .andExpect(jsonPath("$.aVerifier").value(true));
    }

    @Test
    void texteVideRefuseAvantPython() throws Exception {
        mvc.perform(post("/avis/analyse").contentType(MediaType.APPLICATION_JSON)
                        .content("{\"texte\":\"   \"}"))
                .andExpect(status().isUnprocessableEntity())
                .andExpect(jsonPath("$.erreur.code").value("ENTREE_INVALIDE"));
    }

    @Test
    void cleAbsenteRenvoie401() throws Exception {
        MockMvc sansCle = creerMvc("");
        sansCle.perform(post("/avis/analyse").contentType(MediaType.APPLICATION_JSON)
                        .content("{\"texte\":\"bon\"}"))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.erreur.code").value("NON_AUTHENTIFIE"));
    }

    @Test
    void apiArreteeRenvoie503() throws Exception {
        python.stop(0);
        python = null;
        mvc.perform(post("/avis/analyse").contentType(MediaType.APPLICATION_JSON)
                        .content("{\"texte\":\"bon\"}"))
                .andExpect(status().isServiceUnavailable())
                .andExpect(jsonPath("$.erreur.code").value("API_INJOIGNABLE"));
    }
}
