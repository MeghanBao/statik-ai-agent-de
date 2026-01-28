import streamlit as st
import calculation
import rag_module
import llm_module

st.set_page_config(page_title="Statik AI Agent – Deutschland", page_icon="🤖")

st.title("🤖 Statik AI Agent – Deutschland 🌍")

st.markdown("""
Dieses Projekt ist ein **AI-Agent für den Statikbereich in Deutschland**.  
Es kombiniert **einfache Berechnung**, **RAG-Dokumentensuche** und **AI-generierte deutsche Erklärungen**.
""")

st.warning("⚠️ **Hinweis:** Alle Berechnungen dienen **nur als Orientierung / Referenz** und ersetzen keine qualifizierte statische Berechnung.")

# Sidebar for inputs
st.sidebar.header("Eingabeparameter")
L = st.sidebar.number_input("Länge des Trägers (L) [m]", value=6.0, step=0.1)
w = st.sidebar.number_input("Gleichmäßig verteilte Last (w) [kN/m]", value=5.0, step=0.1)
E = st.sidebar.number_input("Elastizitätsmodul (E) [MPa]", value=210000.0, step=1000.0)
I = st.sidebar.number_input("Flächenträgheitsmoment (I) [m⁴]", value=8.33e-6, format="%.2e")

frage = st.text_area("Frage (Deutsch)", value="Wie hoch ist das maximale Biegemoment und die Durchbiegung?")

if st.button("Berechnen & Erklären"):
    # Calculations
    M = calculation.calculate_bending_moment(L, w)
    delta = calculation.calculate_deflection(L, w, E, I)
    
    st.header("Ergebnisse")
    col1, col2 = st.columns(2)
    col1.metric("Max. Biegemoment M", f"{M:.2f} kNm")
    col2.metric("Max. Durchbiegung δ", f"{delta:.2f} mm")
    
    # RAG & LLM (Placeholders)
    docs = rag_module.retrieve_documents(frage)
    explanation = llm_module.generate_explanation(frage, M, delta, docs)
    
    st.subheader("AI-Erklärung")
    st.write(explanation)
    
    st.info("Basierend auf der Berechnung und relevanten Dokumenten, bitte beachten Sie: Diese Berechnung dient nur als Orientierung und ersetzt keine offizielle statische Berechnung durch einen qualifizierten Ingenieur.")
