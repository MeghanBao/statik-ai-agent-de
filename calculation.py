"""
statik-ai-agent-de
Berechnungsmodul für statische Berechnungen
Erweitert: Einfeldträger, Durchlaufträger, Kragträger
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict
from dataclasses import asdict

@dataclass
class TraegerBerechnung:
    """Datenklasse für Trägerberechnungsergebnisse"""
    traeger_typ: str  # 'einfeld', 'durchlauf', 'krag'
    laenge: float  # m (Gesamtlänge oder Einzelfeld)
    streckenlast: float  # kN/m
    
    # Material
    emodul: float  # MPa (N/mm²)
    traegheitsmoment: float  # m⁴
    
    # Ergebnisse
    biegemoment_max: float = 0.0  # kNm
    durchbiegung_max: float = 0.0  # mm
    querkraft_max: float = 0.0  # kN
    
    # Für Durchlaufträger
    felder: List[float] = field(default_factory=list)  # Feldlängen in m
    max_feld_index: int = 0  # Index des Feldes mit max. Moment
    
    # Grenzwerte
    grenzdurchbiegung_l300: float = 0.0  # mm (L/300)
    grenzdurchbiegung_l250: float = 0.0  # mm (L/250)
    ausnutzung_l300: float = 0.0  # %

    def to_dict(self) -> dict:
        """Konvertiert Dataclass zu Dictionary für JSON-Serialisierung."""
        return asdict(self)


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
        traeger_typ='einfeld',
        laenge=laenge,
        streckenlast=streckenlast,
        emodul=emodul,
        traegheitsmoment=traegheitsmoment
    )
    
    # Maximales Biegemoment für Einfeldträger mit q
    # M_max = q × L² / 8
    result.biegemoment_max = (streckenlast * laenge**2) / 8.0
    
    # Maximale Querkraft
    # Q_max = q × L / 2
    result.querkraft_max = (streckenlast * laenge) / 2.0
    
    # Maximale Durchbiegung für Einfeldträger
    # δ_max = (5 × q × L⁴) / (384 × E × I)
    emodul_knm2 = emodul * 1000  # kN/m²
    
    result.durchbiegung_max = (
        (5 * streckenlast * laenge**4) / 
        (384 * emodul_knm2 * traegheitsmoment)
    ) * 1000
    
    # Grenzdurchbiegungen
    result.grenzdurchbiegung_l300 = (laenge * 1000) / 300
    result.grenzdurchbiegung_l250 = (laenge * 1000) / 250
    
    # Ausnutzung
    if result.grenzdurchbiegung_l300 > 0:
        result.ausnutzung_l300 = (
            result.durchbiegung_max / result.grenzdurchbiegung_l300
        ) * 100
    
    return result


def berechne_kragtraeger(
    laenge: float,
    streckenlast: float,
    emodul: float,
    traegheitsmoment: float
) -> TraegerBerechnung:
    """
    Berechnet einen Kragträger (einseitig eingespannt) mit Gleichstreckenlast.
    """
    result = TraegerBerechnung(
        traeger_typ='krag',
        laenge=laenge,
        streckenlast=streckenlast,
        emodul=emodul,
        traegheitsmoment=traegheitsmoment
    )
    
    # Maximales Biegemoment am Einspannpunkt
    result.biegemoment_max = (streckenlast * laenge**2) / 2.0
    
    # Maximale Querkraft
    result.querkraft_max = streckenlast * laenge
    
    # Maximale Durchbiegung am freien Ende
    emodul_knm2 = emodul * 1000
    
    result.durchbiegung_max = (
        (streckenlast * laenge**4) / 
        (8 * emodul_knm2 * traegheitsmoment)
    ) * 1000
    
    # Grenzdurchbiegungen (strenger für Kragträger)
    result.grenzdurchbiegung_l300 = (laenge * 1000) / 300
    result.grenzdurchbiegung_l200 = (laenge * 1000) / 200
    
    if result.grenzdurchbiegung_l200 > 0:
        result.ausnutzung_l300 = (
            result.durchbiegung_max / result.grenzdurchbiegung_l200
        ) * 100
    
    return result


def berechne_durchlaufträger(
    felder: List[float],
    streckenlast: float,
    emodul: float,
    traegheitsmoment: float
) -> TraegerBerechnung:
    """
    Berechnet einen Durchlaufträger mit Gleichstreckenlast.
    Unterstützt 2 oder 3 Felder.
    """
    n_felder = len(felder)
    
    if n_felder not in [2, 3]:
        raise ValueError("Nur 2- oder 3-Feld-Durchlaufträger werden unterstützt!")
    
    result = TraegerBerechnung(
        traeger_typ='durchlauf',
        laenge=sum(felder),
        streckenlast=streckenlast,
        emodul=emodul,
        traegheitsmoment=traegheitsmoment,
        felder=felder
    )
    
    emodul_knm2 = emodul * 1000
    
    # Längstes Feld finden
    max_L = max(felder)
    max_idx = felder.index(max_L)
    result.max_feld_index = max_idx
    
    if n_felder == 2:
        # 2-Feld-Träger
        result.biegemoment_max = streckenlast * max_L**2 / 8  # Stützmoment maßgebend
        result.querkraft_max = max(streckenlast * f / 2 for f in felder)
        reduction = 0.7
    else:
        # 3-Feld-Träger
        result.biegemoment_max = streckenlast * max_L**2 / 8  # Stützmoment
        result.querkraft_max = max(streckenlast * f / 2 for f in felder)
        reduction = 0.65
    
    # Durchbiegung (günstiger als Einfeldträger)
    result.durchbiegung_max = (
        (5 * streckenlast * max_L**4) / 
        (384 * emodul_knm2 * traegheitsmoment)
    ) * 1000 * reduction
    
    # Grenzdurchbiegungen
    result.grenzdurchbiegung_l300 = (max_L * 1000) / 300
    result.grenzdurchbiegung_l250 = (max_L * 1000) / 250
    
    if result.grenzdurchbiegung_l300 > 0:
        result.ausnutzung_l300 = (
            result.durchbiegung_max / result.grenzdurchbiegung_l300
        ) * 100
    
    return result


def get_traeger_typen() -> Dict[str, str]:
    """Gibt verfügbare Trägertypen zurück."""
    return {
        'einfeld': 'Einfeldträger (2 Auflager)',
        'krag': 'Kragträger (einseitig eingespannt)',
        'durchlauf': 'Durchlaufträger (2-3 Felder)'
    }


# Wrapper-Funktionen für app.py (Legacy-Support)
def calculate_bending_moment(L: float, w: float) -> float:
    return (w * L**2) / 8.0

def calculate_deflection(L: float, w: float, E: float, I: float) -> float:
    E_knm2 = E * 1000
    delta = (5 * w * L**4) / (384 * E_knm2 * I)
    return delta * 1000

def calculate_shear_force(L: float, w: float) -> float:
    return (w * L) / 2.0


# Materialien und Profile (Legacy)
def get_material_e_modul(material: str) -> float:
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
    ipe_profile = {
        "IPE 80": 80.1e-8, "IPE 100": 171e-8, "IPE 120": 318e-8,
        "IPE 140": 541e-8, "IPE 160": 869e-8, "IPE 180": 1320e-8,
        "IPE 200": 1940e-8, "IPE 220": 2770e-8, "IPE 240": 3890e-8,
        "IPE 270": 5790e-8, "IPE 300": 8360e-8, "IPE 330": 11770e-8,
        "IPE 360": 16270e-8, "IPE 400": 23130e-8, "IPE 450": 33740e-8,
        "IPE 500": 48200e-8, "IPE 550": 67120e-8, "IPE 600": 92080e-8,
    }
    return ipe_profile.get(profil, 1940e-8)

def format_ergebnis(result: TraegerBerechnung) -> str:
    output = []
    output.append("=" * 50)
    output.append("STATISCHE BERECHNUNG")
    output.append("=" * 50)
    output.append(f"Trägertyp: {result.traeger_typ}")
    output.append(f"Länge: {result.laenge:.2f} m")
    output.append(f"Streckenlast: {result.streckenlast:.2f} kN/m")
    output.append(f"E-Modul: {result.emodul:,.0f} MPa")
    output.append(f"Trägheitsmoment: {result.traegheitsmoment:.4e} m⁴")
    output.append("")
    output.append("Ergebnisse:")
    output.append(f"  Max. Biegemoment: {result.biegemoment_max:.2f} kNm")
    output.append(f"  Max. Querkraft: {result.querkraft_max:.2f} kN")
    output.append(f"  Max. Durchbiegung: {result.durchbiegung_max:.2f} mm")
    output.append("")
    output.append(f"Ausnutzung L/300: {result.ausnutzung_l300:.1f}%")
    output.append("=" * 50)
    return "\n".join(output)


if __name__ == "__main__":
    # Test
    print("🧪 Erweitertes Berechnungsmodul Test")
    print("=" * 50)
    
    # Einfeldträger
    print("\n1. Einfeldträger (6m):")
    result1 = berechne_einfeldtraeger(6.0, 5.0, 210000, 1940e-8)
    print(format_ergebnis(result1))
    
    # Kragträger
    print("\n2. Kragträger (3m):")
    result2 = berechne_kragtraeger(3.0, 5.0, 210000, 1940e-8)
    print(format_ergebnis(result2))
    
    # Durchlaufträger 2-Feld
    print("\n3. Durchlaufträger (4m + 5m):")
    result3 = berechne_durchlaufträger([4.0, 5.0], 5.0, 210000, 1940e-8)
    print(format_ergebnis(result3))
    
    # Durchlaufträger 3-Feld
    print("\n4. Durchlaufträger (4m + 5m + 4m):")
    result4 = berechne_durchlaufträger([4.0, 5.0, 4.0], 5.0, 210000, 1940e-8)
    print(format_ergebnis(result4))
    
    print("\n✅ Alle Berechnungen erfolgreich!")
