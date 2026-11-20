package ma.emsi.avis;

import org.springframework.http.HttpStatusCode;

public class ErreurService extends RuntimeException {
    private final HttpStatusCode statut;
    private final String code;

    public ErreurService(HttpStatusCode statut, String code, String message) {
        super(message);
        this.statut = statut;
        this.code = code;
    }

    public HttpStatusCode statut() {
        return statut;
    }

    public String code() {
        return code;
    }
}
