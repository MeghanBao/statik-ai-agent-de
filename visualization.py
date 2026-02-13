"""
statik-ai-agent-de
Visualisierungsmodul für Diagramme - Erweitert
Unterstützt: Einfeldträger, Kragträger, Durchlaufträger
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from typing import List, Optional

# Matplotlib Stil setzen
plt.style.use('seaborn-v0_8-whitegrid')


def plot_bending_moment(L: float, w: float, n_points: int = 100):
    """
    Erstellt Diagramm des Biegemomentenverlaufs (Einfeldträger).
    """
    x = np.linspace(0, L, n_points)
    M = (w * x * (L - x)) / 2
    
    M_max = (w * L**2) / 8
    x_max = L / 2
    
    fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
    ax.plot(x, M, 'b-', linewidth=2.5, label='Biegemoment M(x)')
    ax.plot(x_max, M_max, 'ro', markersize=10, label=f'M_max = {M_max:.2f} kNm')
    ax.fill_between(x, 0, M, alpha=0.3, color='blue')
    
    ax.set_xlabel('Position x [m]', fontsize=11)
    ax.set_ylabel('Biegemoment M [kNm]', fontsize=11)
    ax.set_title('Biegemomentenverlauf - Einfeldträger', fontsize=13, fontweight='bold')
    ax.legend(loc='upper right')
    ax.axhline(y=0, color='k', linewidth=0.8)
    ax.set_xlim(0, L)
    ax.set_ylim(0, M_max * 1.15)
    
    plt.tight_layout()
    return fig


def plot_bending_moment_krag(L: float, w: float, n_points: int = 100):
    """
    Erstellt Biegemomentenverlauf für Kragträger.
    """
    x = np.linspace(0, L, n_points)
    # M(x) = -w * x² / 2 (negativ am Einspannpunkt)
    M = -w * x**2 / 2
    
    M_max = w * L**2 / 2  # Am Einspannpunkt (x=0)
    
    fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
    
    # Momentenlinie (negative Werte nach oben darstellen)
    ax.plot(x, -M, 'r-', linewidth=2.5, label='|M(x)|')
    ax.fill_between(x, 0, -M, alpha=0.3, color='red')
    
    # Einspannung markieren
    ax.axvline(x=0, color='black', linewidth=3, label='Einspannung')
    ax.plot(0, M_max, 'ro', markersize=10, label=f'|M_max| = {M_max:.2f} kNm')
    
    ax.set_xlabel('Position x [m] (vom freien Ende)', fontsize=11)
    ax.set_ylabel('Biegemoment |M| [kNm]', fontsize=11)
    ax.set_title('Biegemomentenverlauf - Kragträger', fontsize=13, fontweight='bold')
    ax.legend(loc='upper right')
    ax.set_xlim(0, L)
    ax.set_ylim(0, M_max * 1.15)
    
    plt.tight_layout()
    return fig


def plot_bending_moment_durchlauf(felder: List[float], w: float, n_points: int = 50):
    """
    Erstellt Biegemomentenverlauf für Durchlaufträger (2 oder 3 Felder).
    """
    x_total = np.array([])
    M_total = np.array([])
    
    x_pos = 0
    max_moments = []
    
    for i, L in enumerate(felder):
        x = np.linspace(0, L, n_points)
        
        if i == 0:
            # Erstes Feld: M+ in Feldmitte, negatives Moment am Auflager
            x_local = x - L/2
            M = w * (L**2/8 - x_local**2/2)
        elif i == len(felder) - 1:
            # Letztes Feld
            x_local = x - L/2
            M = w * (L**2/8 - x_local**2/2)
        else:
            # Mittlere Felder
            x_local = x - L/2
            M = w * (L**2/10 - x_local**2/2)
        
        x_total = np.append(x_total, x + x_pos)
        M_total = np.append(M_total, M)
        
        max_moments.append((x_pos + L/2, np.max(M)))
        x_pos += L
    
    M_max = max(max_moments, key=lambda x: x[1])
    
    fig, ax = plt.subplots(figsize=(12, 5), dpi=100)
    
    # Positive und negative Momente unterschiedlich färben
    ax.plot(x_total, M_total, 'b-', linewidth=2.5, label='Biegemoment M(x)')
    
    # Nulllinie
    ax.axhline(y=0, color='k', linewidth=0.8)
    
    # Auflager markieren
    x_auflager = np.cumsum([0] + felder[:-1])
    for x_a in x_auflager:
        ax.axvline(x=x_a, color='gray', linestyle='--', alpha=0.5)
    
    # Max. Moment markieren
    ax.plot(M_max[0], M_max[1], 'ro', markersize=10, label=f'M_max = {M_max[1]:.2f} kNm')
    
    ax.fill_between(x_total, 0, M_total, where=(M_total >= 0), alpha=0.3, color='blue', label='Positive Momente')
    ax.fill_between(x_total, 0, M_total, where=(M_total < 0), alpha=0.3, color='red', label='Negative Momente')
    
    ax.set_xlabel('Position x [m]', fontsize=11)
    ax.set_ylabel('Biegemoment M [kNm]', fontsize=11)
    ax.set_title(f'Biegemomentenverlauf - Durchlaufträger ({len(felder)} Felder)', fontsize=13, fontweight='bold')
    ax.legend(loc='upper right', fontsize=8)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_deflection(L: float, w: float, E: float, I: float, traeger_typ: str = 'einfeld', felder: Optional[List[float]] = None, exaggeration: float = 100):
    """
    Erstellt Biegelinie mit optionaler Anpassung für verschiedene Trägertypen.
    """
    E_knm2 = E * 1000
    
    if traeger_typ == 'einfeld':
        x = np.linspace(0, L, 100)
        delta = (w * x / (24 * E_knm2 * I)) * (L**3 - 2*L*x**2 + x**3) * 1000
        delta_max = 5 * w * L**4 / (384 * E_knm2 * I) * 1000
        x_max = L / 2
        
    elif traeger_typ == 'krag':
        x = np.linspace(0, L, 100)
        delta = w * x**4 / (8 * E_knm2 * I) * 1000
        delta_max = w * L**4 / (8 * E_knm2 * I) * 1000
        x_max = L
        
    elif traeger_typ == 'durchlauf' and felder:
        x = np.linspace(0, felder[0], 50)
        delta = (w * x / (24 * E_knm2 * I)) * (felder[0]**3 - 2*felder[0]*x**2 + x**3) * 1000
        delta_max = delta.max()
        x_max = x[np.argmax(delta)]
        L = sum(felder)
    else:
        # Fallback
        return plot_deflection(L, w, E, I, 'einfeld', None, exaggeration)
    
    fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
    
    ax.plot(x, delta * exaggeration, 'g-', linewidth=2.5, label=f'Biegelinie ({exaggeration}× übertrieben)')
    ax.axhline(y=0, color='k', linewidth=1.5, linestyle='--', label='Ursprüngliche Lage')
    ax.plot(x_max, delta_max * exaggeration, 'ro', markersize=10, label=f'δ_max = {delta_max:.2f} mm')
    ax.fill_between(x, 0, delta * exaggeration, alpha=0.3, color='green')
    
    ax.set_xlabel('Position x [m]', fontsize=11)
    ax.set_ylabel(f'Durchbiegung δ [mm] ({exaggeration}× übertrieben)', fontsize=11)
    ax.set_title(f'Biegelinie - {traeger_typ.capitalize()}träger', fontsize=13, fontweight='bold')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    
    info_text = f'Tatsächliche max. Durchbiegung: {delta_max:.2f} mm'
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes, fontsize=9,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    return fig


def plot_comparison_chart(L: float, w: float, E: float, I: float):
    """
    Erstellt Vergleichs-Chart mit verschiedenen Profilen.
    """
    from calculation import get_ipe_traegheitsmoment
    
    profile = ['IPE 180', 'IPE 200', 'IPE 220', 'IPE 240', 'IPE 270', 'IPE 300']
    durchbiegungen = []
    
    E_knm2 = E * 1000
    
    for profil in profile:
        I_profil = get_ipe_traegheitsmoment(profil)
        delta = 5 * w * L**4 / (384 * E_knm2 * I_profil) * 1000
        durchbiegungen.append(delta)
    
    grenzwert = L * 1000 / 300
    
    fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
    bars = ax.bar(profile, durchbiegungen, color='steelblue', edgecolor='black', alpha=0.8)
    ax.axhline(y=grenzwert, color='red', linestyle='--', linewidth=2, label=f'Grenzwert L/300 = {grenzwert:.1f} mm')
    
    for i, profil in enumerate(profile):
        if abs(get_ipe_traegheitsmoment(profil) - I) < 1e-8:
            bars[i].set_color('orange')
    
    ax.set_xlabel('Profil', fontsize=11)
    ax.set_ylabel('Max. Durchbiegung [mm]', fontsize=11)
    ax.set_title('Durchbiegungsvergleich verschiedener IPE-Profile', fontsize=13, fontweight='bold')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3, axis='y')
    
    for i, delta in enumerate(durchbiegungen):
        ax.text(i, delta + 0.5, f'{delta:.1f} mm', ha='center', fontsize=9)
    
    plt.tight_layout()
    return fig


if __name__ == "__main__":
    print("🎨 Visualisierungsmodul Test - Erweitert")
    print("=" * 50)
    
    from calculation import berechne_einfeldtraeger, berechne_kragtraeger, berechne_durchlaufträger
    
    print("\n1. Einfeldträger...")
    fig1 = plot_bending_moment(6.0, 5.0)
    
    print("\n2. Kragträger...")
    fig2 = plot_bending_moment_krag(3.0, 5.0)
    
    print("\n3. Durchlaufträger (2 Felder)...")
    fig3 = plot_bending_moment_durchlauf([4.0, 5.0], 5.0)
    
    print("\n4. Biegelinie (Einfeldträger)...")
    fig4 = plot_deflection(6.0, 5.0, 210000, 1940e-8)
    
    print("\n✅ Alle Diagramme erstellt!")
