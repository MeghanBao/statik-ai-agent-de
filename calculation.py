"""
statik-ai-agent-de
Berechnungsmodul - Erweitert
NEU: Rahmenberechnung, Plattenberechnung
"""

import numpy as np
from dataclasses import dataclass, field, asdict
from typing import List, Tuple, Optional, Dict

@dataclass
class TraegerBerechnung:
    """Datenklasse für Trägerberechnungsergebnisse"""
    traeger_typ: str
    laenge: float
    streckenlast: float
    
    # Material
    emodul: float
    traegheitsmoment: float
    
    # Ergebnisse
    biegemoment_max: float = 0.0
    durchbiegung_max: float = 0.0
    querkraft_max: float = 0.0
    
    # Für Durchlaufträger
    felder: List[float] = field(default_factory=list)
    max_feld_index: int = 0
    
    # Grenzwerte
    grenzdurchbiegung_l300: float = 0.0
    grenzdurchbiegung_l250: float = 0.0
    ausnutzung_l300: float = 0.0
    
    # Für Kragträger
    grenzdurchbiegung_l200: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RahmenBerechnung:
    """Datenklasse für Rahmenberechnung"""
    rahmen_typ: str  # 'eingeschossig', 'zweischossig'
    breite: float  # m
    hoehe: float  # m
    streckenlast: float  # kN/m auf Riegel
    
    # Material
    emodul: float
    traegheitsmoment: float  # m⁴
    
    # Ergebnisse
    schwingungsmoment: float = 0.0  # kNm (Stütze)
    riegelmoment: float = 0.0  # kNm
    stuetzkraft_vert: float = 0.0  # kN
    stuetzkraft_horiz: float = 0.0  # kN (Kopfband)
    
    # Durchbiegung
    durchbiegung_riegel: float = 0.0  # mm
    grenzdurchbiegung: float = 0.0
    ausnutzung: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class PlatteBerechnung:
    """Datenklasse für Plattenberechnung"""
    platten_typ: str  # 'einfeld', 'durchlauf'
    laenge_x: float  # m
    laenge_y: float  # m
    last: float  # kN/m²
    
    # Material
    emodul: float
    dicke: float  # m
    
    # Ergebnisse
    max_moment_x: float = 0.0  # kNm/m
    max_moment_y: float = 0.0  # kNm/m
    max_durchbiegung: float = 0.0  # mm
    bewehrung_x: float = 0.0  # cm²/m
    bewehrung_y: float = 0.0  # cm²/m
    grenzdurchbiegung: float = 0.0
    ausnutzung: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


# ==================== TRÄGER BERECHNUNGEN ====================

def berechne_einfeldtraeger(laenge: float, streckenlast: float, emodul: float, traegheitsmoment: float) -> TraegerBerechnung:
    """Berechnet einen Einfeldträger mit Gleichstreckenlast."""
    result = TraegerBerechnung('einfeld', laenge, streckenlast, emodul, traegheitsmoment)
    
    result.biegemoment_max = (streckenlast * laenge**2) / 8.0
    result.querkraft_max = (streckenlast * laenge) / 2.0
    
    emodul_knm2 = emodul * 1000
    result.durchbiegung_max = (5 * streckenlast * laenge**4) / (384 * emodul_knm2 * traegheitsmoment) * 1000
    
    result.grenzdurchbiegung_l300 = (laenge * 1000) / 300
    result.grenzdurchbiegung_l250 = (laenge * 1000) / 250
    
    if result.grenzdurchbiegung_l300 > 0:
        result.ausnutzung_l300 = (result.durchbiegung_max / result.grenzdurchbiegung_l300) * 100
    
    return result


def berechne_kragtraeger(laenge: float, streckenlast: float, emodul: float, traegheitsmoment: float) -> TraegerBerechnung:
    """Berechnet einen Kragträger."""
    result = TraegerBerechnung('krag', laenge, streckenlast, emodul, traegheitsmoment)
    
    result.biegemoment_max = (streckenlast * laenge**2) / 2.0
    result.querkraft_max = streckenlast * laenge
    
    emodul_knm2 = emodul * 1000
    result.durchbiegung_max = (streckenlast * laenge**4) / (8 * emodul_knm2 * traegheitsmoment) * 1000
    
    result.grenzdurchbiegung_l300 = (laenge * 1000) / 300
    result.grenzdurchbiegung_l200 = (laenge * 1000) / 200
    
    if result.grenzdurchbiegung_l200 > 0:
        result.ausnutzung_l300 = (result.durchbiegung_max / result.grenzdurchbiegung_l200) * 100
    
    return result


