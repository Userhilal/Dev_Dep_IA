package ma.emsi.avis;

public record AnalyseResponse(String verdict, double confiance, boolean aVerifier) { }
