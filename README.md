# Statik AI Agent – Deutschland 🤖🇩🇪

> KI-gestützter Assistent für statische Berechnungen im Hochbau

Ein intelligenter KI-Agent für den Statikbereich in Deutschland. Dieses Tool kombiniert klassische baustatische Berechnungen mit modernem Retrieval-Augmented Generation (RAG), um Ingenieuren und Architekten schnelle Orientierungswerte und normbasierte Erklärungen zu liefern.

⚠️ **Wichtiger Hinweis:** Alle Berechnungen und KI-generierten Texte dienen ausschließlich der Orientierung. Sie ersetzen keine qualifizierte statische Berechnung durch einen staatlich geprüften Tragwerksplaner.

---

## ✨ Funktionen

### 🏗️ Statische Berechnungen

| Trägertyp | Beschreibung |
|-----------|--------------|
| **Einfeldträger** | Auf zwei Auflagern gelagert |
| **Kragträger** | Einseitig eingespannt |
| **Durchlaufträger** | 2 oder 3 Felder |

### 🏛️ Rahmenberechnung

| Rahmentyp | Beschreibung |
|-----------|--------------|
| **Eingeschossig** | Mit Pultdach |
| **Zweigeschossig** | Für mehrgeschossige Gebäude |

### 📐 Plattenberechnung

| Plattentyp | Beschreibung |
|-----------|--------------|
| **Einfeldplatte** | Allseitig gelagert |
| **Durchlaufplatte** | 2–4 Felder |

### 🤖 KI-Assistent

- Automatische Ergebnisauswertung
- Deutschsprachige Erklärungen
- Normenkonforme Bewertung (L/300, L/250)
- Optional mit OpenAI oder lokaler Fallback

### 📚 RAG-Wissensdatenbank

- 20+ deutsche Normen
- DIN EN 1990 bis 1995
- Semantische Suche

---

## 🚀 Installation

`ash
# Repository klonen
git clone https://github.com/MeghanBao/statik-ai-agent-de.git
cd statik-ai-agent-de

# Virtuelle Umgebung erstellen
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate      # Windows

# Abhängigkeiten installieren
pip install -r requirements.txt

# Anwendung starten
streamlit run app.py
`

Öffne [http://localhost:8501](http://localhost:8501)

---

## 📖 Verwendung

### 1. Trägerberechnung

1. Wähle **Träger** aus
2. Trägertyp auswählen (Einfeld, Krag, Durchlauf)
3. Länge und Last eingeben
4. Material und Profil wählen
5. **Berechnung starten**

### 2. Rahmenberechnung

1. Wähle **Rahmen**
2. System wählen (eingeschossig/zweigeschossig)
3. Abmessungen eingeben
4. Berechnung durchführen

### 3. Plattenberechnung

1. Wähle **Platte**
2. Plattentyp wählen
3. Abmessungen und Last eingeben
4. Bewehrung wird automatisch berechnet

### 4. KI-Assistent

Nach jeder Berechnung kannst du dem KI-Assistenten Fragen stellen:

> "Ist die Durchbiegung für einen Deckenbalken im Wohnungsbau akzeptabel?"

---

## 🔧 Konfiguration

### OpenAI (optional)

`ash
export OPENAI_API_KEY=sk-dein_api_key
export OPENAI_MODEL=gpt-4o-mini
streamlit run app.py
`

Ohne API-Key wird eine lokale Template-Erklärung verwendet.

---

## 📁 Projektstruktur

`
statik-ai-agent-de/
├── app.py                 # Streamlit UI
├── calculation.py         # Berechnungslogik
├── visualization.py      # Diagramme
├── rag_module.py         # RAG-Wissensdatenbank
├── llm_module.py         # KI-Schnittstelle
├── pdf_export.py         # PDF-Export
├── requirements.txt      # Python-Abhängigkeiten
└── README.md
`

---

## 🛠️ Technologie-Stack

- **Frontend:** Streamlit
- **Berechnung:** NumPy
- **Visualisierung:** Matplotlib
- **RAG:** ChromaDB + Sentence Transformers
- **KI:** OpenAI (optional)

---

## ⚖️ Haftung

Die Nutzung erfolgt auf eigene Verantwortung:

- Nur als Referenz geeignet
- Ersetzt keine statische Prüfung
- Qualifizierter Statiker erforderlich

---

## 📄 Lizenz

MIT License

---

_Made with ❤️ by Dudubot_
