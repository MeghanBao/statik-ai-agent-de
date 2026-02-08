"""
statik-ai-agent-de
Visualisierungsmodul für Diagramme
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# Matplotlib Stil setzen
plt.style.use('seaborn-v0_8-whitegrid')


def plot_bending_moment(L: float, w: float, n_points: int = 100):
    """
    Erstellt Diagramm des Biegemomentenverlaufs.
    
    Args:
        L: Trägerlänge in m
        w: Streckenlast in kN/m
        n_points: Anzahl der Punkte für die Kurve
        
    Returns:
        matplotlib Figure
    """
    # Positionen entlang des Trägers
    x = np.linspace(0, L, n_points)
    
    # Biegemoment für Einfeldträger mit Gleichstreckenlast
    # M(x) = (w * L / 2) * x - (w * x^2 / 2)
    # = w * x * (L - x) / 2
    M = (w * x * (L - x)) / 2
    
    # Maximalwerte
    M_max = (w * L**2) / 8
    x_max = L / 2
    
    # Plot erstellen
    fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
    
    # Biegemomentenlinie
    ax.plot(x, M, 'b-', linewidth=2.5, label='Biegemoment M(x)')
    
    # Maximales Moment markieren
    ax.plot(x_max, M_max, 'ro', markersize=10, label=f'M_max = {M_max:.2f} kNm')
    
    # Füllen des Diagramms
    ax.fill_between(x, 0, M, alpha=0.3, color='blue')
    
    # Achsen und Beschriftung
    ax.set_xlabel('Position x [m]', fontsize=11)
    ax.set_ylabel('Biegemoment M [kNm]', fontsize=11)
    ax.set_title('Biegemomentenverlauf - Einfeldträger mit Gleichstreckenlast', fontsize=13, fontweight='bold')
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # Null-Linie
    ax.axhline(y=0, color='k', linewidth=0.8)
    
    # Achsenlimits
    ax.set_xlim(0, L)
    ax.set_ylim(0, M_max * 1.15)
    
    # Werte an den Auflagern und Mitte
    ax.text(0.02, 0.5, f'M = 0', fontsize=9, verticalalignment='bottom')
    ax.text(x_max, M_max + 0.05 * M_max, f'M_max\n{M_max:.2f} kNm', 
            fontsize=9, ha='center', fontweight='bold', color='red')
    ax.text(L - 0.1, 0.5, f'M = 0', fontsize=9, ha='right', verticalalignment='bottom')
    
    plt.tight_layout()
    return fig


def plot_deflection(L: float, w: float, E: float, I: float, n_points: int = 100):
    """
    Erstellt Diagramm der Biegelinie (Durchbiegung).
    
    Args:
        L: Trägerlänge in m
        w: Streckenlast in kN/m
        E: E-Modul in MPa (N/mm²)
        I: Trägheitsmoment in m⁴
        n_points: Anzahl der Punkte für die Kurve
        
    Returns:
        matplotlib Figure
    """
    # Positionen entlang des Trägers
    x = np.linspace(0, L, n_points)
    
    # Durchbiegung für Einfeldträger
    # δ(x) = (w * x / (24 * E * I)) * (L³ - 2*L*x² + x³)
    # Umrechnung E in kN/m²
    E_knm2 = E * 1000
    
    delta = (w * x / (24 * E_knm2 * I)) * (L**3 - 2*L*x**2 + x**3)
    
    # Maximale Durchbiegung (in Feldmitte)
    delta_max = (5 * w * L**4) / (384 * E_knm2 * I)
    x_max = L / 2
    
    # Verhältnis für Darstellung
    # Die Durchbiegung ist sehr klein im Vergleich zur Länge
    # Wir zeigen sie vergrößert an (übertrieben)
    exaggeration = 100  # 100x übertrieben für Sichtbarkeit
    
    # Plot erstellen
    fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
    
    # Biegelinie (vergrößert dargestellt)
    ax.plot(x, delta * exaggeration * 1000, 'g-', linewidth=2.5, label=f'Biegelinie (100× übertrieben)')
    
    # Ursprüngliche Trägerlinie
    ax.axhline(y=0, color='k', linewidth=1.5, linestyle='--', label='Ursprüngliche Lage')
    
    # Maximale Durchbiegung markieren
    ax.plot(x_max, delta_max * exaggeration * 1000, 'ro', markersize=10, 
            label=f'δ_max = {delta_max*1000:.2f} mm (tatsächlich)')
    
    # Füllen des Diagramms
    ax.fill_between(x, 0, delta * exaggeration * 1000, alpha=0.3, color='green')
    
    # Achsen und Beschriftung
    ax.set_xlabel('Position x [m]', fontsize=11)
    ax.set_ylabel(f'Durchbiegung δ [mm] ({exaggeration}× übertrieben)', fontsize=11)
    ax.set_title('Biegelinie - Einfeldträger (Maßstab übertrieben für Darstellung)', fontsize=13, fontweight='bold')
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # Achsenlimits
    ax.set_xlim(0, L)
    ax.set_ylim(-0.5, delta_max * exaggeration * 1000 * 1.2)
    
    # Info-Box
    info_text = f'Tatsächliche max. Durchbiegung: {delta_max*1000:.2f} mm\n'
    info_text += f'Verhältnis δ/L = 1/{L/(delta_max*1000):.0f}'
    
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes, fontsize=9,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    return fig


def plot_comparison_chart(L: float, w: float, E: float, I: float):
    """
    Erstellt einen Vergleichs-Chart mit verschiedenen Profilen.
    
    Args:
        L: Trägerlänge in m
        w: Streckenlast in kN/m
        E: E-Modul in MPa
        I: Aktuelles Trägheitsmoment
        
    Returns:
        matplotlib Figure
    """
    # Verschiedene Profile vergleichen
    from calculation import get_ipe_traegheitsmoment
    
    profile = ['IPE 180', 'IPE 200', 'IPE 220', 'IPE 240', 'IPE 270', 'IPE 300']
    durchbiegungen = []
    
    E_knm2 = E * 1000
    
    for profil in profile:
        I_profil = get_ipe_traegheitsmoment(profil)
        delta = (5 * w * L**4) / (384 * E_knm2 * I_profil) * 1000  # in mm
        durchbiegungen.append(delta)
    
    # Grenzwert L/300
    grenzwert = (L * 1000) / 300
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
    
    # Balkendiagramm
    bars = ax.bar(profile, durchbiegungen, color='steelblue', edgecolor='black', alpha=0.8)
    
    # Grenzwert-Linie
    ax.axhline(y=grenzwert, color='red', linestyle='--', linewidth=2, label=f'Grenzwert L/300 = {grenzwert:.1f} mm')
    
    # Aktuelles Profil hervorheben
    aktuelles_I = I
    for i, profil in enumerate(profile):
        if abs(get_ipe_traegheitsmoment(profil) - aktuelles_I) < 1e-8:
            bars[i].set_color('orange')
            bars[i].set_label('Aktuelles Profil')
    
    # Beschriftung
    ax.set_xlabel('Profil', fontsize=11)
    ax.set_ylabel('Max. Durchbiegung [mm]', fontsize=11)
    ax.set_title('Durchbiegungsvergleich verschiedener IPE-Profile', fontsize=13, fontweight='bold')
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Werte über Balken
    for i, (profil, delta) in enumerate(zip(profile, durchbiegungen)):
        ax.text(i, delta + 0.5, f'{delta:.1f} mm', ha='center', fontsize=9)
    
    plt.tight_layout()
    return fig


def create_summary_diagram(result):
    """
    Erstellt ein zusammenfassendes Diagramm mit allen Ergebnissen.
    
    Args:
        result: TraegerBerechnung Objekt
        
    Returns:
        matplotlib Figure
    """
    fig = plt.figure(figsize=(12, 8), dpi=100)
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
    
    # Systemskizze
    ax1 = fig.add_subplot(gs[0, :])
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 3)
    ax1.axis('off')
    ax1.set_title('Systemübersicht', fontsize=14, fontweight='bold')
    
    # Träger
    ax1.plot([1, 9], [1.5, 1.5], 'k-', linewidth=4)
    # Auflager
    ax1.plot([1, 1], [1.5, 1.2], 'k-', linewidth=3)
    ax1.plot([0.8, 1.2], [1.2, 1.2], 'k-', linewidth=3)
    ax1.plot([9, 9], [1.5, 1.2], 'k-', linewidth=3)
    ax1.plot([8.8, 9.2], [1.2, 1.2], 'k-', linewidth=3)
    # Last
    for i in range(2, 9):
        ax1.arrow(i, 2.5, 0, -0.5, head_width=0.2, head_length=0.1, fc='red', ec='red')
    ax1.text(5, 2.7, f'q = {result.streckenlast:.1f} kN/m', ha='center', fontsize=11, color='red')
    ax1.text(5, 0.8, f'L = {result.laenge:.1f} m', ha='center', fontsize=11)
    
    # Ergebnis-Boxen
    box_props = dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.8)
    ax1.text(2.5, 2.2, f'M_max = {result.biegemoment_max:.2f} kNm', fontsize=10, bbox=box_props)
    ax1.text(7.5, 2.2, f'δ_max = {result.durchbiegung_max:.2f} mm', fontsize=10, bbox=box_props)
    
    # Biegemomentenverlauf (klein)
    ax2 = fig.add_subplot(gs[1, 0])
    x = np.linspace(0, result.laenge, 50)
    M = (result.streckenlast * x * (result.laenge - x)) / 2
    ax2.plot(x, M, 'b-', linewidth=2)
    ax2.fill_between(x, 0, M, alpha=0.3, color='blue')
    ax2.set_title('Biegemoment', fontsize=11)
    ax2.set_xlabel('x [m]')
    ax2.set_ylabel('M [kNm]')
    ax2.grid(True, alpha=0.3)
    
    # Biegelinie (klein)
    ax3 = fig.add_subplot(gs[1, 1])
    E_knm2 = result.emodul * 1000
    delta = (result.streckenlast * x / (24 * E_knm2 * result.traegheitsmoment)) * \
            (result.laenge**3 - 2*result.laenge*x**2 + x**3) * 1000  # mm
    ax3.plot(x, delta, 'g-', linewidth=2)
    ax3.fill_between(x, 0, delta, alpha=0.3, color='green')
    ax3.set_title('Durchbiegung', fontsize=11)
    ax3.set_xlabel('x [m]')
    ax3.set_ylabel('δ [mm]')
    ax3.grid(True, alpha=0.3)
    
    plt.suptitle('Zusammenfassung der Berechnung', fontsize=16, fontweight='bold', y=0.98)
    
    return fig


if __name__ == "__main__":
    # Test
    print("🎨 Visualisierungsmodul Test")
    print("=" * 50)
    
    from calculation import berechne_einfeldtraeger
    
    result = berechne_einfeldtraeger(
        laenge=6.0,
        streckenlast=5.0,
        emodul=210000,
        traegheitsmoment=1940e-8
    )
    
    print("\n1. Biegemomentenverlauf...")
    fig1 = plot_bending_moment(result.laenge, result.streckenlast)
    
    print("2. Biegelinie...")
    fig2 = plot_deflection(result.laenge, result.streckenlast, result.emodul, result.traegheitsmoment)
    
    print("3. Profilvergleich...")
    fig3 = plot_comparison_chart(result.laenge, result.streckenlast, result.emodul, result.traegheitsmoment)
    
    print("4. Zusammenfassung...")
    fig4 = create_summary_diagram(result)
    
    plt.show()
    print("\n✅ Alle Diagramme erstellt!")
