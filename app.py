"""
statik-ai-agent-de
Hauptanwendung mit Streamlit UI - Erweitert
Neu: Dynamische Updates, Mehr Trägertypen, PDF-Export
"""

import streamlit as st
from calculation import (
    berechne_einfeldtraeger,
    berechne_kragtraeger,
    berechne_durchlaufträger,
    get_material_e_modul,
    get_ipe_traegheitsmoment,
    format_ergebnis,
    get_traeger_typen,
)
from visualization import (
    plot_bending_moment,
    plot_bending_moment_krag,
    plot_bending_moment_durchlauf,
    plot_deflection,
    plot_comparison_chart,
)
from pdf_export import PDFReport

# Page config
st.set_page_config(
    page_title="Statik AI Agent - Deutschland",
    page_icon="🏗️",
    layout="wide",
)

# CSS für besseres Styling
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
        st.header("📊 Trägertyp")
        
        traeger_typ = st.selectbox(
            "Wählen Sie den Trägertyp",
            options=['Einfeldträger', 'Kragträger', 'Durchlaufträger (2 Felder)', 'Durchlaufträger (3 Felder)'],
            index=0
        )
        
        # Mapping zu internem Typ
        typ_mapping = {
            'Einfeldträger': 'einfeld',
            'Kragträger': 'krag',
            'Durchlaufträger (2 Felder)': 'durchlauf_2',
            'Durchlaufträger (3 Felder)': 'durchlauf_3',
        }
        
        st.header("📐 Eingabeparameter")
        
        # Feldlängen für Durchlaufträger
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
        
        # Streckenlast
        streckenlast = st.number_input("Streckenlast (kN/m)", 0.1, 50.0, 5.0, 0.5)
        
        # Material
        st.subheader("Material")
        material = st.selectbox(
            "Material",
            ["Stahl (S235)", "Stahl (S355)", "Beton C20/25", 
             "Beton C30/37", "Holz (Fichte)", "Holz (Eiche)", 
             "Aluminium"]
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
        
        # PDF Export
        st.divider()
        st.subheader("📄 PDF-Export")
        
        if st.button("📄 PDF-Bericht erstellen", use_container_width=True):
            try:
                # Berechnung durchführen
                if 'Durchlaufträger' in traeger_typ:
                    result = berechne_durchlaufträger(felder, streckenlast, emodul, traegheitsmoment)
                elif traeger_typ == 'Kragträger':
                    result = berechne_kragtraeger(laenge, streckenlast, emodul, traegheitsmoment)
                else:
                    result = berechne_einfeldtraeger(laenge, streckenlast, emodul, traegheitsmoment)
                
                # PDF generieren
                pdf = PDFReport()
                filename = pdf.generate_report(result, material, profil)
                
                st.success(f"✅ PDF erstellt: {filename}")
                
                # Download Button
                with open(filename, "rb") as f:
                    st.download_button(
                        "📥 PDF herunterladen",
                        f,
                        file_name=filename,
                        mime="application/pdf",
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"❌ Fehler: {e}")
        
        # Berechnen Button
        st.divider()
        berechnen = st.button("🔍 Berechnung starten", use_container_width=True, type="primary")
    
    # Hauptbereich
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📐 Berechnungsergebnisse")
        
        if berechnen:
            # Berechnung durchführen
            try:
                if 'Durchlaufträger' in traeger_typ:
                    result = berechne_durchlaufträger(felder, streckenlast, emodul, traegheitsmoment)
                elif traeger_typ == 'Kragträger':
                    result = berechne_kragtraeger(laenge, streckenlast, emodul, traegheitsmoment)
                else:
                    result = berechne_einfeldtraeger(laenge, streckenlast, emodul, traegheitsmoment)
                
                # Ergebnisse anzeigen
                st.markdown('<div class="result-box">', unsafe_allow_html=True)
                
                # Metrics
                met_col1, met_col2, met_col3 = st.columns(3)
                
                with met_col1:
                    st.metric("Max. Biegemoment", f"{result.biegemoment_max:.2f} kNm")
                
                with met_col2:
                    st.metric("Max. Querkraft", f"{result.querkraft_max:.2f} kN")
                
                with met_col3:
                    st.metric("Max. Durchbiegung", f"{result.durchbiegung_max:.2f} mm")
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Gebrauchstauglichkeit
                st.subheader("✅ Gebrauchstauglichkeit")
                
                gt_col1, gt_col2, gt_col3 = st.columns(3)
                
                with gt_col1:
                    st.metric("Grenzwert L/300", f"{result.grenzdurchbiegung_l300:.2f} mm")
                
                with gt_col2:
                    if 'Kragträger' in traeger_typ:
                        grenz_l200 = result.grenzdurchbiegung_l300 * 1.5  # L/200
                        st.metric("Grenzwert L/200", f"{grenz_l200:.2f} mm")
                    else:
                        st.metric("Grenzwert L/250", f"{result.grenzdurchbiegung_l250:.2f} mm")
                
                with gt_col3:
                    if result.ausnutzung_l300 <= 100:
                        delta_color = "normal"
                        status_icon = "✅"
                    elif result.ausnutzung_l300 <= 120:
                        delta_color = "off"
                        status_icon = "⚠️"
                    else:
                        delta_color = "inverse"
                        status_icon = "❌"
                    
                    st.metric("Ausnutzung L/300", f"{result.ausnutzung_l300:.1f}%", delta=status_icon, delta_color=delta_color)
                
                # Bewertungstext
                st.divider()
                st.subheader("🤖 KI-Bewertung")
                
                if result.ausnutzung_l300 <= 100:
                    st.success(f"**Die Durchbiegung liegt im zulässigen Bereich (L/300)**\n\nDie berechnete Durchbiegung von {result.durchbiegung_max:.2f} mm überschreitet den Grenzwert von {result.grenzdurchbiegung_l300:.2f} mm nicht.")
                elif result.ausnutzung_l300 <= 120:
                    st.warning(f"**Die Durchbiegung überschreitet L/300 leicht**\n\nDie berechnete Durchbiegung liegt {result.ausnutzung_l300 - 100:.1f}% über dem Grenzwert. Eine Überprüfung wird empfohlen.")
                else:
                    st.error(f"**Die Durchbiegung überschreitet L/300 deutlich!**\n\nEmpfohlene Maßnahmen:\n- Verwendung eines größeren Profils\n- Reduzierung der Spannweite\n- Reduzierung der Last\n- Verwendung eines Materials mit höherem E-Modul")
                
                # Dynamische Charts
                st.divider()
                st.subheader("📊 Diagramme")
                
                # Tab für verschiedene Diagramme
                tab1, tab2, tab3 = st.tabs(["📈 Biegemoment", "📉 Durchbiegung", "🔄 Vergleich"])
                
                with tab1:
                    if 'Durchlaufträger' in traeger_typ:
                        fig_mom = plot_bending_moment_durchlauf(felder, streckenlast)
                    elif traeger_typ == 'Kragträger':
                        fig_mom = plot_bending_moment_krag(laenge, streckenlast)
                    else:
                        fig_mom = plot_bending_moment(laenge if 'Einfeld' in traeger_typ else felder[0], streckenlast)
                    st.pyplot(fig_mom)
                
                with tab2:
                    if 'Durchlaufträger' in traeger_typ:
                        fig_def = plot_deflection(sum(felder), streckenlast, emodul, traegheitsmoment, 'durchlauf', felder)
                    elif traeger_typ == 'Kragträger':
                        fig_def = plot_deflection(laenge, streckenlast, emodul, traegheitsmoment, 'krag')
                    else:
                        fig_def = plot_deflection(laenge, streckenlast, emodul, traegheitsmoment)
                    st.pyplot(fig_def)
                
                with tab3:
                    if 'Einfeldträger' in traeger_typ:
                        fig_comp = plot_comparison_chart(laenge, streckenlast, emodul, traegheitsmoment)
                        st.pyplot(fig_comp)
                    else:
                        st.info("Profilvergleich nur für Einfeldträger verfügbar.")
                
                # Detaillierte Ausgabe
                with st.expander("📋 Detaillierte Berechnung"):
                    st.text(format_ergebnis(result))
                
            except Exception as e:
                st.error(f"Berechnungsfehler: {e}")
        
        else:
            st.info("👈 Bitte geben Sie die Parameter in der Seitenleiste ein und starten Sie die Berechnung.")
    
    with col2:
        st.header("📚 Informationen")
        
        with st.expander("ℹ️ Unterstützte Trägertypen"):
            st.markdown("""
            **Einfeldträger**
            - Einfach auf zwei Stützen gelagert
            - Maximales Moment in Feldmitte
            
            **Kragträger**
            - Einseitig eingespannt
            - Maximales Moment am Einspannpunkt
            
            **Durchlaufträger**
            - Mehrfeldrig (2-3 Felder)
            - Günstigeres Tragverhalten
            """)
        
        with st.expander("📏 Grenzwerte"):
            st.markdown("""
            **Gebrauchstauglichkeit**
            
            - **L/300**: Wohngebäude, Büros
            - **L/250**: Industriebauten
            - **L/200**: Kragträger, Dächer
            """)
        
        with st.expander("🔧 Materialien"):
            st.markdown("""
            | Material | E-Modul |
            |----------|---------|
            | Stahl | 210.000 MPa |
            | Beton C30/37 | 33.000 MPa |
            | Holz (Fichte) | 10.000 MPa |
            | Aluminium | 70.000 MPa |
            """)

if __name__ == "__main__":
    main()
