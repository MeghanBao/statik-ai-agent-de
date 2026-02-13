"""
statik-ai-agent-de
PDF-Export-Modul für Berechnungsberichte
"""

from datetime import datetime
from typing import Optional
from calculation import TraegerBerechnung


class PDFReport:
    """
    Erstellt professionelle PDF-Berechnungsberichte.
    """
    
    def __init__(self):
        self.page_width = 210  # A4 width in mm
        self.margin = 20
        self.content_width = self.page_width - 2 * self.margin
    
    def generate_report(
        self,
        result: TraegerBerechnung,
        material: str,
        profil: str,
        output_path: str = "statik_bericht.pdf"
    ) -> str:
        """
        Generiert einen PDF-Bericht.
        
        Args:
            result: Berechnungsergebnisse
            material: Verwendetes Material
            profil: Verwendetes Profil
            output_path: Ausgabe-Pfad
            
        Returns:
            Pfad zur generierten PDF-Datei
        """
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.lib.units import mm
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
        except ImportError:
            return self._generate_simple_text_report(result, material, profil, output_path)
        
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=self.margin * mm,
            leftMargin=self.margin * mm,
            topMargin=self.margin * mm,
            bottomMargin=self.margin * mm
        )
        
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        heading_style = ParagraphStyle(
            'Heading',
            parent=styles['Heading2'],
            fontSize=12,
            spaceBefore=15,
            spaceAfter=10,
            textColor=colors.darkblue
        )
        
        normal_style = ParagraphStyle(
            'Normal',
            parent=styles['Normal'],
            fontSize=10,
            spaceBefore=5,
            spaceAfter=5
        )
        
        # Build content
        story = []
        
        # Title
        story.append(Paragraph("Statik AI Agent - Berechnungsbericht", title_style))
        story.append(Spacer(1, 10))
        
        # Date
        story.append(Paragraph(
            f"Erstellt am: {datetime.now().strftime('%d.%m.%Y um %H:%M')}",
            ParagraphStyle('Date', parent=styles['Normal'], fontSize=9, textColor=colors.grey)
        ))
        
        story.append(Spacer(1, 20))
        
        # Input Parameters
        story.append(Paragraph("1. Eingabeparameter", heading_style))
        
        input_data = [
            ['Parameter', 'Wert', 'Einheit'],
            ['Trägerlänge (L)', f'{result.laenge:.2f}', 'm'],
            ['Streckenlast (q)', f'{result.streckenlast:.2f}', 'kN/m'],
            ['Material', material, '-'],
            ['Profil', profil, '-'],
            ['E-Modul', f'{result.emodul:,.0f}', 'MPa'],
        ]
        
        table = Table(input_data, colWidths=[80, 60, 40])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(table)
        story.append(Spacer(1, 20))
        
        # Results
        story.append(Paragraph("2. Berechnungsergebnisse", heading_style))
        
        results_data = [
            ['Wert', 'Ergebnis', 'Einheit'],
            ['Max. Biegemoment', f'{result.biegemoment_max:.2f}', 'kNm'],
            ['Max. Querkraft', f'{result.querkraft_max:.2f}', 'kN'],
            ['Max. Durchbiegung', f'{result.durchbiegung_max:.2f}', 'mm'],
            ['Grenzwert L/300', f'{result.grenzdurchbiegung_l300:.2f}', 'mm'],
            ['Ausnutzung L/300', f'{result.ausnutzung_l300:.1f}', '%'],
        ]
        
        results_table = Table(results_data, colWidths=[80, 60, 40])
        results_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.darkgreen),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(results_table)
        story.append(Spacer(1, 20))
        
        # Bewertung
        story.append(Paragraph("3. Bewertung", heading_style))
        
        if result.ausnutzung_l300 <= 100:
            bewertung = "✅ Die Durchbiegung liegt im zulässigen Bereich (L/300)."
            bewertung_color = colors.darkgreen
        elif result.ausnutzung_l300 <= 120:
            bewertung = "⚠️ Die Durchbiegung überschreitet L/300 leicht. Eine Überprüfung wird empfohlen."
            bewertung_color = colors.orange
        else:
            bewertung = "❌ Die Durchbiegung überschreitet L/300 deutlich! Maßnahmen erforderlich."
            bewertung_color = colors.red
        
        story.append(Paragraph(bewertung, ParagraphStyle(
            'Bewertung',
            parent=styles['Normal'],
            fontSize=11,
            textColor=bewertung_color,
            spaceBefore=10
        )))
        
        story.append(Spacer(1, 20))
        
        # Disclaimer
        story.append(Paragraph("4. Haftungsausschluss", heading_style))
        disclaimer = """
        <b>Wichtiger Hinweis:</b><br/>
        Dieser Bericht wurde mit dem Statik AI Agent erstellt und dient ausschließlich 
        der Orientierung. Die berechneten Werte ersetzen keine qualifizierte statische 
        Berechnung durch einen staatlich geprüften Tragwerksplaner. Für verbindliche 
        Ergebnisse ist immer ein qualifizierter Statiker hinzuzuziehen.
        """
        story.append(Paragraph(disclaimer, normal_style))
        
        # Build PDF
        doc.build(story)
        
        return output_path
    
    def _generate_simple_text_report(
        self,
        result: TraegerBerechnung,
        material: str,
        profil: str,
        output_path: str
    ) -> str:
        """
        Generiert einen einfachen Text-Bericht (wenn reportlab nicht verfügbar).
        """
        content = []
        content.append("=" * 60)
        content.append("STATIK AI AGENT - BERECHNUNGSBERICHT")
        content.append("=" * 60)
        content.append("")
        content.append(f"Erstellt am: {datetime.now().strftime('%d.%m.%Y um %H:%M')}")
        content.append("")
        content.append("1. EINGABEPARAMETER")
        content.append("-" * 40)
        content.append(f"  Trägerlänge (L):      {result.laenge:.2f} m")
        content.append(f"  Streckenlast (q):     {result.streckenlast:.2f} kN/m")
        content.append(f"  Material:             {material}")
        content.append(f"  Profil:               {profil}")
        content.append(f"  E-Modul:             {result.emodul:,.0f} MPa")
        content.append("")
        content.append("2. BERECHNUNGSERGEBNISSE")
        content.append("-" * 40)
        content.append(f"  Max. Biegemoment:     {result.biegemoment_max:.2f} kNm")
        content.append(f"  Max. Querkraft:       {result.querkraft_max:.2f} kN")
        content.append(f"  Max. Durchbiegung:    {result.durchbiegung_max:.2f} mm")
        content.append(f"  Grenzwert L/300:      {result.grenzdurchbiegung_l300:.2f} mm")
        content.append(f"  Ausnutzung L/300:     {result.ausnutzung_l300:.1f}%")
        content.append("")
        content.append("3. BEWERTUNG")
        content.append("-" * 40)
        
        if result.ausnutzung_l300 <= 100:
            content.append("  ✅ Die Durchbiegung liegt im zulässigen Bereich (L/300).")
        elif result.ausnutzung_l300 <= 120:
            content.append("  ⚠️ Die Durchbiegung überschreitet L/300 leicht.")
        else:
            content.append("  ❌ Die Durchbiegung überschreitet L/300 deutlich!")
        
        content.append("")
        content.append("4. HAFTUNGSAUSSCHLUSS")
        content.append("-" * 40)
        content.append("  Dieser Bericht dient ausschließlich der Orientierung.")
        content.append("  Er ersetzt keine qualifizierte statische Berechnung")
        content.append("  durch einen staatlich geprüften Tragwerksplaner.")
        content.append("")
        content.append("=" * 60)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
        
        return output_path


def export_pdf(result: TraegerBerechnung, material: str, profil: str) -> str:
    """
    Helper-Funktion für PDF-Export.
    """
    pdf = PDFReport()
    filename = f"statik_bericht_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    pdf.generate_report(result, material, profil, filename)
    return filename


if __name__ == "__main__":
    # Test
    print("📄 PDF-Export Test")
    print("=" * 50)
    
    from calculation import berechne_einfeldtraeger
    
    result = berechne_einfeldtraeger(
        laenge=6.0,
        streckenlast=5.0,
        emodul=210000,
        traegheitsmoment=1940e-8
    )
    
    pdf = PDFReport()
    filename = pdf.generate_report(result, "Stahl (S235)", "IPE 200")
    
    print(f"\n✅ PDF-Bericht generiert: {filename}")
