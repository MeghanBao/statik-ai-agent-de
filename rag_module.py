"""
statik-ai-agent-de
RAG-Modul für Dokumenten-Retrieval - Erweitert
NEU: Erweiterte Normen-Bibliothek
"""

from typing import List, Dict, Optional
import os

# ChromaDB für Vektorsuche
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("Warnung: ChromaDB nicht installiert. RAG-Funktionalität eingeschränkt.")

# Embeddings
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False


class StatikRAG:
    """
    RAG-System für statische Berechnungsnormen.
    """
    
    def __init__(self, db_path: str = "./chroma_db"):
        self.db_path = db_path
        self.collection = None
        self.embedding_model = None
        
        if CHROMADB_AVAILABLE:
            self._init_chroma()
        
        if EMBEDDINGS_AVAILABLE:
            self._init_embeddings()
    
    def _init_chroma(self):
        self.client = chromadb.Client(
            Settings(
                persist_directory=self.db_path,
                anonymized_telemetry=False
            )
        )
        
        self.collection = self.client.get_or_create_collection(
            name="statik_normen",
            metadata={"hnsw:space": "cosine"}
        )
    
    def _init_embeddings(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        try:
            self.embedding_model = SentenceTransformer(model_name)
            print(f"✓ Embedding-Modell geladen: {model_name}")
        except Exception as e:
            print(f"✗ Fehler beim Laden des Embedding-Modells: {e}")
            self.embedding_model = None
    
    def add_document(self, text: str, metadata: Dict = None, doc_id: Optional[str] = None) -> bool:
        if not CHROMADB_AVAILABLE or self.collection is None:
            return False
        
        if not EMBEDDINGS_AVAILABLE or self.embedding_model is None:
            return False
        
        try:
            embedding = self.embedding_model.encode(text).tolist()
            
            if doc_id is None:
                import hashlib
                doc_id = hashlib.md5(text.encode()).hexdigest()
            
            self.collection.add(
                embeddings=[embedding],
                documents=[text],
                metadatas=[metadata or {}],
                ids=[doc_id]
            )
            
            return True
            
        except Exception as e:
            print(f"✗ Fehler beim Hinzufügen des Dokuments: {e}")
            return False
    
    def search(self, query: str, n_results: int = 3) -> List[Dict]:
        if not CHROMADB_AVAILABLE or self.collection is None:
            return []
        
        if not EMBEDDINGS_AVAILABLE or self.embedding_model is None:
            return []
        
        try:
            query_embedding = self.embedding_model.encode(query).tolist()
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            formatted_results = []
            for i in range(len(results["ids"][0])):
                formatted_results.append({
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "similarity": 1 - results["distances"][0][i]
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"✗ Fehler bei der Suche: {e}")
            return []
    
    def get_norm_context(self, thema: str) -> str:
        results = self.search(thema, n_results=2)
        
        if not results:
            return "Keine spezifischen Normen-Informationen verfügbar."
        
        context_parts = []
        for r in results:
            source = r["metadata"].get("quelle", "Unbekannte Quelle")
            context_parts.append(f"[{source}] {r['text']}")
        
        return "\n\n".join(context_parts)


# Erweiterte Normen-Bibliothek
ERWEITERTE_NORMEN = [
    # Gebrauchstauglichkeit
    {
        "text": """Gebrauchstauglichkeitsnachweise nach DIN EN 1990:
        Für Decken in Wohngebäuden gilt typischerweise eine Grenzdurchbiegung von L/300.
        Dies bedeutet, dass die maximale Durchbiegung eines Trägers die Länge geteilt durch 300 nicht überschreiten darf.
        Beispiel: Ein 6m Träger darf maximal 20mm durchbiegen (6000/300 = 20).""",
        "metadata": {"quelle": "DIN EN 1990", "kapitel": "Gebrauchstauglichkeit", "kategorie": "durchbiegung"}
    },
    {
        "text": """Grenzdurchbiegungen nach Nutzungskategorie:
        - Wohngebäude, Büros: L/250 bis L/300
        - Industriebauten: L/250 bis L/200
        - Dächer (nicht betretbar): L/200
        - Dächer (betretbar): L/250
        - Krane, Maschinenfundamente: L/500 oder strenger
        - Vorgefertigte Platten: L/500""",
        "metadata": {"quelle": "DIN EN 1990 Anhang A", "kapitel": "Grenzwerte", "kategorie": "durchbiegung"}
    },
    {
        "text": """Durchbiegungsnachweis für Kragträger:
        Kragträger haben strengere Grenzwerte因为 sie empfindlicher auf Durchbiegung reagieren.
        Üblicher Grenzwert: L/200 für freitragende Konstruktionen.
        Zusätzlich ist die Schwingungsamplitude zu prüfen.""",
        "metadata": {"quelle": "DIN EN 1992-1-1", "kapitel": "Kragträger", "kategorie": "durchbiegung"}
    },
    
    # Biegemoment
    {
        "text": """Biegemomentberechnung nach Euler-Bernoulli:
        Für einen Einfeldträger mit Gleichstreckenlast q über die Länge L beträgt das maximale Biegemoment:
        M_max = q × L² / 8
        Das Maximum tritt in Feldmitte auf.""",
        "metadata": {"quelle": "Baustatik Grundlagen", "kapitel": "Biegemoment", "kategorie": "moment"}
    },
    {
        "text": """Biegemoment für Kragträger:
        Bei einem Kragträger mit Gleichstreckenlast q und Länge L:
        M_max = q × L² / 2
        Das maximale Biegemoment tritt am Einspannpunkt auf.""",
        "metadata": {"quelle": "Baustatik Grundlagen", "kapitel": "Kragträger", "kategorie": "moment"}
    },
    {
        "text": """Biegemoment für Durchlaufträger:
        Durchlaufträger haben günstigere Schnittgrößen als Einfeldträger.
        Das Stützmoment beträgt etwa q × L² / 10 bis q × L² / 12.
        Das Feldmoment ist entsprechend kleiner.""",
        "metadata": {"quelle": "Baustatik Grundlagen", "kapitel": "Durchlaufträger", "kategorie": "moment"}
    },
    {
        "text": """Rahmenberechnung - Schnittgrößen:
        Bei eingeschossigen Rahmen mit geneigtem Dach:
        - Stützmomente: q × L² / 10 bis q × L² / 12
        - Riegelmomente: q × L² / 24
        Die Horizontalkräfte aus Dachneigung sind zu berücksichtigen.""",
        "metadata": {"quelle": "DIN EN 1993-1-1", "kapitel": "Rahmen", "kategorie": "moment"}
    },
    
    # Durchbiegung
    {
        "text": """Durchbiegungsberechnung:
        Die maximale Durchbiegung eines Einfeldträgers unter Gleichstreckenlast:
        w_max = (5 × q × L⁴) / (384 × E × I)
        Dabei ist E der Elastizitätsmodul und I das Flächenträgheitsmoment.
        Die Formel gilt für linear-elastisches Verhalten.""",
        "metadata": {"quelle": "Baustatik Grundlagen", "kapitel": "Durchbiegung", "kategorie": "durchbiegung"}
    },
    {
        "text": """Durchbiegung Kragträger:
        Maximale Durchbiegung am freien Ende eines Kragträgers:
        w_max = (q × L⁴) / (8 × E × I)
        Die Durchbiegung ist proportional zur 4. Potenz der Länge!""",
        "metadata": {"quelle": "Baustatik Grundlagen", "kapitel": "Kragträger", "kategorie": "durchbiegung"}
    },
    {
        "text": """Durchbiegung von Platten:
        Für allseits gelagerte Platten gilt näherungsweise:
        w_max = k × q × a⁴ / D
        Mit der Biegesteifigkeit D = E × h³ / (12 × (1 - ν²))
        wobei ν die Querdehnzahl ist (für Beton: ν = 0,2).""",
        "metadata": {"quelle": "Plattentheorie", "kapitel": "Durchbiegung", "kategorie": "platte"}
    },
    
    # Stahlbau
    {
        "text": """Stahl S235 vs S355:
        - S235: f_y = 235 MPa, für normale Beanspruchung
        - S355: f_y = 355 MPa, für höhere Festigkeit
        Der E-Modul ist bei beiden: E = 210.000 MPa""",
        "metadata": {"quelle": "DIN EN 1993-1-1", "kapitel": "Stahlwerkstoffe", "kategorie": "material"}
    },
    {
        "text": """IPE-Profile:
        IPE-Profile sind warmgewalzte I-Profile mit parallelen Flanschen.
        Typische Verwendung: Deckenträger, Hallenrahmen, Kranbahnträger.
        Kennwerte: Iy (Trägheitsmoment), W_y (Widerstandsmoment), A (Querschnittsfläche).""",
        "metadata": {"quelle": "DIN EN 10365", "kapitel": "Profile", "kategorie": "profil"}
    },
    
    # Betonbau
    {
        "text": """Beton C20/25 bis C50/60:
        - C20/25: f_ck = 20 MPa (Zylinder), 25 MPa (Würfel)
        - C30/37: f_ck = 30 MPa
        - C50/60: f_ck = 50 MPa
        E-Modul: ca. 30.000 bis 40.000 MPa (abhängig von Festigkeit)""",
        "metadata": {"quelle": "DIN EN 1992-1-1", "kapitel": "Beton", "kategorie": "material"}
    },
    {
        "text": """Plattenbewehrung:
        Erforderliche Bewehrung: A_s = M / (z × f_y)
        Mit Hebelarm z ≈ 0,9 × d (Näherung)
        Minimale Bewehrung: ρ_min = 0,0013 für B500 (Betonstahl)
        Maximalbewehrung: ρ_max = 0,04 × A_c""",
        "metadata": {"quelle": "DIN EN 1992-1-1", "kapitel": "Bewehrung", "kategorie": "platte"}
    },
    
    # Holzbau
    {
        "text": """Holzarten und E-Modul:
        - Fichte/Tanne: E = 9.000-12.000 MPa
        - Eiche: E = 11.000-14.000 MPa
        - Brettschichtholz (BSH): E = 13.000-16.000 MPa
        - LVL (Furnierschichtholz): E = 13.000-15.000 MPa""",
        "metadata": {"quelle": "DIN EN 1995-1-1", "kapitel": "Holz", "kategorie": "material"}
    },
    {
        "text": """Holzquerschnitte:
        Für Holzträger gelten besondere Grenzwerte:
        - Durchbiegung: L/300 bis L/400 für sichtbare Träger
        - Schwingungsnachweis für Decken erforderlich
        - Kriechen beachten (Endkriechzahl φ = 0,6 bis 0,8)""",
        "metadata": {"quelle": "DIN EN 1995-1-1", "kapitel": "Holzträger", "kategorie": "holz"}
    },
    
    # Lasten
    {
        "text": """Lastannahmen nach DIN EN 1991:
        - Eigenlast (GK): γ_G = 1,35
        - Nutzlast (QK): γ_Q = 1,5
        - Schnee: γ_Q = 1,5
        - Wind: γ_Q = 1,5
        Für Wohngebäude: Nutzlast 2,0 kN/m²""",
        "metadata": {"quelle": "DIN EN 1991-1-1", "kapitel": "Lasten", "kategorie": "last"}
    },
    {
        "text": """Charakteristische Nutzlasten:
        - Wohnflächen: 2,0 kN/m²
        - Büroflächen: 3,0 kN/m²
        - Versammlungsräume: 5,0 kN/m²
        - Lagerflächen: 7,5 kN/m²
        - Dächer (nicht betretbar): 0,75 kN/m²""",
        "metadata": {"quelle": "DIN EN 1991-1-1", "tabelle 6.2", "kategorie": "last"}
    },
    
    # Sicherheit
    {
        "text": """Teilsicherheitsbeiwerte:
        - γ_G (ständige Lasten): 1,35 (ungünstig), 1,0 (günstig)
        - γ_Q (veränderliche Lasten): 1,5 (ungünstig), 0 (günstig)
        - γ_M (Material): 1,0 (Stahl), 1,5 (Beton), 1,3 (Holz)""",
        "metadata": {"quelle": "DIN EN 1990", "kapitel": "Sicherheit", "kategorie": "sicherheit"}
    },
]


def init_rag_with_examples() -> StatikRAG:
    """Initialisiert RAG mit erweiterter Normen-Bibliothek."""
    rag = StatikRAG()
    
    print("✓ Füge erweiterte Normen-Bibliothek hinzu...")
    for i, doc in enumerate(ERWEITERTE_NORMEN):
        success = rag.add_document(
            text=doc["text"],
            metadata=doc["metadata"],
            doc_id=f"norm_{i}"
        )
        if success:
            quelle = doc["metadata"]["quelle"]
            kapitel = doc["metadata"]["kapitel"]
            print(f"  ✓ {quelle} - {kapitel}")
    
    return rag


if __name__ == "__main__":
    print("=" * 50)
    print("RAG-Modul Test - Erweiterte Normen")
    print("=" * 50)
    
    rag = init_rag_with_examples()
    
    test_queries = [
        "Was ist die Grenzdurchbiegung für Wohngebäude?",
        "Wie berechnet man Biegemoment?",
        "L/300 Regel",
        "Stahl S235 oder S355?",
        "Holz E-Modul",
        "Plattenbewehrung"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        results = rag.search(query, n_results=2)
        for r in results:
            print(f"  [{r['metadata']['quelle']}] Ähnlichkeit: {r['similarity']:.2f}")
            print(f"  {r['text'][:100]}...")
    
    print("\n✓ RAG-Test abgeschlossen!")
