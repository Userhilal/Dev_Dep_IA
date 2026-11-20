package ma.emsi.avis;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class GestionErreurs {
    public record Detail(String code, String message) { }
    public record Enveloppe(Detail erreur) { }

    @ExceptionHandler(ErreurService.class)
    public ResponseEntity<Enveloppe> erreur(ErreurService exception) {
        return ResponseEntity.status(exception.statut())
                .body(new Enveloppe(new Detail(exception.code(), exception.getMessage())));
    }
}
