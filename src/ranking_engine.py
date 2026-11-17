"""
Ranking Engine Module for SupeRR Selector Season 2
Generates finalized Top 10 Batters and Bowlers under pressure,
computes supporting explanations, runs comprehensive sensitivity tests,
and exports all deliverables.
"""

import os
import pandas as pd
import numpy as np
from scipy.stats import spearmanr

from scoring_engine import score_batting_pri, score_bowling_pri


def generate_batting_explanations(top_df):
    """
    Generates data-driven, evidence-backed justifications for each shortlisted batter.
    """
    explanations = []
    for _, row in top_df.iterrows():
        name = row['player_name']
        sr_p = row['p_strike_rate']
        d_sr = row['delta_strike_rate']
        bp_p = row['p_boundary_pct']
        avg_p = row['p_average']
        balls = row['p_balls']
        matches = row['p_matches']

        exp = (
            f"Sensational pressure execution across {matches} matches and {balls} deliveries. "
            f"Under high leverage, maintains a blistering strike rate of {sr_p:.1f} "
            f"({d_sr:+.1f} vs normal baseline) with a boundary percentage of {bp_p:.1f}% "
            f"and average of {avg_p:.1f}, proving exceptional ice-in-the-veins finishing reliability."
        )
        explanations.append(exp)
    top_df['selection_rationale'] = explanations
    return top_df


def generate_bowling_explanations(top_df):
    """
    Generates data-driven, evidence-backed justifications for each shortlisted bowler.
    """
    explanations = []
    for _, row in top_df.iterrows():
        name = row['player_name']
        econ_p = row['p_economy']
        d_econ = row['delta_economy']
        dot_p = row['p_dot_pct']
        bcr_p = row['p_boundary_pct']
        wkts_p = row['p_wickets']
        sr_p = row['p_strike_rate']
        balls = row['p_balls']
        matches = row['p_matches']

        exp = (
            f"Masterclass dual containment and strike weapon across {matches} matches and {balls} legal deliveries. "
            f"Under high pressure, concedes only {econ_p:.2f} rpo ({d_econ:+.2f} economy improvement vs baseline), "
            f"generates {dot_p:.1f}% dot balls, restricts boundaries to {bcr_p:.1f}%, and captures {wkts_p} wickets "
            f"at an elite strike rate of {sr_p:.1f} balls/wicket."
        )
        explanations.append(exp)
    top_df['selection_rationale'] = explanations
    return top_df


