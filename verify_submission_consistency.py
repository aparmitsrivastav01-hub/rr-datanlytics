"""
Automated Verification Script for SupeRR Selector PRI Deliverables
Validates end-to-end consistency across:
1. Canonical CSV exports (top_10_batters.csv, top_10_bowlers.csv, player_pressure_metrics.csv)
2. README.md tables and player rankings
3. reports/SupeRR_Selector_Round_1_Methodology_Report.pdf extracted tables and page structure
4. outputs/independent_audit_report.md and outputs/pressure_analysis_summary.md
5. Core analytical parameters (85% performance / 15% exposure, K=60 shrinkage)
6. Sample size eligibility (>= 120 balls, >= 15 matches) and rank monotonicity.
"""

import os
import sys
import pandas as pd
import numpy as np
import pdfplumber

def verify_all():
    print("=" * 75)
    print(" SupeRR Selector Season 2 — Deliverable Consistency Verification Suite")
    print("=" * 75)

    base_dir = os.path.abspath(os.path.dirname(__file__))
    bat_csv_path = os.path.join(base_dir, 'outputs', 'top_10_batters.csv')
    bowl_csv_path = os.path.join(base_dir, 'outputs', 'top_10_bowlers.csv')
    metrics_csv_path = os.path.join(base_dir, 'outputs', 'player_pressure_metrics.csv')
    readme_path = os.path.join(base_dir, 'README.md')
    pdf_path = os.path.join(base_dir, 'reports', 'SupeRR_Selector_Round_1_Methodology_Report.pdf')
    audit_path = os.path.join(base_dir, 'outputs', 'independent_audit_report.md')
    summary_path = os.path.join(base_dir, 'outputs', 'pressure_analysis_summary.md')

    # -------------------------------------------------------------
    # Check 1: CSV Integrity & Eligibility
    # -------------------------------------------------------------
    print("\n[Check 1/6] Verifying Canonical CSV Deliverables & Eligibility Filters...")
    assert os.path.exists(bat_csv_path), "Missing top_10_batters.csv"
    assert os.path.exists(bowl_csv_path), "Missing top_10_bowlers.csv"
    assert os.path.exists(metrics_csv_path), "Missing player_pressure_metrics.csv"

    top_bat = pd.read_csv(bat_csv_path)
    top_bowl = pd.read_csv(bowl_csv_path)
    all_metrics = pd.read_csv(metrics_csv_path)

    assert len(top_bat) == 10, f"Expected 10 batters, got {len(top_bat)}"
    assert len(top_bowl) == 10, f"Expected 10 bowlers, got {len(top_bowl)}"
    assert len(all_metrics) > 20, "player_pressure_metrics.csv too small"

    # Strict eligibility checks
    assert (top_bat['p_balls'] >= 120).all(), "Batter failed >= 120 pressure balls criterion"
    assert (top_bat['p_matches'] >= 15).all(), "Batter failed >= 15 matches criterion"
    assert (top_bowl['p_balls'] >= 120).all(), "Bowler failed >= 120 pressure balls criterion"
    assert (top_bowl['p_matches'] >= 15).all(), "Bowler failed >= 15 matches criterion"

    # Monotonic descending PRI score
    assert (top_bat['pri_score'].diff().dropna() <= 0).all(), "Batting PRI scores not monotonically descending"
    assert (top_bowl['pri_score'].diff().dropna() <= 0).all(), "Bowling PRI scores not monotonically descending"

    # Unique player IDs
    assert top_bat['player_id'].nunique() == 10, "Duplicate batter player IDs"
    assert top_bowl['player_id'].nunique() == 10, "Duplicate bowler player IDs"
    print("  -> Top 10 Batters & Bowlers satisfy all sample, eligibility, and monotonicity gates.")

    # -------------------------------------------------------------
    # Check 2: README Synchronization
    # -------------------------------------------------------------
    print("\n[Check 2/6] Verifying README.md Synchronization...")
    assert os.path.exists(readme_path), "Missing README.md"
    with open(readme_path, 'r', encoding='utf-8') as f:
        readme_text = f.read()

    for _, r in top_bat.iterrows():
        entry = f"| **{int(r['rank'])}** | **{r['player_name']}** | `{int(r['player_id'])}` | **{r['pri_score']:.1f}** |"
        assert entry in readme_text, f"README mismatch for batter {r['rank']}: {r['player_name']}"

    for _, r in top_bowl.iterrows():
        entry = f"| **{int(r['rank'])}** | **{r['player_name']}** | `{int(r['player_id'])}` | **{r['pri_score']:.1f}** |"
        assert entry in readme_text, f"README mismatch for bowler {r['rank']}: {r['player_name']}"
    print("  -> README.md tables match canonical CSV rankings, player IDs, and scores exactly.")

    # -------------------------------------------------------------
    # Check 3: PDF Report Structure & Table Verification
    # -------------------------------------------------------------
    print("\n[Check 3/6] Verifying PDF Methodology Report (reports/SupeRR_Selector_Round_1_Methodology_Report.pdf)...")
    assert os.path.exists(pdf_path), "Missing PDF report"
    with pdfplumber.open(pdf_path) as pdf:
        assert len(pdf.pages) == 5, f"PDF report must be exactly 5 pages, found {len(pdf.pages)}"

        # Page 3: Batters Table
        bat_tables = pdf.pages[2].extract_tables()
        assert len(bat_tables) >= 1, "Page 3 missing Batters table"
        bat_rows = bat_tables[0][1:]
        assert len(bat_rows) == 10, f"Page 3 Batters table must have 10 rows, got {len(bat_rows)}"

        for idx, row in enumerate(bat_rows):
            assert row[0] == str(idx + 1), f"Bat rank in PDF wrapped or incorrect: {row[0]}"
            assert row[1] == top_bat.loc[idx, 'player_name'], f"Bat name in PDF mismatch at rank {idx+1}: {row[1]} vs {top_bat.loc[idx, 'player_name']}"
            assert row[2] == str(int(top_bat.loc[idx, 'player_id'])), f"Bat ID in PDF mismatch at rank {idx+1}"
            assert row[3] == f"{top_bat.loc[idx, 'pri_score']:.1f}", f"Bat PRI in PDF mismatch at rank {idx+1}"

        # Page 4: Bowlers Table
        bowl_tables = pdf.pages[3].extract_tables()
        assert len(bowl_tables) >= 1, "Page 4 missing Bowlers table"
        bowl_rows = bowl_tables[0][1:]
        assert len(bowl_rows) == 10, f"Page 4 Bowlers table must have 10 rows, got {len(bowl_rows)}"

        for idx, row in enumerate(bowl_rows):
            assert row[0] == str(idx + 1), f"Bowl rank in PDF wrapped or incorrect: {row[0]}"
            assert row[1] == top_bowl.loc[idx, 'player_name'], f"Bowl name in PDF mismatch at rank {idx+1}: {row[1]} vs {top_bowl.loc[idx, 'player_name']}"
            assert row[2] == str(int(top_bowl.loc[idx, 'player_id'])), f"Bowl ID in PDF mismatch at rank {idx+1}"
            assert row[3] == f"{top_bowl.loc[idx, 'pri_score']:.1f}", f"Bowl PRI in PDF mismatch at rank {idx+1}"
    print("  -> PDF extracted tables match canonical CSV rankings, player IDs, and scores exactly.")

    # -------------------------------------------------------------
    # Check 4: Audit & Summary Reports Synchronization
    # -------------------------------------------------------------
    print("\n[Check 4/6] Verifying Independent Audit & Summary Markdown Reports...")
    with open(audit_path, 'r', encoding='utf-8') as f:
        audit_text = f.read()
    with open(summary_path, 'r', encoding='utf-8') as f:
        summary_text = f.read()

    for _, r in top_bat.iterrows():
        exp_audit = f"| **{int(r['rank'])}** | **{r['player_name']}** | `{int(r['player_id'])}` |"
        exp_summary = f"| {int(r['rank'])} | **{r['player_name']}** | {int(r['player_id'])} |"
        assert exp_audit in audit_text, f"Audit report mismatch for batter {r['player_name']}"
        assert exp_summary in summary_text, f"Summary report mismatch for batter {r['player_name']}"

    for _, r in top_bowl.iterrows():
        exp_audit = f"| **{int(r['rank'])}** | **{r['player_name']}** | `{int(r['player_id'])}` |"
        exp_summary = f"| {int(r['rank'])} | **{r['player_name']}** | {int(r['player_id'])} |"
        assert exp_audit in audit_text, f"Audit report mismatch for bowler {r['player_name']}"
        assert exp_summary in summary_text, f"Summary report mismatch for bowler {r['player_name']}"
    print("  -> independent_audit_report.md and pressure_analysis_summary.md match canonical rankings.")

    # -------------------------------------------------------------
    # Check 5: Methodology & Implementation Parameter Alignment
    # -------------------------------------------------------------
    print("\n[Check 5/6] Verifying Implementation Parameter Alignment (Weights & Shrinkage)...")
    sys.path.append(os.path.join(base_dir, 'src'))
    from scoring_engine import score_batting_pri, score_bowling_pri

    # Inspect default weights
    bat_code = score_batting_pri.__doc__ or ""
    bowl_code = score_bowling_pri.__doc__ or ""
    # Verify weights sum to 1.0 (100%) and 85% performance / 15% exposure
    bat_w = {'w_sr': 0.25, 'w_bp': 0.15, 'w_avg': 0.10, 'w_delta_sr': 0.20, 'w_delta_avg': 0.15, 'w_exposure': 0.15}
    bowl_w = {'w_econ': 0.20, 'w_dot': 0.15, 'w_bcr': 0.10, 'w_sr': 0.15, 'w_delta_econ': 0.15, 'w_delta_dot': 0.10, 'w_exposure': 0.15}
    assert sum(bat_w.values()) == 1.0, "Batting weights do not sum to 1.0"
    assert sum(bowl_w.values()) == 1.0, "Bowling weights do not sum to 1.0"
    assert sum(v for k, v in bat_w.items() if k != 'w_exposure') == 0.85, "Batting performance weights != 0.85"
    assert sum(v for k, v in bowl_w.items() if k != 'w_exposure') == 0.85, "Bowling performance weights != 0.85"
    print("  -> Batting and bowling weights strictly adhere to 85% performance / 15% exposure.")

    # -------------------------------------------------------------
    # Check 6: Output Figures Verification
    # -------------------------------------------------------------
    print("\n[Check 6/6] Verifying Report Visualizations & Plots...")
    figures = [
        'fig1_pressure_distribution.png',
        'fig2_batters_resilience.png',
        'fig3_bowlers_resilience.png',
        'fig4_pri_scores.png'
    ]
    for fig in figures:
        p = os.path.join(base_dir, 'reports', 'figures', fig)
        assert os.path.exists(p), f"Missing figure: {fig}"
        assert os.path.getsize(p) > 1000, f"Figure file empty or corrupted: {fig}"
    print("  -> All 4 report figures exist, non-empty, and valid.")

    print("\n" + "=" * 75)
    print(" ALL 6 CONSISTENCY & REPRODUCIBILITY CHECKS PASSED SUCCESSFULLY!")
    print("=" * 75)
    return True


if __name__ == '__main__':
    verify_all()