def berechne_durchlauftrager(felder: List[float], streckenlast: float, emodul: float, traegheitsmoment: float) -> TraegerBerechnung:
    """Berechnet einen Durchlaufträger (2-3 Felder)."""
    n_felder = len(felder)
    if n_felder not in [2, 3]:
        raise ValueError("Nur 2- oder 3-Feld-Durchlaufträger werden unterstützt!")
    
    result = TraegerBerechnung('durchlauf', sum(felder), streckenlast, emodul, traegheitsmoment, felder=felder)
    
    max_L = max(felder)
    max_idx = felder.index(max_L)
    result.max_feld_index = max_idx
    
    reduction = 0.7 if n_felder == 2 else 0.65
    
    result.biegemoment_max = streckenlast * max_L**2 / 8
    result.querkraft_max = max(streckenlast * f / 2 for f in felder)
    
    emodul_knm2 = emodul * 1000
    result.durchbiegung_max = (5 * streckenlast * max_L**4) / (384 * emodul_knm2 * traegheitsmoment) * 1000 * reduction
    
    result.grenzdurchbiegung_l300 = (max_L * 1000) / 300
    result.grenzdurchbiegung_l250 = (max_L * 1000) / 250
    
    if result.grenzdurchbiegung_l300 > 0:
        result.ausnutzung_l300 = (result.durchbiegung_max / result.grenzdurchbiegung_l300) * 100
    
    return result


# ==================== RAHMEN BERECHNUNGEN ====================

def berechne_rahmen_eingeschossig(breite: float, hoehe: float, streckenlast: float, 
                                   emodul: float, traegheitsmoment: float) -> RahmenBerechnung:
    """
    Berechnet einen eingeschossigen Rahmen mit geneigtem Dach.
    Vereinfachte Berechnung nach der Starrrahmentheorie.
    """
    result = RahmenBerechnung(
        rahmen_typ='eingeschossig',
        breite=breite,
        hoehe=hoehe,
        streckenlast=streckenlast,
        emodul=emodul,
        traegheitsmoment=traegheitsmoment
    )
    
    # Vereinfachte Rahmenberechnung
    # Annahme: 45° Dachneigung für vereinfachte Statik
    alpha = np.radians(30)  # 30° Dachneigung
    
    # Stütze: Biegemoment am Kopf (näherungsweise)
    # M = q * L² / 12 für eingespannte Stütze
    result.schwingungsmoment = (streckenlast * breite**2) / 12
    
    # Riegel: Biegemoment (Einspannung an beiden Seiten)
    result.riegelmoment = (streckenlast * breite**2) / 24
    
    # Auflagerkräfte
    # Vertikal: q * L / 2 pro Stütze
    result.stuetzkraft_vert = (streckenlast * breite) / 2
    
    # Horizontal (aus Dachschräge)
    # Vereinfacht: Horizontalkraft aus Dachneigung
    result.stuetzkraft_horiz = (streckenlast * breite * np.tan(alpha)) / 4
    
    # Durchbiegung des Riegels
    # Vereinfacht wie Einfeldträger
    emodul_knm2 = emodul * 1000
    result.durchbiegung_riegel = (5 * streckenlast * breite**4) / (384 * emodul_knm2 * traegheitsmoment) * 1000
    
    # Grenzdurchbiegung
    result.grenzdurchbiegung = (breite * 1000) / 300
    
    if result.grenzdurchbiegung > 0:
        result.ausnutzung = (result.durchbiegung_riegel / result.grenzdurchbiegung) * 100
    
    return result


def berechne_rahmen_zweischossig(breite: float, hoehe_eg: float, hoehe_og: float,
                                  streckenlast: float, emodul: float, 
                                  traegheitsmoment: float) -> RahmenBerechnung:
    """Berechnet einen zweigeschossigen Rahmen."""
    result = RahmenBerechnung(
        rahmen_typ='zweischossig',
        breite=breite,
        hoehe=hoehe_eg + hoehe_og,
        streckenlast=streckenlast,
        emodul=emodul,
        traegheitsmoment=traegheitsmoment
    )
    
    # Zweigeschossig: Größere Momente durch Auflast
    # Vereinfacht: Summe aus EG + OG
    gesamt_hoehe = hoehe_eg + hoehe_og
    
    # Stützmomente (größer wegen 2 Geschosse)
    result.schwingungsmoment = (streckenlast * breite**2) / 10
    
    # Riegelmomente
    result.riegelmoment = (streckenlast * breite**2) / 20
    
    # Auflagerkräfte
    result.stuetzkraft_vert = (streckenlast * breite) / 2 * 2  # 2 Geschosse
    result.stuetzkraft_horiz = (streckenlast * breite) / 20
    
    # Durchbiegung (größere Spannweite)
    emodul_knm2 = emodul * 1000
    result.durchbiegung_riegel = (5 * streckenlast * breite**4) / (384 * emodul_knm2 * traegheitsmoment) * 1000
    
    result.grenzdurchbiegung = (breite * 1000) / 300
    
    if result.grenzdurchbiegung > 0:
        result.ausnutzung = (result.durchbiegung_riegel / result.grenzdurchbiegung) * 100
    
    return result


