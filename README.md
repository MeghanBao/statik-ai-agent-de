# 🤖 Statik AI Agent – Deutschland 🌍

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Ein intelligenter **KI-Agent für den Statikbereich in Deutschland**. Dieses Tool kombiniert klassische baustatische Berechnungen mit modernem **Retrieval-Augmented Generation (RAG)**, um Ingenieuren und Architekten schnelle Orientierungswerte und normbasierte Erklärungen zu liefern.

> [!WARNING]
> **Wichtiger Hinweis:** Alle Berechnungen und KI-generierten Texte dienen **ausschließlich der Orientierung**. Sie ersetzen keine qualifizierte statische Berechnung durch einen staatlich geprüften Tragwerksplaner.

---

## ✨ Hauptfunktionen (MVP)

### 🏗️ Statische Berechnung
- Berechnung des **maximalen Biegemoments (M)** für Einfeldträger.
- Ermittlung der **maximalen Durchbiegung (δ)** unter Berücksichtigung von Materialsteifigkeit und Profilgeometrie.

### 📚 RAG-Dokumentensuche
- Intelligente Suche in relevanten technischen Baubestimmungen und Normen (z.B. **DIN EN 1993 / Eurocode 3**).
- Kontextualisierung der Ergebnisse durch hinterlegte Referenzdokumente.

### 🤖 KI-Interpretationen
- Deutschsprachige Erklärungen der statischen Zusammenhänge.
- Bewertung der Ergebnisse im Hinblick auf Gebrauchstauglichkeitsgrenzwerte (z.B. L/300).

---

## 🛠️ Technologie-Stack

- **Frontend:** [Streamlit](https://streamlit.io/) – Für eine intuitive, webbasierte Benutzeroberfläche.
- **Berechnung:** [NumPy](https://numpy.org/) – Effiziente mathematische Operationen.
- **KI-Logik:** Python-basierte Module für RAG und LLM-Integration (aktuell als erweiterbare Architektur vorbereitet).

---

## 📁 Projektstruktur

```text
statik-ai-agent-de/
├── app.py            # Hauptanwendung (Streamlit UI & Orchestrierung)
├── calculation.py    # Physikalische Berechnungslogik (Statik)
├── rag_module.py     # Dokumenten-Retrieval (Vektorsuche-Anbindung)
├── llm_module.py     # Sprachmodell-Schnittstelle & Prompting
├── requirements.txt  # Liste der Python-Abhängigkeiten
└── README.md         # Projektdokumentation
```

---

## 🚀 Installation & Start

### Voraussetzungen
- Python 3.8 oder höher
- `pip` (Python Package Installer)

### Schritt-für-Schritt Anleitung

1. **Repository klonen**
   ```bash
   git clone https://github.com/MeghanBao/statik-ai-agent-de.git
   cd statik-ai-agent-de
   ```

2. **Virtuelle Umgebung einrichten (empfohlen)**
   ```bash
   python -m venv venv
   # Aktivierung unter Windows:
   venv\Scripts\activate
   # Aktivierung unter Linux/macOS:
   source venv/bin/activate
   ```

3. **Abhängigkeiten installieren**
   ```bash
   pip install -r requirements.txt
   ```

4. **Anwendung starten**
   streamlit run app.py
   ```
   Die App ist nun standardmäßig unter `http://localhost:8501` erreichbar.

### ⚙️ Eigene Konfiguration (Port & Adresse)
Falls Port `8501` bereits belegt ist oder du die App unter einer anderen Adresse erreichbar machen willst, nutze folgende Befehle:

- **Anderen Port verwenden:**
  ```bash
  streamlit run app.py --server.port 8888
  ```
- **Von anderen Geräten im Netzwerk zugreifen:**
  ```bash
  streamlit run app.py --server.address 0.0.0.0
  ```

---

## 📌 Beispiel für eine Anfrage

**Eingabewerte:**
- **Länge (L):** 6.0 m
- **Last (w):** 5.0 kN/m
- **E-Modul:** 210.000 MPa (Stahl)
- **I-Moment (I):** 8.33e-6 m⁴
- **Frage:** "Ist die Durchbiegung für einen Deckenbalken im Wohnungsbau akzeptabel?"

**Ergebnis:**
- Die App berechnet die Werte und liefert eine KI-gestützte Einordnung basierend auf der L/300 Regel für die Gebrauchstauglichkeit.

---

## 🗺️ Roadmap

- [ ] **Echte LLM-Anbindung:** Integration von OpenAI GPT-4 oder lokalen LLaMA-Modellen.
- [ ] **Vektordatenbank:** Implementierung von ChromaDB oder Pinecone für umfangreiche Normen-Bibliotheken.
- [ ] **Visualisierung:** Dynamische Darstellung von Momentenlinien und Biegelinien mit `matplotlib` oder `plotly`.
- [ ] **PDF-Export:** Generierung automatisierter Kurzberichte.

---

## ⚖️ Haftungsausschluss

Die Nutzung dieser Software erfolgt auf eigene Gefahr.
1. Die Software dient **nur als Referenz**.
2. Sie ersetzt **keine statische Prüfung** nach geltenden Normen.
3. Für verbindliche Ergebnisse ist **immer** ein qualifizierter Statiker hinzuzuziehen.

---

## 📄 Lizenz

Dieses Projekt ist unter der **MIT-Lizenz** lizenziert. Weitere Details finden Sie in der [LICENSE](LICENSE) Datei.