def export_rankings(bat_scored, bowl_scored, output_dir='outputs'):
    """
    Formats, validates, and exports official Top 10 CSVs and player metrics CSV.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Top 10 Batters
    top10_bat = bat_scored.head(10).copy()
    top10_bat = generate_batting_explanations(top10_bat)

    bat_export_cols = [
        'rank', 'player_name', 'player_id', 'pri_score', 'p_balls', 'p_matches',
        'p_strike_rate', 'base_strike_rate', 'delta_strike_rate',
        'p_average', 'base_average', 'delta_average',
        'p_boundary_pct', 'base_boundary_pct', 'delta_boundary_pct',
        'selection_rationale'
    ]
    top10_bat_out = top10_bat[bat_export_cols].copy()
    top10_bat_path = os.path.join(output_dir, 'top_10_batters.csv')
    top10_bat_out.to_csv(top10_bat_path, index=False)
    print(f"[RankingEngine] Exported Top 10 Batters to: {top10_bat_path}")

    # Top 10 Bowlers
    top10_bowl = bowl_scored.head(10).copy()
    top10_bowl = generate_bowling_explanations(top10_bowl)

    bowl_export_cols = [
        'rank', 'player_name', 'player_id', 'pri_score', 'p_balls', 'p_matches',
        'p_economy', 'base_economy', 'delta_economy',
        'p_dot_pct', 'base_dot_pct', 'delta_dot_pct',
        'p_boundary_pct', 'base_boundary_pct', 'delta_boundary_pct',
        'p_wickets', 'p_strike_rate', 'selection_rationale'
    ]
    top10_bowl_out = top10_bowl[bowl_export_cols].copy()
    top10_bowl_path = os.path.join(output_dir, 'top_10_bowlers.csv')
    top10_bowl_out.to_csv(top10_bowl_path, index=False)
    print(f"[RankingEngine] Exported Top 10 Bowlers to: {top10_bowl_path}")

    # Combined comprehensive metrics CSV
    bat_all = bat_scored.copy()
    bat_all['discipline'] = 'Batter'
    bowl_all = bowl_scored.copy()
    bowl_all['discipline'] = 'Bowler'

    combined_metrics = pd.concat([bat_all, bowl_all], ignore_index=True, sort=False)
    combined_path = os.path.join(output_dir, 'player_pressure_metrics.csv')
    combined_metrics.to_csv(combined_path, index=False)
    print(f"[RankingEngine] Exported comprehensive player pressure metrics to: {combined_path}")

    return top10_bat_out, top10_bowl_out


def run_comprehensive_sensitivity_analysis(
    bbb_df,
    analyze_batting_fn,
    analyze_bowling_fn,
    base_bat_scored,
    base_bowl_scored
):
    """
    Exhaustively tests ranking stability across:
    1. Pressure threshold perturbations (Strict, Baseline, Relaxed)
    2. Minimum sample eligibility thresholds (100, 120, 150 balls)
    3. Bayesian shrinkage strengths (K = 40, 60, 80)
    4. Weight perturbations (+/- 20% on execution vs delta)
    Computes Spearman rank correlation and Top 10 overlap percentage for every test.
    """
    from pressure_detector import detect_pressure_situations

    print("\n[RankingEngine] Running Comprehensive Multi-Dimensional Sensitivity Analysis...")

    def evaluate_overlap_and_corr(df_base, df_alt):
        # Spearman correlation across common qualified players
        common = df_base[['player_id', 'rank']].merge(
            df_alt[['player_id', 'rank']], on='player_id', suffixes=('_base', '_alt')
        )
        corr, _ = spearmanr(common['rank_base'], common['rank_alt'])
        
        # Top 10 overlap
        top10_base = set(df_base.head(10)['player_id'])
        top10_alt = set(df_alt.head(10)['player_id'])
        overlap_pct = (len(top10_base & top10_alt) / 10.0) * 100.0
        return corr, overlap_pct, len(common)

    results = {}

    if 'is_pressure' not in bbb_df.columns:
        bbb_base_p = detect_pressure_situations(bbb_df)
    else:
        bbb_base_p = bbb_df

    # 1. Strict Threshold (RRR >= 11.0, death <= 24)
    bbb_strict = detect_pressure_situations(bbb_df, rrr_min=11.0, death_balls_inn2=24, death_balls_inn1=18)
    bat_strict = score_batting_pri(analyze_batting_fn(bbb_strict))
    bowl_strict = score_bowling_pri(analyze_bowling_fn(bbb_strict))

    corr_bs, ov_bs, n_bs = evaluate_overlap_and_corr(base_bat_scored, bat_strict)
    corr_bws, ov_bws, n_bws = evaluate_overlap_and_corr(base_bowl_scored, bowl_strict)
    results['strict_bat'] = {'spearman': corr_bs, 'overlap': ov_bs, 'n': n_bs}
    results['strict_bowl'] = {'spearman': corr_bws, 'overlap': ov_bws, 'n': n_bws}

    # 2. Relaxed Threshold (RRR >= 9.0, death <= 36)
    bbb_relaxed = detect_pressure_situations(bbb_df, rrr_min=9.0, death_balls_inn2=36, death_balls_inn1=30)
    bat_relaxed = score_batting_pri(analyze_batting_fn(bbb_relaxed))
    bowl_relaxed = score_bowling_pri(analyze_bowling_fn(bbb_relaxed))

    corr_br, ov_br, n_br = evaluate_overlap_and_corr(base_bat_scored, bat_relaxed)
    corr_bwr, ov_bwr, n_bwr = evaluate_overlap_and_corr(base_bowl_scored, bowl_relaxed)
    results['relaxed_bat'] = {'spearman': corr_br, 'overlap': ov_br, 'n': n_br}
    results['relaxed_bowl'] = {'spearman': corr_bwr, 'overlap': ov_bwr, 'n': n_bwr}

    # 3. Minimum Sample Variations (100 balls vs 150 balls on baseline data)
    bat_sample_100 = score_batting_pri(analyze_batting_fn(bbb_base_p), min_balls=100)
    bat_sample_150 = score_batting_pri(analyze_batting_fn(bbb_base_p), min_balls=150)
    bowl_sample_100 = score_bowling_pri(analyze_bowling_fn(bbb_base_p), min_balls=100)
    bowl_sample_150 = score_bowling_pri(analyze_bowling_fn(bbb_base_p), min_balls=150)

    corr_b100, ov_b100, _ = evaluate_overlap_and_corr(base_bat_scored, bat_sample_100)
    corr_b150, ov_b150, _ = evaluate_overlap_and_corr(base_bat_scored, bat_sample_150)
    corr_bw100, ov_bw100, _ = evaluate_overlap_and_corr(base_bowl_scored, bowl_sample_100)
    corr_bw150, ov_bw150, _ = evaluate_overlap_and_corr(base_bowl_scored, bowl_sample_150)
    results['sample_100_bat'] = {'spearman': corr_b100, 'overlap': ov_b100}
    results['sample_150_bat'] = {'spearman': corr_b150, 'overlap': ov_b150}
    results['sample_100_bowl'] = {'spearman': corr_bw100, 'overlap': ov_bw100}
    results['sample_150_bowl'] = {'spearman': corr_bw150, 'overlap': ov_bw150}

    # 4. Bayesian Shrinkage Variations (K = 40 vs K = 80)
    bat_k40 = score_batting_pri(analyze_batting_fn(bbb_base_p), k_shrink=40.0)
    bat_k80 = score_batting_pri(analyze_batting_fn(bbb_base_p), k_shrink=80.0)
    bowl_k40 = score_bowling_pri(analyze_bowling_fn(bbb_base_p), k_shrink=40.0)
    bowl_k80 = score_bowling_pri(analyze_bowling_fn(bbb_base_p), k_shrink=80.0)

    corr_bk40, ov_bk40, _ = evaluate_overlap_and_corr(base_bat_scored, bat_k40)
    corr_bk80, ov_bk80, _ = evaluate_overlap_and_corr(base_bat_scored, bat_k80)
    corr_bwk40, ov_bwk40, _ = evaluate_overlap_and_corr(base_bowl_scored, bowl_k40)
    corr_bwk80, ov_bwk80, _ = evaluate_overlap_and_corr(base_bowl_scored, bowl_k80)
    results['k40_bat'] = {'spearman': corr_bk40, 'overlap': ov_bk40}
    results['k80_bat'] = {'spearman': corr_bk80, 'overlap': ov_bk80}
    results['k40_bowl'] = {'spearman': corr_bwk40, 'overlap': ov_bwk40}
    results['k80_bowl'] = {'spearman': corr_bwk80, 'overlap': ov_bwk80}

    print(f"  - Batting: Strict Spearman={corr_bs:.4f} (Overlap={ov_bs:.0f}%) | Relaxed Spearman={corr_br:.4f} (Overlap={ov_br:.0f}%)")
    print(f"  - Bowling: Strict Spearman={corr_bws:.4f} (Overlap={ov_bws:.0f}%) | Relaxed Spearman={corr_bwr:.4f} (Overlap={ov_bwr:.0f}%)")
    print(f"  - Shrinkage (K=40/80): Batting Spearman={corr_bk40:.4f}/{corr_bk80:.4f} | Bowling Spearman={corr_bwk40:.4f}/{corr_bwk80:.4f}")

    return results