# ==================== PLATTEN BERECHNUNGEN ====================

def berechne_platte_einfeld(laenge_x: float, laenge_y: float, last: float,
                            emodul: float, dicke: float) -> PlatteBerechnung:
    """
    Berechnet eine einfeld gelagerte Platte.
    Vereinfacht nach Lorentz/Navier für isotrop gelagerte Platten.
    """
    result = PlatteBerechnung(
        platten_typ='einfeld',
        laenge_x=laenge_x,
        laenge_y=laenge_y,
        last=last,
        emodul=emodul,
        dicke=dicke
    )
    
    # Seitenverhältnis
    lambda_seite = laenge_y / laenge_x if laenge_x > 0 else 1.0
    
    # Biegesteifigkeit D
    # Für Beton: E * h³ / (12 * (1 - nu²)) mit nu = 0.2
    nu = 0.2  # Querdehnzahl Beton
    D = (emodul * 1000 * dicke**3) / (12 * (1 - nu**2))
    
    # Max. Biegemomente (vereinfacht)
    # Für λ > 1: Haupttragrichtung in x
    if lambda_seite >= 1:
        # Platte in x-Richtung bemessen
        result.max_moment_x = (last * laenge_x**2) / 8
        result.max_moment_y = result.max_moment_x * 0.5  # Querverteilung
    else:
        # Platte in y-Richtung bemessen
        result.max_moment_y = (last * laenge_y**2) / 8
        result.max_moment_x = result.max_moment_y * 0.5
    
    # Max. Durchbiegung
    # w_max = (16 * q * a⁴) / (π⁶ * D) * Sum(...) - vereinfacht
    k_deflection = 0.00406  # Für allseits gelagerte Platte
    result.max_durchbiegung = k_deflection * (last * 1000 * laenge_x**4) / D * 1000  # in mm
    
    # Grenzdurchbiegung: L/250 für Platten
    result.grenzdurchbiegung = (laenge_x * 1000) / 250
    
    if result.grenzdurchbiegung > 0:
        result.ausnutzung = (result.max_durchbiegung / result.grenzdurchbiegung) * 100
    
    # Bewehrung (vereinfacht nach DIN EN 1992)
    # M / (z * f_y) mit z ≈ 0.9 * h
    f_yk = 500  # Betonstahl B500
    gamma_s = 1.15
    f_yd = f_yk / gamma_s
    
    z_x = 0.9 * dicke * 1000  # in mm
    z_y = 0.9 * dicke * 1000
    
    # Erforderliche Bewehrung in cm²/m
    result.bewehrung_x = (result.max_moment_x * 1e6) / (z_x * f_yd) / 100  # cm²/m
    result.bewehrung_y = (result.max_moment_y * 1e6) / (z_y * f_yd) / 100
    
    return result


def berechne_platte_durchlauf(laenge_x: float, laenge_y: float, last: float,
                               emodul: float, dicke: float, felder: int = 2) -> PlatteBerechnung:
    """Berechnet eine durchlaufende Platte (2-4 Felder)."""
    result = PlatteBerechnung(
        platten_typ='durchlauf',
        laenge_x=laenge_x,
        laenge_y=laenge_y,
        last=last,
        emodul=emodul,
        dicke=dicke
    )
    
    # Durchlaufplatte: Günstigere Schnittgrößen
    # Reduktionsfaktor je nach Feldanzahl
    reduction = {2: 0.7, 3: 0.65, 4: 0.6}.get(felder, 0.65)
    
    # Basisberechnung wie Einfeld
    einfeld = berechne_platte_einfeld(laenge_x, laenge_y, last, emodul, dicke)
    
    # Reduzierte Momente
    result.max_moment_x = einfeld.max_moment_x * reduction
    result.max_moment_y = einfeld.max_moment_y * reduction
    
    # Durchbiegung (günstiger)
    result.max_durchbiegung = einfeld.max_durchbiegung * reduction
    
    # Grenzdurchbiegung
    result.grenzdurchbiegung = (laenge_x * 1000) / 250
    
    if result.grenzdurchbiegung > 0:
        result.ausnutzung = (result.max_durchbiegung / result.grenzdurchbiegung) * 100
    
    # Bewehrung (reduziert)
    f_yk = 500
    gamma_s = 1.15
    f_yd = f_yk / gamma_s
    z_x = 0.9 * dicke * 1000
    
    result.bewehrung_x = (result.max_moment_x * 1e6) / (z_x * f_yd) / 100
    result.bewehrung_y = (result.max_moment_y * 1e6) / (z_x * f_yd) / 100
    
    return result


# ==================== HILFSFUNKTIONEN ====================

