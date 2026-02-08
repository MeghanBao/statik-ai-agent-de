"""
statik-ai-agent-de
Hauptanwendung mit Streamlit UI
"""

import streamlit as st
from calculation import (
    berechne_einfeldtraeger,
    get_material_e_modul,
    get_ipe_traegheitsmoment,
    format_ergebnis,
)

# Page config
st.set_page_config(
    page_title="Statik AI Agent - Deutschland",
    page_icon="🏗️",
    layout="wide",
)

# CSS für besseres Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .result-box {
        background-color: #f8f9fa;
        border: 2px solid #dee2e6;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .success-text {
        color: #28a745;
        font-weight: bold;
    }
    .warning-text {
        color: #ffc107;
        font-weight: bold;
    }
    .danger-text {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<p class="main-header">🏗️ Statik AI Agent - Deutschland</p>', 
                unsafe_allow_html=True)
    st.markdown("KI-gestützte statische Berechnungen für Ingenieure")
    
    # Warnung
    st.markdown("""
    <div class="warning-box">
        <strong>⚠️ Wichtiger Hinweis:</strong><br>
        Alle Berechnungen dienen ausschließlich der Orientierung. 
        Sie ersetzen keine qualifizierte statische Berechnung durch einen 
        staatlich geprüften Tragwerksplaner.
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Berechnungsparameter")
        
        # Länge
        laenge = st.slider(
            "Trägerlänge (m)",
            min_value=1.0,
            max_value=20.0,
            value=6.0,
            step=0.5
        )
        
        # Streckenlast
        streckenlast = st.number_input(
            "Streckenlast (kN/m)",
            min_value=0.1,
            max_value=50.0,
            value=5.0,
            step=0.5
        )
        
        # Material
        st.subheader("Material")
        material = st.selectbox(
            "Wählen Sie ein Material",
            ["Stahl (S235)", "Stahl (S355)", "Beton C20/25", 
             "Beton C30/37", "Holz (Fichte)", "Holz (Eiche)", 
             "Aluminium"]
        )
        emodul = get_material_e_modul(material)
        st.info(f"E-Modul: {emodul:,.0f} MPa")
        
        # Profil
        st.subheader("Querschnitt")
        profil_typ = st.radio("Profiltyp", ["IPE-Profil", "Manuelle Eingabe"])
        
        if profil_typ == "IPE-Profil":
            profil = st.selectbox(
                "IPE-Profil wählen",
                ["IPE 80", "IPE 100", "IPE 120", "IPE 140", "IPE 160", 
                 "IPE 180", "IPE 200", "IPE 220", "IPE 240", "IPE 270",
                 "IPE 300", "IPE 330", "IPE 360", "IPE 400", "IPE 450",
                 "IPE 500", "IPE 550", "IPE 600"]
            )
            traegheitsmoment = get_ipe_traegheitsmoment(profil)
        else:
            traegheitsmoment = st.number_input(
                "Trägheitsmoment Iy (cm⁴)",
                min_value=1.0,
                max_value=100000.0,
                value=1940.0,
                step=10.0
            ) * 1e-8  # Umrechnung in m⁴
        
        # Berechnen Button
        berechnen = st.button("🔍 Berechnung starten", use_container_width=True)
    
    # Hauptbereich
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📐 Berechnungsergebnisse")
        
        if berechnen:
            # Berechnung durchführen
            result = berechne_einfeldtraeger(
                laenge=laenge,
                streckenlast=streckenlast,
                emodul=emodul,
                traegheitsmoment=traegheitsmoment
            )
            
            # Ergebnisse anzeigen
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            
            # Metrics
            met_col1, met_col2, met_col3 = st.columns(3)
            
            with met_col1:
                st.metric(
                    "Max. Biegemoment",
                    f"{result.biegemoment_max:.2f} kNm",
                )
            
            with met_col2:
                st.metric(
                    "Max. Querkraft",
                    f"{result.querkraft_max:.2f} kN",
                )
            
            with met_col3:
                st.metric(
                    "Max. Durchbiegung",
                    f"{result.durchbiegung_max:.2f} mm",
                )
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Gebrauchstauglichkeit
            st.subheader("✅ Gebrauchstauglichkeit (Durchbiegung)")
            
            gt_col1, gt_col2, gt_col3 = st.columns(3)
            
            with gt_col1:
                st.metric("Grenzwert L/300", f"{result.grenzdurchbiegung_l300:.2f} mm")
            
            with gt_col2:
                st.metric("Grenzwert L/250", f"{result.grenzdurchbiegung_l250:.2f} mm")
            
            with gt_col3:
                # Farbige Darstellung der Ausnutzung
                if result.ausnutzung_l300 <= 100:
                    delta_color = "normal"
                    status_class = "success-text"
                    status_icon = "✅"
                elif result.ausnutzung_l300 <= 120:
                    delta_color = "off"
                    status_class = "warning-text"
                    status_icon = "⚠️"
                else:
                    delta_color = "inverse"
                    status_class = "danger-text"
                    status_icon = "❌"
                
                st.metric(
                    "Ausnutzung L/300",
                    f"{result.ausnutzung_l300:.1f}%",
                    delta=f"{status_icon}",
                    delta_color=delta_color
                )
            
            # Bewertungstext
            st.divider()
            st.subheader("🤖 KI-Bewertung")
            
            if result.ausnutzung_l300 <= 100:
                st.success("""
                **Die Durchbiegung liegt im zulässigen Bereich (L/300)**
                
                Die berechnete Durchbiegung von {:.2f} mm überschreitet den Grenzwert 
                von {:.2f} mm (L/300) nicht. Der Träger erfüllt die Anforderungen an 
                die Gebrauchstauglichkeit nach üblichen baupraktischen Regeln.
                """.format(result.durchbiegung_max, result.grenzdurchbiegung_l300))
                
            elif result.ausnutzung_l300 <= 120:
                st.warning("""
                **Die Durchbiegung überschreitet L/300 leicht**
                
                Die berechnete Durchbiegung von {:.2f} mm liegt {:.1f}% über dem 
                Grenzwert von {:.2f} mm (L/300). Eine Überprüfung mit einem 
                qualifizierten Tragwerksplaner wird empfohlen.
                """.format(result.durchbiegung_max, result.ausnutzung_l300 - 100, 
                          result.grenzdurchbiegung_l300))
                
            else:
                st.error("""
                **Die Durchbiegung überschreitet L/300 deutlich!**
                
                Die berechnete Durchbiegung von {:.2f} mm liegt {:.1f}% über dem 
                Grenzwert von {:.2f} mm (L/300). 
                
                **Empfohlene Maßnahmen:**
                - Verwendung eines größeren Profils
                - Reduzierung der Spannweite
                - Reduzierung der Last
                - Verwendung eines Materials mit höherem E-Modul
                """.format(result.durchbiegung_max, result.ausnutzung_l300 - 100,
                          result.grenzdurchbiegung_l300))
            
            # Detaillierte Ausgabe
            with st.expander("📋 Detaillierte Berechnung anzeigen"):
                st.text(format_ergebnis(result))
        
        else:
            st.info("👈 Bitte geben Sie die Parameter in der Seitenleiste ein und starten Sie die Berechnung.")
    
    with col2:
        st.header("📚 Informationen")
        
        with st.expander("ℹ️ Was wird berechnet?"):
            st.markdown("""
            **Einfeldträger mit Gleichstreckenlast**
            
            Für einen einfachen Träger auf zwei Stützen mit 
            gleichmäßig verteilter Last werden berechnet:
            
            - **Biegemoment**: M_max = q × L² / 8
            - **Querkraft**: Q_max = q × L / 2  
            - **Durchbiegung**: δ_max = (5 × q × L⁴) / (384 × E × I)
            """)
        
        with st.expander("📏 Grenzwerte"):
            st.markdown("""
            **Gebrauchstauglichkeit (typische Werte)**
            
            - **L/300**: Wohngebäude, Büros
            - **L/250**: Industriebauten, Lager
            - **L/200**: Dächer, nicht zugänglich
            
            *Hinweis: Exakte Werte sind in den einschlägigen 
            Normen (DIN EN 1990, DIN EN 1993) definiert.*
            """)
        
        with st.expander("🔧 Materialien"):
            st.markdown("""
            **E-Modul typischer Werte**
            
            | Material | E-Modul |
            |----------|---------|
            | Stahl | 210.000 MPa |
            | Beton C30/37 | 33.000 MPa |
            | Holz (Fichte) | 10.000 MPa |
            | Aluminium | 70.000 MPa |
            """)

if __name__ == "__main__":
    main()
