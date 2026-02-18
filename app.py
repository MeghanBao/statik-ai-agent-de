"""
statik-ai-agent-de
Hauptanwendung mit Streamlit UI - Phase 3 Erweiterung
NEU: Rahmen- und Plattenberechnungen
"""

import streamlit as st
from calculation import (
    berechne_einfeldtraeger,
    berechne_kragtraeger,
    berechne_durchlauftrager,
    berechne_rahmen_eingeschossig,
    berechne_rahmen_zweischossig,
    berechne_platte_einfeld,
    berechne_platte_durchlauf,
    get_material_e_modul,
    get_ipe_traegheitsmoment,
    format_ergebnis,
)
from visualization import (
    plot_bending_moment,
    plot_bending_moment_krag,
    plot_bending_moment_durchlauf,
    plot_deflection,
    plot_comparison_chart,
)
from pdf_export import PDFReport
from llm_module import StatikLLM

# Page config
st.set_page_config(
    page_title="Statik AI Agent - Deutschland",
    page_icon="🏗️",
    layout="wide",
)

# CSS
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: bold; color: #1f77b4; }
    .warning-box { background-color: #fff3cd; border: 1px solid #ffc107; border-radius: 5px; padding: 1rem; margin: 1rem 0; }
    .result-box { background-color: #f8f9fa; border: 2px solid #dee2e6; border-radius: 10px; padding: 1.5rem; margin: 1rem 0; }
    .success-text { color: #28a745; font-weight: bold; }
    .warning-text { color: #ffc107; font-weight: bold; }
    .danger-text { color: #dc3545; font-weight: bold; }
    .stButton > button { width: 100%; }
</style>
""", unsafe_allow_html=True)


def main():
    if "last_result" not in st.session_state:
        st.session_state.last_result = None

    st.markdown('<p class="main-header">🏗️ Statik AI Agent - Deutschland</p>', unsafe_allow_html=True)
    st.markdown("KI-gestützte statische Berechnungen für Ingenieure")
    
    # Warnung
    st.markdown("""
    <div class="warning-box">
        <strong>⚠️ Wichtiger Hinweis:</strong><br>
        Alle Berechnungen dienen ausschließlich der Orientierung. 
        Sie ersetzen keine qualifizierte statische Berechnung.
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📐 Berechnungstyp")
        
        berechnungs_typ = st.selectbox(
            "Wählen Sie den Typ",
            options=['Träger', 'Rahmen', 'Platte'],
            index=0
        )
        
        st.header("📊 Eingabeparameter")
        
        # ===== TRÄGER =====
        if berechnungs_typ == 'Träger':
            traeger_typ = st.selectbox(
                "Trägertyp",
                options=['Einfeldträger', 'Kragträger', 'Durchlaufträger (2 Felder)', 'Durchlaufträger (3 Felder)'],
                index=0
            )
            
            felder = []
            if 'Durchlaufträger' in traeger_typ:
                if '2 Felder' in traeger_typ:
                    col1, col2 = st.columns(2)
                    felder = [col1.number_input("Feld 1 (m)", 1, 20, 5, 0.5),
                             col2.number_input("Feld 2 (m)", 1, 20, 6, 0.5)]
                else:
                    c1, c2, c3 = st.columns(3)
                    felder = [c1.number_input("Feld 1 (m)", 1, 20, 4, 0.5),
                             c2.number_input("Feld 2 (m)", 1, 20, 5, 0.5),
                             c3.number_input("Feld 3 (m)", 1, 20, 4, 0.5)]
            else:
                laenge = st.slider("Trägerlänge (m)", 1.0, 20.0, 6.0, 0.5)
            
            streckenlast = st.number_input("Streckenlast (kN/m)", 0.1, 50.0, 5.0, 0.5)
            
            # Material
            st.subheader("Material")
            material = st.selectbox(
                "Material",
                ["Stahl (S235)", "Stahl (S355)", "Beton C20/25", 
                 "Beton C30/37", "Beton C35/45", "Holz (Fichte)", 
                 "Holz (BSH)", "Holz (Eiche)", "Aluminium"]
            )
            emodul = get_material_e_modul(material)
            st.info(f"E-Modul: {emodul:,.0f} MPa")
            
            # Profil
            st.subheader("Querschnitt")
            profil_typ = st.radio("Profiltyp", ["IPE-Profil", "Manuell"])
            
            if profil_typ == "IPE-Profil":
                profil = st.selectbox(
                    "IPE-Profil",
                    ["IPE 80", "IPE 100", "IPE 120", "IPE 140", "IPE 160", 
                     "IPE 180", "IPE 200", "IPE 220", "IPE 240", "IPE 270",
                     "IPE 300", "IPE 330", "IPE 360", "IPE 400", "IPE 450",
                     "IPE 500", "IPE 550", "IPE 600"]
                )
                traegheitsmoment = get_ipe_traegheitsmoment(profil)
            else:
                traegheitsmoment = st.number_input("Trägheitsmoment Iy (cm⁴)", 1.0, 100000.0, 1940.0, 10.0) * 1e-8
        
        # ===== RAHMEN =====
        elif berechnungs_typ == 'Rahmen':
            rahmen_typ = st.selectbox(
                "Rahmensystem",
                options=['Eingeschossig', 'Zweigeschossig'],
                index=0
            )
            
            breite = st.number_input("Rahmenbreite (m)", 4.0, 30.0, 8.0, 0.5)
            
            if rahmen_typ == 'Eingeschossig':
                hoehe = st.number_input("Firsthöhe (m)", 2.0, 15.0, 4.0, 0.5)
            else:
                col1, col2 = st.columns(2)
                hoehe_eg = col1.number_input("Höhe EG (m)", 2.0, 6.0, 3.5, 0.5)
                hoehe_og = col2.number_input("Höhe OG (m)", 2.0, 6.0, 3.5, 0.5)
                hoehe = hoehe_eg + hoehe_og
            
            streckenlast = st.number_input("Streckenlast auf Riegel (kN/m)", 0.5, 30.0, 5.0, 0.5)
            
            st.subheader("Material")
            material = st.selectbox(
                "Material",
                ["Stahl (S235)", "Stahl (S355)", "Beton C20/25", "Beton C30/37"],
                index=0
            )
            emodul = get_material_e_modul(material)
            st.info(f"E-Modul: {emodul:,.0f} MPa")
            
            st.subheader("Querschnitt")
            profil = st.selectbox(
                "Profil",
                ["IPE 200", "IPE 220", "IPE 240", "IPE 270", "IPE 300",
                 "IPE 330", "IPE 360", "IPE 400", "IPE 450", "IPE 500"]
            )
            traegheitsmoment = get_ipe_traegheitsmoment(profil)
        
        # ===== PLATTE =====
        else:  # Platte
            platten_typ = st.selectbox(
                "Plattentyp",
                options=['Einfeldplatte', 'Durchlaufplatte (2 Felder)', 
                        'Durchlaufplatte (3 Felder)', 'Durchlaufplatte (4 Felder)'],
                index=0
            )
            
            col1, col2 = st.columns(2)
            laenge_x = col1.number_input("Länge x (m)", 2.0, 15.0, 6.0, 0.5)
            laenge_y = col2.number_input("Länge y (m)", 2.0, 15.0, 4.0, 0.5)
            
            last = st.number_input("Flächenlast (kN/m²)", 0.5, 20.0, 5.0, 0.5)
            
            st.subheader("Material & Geometrie")
            material = st.selectbox(
                "Beton",
                ["Beton C20/25", "Beton C30/37", "Beton C35/45"],
                index=1
            )
            emodul = get_material_e_modul(material)
            st.info(f"E-Modul: {emodul:,.0f} MPa")
            
            dicke = st.slider("Plattendicke (cm)", 10, 40, 20, 1) / 100  # in m
        
        # Berechnen Button
        st.divider()
        berechnen = st.button("🔢 Berechnung starten", use_container_width=True, type="primary")
    
    # Hauptbereich
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📊 Berechnungsergebnisse")
        
        if berechnen:
            try:
                # ===== TRÄGER =====
                if berechnungs_typ == 'Träger':
                    if 'Durchlaufträger' in traeger_typ:
                        result = berechne_durchlauftrager(felder, streckenlast, emodul, traegheitsmoment)
                    elif traeger_typ == 'Kragträger':
                        result = berechne_kragtraeger(laenge, streckenlast, emodul, traegheitsmoment)
                    else:
                        result = berechne_einfeldtraeger(laenge, streckenlast, emodul, traegheitsmoment)
                
                # ===== RAHMEN =====
                elif berechnungs_typ == 'Rahmen':
                    if rahmen_typ == 'Eingeschossig':
                        result = berechne_rahmen_eingeschossig(breite, hoehe, streckenlast, emodul, traegheitsmoment)
                    else:
                        result = berechne_rahmen_zweischossig(breite, hoehe_eg, hoehe_og, streckenlast, emodul, traegheitsmoment)
                
                # ===== PLATTE =====
                else:
                    if 'Einfeld' in platten_typ:
                        result = berechne_platte_einfeld(laenge_x, laenge_y, last, emodul, dicke)
                    else:
                        felder_map = {'2': 2, '3': 3, '4': 4}
                        felder = int(platten_typ.split()[-1][0])
                        result = berechne_platte_durchlauf(laenge_x, laenge_y, last, emodul, dicke, felder)

                st.session_state.last_result = result
                
                # Ergebnisse anzeigen
                st.markdown('<div class="result-box">', unsafe_allow_html=True)
                
                # ===== TRÄGER ERGEBNISSE =====
                if berechnungs_typ == 'Träger':
                    met_col1, met_col2, met_col3 = st.columns(3)
                    with met_col1:
                        st.metric("Max. Biegemoment", f"{result.biegemoment_max:.2f} kNm")
                    with met_col2:
                        st.metric("Max. Querkraft", f"{result.querkraft_max:.2f} kN")
                    with met_col3:
                        st.metric("Max. Durchbiegung", f"{result.durchbiegung_max:.2f} mm")
                    
                    # Gebrauchstauglichkeit
                    st.subheader("📐 Gebrauchstauglichkeit")
                    gt_col1, gt_col2, gt_col3 = st.columns(3)
                    
                    with gt_col1:
                        st.metric("Grenzwert L/300", f"{result.grenzdurchbiegung_l300:.2f} mm")
                    with gt_col2:
                        st.metric("Grenzwert L/250", f"{result.grenzdurchbiegung_l250:.2f} mm")
                    with gt_col3:
                        delta_color = "normal" if result.ausnutzung_l300 <= 100 else "off" if result.ausnutzung_l300 <= 120 else "inverse"
                        st.metric("Ausnutzung L/300", f"{result.ausnutzung_l300:.1f}%", delta_color=delta_color)
                    
                    # Bewertung
                    if result.ausnutzung_l300 <= 100:
                        st.success(f"✅ Die Durchbiegung liegt im zulässigen Bereich (L/300)")
                    elif result.ausnutzung_l300 <= 120:
                        st.warning(f"⚠️ Die Durchbiegung überschreitet L/300 leicht ({result.ausnutzung_l300-100:.1f}%)")
                    else:
                        st.error(f"❌ Die Durchbiegung überschreitet L/300 deutlich!")
                
                # ===== RAHMEN ERGEBNISSE =====
                elif berechnungs_typ == 'Rahmen':
                    met_col1, met_col2, met_col3 = st.columns(3)
                    with met_col1:
                        st.metric("Stützmoment", f"{result.schwingungsmoment:.2f} kNm")
                    with met_col2:
                        st.metric("Riegelmoment", f"{result.riegelmoment:.2f} kNm")
                    with met_col3:
                        st.metric("Durchbiegung", f"{result.durchbiegung_riegel:.2f} mm")
                    
                    st.subheader("📐 Auflagerkräfte")
                    ak_col1, ak_col2 = st.columns(2)
                    with ak_col1:
                        st.metric("Vertikalkraft", f"{result.stuetzkraft_vert:.2f} kN")
                    with ak_col2:
                        st.metric("Horizontalkraft", f"{result.stuetzkraft_horiz:.2f} kN")
                    
                    st.subheader("📐 Gebrauchstauglichkeit")
                    if result.ausnutzung <= 100:
                        st.success(f"✅ Rahmen ist ausreichend steif (Ausnutzung: {result.ausnutzung:.1f}%)")
                    else:
                        st.error(f"❌ Durchbiegung zu hoch! (Ausnutzung: {result.ausnutzung:.1f}%)")
                
                # ===== PLATTEN ERGEBNISSE =====
                else:
                    met_col1, met_col2, met_col3 = st.columns(3)
                    with met_col1:
                        st.metric("Max. Moment x", f"{result.max_moment_x:.2f} kNm/m")
                    with met_col2:
                        st.metric("Max. Moment y", f"{result.max_moment_y:.2f} kNm/m")
                    with met_col3:
                        st.metric("Durchbiegung", f"{result.max_durchbiegung:.2f} mm")
                    
                    st.subheader("📐 Erforderliche Bewehrung")
                    bw_col1, bw_col2 = st.columns(2)
                    with bw_col1:
                        st.metric("Bewehrung x", f"{result.bewehrung_x:.2f} cm²/m")
                    with bw_col2:
                        st.metric("Bewehrung y", f"{result.bewehrung_y:.2f} cm²/m")
                    
                    st.subheader("📐 Gebrauchstauglichkeit")
                    if result.ausnutzung <= 100:
                        st.success(f"✅ Plattensteifigkeit ausreichend (Ausnutzung: {result.ausnutzung:.1f}%)")
                    else:
                        st.error(f"❌ Durchbiegung zu hoch! (Ausnutzung: {result.ausnutzung:.1f}%)")

                st.markdown("</div>", unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Berechnungsfehler: {e}")

        if st.session_state.last_result is None:
            st.info("📝 Bitte geben Sie die Parameter in der Seitenleiste ein und starten Sie die Berechnung.")
        else:
            result = st.session_state.last_result

            with st.expander("📋 Detaillierte Berechnung"):
                st.text(format_ergebnis(result))

            # KI-Assistent
            st.divider()
            st.subheader("🤖 KI-Assistent (optional mit OpenAI)")
            frage = st.text_area(
                "Spezifische Frage zur Berechnung",
                value="Ist diese Konstruktion für den vorgesehenen Zweck geeignet?",
                height=100,
            )

            if st.button("🤖 KI-Erklärung erzeugen", use_container_width=True):
                llm = StatikLLM()
                erklaerung = llm.generate_explanation(result, frage=frage.strip() if frage.strip() else None)
                st.markdown(erklaerung)

                if llm.client is None:
                    st.info("ℹ️ Kein OPENAI_API_KEY gefunden: Es wird die lokale Template-Erklärung verwendet.")
                else:
                    st.success(f"✅ OpenAI-Modell aktiv: {llm.model}")
    
    with col2:
        st.header("ℹ️ Informationen")
        
        with st.expander("📐 Unterstützte Berechnungstypen"):
            st.markdown("""
            **Träger**
            - Einfeldträger (2 Auflager)
            - Kragträger (einseitig eingespannt)
            - Durchlaufträger (2-3 Felder)
            
            **Rahmen**
            - Eingeschossig (Pultdach)
            - Zweigeschossig
            
            **Platten**
            - Einfeldplatte (allseitig gelagert)
            - Durchlaufplatte (2-4 Felder)
            """)
        
        with st.expander("📏 Grenzwerte"):
            st.markdown("""
            **Durchbiegung**
            - L/300: Wohngebäude, Büros
            - L/250: Industriebauten
            - L/200: Kragträger, Dächer
            
            **Platten**
            - L/250: Standard
            """)
        
        with st.expander("🔧 Materialien"):
            st.markdown("""
            | Material | E-Modul |
            |----------|---------|
            | Stahl | 210.000 MPa |
            | Beton C30/37 | 33.000 MPa |
            | Beton C35/45 | 34.000 MPa |
            | Holz (Fichte) | 11.000 MPa |
            | Holz (BSH) | 14.000 MPa |
            | Aluminium | 70.000 MPa |
            """)


if __name__ == "__main__":
    main()
