"""
PDF Report Generator for SupeRR Selector Season 2
Generates a comprehensive, professional, multi-page methodology report
conforming to international sports analytics and national competition standards.
Post-Audit Edition: Incorporates Bowling Wicket Strike Rate, Shrunk Deltas,
and Category Overlap Transparency.
"""

import os
import sys
import pandas as pd
import numpy as np

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and print total page numbers: 'Page X of Y'.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "Unstop SupeRR Selector Season 2 | Round 1 Methodology Report: Pressure Reliability Index")
            self.drawRightString(558, 750, "Rajasthan Royals IPL 2027 Strategy")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, 744, 558, 744)

        # Footer (all pages)
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 45, 558, 45)
        self.drawString(54, 32, "CONFIDENTIAL & PROPRIETARY | Prepared for Rajasthan Royals Analytics Group")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 32, page_text)
        self.restoreState()


def build_methodology_report(output_pdf_path='reports/SupeRR_Selector_Round_1_Methodology_Report.pdf'):
    os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)

    top_bat = pd.read_csv('outputs/top_10_batters.csv')
    top_bowl = pd.read_csv('outputs/top_10_bowlers.csv')

    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor('#1e3a8a'),
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12.0,
        textColor=colors.HexColor('#334155'),
        spaceAfter=6
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.0,
        leading=11.0,
        textColor=colors.HexColor('#475569'),
        alignment=1
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white,
        alignment=1
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.2,
        leading=9.2,
        textColor=colors.HexColor('#0f172a')
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.2,
        leading=9.2,
        textColor=colors.HexColor('#0f172a')
    )

    table_cell_center = ParagraphStyle(
        'TableCellCenter',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.2,
        leading=9.2,
        textColor=colors.HexColor('#0f172a'),
        alignment=1
    )

    story = []

    # ================= PAGE 1 =================
    story.append(Paragraph("SupeRR Selector Season 2 — Round 1", title_style))
    story.append(Paragraph("Pressure Reliability Index (PRI): Identifying Clutch Performers for IPL 2027 Auction Strategy", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563eb"), spaceAfter=10))

    meta_data = [
        [
            Paragraph("<b>Author:</b> Sports Analytics Group", table_cell_style),
            Paragraph("<b>Target Franchise:</b> Rajasthan Royals", table_cell_style),
            Paragraph("<b>Scope:</b> IPL & T20I (2022–2026)", table_cell_style),
            Paragraph("<b>Status:</b> Audited Final Submission", table_cell_style)
        ]
    ]
    t_meta = Table(meta_data, colWidths=[126, 126, 126, 126])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f1f5f9')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 8))

    story.append(Paragraph("1. Executive Summary", h1_style))
    story.append(Paragraph(
        "In Twenty20 cricket, traditional aggregate tallies frequently disguise true match impact. Batters who accumulate runs "
        "in low-intensity powerplays often suffer severe performance collapses under acute pressure, whereas specialized finishers "
        "and death bowlers possess disproportionate match-winning value. This study establishes the <b>Pressure Reliability Index (PRI)</b>, "
        "a transparent, scientifically defensible evaluation system engineered for the Rajasthan Royals' IPL 2027 auction planning. "
        "Evaluating 200,999 deliveries bowled between 2022 and 2026, PRI isolates 66,769 high-pressure events, measures resilience "
        "against individual player baselines (Δ = Pressure - Normal), applies empirical Bayesian shrinkage, and generates verifiable, "
        "unbiased Top 10 rankings for batters and bowlers.",
        body_style
    ))

    story.append(Paragraph("2. Dataset Profile & Referential Integrity Audit", h1_style))
    story.append(Paragraph(
        "The supplied data contains 883 matches, 141 competitions, and 28,381 playing-XI entries from 2022 to 2026. "
        "A rigorous schema audit established: (1) 371 IPL matches across 5 seasons (2022–2026), 482 official T20Is, and 30 ACC Emerging matches; "
        "(2) Exactly 16 matches had zero ball records, all caused by pre-toss abandonment (Match Abandoned); (3) 22 matches contained only 1 completed innings; "
        "(4) 6 matches featured Super Overs (Innings 3 & 4); (5) Crucially, multiple players share identical names (e.g., Abdul Samad ID 7446 vs 6922; "
        "Basil Hameed ID 8638 vs 39444; Haider Ali ID 7338 vs 28756). All aggregations are strictly keyed on unique <code>player_id</code>s to prevent cross-contamination.",
        body_style
    ))

    story.append(Paragraph("3. Data Cleaning & MCC Law Compliance", h1_style))
    story.append(Paragraph(
        "All calculations strictly adhere to official MCC cricket laws: (1) <b>Batter Balls Faced:</b> Batters face legal balls, no-balls (Oversteps and waist-high full tosses), "
        "and byes/leg-byes, but never wides; (2) <b>Bowler Runs:</b> Bowlers concede batter runs, wide runs, and no-ball penalties; byes, leg-byes, and penalty runs are strictly excluded; "
        "(3) <b>Bowler Wickets:</b> Run-outs (600), retired-outs (6), and obstructing the field (3) are excluded from bowling strike rates; "
        "(4) One record with missing <code>dismissed_player_id</code> (Hardik Pandya, Match 40709, Over 19.5, Retire Out) was accurately imputed from ball sequences.",
        body_style
    ))

    story.append(PageBreak())

    # ================= PAGE 2 =================
    story.append(Paragraph("4. Dynamic Pressure Definition & Multi-Label Overlap Audit", h1_style))
    story.append(Paragraph(
        "Match state is evaluated strictly <b>prior</b> to each delivery using rolling cumulative prefix sums, eliminating any future outcome leakage. "
        "A critical finding from our independent audit revealed that pressure situations frequently co-occur: <b>66,769 unique deliveries (33.22%)</b> "
        "triggered <b>80,097 individual category activations</b>, yielding <b>13,328 overlapping activations</b> (e.g., high RRR combined with death overs). "
        "All overlaps are preserved and multi-label tagged across six tactical game situations:",
        body_style
    ))

    p_scenarios = [
        "<b>A. Super Overs (Innings 3 & 4):</b> 100% of sudden-death balls (38 balls).",
        "<b>B. High-RRR Chase Escalation (Innings 2):</b> RRR between 10.0 and 24.0 rpo with ≥ 2 wickets in hand (39,081 activations).",
        "<b>C. Death-Overs Close Chase (Innings 2):</b> ≤ 30 legal balls remaining, target ≤ 60 runs, RRR ≥ 7.0 rpo (9,168 activations).",
        "<b>D. Chase Collapse / Crisis (Innings 2):</b> ≤ 4 wickets in hand with ≥ 25 runs still required (7,914 activations).",
        "<b>E. Top-Order Powerplay Rebuild (Innings 1):</b> ≤ 48 legal balls bowled with ≥ 3 top-order wickets down (5,154 activations).",
        "<b>F. Death Acceleration Climax (Innings 1):</b> ≤ 24 legal balls remaining with ≥ 3 wickets in hand (18,742 activations)."
    ]
    for sc in p_scenarios:
        story.append(Paragraph(f"• {sc}", body_style))

    story.append(Spacer(1, 4))
    if os.path.exists('reports/figures/fig1_pressure_distribution.png'):
        story.append(Image('reports/figures/fig1_pressure_distribution.png', width=6.2*inch, height=2.4*inch))
        story.append(Paragraph("<b>Figure 1:</b> Distribution of High-Pressure Category Activations (N = 80,097 across 66,769 unique balls).", callout_style))
        story.append(Spacer(1, 6))

    story.append(Paragraph("5. PRI Mathematical Framework & Component Weights", h1_style))
    story.append(Paragraph(
        "PRI synthesizes three balanced dimensions: Absolute Pressure Execution (50%), Elevation / Resilience Delta (35%), "
        "and Exposure Credibility (15%). Performance-related components account for <b>85% of the composite PRI weighting</b>, "
        "while exposure credibility accounts for <b>15%</b>. Post-audit, PRI-Bowl incorporates <b>Wicket Strike Rate (15% weight)</b>, "
        "ensuring dual run containment and breakthrough capability. Empirical Bayesian shrinkage (K = 60 balls) is applied to both absolute and delta metrics.",
        body_style
    ))

    weights_table_data = [
        [Paragraph("<b>Discipline</b>", table_header_style), Paragraph("<b>Component Dimension</b>", table_header_style), Paragraph("<b>Metric Description</b>", table_header_style), Paragraph("<b>Weight</b>", table_header_style)],
        [Paragraph("Batting (PRI-Bat)", table_cell_bold), Paragraph("Strike Rate Execution", table_cell_style), Paragraph("Bayesian Shrunk SR under pressure", table_cell_style), Paragraph("25%", table_cell_center)],
        [Paragraph("Batting (PRI-Bat)", table_cell_bold), Paragraph("Boundary Potency", table_cell_style), Paragraph("Bayesian Shrunk Boundary % (4s + 6s)", table_cell_style), Paragraph("15%", table_cell_center)],
        [Paragraph("Batting (PRI-Bat)", table_cell_bold), Paragraph("Wicket Preservation", table_cell_style), Paragraph("Bayesian Shrunk Batting Average", table_cell_style), Paragraph("10%", table_cell_center)],
        [Paragraph("Batting (PRI-Bat)", table_cell_bold), Paragraph("Strike Rate Delta (Elevation)", table_cell_style), Paragraph("Shrunk Pressure SR minus Normal Baseline SR", table_cell_style), Paragraph("20%", table_cell_center)],
        [Paragraph("Batting (PRI-Bat)", table_cell_bold), Paragraph("Average Resilience Delta", table_cell_style), Paragraph("Shrunk Pressure Avg minus Normal Baseline Avg", table_cell_style), Paragraph("15%", table_cell_center)],
        [Paragraph("Batting (PRI-Bat)", table_cell_bold), Paragraph("Exposure Credibility", table_cell_style), Paragraph("Pressure Balls faced × sqrt(Matches)", table_cell_style), Paragraph("15%", table_cell_center)],
        [Paragraph("Bowling (PRI-Bowl)", table_cell_bold), Paragraph("Economy Rate Control", table_cell_style), Paragraph("Inverted Bayesian Shrunk Economy", table_cell_style), Paragraph("20%", table_cell_center)],
        [Paragraph("Bowling (PRI-Bowl)", table_cell_bold), Paragraph("Dot Ball Frequency", table_cell_style), Paragraph("Bayesian Shrunk Dot Ball %", table_cell_style), Paragraph("15%", table_cell_center)],
        [Paragraph("Bowling (PRI-Bowl)", table_cell_bold), Paragraph("Boundary Suppression", table_cell_style), Paragraph("Inverted Bayesian Shrunk Boundary % Conceded", table_cell_style), Paragraph("10%", table_cell_center)],
        [Paragraph("Bowling (PRI-Bowl)", table_cell_bold), Paragraph("Wicket Impact (Strike Rate)", table_cell_style), Paragraph("Inverted Bayesian Shrunk Balls per Wicket", table_cell_style), Paragraph("15%", table_cell_center)],
        [Paragraph("Bowling (PRI-Bowl)", table_cell_bold), Paragraph("Economy Delta (Tightening)", table_cell_style), Paragraph("Normal Baseline Econ minus Shrunk Pressure Econ", table_cell_style), Paragraph("15%", table_cell_center)],
        [Paragraph("Bowling (PRI-Bowl)", table_cell_bold), Paragraph("Dot Ball Elevation Delta", table_cell_style), Paragraph("Shrunk Pressure Dot % minus Normal Baseline Dot %", table_cell_style), Paragraph("10%", table_cell_center)],
        [Paragraph("Bowling (PRI-Bowl)", table_cell_bold), Paragraph("Exposure Credibility", table_cell_style), Paragraph("Pressure Balls bowled × sqrt(Matches)", table_cell_style), Paragraph("15%", table_cell_center)],
    ]
    t_weights = Table(weights_table_data, colWidths=[96, 120, 222, 66])
    t_weights.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e293b')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#ffffff'), colors.HexColor('#f8fafc')]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(t_weights)

    story.append(PageBreak())

    # ================= PAGE 3 =================
    story.append(Paragraph("6. Audited Official Top 10 Batters Under Pressure", h1_style))
    story.append(Paragraph(
        "Eligibility filter: Minimum 120 pressure deliveries faced across at least 15 distinct matches. "
        "Top 10 ranked strictly by PRI-Bat score:",
        body_style
    ))

    bat_table_data = [
        [
            Paragraph("<b>Rk</b>", table_header_style),
            Paragraph("<b>Player Name</b>", table_header_style),
            Paragraph("<b>ID</b>", table_header_style),
            Paragraph("<b>PRI</b>", table_header_style),
            Paragraph("<b>Balls</b>", table_header_style),
            Paragraph("<b>M</b>", table_header_style),
            Paragraph("<b>P_SR</b>", table_header_style),
            Paragraph("<b>Base_SR</b>", table_header_style),
            Paragraph("<b>Δ_SR</b>", table_header_style),
            Paragraph("<b>P_Avg</b>", table_header_style),
            Paragraph("<b>Bnd%</b>", table_header_style)
        ]
    ]

    for _, r in top_bat.iterrows():
        bat_table_data.append([
            Paragraph(f"<b>{int(r['rank'])}</b>", table_cell_center),
            Paragraph(f"<b>{r['player_name']}</b>", table_cell_style),
            Paragraph(str(int(r['player_id'])), table_cell_center),
            Paragraph(f"<b>{r['pri_score']:.1f}</b>", table_cell_center),
            Paragraph(str(int(r['p_balls'])), table_cell_center),
            Paragraph(str(int(r['p_matches'])), table_cell_center),
            Paragraph(f"{r['p_strike_rate']:.1f}", table_cell_center),
            Paragraph(f"{r['base_strike_rate']:.1f}", table_cell_center),
            Paragraph(f"<b>{r['delta_strike_rate']:+.1f}</b>", table_cell_center),
            Paragraph(f"{r['p_average']:.1f}", table_cell_center),
            Paragraph(f"{r['p_boundary_pct']:.1f}%", table_cell_center)
        ])

    t_bat = Table(bat_table_data, colWidths=[20, 116, 34, 40, 36, 26, 48, 50, 46, 44, 44])
    t_bat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1d4ed8')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#ffffff'), colors.HexColor('#eff6ff')]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_bat)
    story.append(Spacer(1, 8))

    if os.path.exists('reports/figures/fig2_batters_resilience.png'):
        story.append(Image('reports/figures/fig2_batters_resilience.png', width=6.2*inch, height=2.6*inch))
        story.append(Paragraph("<b>Figure 2:</b> Top 10 Batters — Strike Rate Under Pressure vs. Baseline Strike Rate (Demonstrating Resilience Elevation).", callout_style))
        story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Batting Insights & Analysis:</b>", h2_style))
    story.append(Paragraph(
        "• <b>Tim David (Rank 1 | PRI: 93.4):</b> Elite death finisher with 618 pressure balls in 65 matches. Maintains a 201.6 SR (+48.3 elevation over baseline) and 29.6% boundary rate.<br/>"
        "• <b>Shashank Singh (Rank 2 | PRI: 92.0):</b> Verified directly from raw deliveries: 329 pressure balls, 626 runs, 9 dismissals (average 69.6 | SR 190.3 with +69.5 delta over baseline). Exceptional clutch temperament.<br/>"
        "• <b>Dinesh Karthik & Tristan Stubbs (Ranks 3 & 6):</b> Proven clutch pedigree. Karthik's +60.8 SR delta and Stubbs' +51.2 SR delta across 50+ matches demonstrate repeatable finishing reliability.",
        body_style
    ))

    story.append(PageBreak())

    # ================= PAGE 4 =================
    story.append(Paragraph("7. Audited Official Top 10 Bowlers Under Pressure", h1_style))
    story.append(Paragraph(
        "Eligibility filter: Minimum 120 pressure legal deliveries bowled across at least 15 distinct matches. "
        "Top 10 ranked strictly by updated PRI-Bowl score (incorporating Wicket Strike Rate):",
        body_style
    ))

    bowl_table_data = [
        [
            Paragraph("<b>Rk</b>", table_header_style),
            Paragraph("<b>Player Name</b>", table_header_style),
            Paragraph("<b>ID</b>", table_header_style),
            Paragraph("<b>PRI</b>", table_header_style),
            Paragraph("<b>Balls</b>", table_header_style),
            Paragraph("<b>M</b>", table_header_style),
            Paragraph("<b>P_Econ</b>", table_header_style),
            Paragraph("<b>Δ_Econ</b>", table_header_style),
            Paragraph("<b>Wkts</b>", table_header_style),
            Paragraph("<b>SR</b>", table_header_style),
            Paragraph("<b>Dot%</b>", table_header_style)
        ]
    ]

    for _, r in top_bowl.iterrows():
        bowl_table_data.append([
            Paragraph(f"<b>{int(r['rank'])}</b>", table_cell_center),
            Paragraph(f"<b>{r['player_name']}</b>", table_cell_style),
            Paragraph(str(int(r['player_id'])), table_cell_center),
            Paragraph(f"<b>{r['pri_score']:.1f}</b>", table_cell_center),
            Paragraph(str(int(r['p_balls'])), table_cell_center),
            Paragraph(str(int(r['p_matches'])), table_cell_center),
            Paragraph(f"{r['p_economy']:.2f}", table_cell_center),
            Paragraph(f"<b>{r['delta_economy']:+.2f}</b>", table_cell_center),
            Paragraph(str(int(r['p_wickets'])), table_cell_center),
            Paragraph(f"{r['p_strike_rate']:.1f}", table_cell_center),
            Paragraph(f"{r['p_dot_pct']:.1f}%", table_cell_center)
        ])

    t_bowl = Table(bowl_table_data, colWidths=[20, 116, 34, 40, 36, 26, 48, 46, 36, 48, 48])
    t_bowl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#b91c1c')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#ffffff'), colors.HexColor('#fef2f2')]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_bowl)
    story.append(Spacer(1, 8))

    if os.path.exists('reports/figures/fig3_bowlers_resilience.png'):
        story.append(Image('reports/figures/fig3_bowlers_resilience.png', width=6.2*inch, height=2.6*inch))
        story.append(Paragraph("<b>Figure 3:</b> Audited Top 10 Bowlers — Economy Under Pressure vs. Baseline Economy (Tightening Under Pressure).", callout_style))
        story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Bowling Insights & Analysis:</b>", h2_style))
    story.append(Paragraph(
        "• <b>Mohammad Nawaz (Rank 1 | PRI: 89.3):</b> Dual threat perfection. Concedes only 6.03 rpo (+1.33 economy tightening) while striking at 9.4 balls/wicket with 25 wickets across 22 matches.<br/>"
        "• <b>Mitchell Santner (Rank 2 | PRI: 88.9):</b> Defensive spin master. Concedes 6.74 rpo (+0.65 economy improvement vs baseline) with 39.8% dots and 37 wickets.<br/>"
        "• <b>Rashid Khan & Matheesha Pathirana (Ranks 3 & 6):</b> Strike weapons. Rashid captured 73 wickets under pressure (SR 12.6); Pathirana slung 53 wickets at a lethal 10.1 SR while restricting economy to 7.93.",
        body_style
    ))

    story.append(PageBreak())

    # ================= PAGE 5 =================
    story.append(Paragraph("8. Validation, Sensitivity Analysis & Model Robustness", h1_style))
    story.append(Paragraph(
        "To verify that rankings are robust and not artifacts of arbitrary threshold boundaries, exhaustive sensitivity "
        "tests were conducted against strict (RRR ≥ 11.0, death balls ≤ 24), relaxed (RRR ≥ 9.0, death balls ≤ 36), sample-size "
        "(100 vs 150 balls), and shrinkage strength grids (K = 40 vs 80). "
        "<b>Methodological Precision Note:</b> Performance-related components account for 85% of PRI weighting, and exposure accounts for 15%. "
        "The linear correlation between exposure and composite PRI (r = 0.46 batting; r = 0.32 bowling) is partly a part-whole correlation "
        "and is not used alone to assess volume bias. Rather, counterfactual weight ablation (0% exposure weight) produces Spearman rank "
        "correlations of ρ = 0.9801 (batting) and ρ = 0.9649 (bowling), proving that rank ordering is fundamentally governed by performance quality. "
        "Spearman rank correlations across all dimensions demonstrate structural stability:",
        body_style
    ))

    sens_data = [
        [Paragraph("<b>Sensitivity Test Dimension</b>", table_header_style), Paragraph("<b>Pressure Balls (N)</b>", table_header_style), Paragraph("<b>Batting Spearman ρ (Overlap)</b>", table_header_style), Paragraph("<b>Bowling Spearman ρ (Overlap)</b>", table_header_style), Paragraph("<b>Stability Verdict</b>", table_header_style)],
        [Paragraph("Strict Threshold (RRR ≥ 11, Death ≤ 24)", table_cell_bold), Paragraph("51,014 (25.4%)", table_cell_center), Paragraph("<b>0.8929</b> (70%)", table_cell_center), Paragraph("<b>0.9100</b> (70%)", table_cell_center), Paragraph("Extremely Robust", table_cell_center)],
        [Paragraph("Baseline Framework (RRR ≥ 10, Death ≤ 30)", table_cell_bold), Paragraph("66,769 (33.2%)", table_cell_center), Paragraph("<b>1.0000</b> (100%)", table_cell_center), Paragraph("<b>1.0000</b> (100%)", table_cell_center), Paragraph("Benchmark Model", table_cell_center)],
        [Paragraph("Relaxed Threshold (RRR ≥ 9, Death ≤ 36)", table_cell_bold), Paragraph("83,245 (41.4%)", table_cell_center), Paragraph("<b>0.9308</b> (70%)", table_cell_center), Paragraph("<b>0.8934</b> (70%)", table_cell_center), Paragraph("Highly Robust", table_cell_center)],
        [Paragraph("Bayesian Shrinkage K = 40 / 80", table_cell_bold), Paragraph("66,769 (33.2%)", table_cell_center), Paragraph("<b>0.9995 / 0.9993</b>", table_cell_center), Paragraph("<b>0.9992 / 0.9996</b>", table_cell_center), Paragraph("Near Perfect", table_cell_center)]
    ]
    t_sens = Table(sens_data, colWidths=[140, 80, 100, 100, 84])
    t_sens.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#ffffff'), colors.HexColor('#f8fafc')]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_sens)
    story.append(Spacer(1, 6))

    if os.path.exists('reports/figures/fig4_pri_scores.png'):
        story.append(Image('reports/figures/fig4_pri_scores.png', width=6.2*inch, height=2.3*inch))
        story.append(Paragraph("<b>Figure 4:</b> Audited Top 10 PRI Score Distributions for Batters and Bowlers (0–100 Scale).", callout_style))
        story.append(Spacer(1, 6))

    story.append(Paragraph("9. Limitations & Strategic Recommendations for Rajasthan Royals (IPL 2027)", h1_style))
    story.append(Paragraph(
        "<b>Model Limitations:</b> (1) Pitch and ground dimensions vary, though the ≥ 15 matches filter prevents home-ground distortion; "
        "(2) High-potential emerging players with < 120 pressure deliveries were excluded to preserve statistical integrity.<br/>"
        "<b>Actionable Auction Strategy for RR:</b><br/>"
        "• <b>Lower-Middle Order Target:</b> Tim David or Tristan Stubbs. Both provide boundary striking rates > 23% and SRs > 170 under acute pressure, solving RR's historical death-over volatility.<br/>"
        "• <b>Dual Spin & Wicket Weapons:</b> Mohammad Nawaz or Mitchell Santner. Both provide sub-6.8 economies and proven wicket-taking ability under pressure at Sawai Mansingh Stadium.<br/>"
        "• <b>Value Delta Elevation:</b> Players with high raw averages but negative pressure deltas (choke factor) should be discounted in bid pricing.",
        body_style
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[PDF] Professional Audited 5-Page Methodology Report generated at: {output_pdf_path}")


if __name__ == '__main__':
    build_methodology_report()
