def calculate_bending_moment(L, w):
    """
    Berechnet das maximale Biegemoment für einen Einfeldträger unter Gleichlast.
    M = (w * L^2) / 8
    """
    return (w * L**2) / 8

def calculate_deflection(L, w, E, I):
    """
    Berechnet die maximale Durchbiegung für einen Einfeldträger unter Gleichlast.
    delta = (5 * w * L^4) / (384 * E * I)
    
    L in m
    w in kN/m
    E in MPa (N/mm^2) -> Umrechnung in kN/m^2: * 1000
    I in m^4
    """
    # E in kN/m^2 umrechnen
    E_kNm2 = E * 1000
    
    delta = (5 * w * L**4) / (384 * E_kNm2 * I)
    return delta * 1000  # Rückgabe in mm
