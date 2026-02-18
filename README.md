# Statik AI Agent – Deutschland 🤖🇩🇪

Ein intelligenter KI-Agent für den Statikbereich in Deutschland. Dieses Tool kombiniert klassische baustatische Berechnungen mit modernem Retrieval-Augmented Generation (RAG), um Ingenieuren und Architekten schnelle Orientierungswerte und normbasierte Erklärungen zu liefern.

⚠️ **Wichtiger Hinweis:** Alle Berechnungen und KI-generierten Texte dienen ausschließlich der Orientierung. Sie ersetzen keine qualifizierte statische Berechnung durch einen staatlich geprüften Tragwerksplaner.

## ✨ Hauptfunktionen

### 🏗️ Statische Berechnung

**Träger:**
- Einfeldträger
- Kragträger (einseitig eingespannt)
- Durchlaufträger (2-3 Felder)

**NEU - Rahmen:**
- Eingeschossiger Rahmen mit Pultdach
- Zweigeschossiger Rahmen

**NEU - Platten:**
- Einfeldplatte (allseitig gelagert)
- Durchlaufplatte (2-4 Felder)
- Bewehrungsberechnung

### 📊 Visualisierung
- Biegemomentenverlauf-Diagramme
- Biegelinien (Durchbiegungsverläufe)
- Profil-Vergleichs-Charts

### 📚 RAG-Dokumentensuche (Erweitert!)
- Intelligente Suche in 20+ deutschen Normen
- DIN EN 1990, 1991, 1992, 1993, 1995
- Kontextbasierte Antworten

### 🤖 KI-Interpretationen
- Deutschsprachige Erklärungen
- Bewertung der Ergebnisse
- Optional mit **OpenAI** oder lokaler Fallback

## 🛠️ Technologie-Stack

- **Frontend:** Streamlit
- **Berechnung:** NumPy
- **Visualisierung:** Matplotlib
- **RAG:** ChromaDB + Sentence Transformers
- **KI:** OpenAI API (optional)

## 🚀 Installation & Start

`ash
# Repository klonen
git clone https://github.com/MeghanBao/statik-ai-agent-de.git
cd statik-ai-agent-de

# Virtuelle Umgebung
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder: venv\Scripts\activate  # Windows

# Abhängigkeiten installieren
pip install -r requirements.txt

# Anwendung starten
streamlit run app.py
`

Die App ist unter http://localhost:8501 erreichbar.

### Optional: OpenAI aktivieren

`ash
export OPENAI_API_KEY="dein_api_key"
streamlit run app.py
`

## 📁 Projektstruktur

`
statik-ai-agent-de/
├── app.py                 # Hauptanwendung (Streamlit UI)
├── calculation.py         # Physikalische Berechnungen + Rahmen + Platten
├── visualization.py       # Diagramme und Charts
├── rag_module.py          # Erweiterte Dokumenten-Retrieval
├── llm_module.py         # Sprachmodell-Schnittstelle
├── pdf_export.py         # PDF-Berichte
└── requirements.txt       # Python-Abhängigkeiten
`

## 🗺️ Roadmap

### ✅ Phase 3 Abgeschlossen

- [x] PDF-Export für Kurzberichte
- [x] Dynamische Diagramme (Streamlit Tabs)
- [x] Mehr Trägertypen (Durchlaufträger, Kragträger)
- [x] KI-Assistent mit optionaler OpenAI-Anbindung und Fallback
- [x] **RAHMENBERECHNUNG** - Eingeschossig & Zweigeschossig
- [x] **PLATTENBERECHNUNG** - Einfeld & Durchlauf mit Bewehrung
- [x] **Erweiterte Normen-Bibliothek** - 20+ Normen (DIN EN 1990-1995)
- [x] Neue Materialien - BSH, C35/45

### ⏳ Zukünftige Erweiterungen

- 3D-Visualisierung
- Weitere Rahmenformen (Giebel, Sattel)
- Fundamentberechnungen
- Erdbebennachweise

## ⚖️ Haftungsausschluss

Die Nutzung dieser Software erfolgt auf eigene Gefahr.

- Die Software dient nur als Referenz
- Sie ersetzt keine statische Prüfung nach geltenden Normen
- Für verbindliche Ergebnisse ist immer ein qualifizierter Statiker hinzuzuziehen

## 📄 Lizenz

MIT License

---

_Made with ❤️ by Dudubot_
