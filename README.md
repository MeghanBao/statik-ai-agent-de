# Statik AI Agent – Deutschland 🤖🇩🇪

Ein intelligenter KI-Agent für den Statikbereich in Deutschland. Dieses Tool kombiniert klassische baustatische Berechnungen mit modernem Retrieval-Augmented Generation (RAG), um Ingenieuren und Architekten schnelle Orientierungswerte und normbasierte Erklärungen zu liefern.

⚠️ **Wichtiger Hinweis:** Alle Berechnungen und KI-generierten Texte dienen ausschließlich der Orientierung. Sie ersetzen keine qualifizierte statische Berechnung durch einen staatlich geprüften Tragwerksplaner.

## ✨ Hauptfunktionen

### 🏗️ Statische Berechnung
- Berechnung des maximalen Biegemoments (M) für Einfeldträger
- Ermittlung der maximalen Durchbiegung (δ) unter Berücksichtigung von Materialsteifigkeit und Profilgeometrie
- IPE-Profile und Materialien (Stahl, Beton, Holz, Aluminium)

### 📊 Visualisierung
- Biegemomentenverlauf-Diagramme
- Biegelinien (Durchbiegungsverläufe)
- Profil-Vergleichs-Charts

### 📚 RAG-Dokumentensuche
- Intelligente Suche in relevanten technischen Baubestimmungen
- Kontextualisierung der Ergebnisse durch hinterlegte Referenzdokumente

### 🤖 KI-Interpretationen
- Deutschsprachige Erklärungen der statischen Zusammenhänge
- Bewertung der Ergebnisse im Hinblick auf Gebrauchstauglichkeitsgrenzwerte (z.B. L/300)

## 🛠️ Technologie-Stack

- **Frontend:** Streamlit – Für eine intuitive, webbasierte Benutzeroberfläche
- **Berechnung:** NumPy – Effiziente mathematische Operationen
- **Visualisierung:** Matplotlib – Diagramme und Charts
- **RAG:** ChromaDB + Sentence Transformers – Dokumenten-Retrieval
- **KI:** OpenAI API (optional) – Für erweiterte Erklärungen

## 🚀 Installation & Start

### Voraussetzungen
- Python 3.8 oder höher
- pip

### Schritt-für-Schritt

```bash
# Repository klonen
git clone https://github.com/MeghanBao/statik-ai-agent-de.git
cd statik-ai-agent-de

# Virtuelle Umgebung einrichten (empfohlen)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder: venv\Scripts\activate  # Windows

# Abhängigkeiten installieren
pip install -r requirements.txt

# Anwendung starten
streamlit run app.py
```

Die App ist unter `http://localhost:8501` erreichbar.

## 📋 Beispiel

**Eingabewerte:**
- Länge (L): 6.0 m
- Last (w): 5.0 kN/m
- E-Modul: 210.000 MPa (Stahl)
- I-Moment (I): 8.33e-6 m⁴ (IPE 200)

**Frage:** "Ist die Durchbiegung für einen Deckenbalken im Wohnungsbau akzeptabel?"

**Ergebnis:**
- Die App berechnet die Werte und liefert eine KI-gestützte Einordnung basierend auf der L/300 Regel für die Gebrauchstauglichkeit.

## 📁 Projektstruktur

```
statik-ai-agent-de/
├── app.py                 # Hauptanwendung (Streamlit UI)
├── calculation.py         # Physikalische Berechnungslogik
├── visualization.py       # Diagramme und Charts
├── rag_module.py          # Dokumenten-Retrieval (Vektorsuche)
├── llm_module.py          # Sprachmodell-Schnittstelle
└── requirements.txt       # Python-Abhängigkeiten
```

## 🗺️ Roadmap

### ✅ Abgeschlossen (Today!)
- [x] PDF-Export für Kurzberichte
- [x] Dynamische Diagramme (Streamlit Tabs)
- [x] Mehr Trägertypen (Durchlaufträger, Kragträger)

### ⏳ Kommend
- [ ] Echte LLM-Anbindung (OpenAI GPT-4)
- [ ] Vektordatenbank mit umfangreichen Normen-Bibliotheken
- [ ] Weitere Trägertypen (Rahmen, Platten)

## ⚖️ Haftungsausschluss

Die Nutzung dieser Software erfolgt auf eigene Gefahr.

- Die Software dient nur als Referenz
- Sie ersetzt keine statische Prüfung nach geltenden Normen
- Für verbindliche Ergebnisse ist immer ein qualifizierter Statiker hinzuzuziehen

## 📄 Lizenz

MIT License - siehe [LICENSE](LICENSE) Datei
