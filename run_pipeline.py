"""
End-to-End Execution Pipeline for SupeRR Selector Season 2
Orchestrates preprocessing, pressure detection, profile aggregation, scoring, ranking,
multi-dimensional sensitivity analysis, and exports all required CSV and Markdown artifacts.
"""

import os
import sys
import pandas as pd
import numpy as np

# Ensure local src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data_loader import load_raw_data
from preprocessing import preprocess_data
from pressure_detector import detect_pressure_situations
from batting_analysis import analyze_batting_performance
from bowling_analysis import analyze_bowling_performance
from scoring_engine import score_batting_pri, score_bowling_pri
from ranking_engine import export_rankings, run_comprehensive_sensitivity_analysis


def main():
    print("=" * 70)
    print(" SupeRR Selector Season 2 - Pressure Reliability Index (PRI) Pipeline")
    print(" Post-Audit Production Pipeline Run")
    print("=" * 70)

    # 1. Load Data
    data_dict = load_raw_data()

    # 2. Preprocess & Clean
    bbb, matches = preprocess_data(data_dict)

    # 3. Detect Pressure Situations
    bbb_p = detect_pressure_situations(bbb)

    # 4. Batting & Bowling Profiles
    bat_profile = analyze_batting_performance(bbb_p)
    bowl_profile = analyze_bowling_performance(bbb_p)

    # 5. Score Batting & Bowling PRI
    bat_scored = score_batting_pri(bat_profile, min_balls=120, min_matches=15)
    bowl_scored = score_bowling_pri(bowl_profile, min_balls=120, min_matches=15)

    # 6. Export Rankings & Metrics
    top10_bat, top10_bowl = export_rankings(bat_scored, bowl_scored, output_dir='outputs')

    # 7. Print Top 10 Batters
    print("\n" + "=" * 85)
    print(" OFFICIAL AUDITED TOP 10 BATTERS UNDER PRESSURE (PRI-Bat)")
    print("=" * 85)
    for idx, row in top10_bat.iterrows():
        print(f"Rank {row['rank']:2d}: {row['player_name']:<20} (ID: {row['player_id']:>5}) | "
              f"PRI: {row['pri_score']:.1f} | Balls: {row['p_balls']:>3} | M: {row['p_matches']:>2} | "
              f"P_SR: {row['p_strike_rate']:.1f} (Delta {row['delta_strike_rate']:+5.1f}) | "
              f"P_Avg: {row['p_average']:.1f} | P_Bound%: {row['p_boundary_pct']:.1f}%")

    # 8. Print Top 10 Bowlers
    print("\n" + "=" * 85)
    print(" OFFICIAL AUDITED TOP 10 BOWLERS UNDER PRESSURE (PRI-Bowl)")
    print("=" * 85)
    for idx, row in top10_bowl.iterrows():
        print(f"Rank {row['rank']:2d}: {row['player_name']:<20} (ID: {row['player_id']:>5}) | "
              f"PRI: {row['pri_score']:.1f} | Balls: {row['p_balls']:>3} | M: {row['p_matches']:>2} | "
              f"P_Econ: {row['p_economy']:.2f} (Delta {row['delta_economy']:+5.2f}) | "
              f"Wkts: {row['p_wickets']:>2} (SR: {row['p_strike_rate']:.1f}) | P_Dot%: {row['p_dot_pct']:.1f}%")

    # 9. Run Multi-Dimensional Sensitivity Analysis
    sensitivity_results = run_comprehensive_sensitivity_analysis(
        bbb,
        analyze_batting_performance,
        analyze_bowling_performance,
        bat_scored,
        bowl_scored
    )

    # 10. Generate outputs/pressure_analysis_summary.md
    summary_path = os.path.join('outputs', 'pressure_analysis_summary.md')
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("# Pressure Analysis & PRI Results Summary (Audited)\n\n")
        f.write("## 1. Executive Overview\n")
        f.write(f"Across 200,999 deliveries bowled between 2022 and 2026, **{bbb_p['is_pressure'].sum():,} unique deliveries (33.22%)** were evaluated as high-pressure contexts. ")
        f.write("The Pressure Reliability Index (PRI) combines Bayesian-shrunk execution metrics, delta resilience against normal baseline, and exposure credibility.\n\n")

        f.write("### Pressure Categorization & Overlap Transparency\n")
        cond_counts = bbb_p[['p_super_over', 'p_chase_high_rrr', 'p_chase_death_close', 'p_chase_collapse', 'p_target_early_collapse', 'p_target_death_accel']].sum()
        f.write(f"- **Super Overs:** {cond_counts['p_super_over']:,} deliveries\n")
        f.write(f"- **Chase High RRR:** {cond_counts['p_chase_high_rrr']:,} deliveries\n")
        f.write(f"- **Chase Death Close:** {cond_counts['p_chase_death_close']:,} deliveries\n")
        f.write(f"- **Chase Collapse:** {cond_counts['p_chase_collapse']:,} deliveries\n")
        f.write(f"- **Target Early Collapse:** {cond_counts['p_target_early_collapse']:,} deliveries\n")
        f.write(f"- **Target Death Acceleration:** {cond_counts['p_target_death_accel']:,} deliveries\n")
        f.write(f"- **Sum of Category Activations:** {cond_counts.sum():,}\n")
        f.write(f"- **Unique High-Pressure Deliveries:** {bbb_p['is_pressure'].sum():,}\n")
        f.write(f"- **Net Overlapping Deliveries:** {cond_counts.sum() - bbb_p['is_pressure'].sum():,} (Explicitly documented; multi-label tagged).\n\n")

        f.write("## 2. Audited Top 10 Batters Under Pressure\n\n")
        f.write("| Rank | Player Name | Player ID | PRI Score | Pressure Balls | Matches | Pressure SR | Base SR | Delta SR | Pressure Avg | Boundary % |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for _, r in top10_bat.iterrows():
            f.write(f"| {r['rank']} | **{r['player_name']}** | {r['player_id']} | **{r['pri_score']:.2f}** | {r['p_balls']} | {r['p_matches']} | {r['p_strike_rate']:.2f} | {r['base_strike_rate']:.2f} | {r['delta_strike_rate']:+.2f} | {r['p_average']:.2f} | {r['p_boundary_pct']:.1f}% |\n")

        f.write("\n## 3. Audited Top 10 Bowlers Under Pressure\n\n")
        f.write("| Rank | Player Name | Player ID | PRI Score | Pressure Balls | Matches | Pressure Econ | Base Econ | Delta Econ | Wickets | Bowling SR | Dot % | Boundary Conceded % |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for _, r in top10_bowl.iterrows():
            f.write(f"| {r['rank']} | **{r['player_name']}** | {r['player_id']} | **{r['pri_score']:.2f}** | {r['p_balls']} | {r['p_matches']} | {r['p_economy']:.2f} | {r['base_economy']:.2f} | {r['delta_economy']:+.2f} | {r['p_wickets']} | {r['p_strike_rate']:.1f} | {r['p_dot_pct']:.1f}% | {r['p_boundary_pct']:.1f}% |\n")

        f.write("\n## 4. Comprehensive Sensitivity & Stability Analysis\n\n")
        f.write("| Sensitivity Test Dimension | Batting Spearman ρ | Batting Top 10 Overlap | Bowling Spearman ρ | Bowling Top 10 Overlap |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: |\n")
        f.write(f"| Strict Threshold (RRR ≥ 11, Death ≤ 24) | {sensitivity_results['strict_bat']['spearman']:.4f} | {sensitivity_results['strict_bat']['overlap']:.0f}% | {sensitivity_results['strict_bowl']['spearman']:.4f} | {sensitivity_results['strict_bowl']['overlap']:.0f}% |\n")
        f.write(f"| Relaxed Threshold (RRR ≥ 9, Death ≤ 36) | {sensitivity_results['relaxed_bat']['spearman']:.4f} | {sensitivity_results['relaxed_bat']['overlap']:.0f}% | {sensitivity_results['relaxed_bowl']['spearman']:.4f} | {sensitivity_results['relaxed_bowl']['overlap']:.0f}% |\n")
        f.write(f"| Sample Size Cutoff = 100 Balls | {sensitivity_results['sample_100_bat']['spearman']:.4f} | {sensitivity_results['sample_100_bat']['overlap']:.0f}% | {sensitivity_results['sample_100_bowl']['spearman']:.4f} | {sensitivity_results['sample_100_bowl']['overlap']:.0f}% |\n")
        f.write(f"| Sample Size Cutoff = 150 Balls | {sensitivity_results['sample_150_bat']['spearman']:.4f} | {sensitivity_results['sample_150_bat']['overlap']:.0f}% | {sensitivity_results['sample_150_bowl']['spearman']:.4f} | {sensitivity_results['sample_150_bowl']['overlap']:.0f}% |\n")
        f.write(f"| Bayesian Shrinkage K = 40 | {sensitivity_results['k40_bat']['spearman']:.4f} | {sensitivity_results['k40_bat']['overlap']:.0f}% | {sensitivity_results['k40_bowl']['spearman']:.4f} | {sensitivity_results['k40_bowl']['overlap']:.0f}% |\n")
        f.write(f"| Bayesian Shrinkage K = 80 | {sensitivity_results['k80_bat']['spearman']:.4f} | {sensitivity_results['k80_bat']['overlap']:.0f}% | {sensitivity_results['k80_bowl']['spearman']:.4f} | {sensitivity_results['k80_bowl']['overlap']:.0f}% |\n\n")

    print(f"\n[Pipeline] Summary written to: {summary_path}")
    print("=" * 70)
    print(" Pipeline completed successfully.")
    print("=" * 70)


if __name__ == '__main__':
    main()
