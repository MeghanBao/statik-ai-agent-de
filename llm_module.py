def generate_explanation(query, M, delta, docs):
    """
    Platzhalter für AI-Erklärungsmodul.
    Hier würde ein LLM (wie GPT-4) die Ergebnisse interpretieren.
    """
    doc_refs = ", ".join(docs)
    
    explanation = f"""
    Basierend auf Ihrer Frage: '{query}'
    
    Die statischen Kennwerte ergeben ein maximales Biegemoment von **{M:.2f} kNm** 
    und eine maximale Durchbiegung von **{delta:.2f} mm**.
    
    Unter Berücksichtigung von **{doc_refs}** sollten Sie sicherstellen, 
    dass die zulässigen Grenzwerte für die Gebrauchstauglichkeit eingehalten werden (meist L/300 oder L/500).
    
    *Hinweis: Dies ist eine KI-generierte Zusammenfassung.*
    """
    return explanation
