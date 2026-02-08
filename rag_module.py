"""
statik-ai-agent-de
RAG-Modul für Dokumenten-Retrieval
Grundstruktur - erweiterbar für Normen-Datenbank
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
    
    Features:
    - Dokumenten-Indizierung (DIN EN 1993, Eurocodes, etc.)
    - Semantische Suche über Vektordatenbank
    - Kontextbasierte Antworten
    """
    
    def __init__(self, db_path: str = "./chroma_db"):
        """
        Initialisiert das RAG-System.
        
        Args:
            db_path: Pfad zur ChromaDB-Datenbank
        """
        self.db_path = db_path
        self.collection = None
        self.embedding_model = None
        
        if CHROMADB_AVAILABLE:
            self._init_chroma()
        
        if EMBEDDINGS_AVAILABLE:
            self._init_embeddings()
    
    def _init_chroma(self):
        """Initialisiert ChromaDB."""
        self.client = chromadb.Client(
            Settings(
                persist_directory=self.db_path,
                anonymized_telemetry=False
            )
        )
        
        # Collection für Statik-Normen
        self.collection = self.client.get_or_create_collection(
            name="statik_normen",
            metadata={"hnsw:space": "cosine"}
        )
    
    def _init_embeddings(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        """
        Initialisiert das Embedding-Modell.
        
        Args:
            model_name: Name des Sentence-Transformer Modells
        """
        try:
            self.embedding_model = SentenceTransformer(model_name)
            print(f"✅ Embedding-Modell geladen: {model_name}")
        except Exception as e:
            print(f"⚠️ Fehler beim Laden des Embedding-Modells: {e}")
            self.embedding_model = None
    
    def add_document(self, text: str, metadata: Dict = None, doc_id: Optional[str] = None) -> bool:
        """
        Fügt ein Dokument zur Wissensdatenbank hinzu.
        
        Args:
            text: Dokumenten-Text
            metadata: Zusätzliche Metadaten (z.B. {"quelle": "DIN EN 1993-1-1"})
            doc_id: Eindeutige Dokumenten-ID
            
        Returns:
            True bei Erfolg, False bei Fehler
        """
        if not CHROMADB_AVAILABLE or self.collection is None:
            print("⚠️ ChromaDB nicht verfügbar. Dokument wird nicht hinzugefügt.")
            return False
        
        if not EMBEDDINGS_AVAILABLE or self.embedding_model is None:
            print("⚠️ Embeddings nicht verfügbar. Dokument wird nicht hinzugefügt.")
            return False
        
        try:
            # Embedding generieren
            embedding = self.embedding_model.encode(text).tolist()
            
            # ID generieren falls nicht angegeben
            if doc_id is None:
                import hashlib
                doc_id = hashlib.md5(text.encode()).hexdigest()
            
            # Zu ChromaDB hinzufügen
            self.collection.add(
                embeddings=[embedding],
                documents=[text],
                metadatas=[metadata or {}],
                ids=[doc_id]
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Fehler beim Hinzufügen des Dokuments: {e}")
            return False
    
    def search(self, query: str, n_results: int = 3) -> List[Dict]:
        """
        Sucht nach relevanten Dokumenten.
        
        Args:
            query: Suchanfrage
            n_results: Anzahl der Ergebnisse
            
        Returns:
            Liste der relevantesten Dokumente
        """
        if not CHROMADB_AVAILABLE or self.collection is None:
            return []
        
        if not EMBEDDINGS_AVAILABLE or self.embedding_model is None:
            return []
        
        try:
            # Query-Embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Suche durchführen
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            # Ergebnisse formatieren
            formatted_results = []
            for i in range(len(results["ids"][0])):
                formatted_results.append({
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "similarity": 1 - results["distances"][0][i]  # Cosine Similarity
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"❌ Fehler bei der Suche: {e}")
            return []
    
    def get_norm_context(self, thema: str) -> str:
        """
        Holt kontextuelle Informationen zu einem Statik-Thema.
        
        Args:
            thema: Thema (z.B. "Biegemoment", "Durchbiegung", "L/300")
            
        Returns:
            Kontext-String mit relevanten Normen-Informationen
        """
        results = self.search(thema, n_results=2)
        
        if not results:
            return "Keine spezifischen Normen-Informationen verfügbar."
        
        context_parts = []
        for r in results:
            source = r["metadata"].get("quelle", "Unbekannte Quelle")
            context_parts.append(f"[{source}] {r['text']}")
        
        return "\n\n".join(context_parts)


# Beispiel-Normen-Dokumente (können erweitert werden)
BEISPIEL_NORMEN = [
    {
        "text": """Gebrauchstauglichkeitsnachweise nach DIN EN 1990:
        Für Decken in Wohngebäuden gilt typischerweise eine Grenzdurchbiegung von L/300.
        Dies bedeutet, dass die maximale Durchbiegung eines Trägers die Länge geteilt durch 300 nicht überschreiten darf.
        Beispiel: Ein 6m Träger darf maximal 20mm durchbiegen (6000/300 = 20).""",
        "metadata": {"quelle": "DIN EN 1990", "kapitel": "Gebrauchstauglichkeit"}
    },
    {
        "text": """Biegemomentberechnung nach Euler-Bernoulli:
        Für einen Einfeldträger mit Gleichstreckenlast q über die Länge L beträgt das maximale Biegemoment:
        M_max = q × L² / 8
        Das Maximum tritt in Feldmitte auf.""",
        "metadata": {"quelle": "Baustatik Grundlagen", "kapitel": "Biegemoment"}
    },
    {
        "text": """Durchbiegungsberechnung:
        Die maximale Durchbiegung eines Einfeldträgers unter Gleichstreckenlast:
        w_max = (5 × q × L⁴) / (384 × E × I)
        Dabei ist E der Elastizitätsmodul und I das Flächenträgheitsmoment.""",
        "metadata": {"quelle": "Baustatik Grundlagen", "kapitel": "Durchbiegung"}
    },
    {
        "text": """Grenzdurchbiegungen nach Nutzung:
        - Wohngebäude, Büros: L/300
        - Industriebauten: L/250 bis L/200
        - Dächer (nicht betretbar): L/200
        - Krane, Maschinenfundamente: L/500 oder strenger""",
        "metadata": {"quelle": "DIN EN 1990 Anhang", "kapitel": "Grenzwerte"}
    },
]


def init_rag_with_examples() -> StatikRAG:
    """
    Initialisiert RAG mit Beispiel-Dokumenten.
    """
    rag = StatikRAG()
    
    print("🔄 Füge Beispiel-Normen hinzu...")
    for i, doc in enumerate(BEISPIEL_NORMEN):
        success = rag.add_document(
            text=doc["text"],
            metadata=doc["metadata"],
            doc_id=f"norm_{i}"
        )
        if success:
            print(f"  ✅ {doc['metadata']['quelle']} - {doc['metadata']['kapitel']}")
    
    return rag


if __name__ == "__main__":
    # Test
    print("🧪 RAG-Modul Test")
    print("=" * 50)
    
    rag = init_rag_with_examples()
    
    # Test-Suche
    test_queries = [
        "Was ist die Grenzdurchbiegung für Wohngebäude?",
        "Wie berechnet man das Biegemoment?",
        "L/300 Regel"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        results = rag.search(query, n_results=2)
        for r in results:
            print(f"  [{r['metadata']['quelle']}] Ähnlichkeit: {r['similarity']:.2f}")
            print(f"  {r['text'][:100]}...")
