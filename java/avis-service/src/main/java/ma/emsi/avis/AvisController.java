package ma.emsi.avis;

import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class AvisController {
    private final SentimentGateway passerelle;

    public AvisController(SentimentGateway passerelle) {
        this.passerelle = passerelle;
    }

    @PostMapping(value = "/avis/analyse", consumes = MediaType.APPLICATION_JSON_VALUE)
    public AnalyseResponse analyser(@RequestBody AnalyseRequest requete) {
        return passerelle.analyser(requete.texte());
    }
}
