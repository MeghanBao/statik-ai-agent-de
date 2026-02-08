"""
statik-ai-agent-de
LLM-Modul für KI-gestützte Erklärungen
"""

from typing import Optional, Dict
from calculation import TraegerBerechnung


class StatikLLM:
    """
    LLM-Interface für statische Berechnungen.
    
    Erzeugt deutschsprachige Erklärungen und Bewertungen
    basierend auf Berechnungsergebnissen.
    """
    
    def __init__(self):
        """Initialisiert das LLM-Modul."""
        self.context = ""
    
    def set_rag_context(self, context: str):
        """
        Setzt den RAG-Kontext für verbesserte Antworten.
        
        Args:
            context: Normen-Kontext aus RAG-Modul
        """
        self.context = context
    
    def generate_explanation(self, result: TraegerBerechnung, frage: Optional[str] = None) -> str:
        """
        Generiert eine Erklärung zu den Berechnungsergebnissen.
        
        Args:
            result: Berechnungsergebnisse
            frage: Optionale spezifische Frage
            
        Returns:
            Deutschsprachige Erklärung
        """
        # Template-basierte Erklärung (kann später durch echtes LLM ersetzt werden)
        
        parts = []
        
        # Einleitung
        parts.append(self._generate_intro(result))
        
        # Ergebnis-Interpretation
        parts.append(self._interpret_results(result))
        
        # Handlungsempfehlung
        parts.append(self._generate_recommendation(result))
        
        # Antwort auf spezifische Frage
        if frage:
            parts.append(self._answer_specific_question(result, frage))
        
        return "\n\n".join(parts)
    
    def _generate_intro(self, result: TraegerBerechnung) -> str:
        """Generiert die Einleitung."""
        return f"""### Berechnungsübersicht

Für den untersuchten **Einfeldträger** mit einer Länge von **{result.laenge:.1f} m** 
und einer Streckenlast von **{result.streckenlast:.1f} kN/m** ergeben sich folgende 
charakteristische Werte:

- **Maximales Biegemoment**: {result.biegemoment_max:.2f} kNm
- **Maximale Querkraft**: {result.querkraft_max:.2f} kN  
- **Maximale Durchbiegung**: {result.durchbiegung_max:.2f} mm
"""
    
    def _interpret_results(self, result: TraegerBerechnung) -> str:
        """Interpretiert die Ergebnisse."""
        
        # Durchbiegungs-Bewertung
        if result.ausnutzung_l300 <= 100:
            durchbiegung_text = (
                f"✅ **Die Durchbiegung liegt im zulässigen Bereich.**\n\n"
                f"Mit {result.durchbiegung_max:.2f} mm liegt die Durchbiegung unter dem "
                f"Grenzwert von {result.grenzdurchbiegung_l300:.2f} mm (L/300). "
                f"Die Ausnutzung beträgt {result.ausnutzung_l300:.1f}%."
            )
        elif result.ausnutzung_l300 <= 120:
            durchbiegung_text = (
                f"⚠️ **Die Durchbiegung überschreitet den Grenzwert leicht.**\n\n"
                f"Mit {result.durchbiegung_max:.2f} mm liegt die Durchbiegung {result.ausnutzung_l300 - 100:.1f}% "
                f"über dem Grenzwert von {result.grenzdurchbiegung_l300:.2f} mm (L/300). "
                f"Eine Überprüfung durch einen Fachplaner wird empfohlen."
            )
        else:
            durchbiegung_text = (
                f"❌ **Die Durchbiegung überschreitet den Grenzwert deutlich!**\n\n"
                f"Mit {result.durchbiegung_max:.2f} mm liegt die Durchbiegung {result.ausnutzung_l300 - 100:.1f}% "
                f"über dem Grenzwert. Die Konstruktion erfüllt die Anforderungen nicht."
            )
        
        # Biegemoment-Interpretation
        biegemoment_text = (
            f"\n\nDas maximale Biegemoment von **{result.biegemoment_max:.2f} kNm** "
            f"tritt in Feldmitte auf. Dieser Wert ist für die Bemessung des "
            f"Querschnitts maßgebend."
        )
        
        return durchbiegung_text + biegemoment_text
    
    def _generate_recommendation(self, result: TraegerBerechnung) -> str:
        """Generiert Handlungsempfehlungen."""
        
        if result.ausnutzung_l300 <= 100:
            return """### Empfehlung

Die Konstruktion scheint für die vorliegende Beanspruchung geeignet zu sein. 
Für eine endgültige Beurteilung sollten jedoch folgende Aspekte geprüft werden:

- **Tragfähigkeit**: Ist der Querschnitt für das Biegemoment ausreichend bemessen?
- **Querkraft**: Sind die Schubspannungen im zulässigen Bereich?
- **Anschlüsse**: Sind die Auflagerungen konstruktiv sinnvoll ausgebildet?
- **Dauerhaftigkeit**: Welcher Korrosionsschutz ist erforderlich?"""
        
        else:
            return f"""### Empfohlene Maßnahmen

Da die Durchbiegung den zulässigen Wert überschreitet, werden folgende 
Optimierungsmöglichkeiten vorgeschlagen:

**1. Profilvergrößerung**
   - Wahl eines größeren IPE-Profils mit höherem Trägheitsmoment
   - Aktuelles Profil zu schwach für die vorliegende Spannweite

**2. Spannweitenreduktion**
   - Einbau von Zwischenstützen
   - Aufteilung in zwei kürzere Felder

**3. Materialänderung**
   - Bei Holz: Wechsel zu Stahl oder Brettschichtholz
   - Höherer E-Modul führt zu geringerer Durchbiegung

**4. Lastreduktion**
   - Überprüfung der angesetzten Nutzlasten
   - Optimierung der Konstruktionsdetails

**Berechnete Ausnutzung: {result.ausnutzung_l300:.1f}%**
"""
    
    def _answer_specific_question(self, result: TraegerBerechnung, frage: str) -> str:
        """Beantwortet eine spezifische Frage."""
        
        frage_lower = frage.lower()
        
        # Muster-Erkennung für häufige Fragen
        if "deckenbalken" in frage_lower or "wohnungsbau" in frage_lower:
            return self._answer_deckenbalken(result)
        elif "sicherheit" in frage_lower or "faktor" in frage_lower:
            return self._answer_sicherheit()
        elif "verbessern" in frage_lower or "optimieren" in frage_lower:
            return self._answer_optimierung(result)
        else:
            return f"""### Antwort auf Ihre Frage

Basierend auf den berechneten Werten kann ich folgendes sagen:

Die Konstruktion mit einer maximalen Durchbiegung von {result.durchbiegung_max:.2f} mm 
und einer Ausnutzung von {result.ausnutzung_l300:.1f}% bezogen auf L/300 sollte 
individuell bewertet werden.

{f"Die Durchbiegung liegt im zulässigen Bereich." if result.ausnutzung_l300 <= 100 else "Eine Überdimensionierung des Trägers wird empfohlen."}
"""
    
    def _answer_deckenbalken(self, result: TraegerBerechnung) -> str:
        """Antwort für Deckenbalken-Fragen."""
        return """### Deckenbalken im Wohnungsbau

Für Deckenbalken in Wohngebäuden gelten besondere Anforderungen:

**Gebrauchstauglichkeit (L/300):**
- Vermeidung von Rissen in Deckenbelägen
- Schwingungsverhalten (Fußgängeranregung)
- Ästhetik (sichtbare Durchbiegung)

**Empfehlung für Wohngebäude:**
""" + (f"""
✅ Die berechnete Durchbiegung von {result.durchbiegung_max:.2f} mm ist für einen 
Deckenbalken im Wohnungsbau akzeptabel.
""" if result.ausnutzung_l300 <= 100 else f"""
⚠️ Die Durchbiegung von {result.durchbiegung_max:.2f} mm könnte im Wohnungsbau 
zu Beeinträchtigungen führen. Ein größeres Profil wird empfohlen.
""")
    
    def _answer_sicherheit(self) -> str:
        """Antwort zu Sicherheitsfragen."""
        return """### Sicherheit und Teilsicherheitsbeiwerte

**Wichtig:** Diese Berechnung berücksichtigt **keine** Teilsicherheitsbeiwerte!

Nach DIN EN 1990 sind für Bemessungen folgende Faktoren zu berücksichtigen:

- **γ_G** = 1.35 (ständige Lasten, ungünstig)
- **γ_Q** = 1.5 (veränderliche Lasten, ungünstig)
- **γ_M** = 1.0-1.1 (Material, je nach Material)

**Für eine verbindliche statische Berechnung** müssen:
- Alle Lastfälle untersucht werden
- Kombinationsregeln angewendet werden
- Teilsicherheitsbeiwerte berücksichtigt werden
- Der Nachweis geführt werden

→ Konsultieren Sie einen statisch geprüften Tragwerksplaner!"""
    
    def _answer_optimierung(self, result: TraegerBerechnung) -> str:
        """Antwort zu Optimierungsfragen."""
        
        # Berechne benötigtes I für L/300
        erforderliches_i = (
            (5 * result.streckenlast * result.laenge**4) /
            (384 * result.emodul * 1000 * (result.laenge * 1000 / 300))
        ) * 1e8  # Umrechnung in cm⁴
        
        aktuelles_i_cm4 = result.traegheitsmoment * 1e8
        
        return f"""### Optimierungsmöglichkeiten

**Analyse:**
- Aktuelles Trägheitsmoment: {aktuelles_i_cm4:.0f} cm⁴
- Erforderlich für L/300: ca. {erforderliches_i:.0f} cm⁴

**Empfohlene IPE-Profile:**
""" + self._suggest_profiles(erforderliches_i)
    
    def _suggest_profiles(self, erforderliches_i: float) -> str:
        """Schlägt geeignete IPE-Profile vor."""
        from calculation import get_ipe_traegheitsmoment
        
        profile = [
            "IPE 180", "IPE 200", "IPE 220", "IPE 240", 
            "IPE 270", "IPE 300", "IPE 330"
        ]
        
        vorschlaege = []
        for profil in profile:
            i_wert = get_ipe_traegheitsmoment(profil) * 1e8  # in cm⁴
            if i_wert >= erforderliches_i * 0.9:  # 10% Toleranz
                vorschlaege.append(f"  - {profil}: Iy = {i_wert:.0f} cm⁴")
        
        if vorschlaege:
            return "Folgende Profile wären geeignet:\n" + "\n".join(vorschlaege[:3])
        else:
            return "Für diese Spannweite und Last wird ein größeres Profil als IPE 330 benötigt."


if __name__ == "__main__":
    # Test
    from calculation import berechne_einfeldtraeger
    
    print("🧠 LLM-Modul Test")
    print("=" * 50)
    
    result = berechne_einfeldtraeger(
        laenge=6.0,
        streckenlast=5.0,
        emodul=210000,
        traegheitsmoment=1940e-8
    )
    
    llm = StatikLLM()
    
    # Standard-Erklärung
    print("\n📋 Standard-Erklärung:")
    print(llm.generate_explanation(result))
    
    # Mit spezifischer Frage
    print("\n" + "=" * 50)
    print("\n❓ Mit Frage 'Ist das für einen Deckenbalken ok?':")
    print(llm.generate_explanation(result, frage="Ist das für einen Deckenbalken ok?"))