def get_traeger_typen() -> Dict[str, str]:
    return {
        'einfeld': 'Einfeldträger (2 Auflager)',
        'krag': 'Kragträger (einseitig eingespannt)',
        'durchlauf': 'Durchlaufträger (2-3 Felder)'
    }


def get_rahmen_typen() -> Dict[str, str]:
    return {
        'eingeschossig': 'Eingeschossiger Rahmen mit Pultdach',
        'zweischossig': 'Zweigeschossiger Rahmen'
    }


def get_platten_typen() -> Dict[str, str]:
    return {
        'einfeld': 'Einfeldplatte (allseitig gelagert)',
        'durchlauf': 'Durchlaufplatte (2-4 Felder)'
    }


def calculate_bending_moment(L: float, w: float) -> float:
    return (w * L**2) / 8.0


def calculate_deflection(L: float, w: float, E: float, I: float) -> float:
    E_knm2 = E * 1000
    delta = (5 * w * L**4) / (384 * E_knm2 * I)
    return delta * 1000


def calculate_shear_force(L: float, w: float) -> float:
    return (w * L) / 2.0


def get_material_e_modul(material: str) -> float:
    materialien = {
        "Stahl (S235)": 210000,
        "Stahl (S355)": 210000,
        "Beton C20/25": 30000,
        "Beton C30/37": 33000,
        "Beton C35/45": 34000,
        "Holz (Fichte)": 11000,
        "Holz (Tanne)": 11000,
        "Holz (Eiche)": 12000,
        "Holz (BSH)": 14000,
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


def format_ergebnis(result) -> str:
    output = []
    output.append("=" * 50)
    output.append("STATISCHE BERECHNUNG")
    output.append("=" * 50)
    
    if isinstance(result, TraegerBerechnung):
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
        
    elif isinstance(result, RahmenBerechnung):
        output.append(f"Rahmentyp: {result.rahmen_typ}")
        output.append(f"Breite: {result.breite:.2f} m")
        output.append(f"Höhe: {result.hoehe:.2f} m")
        output.append(f"Streckenlast: {result.streckenlast:.2f} kN/m")
        output.append("")
        output.append("Ergebnisse:")
        output.append(f"  Stützmoment: {result.schwingungsmoment:.2f} kNm")
        output.append(f"  Riegelmoment: {result.riegelmoment:.2f} kNm")
        output.append(f"  Vert. Auflagerkraft: {result.stuetzkraft_vert:.2f} kN")
        output.append(f"  Horiz. Auflagerkraft: {result.stuetzkraft_horiz:.2f} kN")
        output.append(f"  Durchbiegung: {result.durchbiegung_riegel:.2f} mm")
        output.append("")
        output.append(f"Ausnutzung: {result.ausnutzung:.1f}%")
        
    elif isinstance(result, PlatteBerechnung):
        output.append(f"Platventyp: {result.platten_typ}")
        output.append(f"Abmessungen: {result.laenge_x:.2f} x {result.laenge_y:.2f} m")
        output.append(f"Plattendicke: {result.dicke*1000:.0f} mm")
        output.append(f"Flächenlast: {result.last:.2f} kN/m²")
        output.append("")
        output.append("Ergebnisse:")
        output.append(f"  Max. Moment x: {result.max_moment_x:.2f} kNm/m")
        output.append(f"  Max. Moment y: {result.max_moment_y:.2f} kNm/m")
        output.append(f"  Durchbiegung: {result.max_durchbiegung:.2f} mm")
        output.append(f"  Bewehrung x: {result.bewehrung_x:.2f} cm²/m")
        output.append(f"  Bewehrung y: {result.bewehrung_y:.2f} cm²/m")
        output.append("")
        output.append(f"Ausnutzung: {result.ausnutzung:.1f}%")
    
    output.append("=" * 50)
    return "\n".join(output)


if __name__ == "__main__":
    print("=" * 50)
    print("Erweitertes Berechnungsmodul Test")
    print("=" * 50)
    
    # Test Rahmen
    print("\n1. Eingeschossiger Rahmen (8m x 4m):")
    r1 = berechne_rahmen_eingeschossig(8.0, 4.0, 5.0, 210000, 1940e-8)
    print(format_ergebnis(r1))
    
    # Test Platte
    print("\n2. Einfeldplatte (6m x 4m):")
    p1 = berechne_platte_einfeld(6.0, 4.0, 5.0, 33000, 0.20)
    print(format_ergebnis(p1))
    
    # Test Durchlaufplatte
    print("\n3. Durchlaufplatte (3 Felder):")
    p2 = berechne_platte_durchlauf(5.0, 4.0, 5.0, 33000, 0.20, 3)
    print(format_ergebnis(p2))
    
    print("\n✓ Alle Berechnungen erfolgreich!")
