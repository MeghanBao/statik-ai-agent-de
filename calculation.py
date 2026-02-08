"""
statik-ai-agent-de
Berechnungsmodul für statische Berechnungen
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple, Optional

@dataclass
class TraegerBerechnung:
    """Datenklasse für Trägerberechnungsergebnisse"""
    laenge: float  # m
    streckenlast: float  # kN/m
    emodul: float  # MPa (N/mm²)
    traegheitsmoment: float  # m⁴
    
    # Ergebnisse
    biegemoment_max: float = 0.0  # kNm
    durchbiegung_max: float = 0.0  # mm
    querkraft_max: float = 0.0  # kN
    
    # Grenzwerte
    grenzdurchbiegung_l300: float = 0.0  # mm (L/300)
    grenzdurchbiegung_l250: float = 0.0  # mm (L/250)
    ausnutzung_l300: float = 0.0  # %


def berechne_einfeldtraeger(
    laenge: float,
    streckenlast: float,
    emodul: float,
    traegheitsmoment: float
) -> TraegerBerechnung:
    """
    Berechnet einen Einfeldträger mit Gleichstreckenlast.
    
    Args:
        laenge: Trägerlänge in m
        streckenlast: Streckenlast in kN/m
        emodul: E-Modul in MPa (N/mm²)
        traegheitsmoment: Flächenträgheitsmoment in m⁴
    
    Returns:
        TraegerBerechnung mit allen Ergebnissen
    """
    result = TraegerBerechnung(
        laenge=laenge,
        streckenlast=streckenlast,
        emodul=emodul,
        traegheitsmoment=traegheitsmoment
    )
    
    # Maximales Biegemoment für Einfeldträger mit q
    # M_max = q * L² / 8
    result.biegemoment_max = (streckenlast * laenge**2) / 8.0
    
    # Maximale Querkraft
    # Q_max = q * L / 2
    result.querkraft_max = (streckenlast * laenge) / 2.0
    
    # Maximale Durchbiegung für Einfeldträger
    # δ_max = (5 * q * L⁴) / (384 * E * I)
    # Umrechnung: E in MPa = N/mm² = kN/m² * 1000
    # E [kN/m²] = E [MPa] * 1000
    emodul_knm2 = emodul * 1000  # kN/m²
    
    result.durchbiegung_max = (
        (5 * streckenlast * laenge**4) / 
        (384 * emodul_knm2 * traegheitsmoment)
    ) * 1000  # Umrechnung in mm
    
    # Grenzdurchbiegungen nach Gebrauchstauglichkeit
    result.grenzdurchbiegung_l300 = (laenge * 1000) / 300  # L/300 in mm
    result.grenzdurchbiegung_l250 = (laenge * 1000) / 250  # L/250 in mm
    
    # Ausnutzung
    if result.grenzdurchbiegung_l300 > 0:
        result.ausnutzung_l300 = (
            result.durchbiegung_max / result.grenzdurchbiegung_l300
        ) * 100
    
    return result


def get_material_e_modul(material: str) -> float:
    """
    Gibt den E-Modul für gängige Baustoffe zurück.
    
    Args:
        material: Materialbezeichnung
        
    Returns:
        E-Modul in MPa
    """
    materialien = {
        "Stahl (S235)": 210000,
        "Stahl (S355)": 210000,
        "Beton C20/25": 30000,
        "Beton C30/37": 33000,
        "Holz (Fichte)": 10000,
        "Holz (Eiche)": 12000,
        "Aluminium": 70000,
    }
    return materialien.get(material, 210000)


def get_ipe_traegheitsmoment(profil: str) -> float:
    """
    Gibt das Trägheitsmoment für IPE-Profile zurück.
    
    Args:
        profil: IPE-Profil (z.B. "IPE 200")
        
    Returns:
        Iy in m⁴
    """
    # Iy-Werte für IPE-Profile in cm⁴, umgerechnet in m⁴
    ipe_profile = {
        "IPE 80": 80.1e-8,
        "IPE 100": 171e-8,
        "IPE 120": 318e-8,
        "IPE 140": 541e-8,
        "IPE 160": 869e-8,
        "IPE 180": 1320e-8,
        "IPE 200": 1940e-8,
        "IPE 220": 2770e-8,
        "IPE 240": 3890e-8,
        "IPE 270": 5790e-8,
        "IPE 300": 8360e-8,
        "IPE 330": 11770e-8,
        "IPE 360": 16270e-8,
        "IPE 400": 23130e-8,
        "IPE 450": 33740e-8,
        "IPE 500": 48200e-8,
        "IPE 550": 67120e-8,
        "IPE 600": 92080e-8,
    }
    return ipe_profile.get(profil, 1940e-8)  # Default: IPE 200


def format_ergebnis(result: TraegerBerechnung) -> str:
    """
    Formatiert die Berechnungsergebnisse als lesbaren Text.
    """
    output = []
    output.append("=" * 50)
    output.append("STATISCHE BERECHNUNG - EINFELDTRÄGER")
    output.append("=" * 50)
    output.append("")
    output.append(f"Eingabewerte:")
    output.append(f"  Länge:           {result.laenge:.2f} m")
    output.append(f"  Streckenlast:    {result.streckenlast:.2f} kN/m")
    output.append(f"  E-Modul:         {result.emodul:,.0f} MPa")
    output.append(f"  Trägheitsmoment: {result.traegheitsmoment:.4e} m⁴")
    output.append("")
    output.append(f"Ergebnisse:")
    output.append(f"  Max. Biegemoment:  {result.biegemoment_max:.2f} kNm")
    output.append(f"  Max. Querkraft:    {result.querkraft_max:.2f} kN")
    output.append(f"  Max. Durchbiegung: {result.durchbiegung_max:.2f} mm")
    output.append("")
    output.append(f"Gebrauchstauglichkeit (Durchbiegung):")
    output.append(f"  Grenzwert L/300:   {result.grenzdurchbiegung_l300:.2f} mm")
    output.append(f"  Grenzwert L/250:   {result.grenzdurchbiegung_l250:.2f} mm")
    output.append(f"  Ausnutzung L/300:  {result.ausnutzung_l300:.1f}%")
    output.append("")
    
    # Bewertung
    if result.ausnutzung_l300 <= 100:
        output.append("✅ Die Durchbiegung liegt im zulässigen Bereich (L/300)")
    elif result.ausnutzung_l300 <= 120:
        output.append("⚠️ Die Durchbiegung überschreitet L/300 leicht")
    else:
        output.append("❌ Die Durchbiegung überschreitet L/300 deutlich!")
    
    output.append("=" * 50)
    
    return "\n".join(output)


# Wrapper-Funktionen für app.py
def calculate_bending_moment(L: float, w: float) -> float:
    """
    Berechnet das maximale Biegemoment.
    
    Args:
        L: Länge in m
        w: Streckenlast in kN/m
        
    Returns:
        Maximales Biegemoment in kNm
    """
    return (w * L**2) / 8.0


def calculate_deflection(L: float, w: float, E: float, I: float) -> float:
    """
    Berechnet die maximale Durchbiegung.
    
    Args:
        L: Länge in m
        w: Streckenlast in kN/m
        E: E-Modul in MPa
        I: Trägheitsmoment in m⁴
        
    Returns:
        Maximale Durchbiegung in mm
    """
    E_knm2 = E * 1000  # Umrechnung in kN/m²
    delta = (5 * w * L**4) / (384 * E_knm2 * I)
    return delta * 1000  # Umrechnung in mm


def calculate_shear_force(L: float, w: float) -> float:
    """
    Berechnet die maximale Querkraft.
    
    Args:
        L: Länge in m
        w: Streckenlast in kN/m
        
    Returns:
        Maximale Querkraft in kN
    """
    return (w * L) / 2.0


if __name__ == "__main__":
    # Test-Berechnung
    result = berechne_einfeldtraeger(
        laenge=6.0,
        streckenlast=5.0,
        emodul=210000,
        traegheitsmoment=1940e-8  # IPE 200
    )
    print(format_ergebnis(result))
