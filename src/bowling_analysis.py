"""
Bowling Analysis Module for SupeRR Selector Season 2
Computes pressure and baseline bowling metrics, delta resilience, and competition splits.
"""

import pandas as pd
import numpy as np


def analyze_bowling_performance(df_bbb):
    """
    Aggregates delivery-level records into player-level bowling profiles,
    comparing pressure performance against normal baseline performance.
    """
    df = df_bbb.copy()

    # Bowler legal deliveries
    legal_df = df[df['is_legal']].copy()

    # 1. Aggregate Pressure Bowling Metrics
    p_df = legal_df[legal_df['is_pressure']]
    p_stats = p_df.groupby(['bowler_id', 'bowler_name']).agg(
        p_balls=('bowler_runs_conceded', 'count'),
        p_runs_conceded=('bowler_runs_conceded', 'sum'),
        p_wickets=('is_bowler_wicket', 'sum'),
        p_dots=('is_bowler_dot', 'sum'),
        p_fours_conceded=('is_four', 'sum'),
        p_sixes_conceded=('is_six', 'sum'),
        p_boundaries_conceded=('is_boundary', 'sum'),
        p_matches=('match_id', 'nunique'),
        p_ipl_balls=('is_ipl', lambda x: x.sum()),
        p_t20i_balls=('competition_type', lambda x: (x == 'T20I').sum())
    ).reset_index()

    p_stats['p_economy'] = (p_stats['p_runs_conceded'] / np.maximum(1, p_stats['p_balls'])) * 6.0
    p_stats['p_dot_pct'] = (p_stats['p_dots'] / np.maximum(1, p_stats['p_balls'])) * 100.0
    p_stats['p_boundary_pct'] = (p_stats['p_boundaries_conceded'] / np.maximum(1, p_stats['p_balls'])) * 100.0
    p_stats['p_strike_rate'] = p_stats['p_balls'] / np.maximum(1, p_stats['p_wickets'])
    p_stats['p_average'] = p_stats['p_runs_conceded'] / np.maximum(1, p_stats['p_wickets'])

    # 2. Aggregate Normal (Baseline) Bowling Metrics
    b_df = legal_df[~legal_df['is_pressure']]
    b_stats = b_df.groupby(['bowler_id', 'bowler_name']).agg(
        base_balls=('bowler_runs_conceded', 'count'),
        base_runs_conceded=('bowler_runs_conceded', 'sum'),
        base_wickets=('is_bowler_wicket', 'sum'),
        base_dots=('is_bowler_dot', 'sum'),
        base_fours_conceded=('is_four', 'sum'),
        base_sixes_conceded=('is_six', 'sum'),
        base_boundaries_conceded=('is_boundary', 'sum'),
        base_matches=('match_id', 'nunique')
    ).reset_index()

    b_stats['base_economy'] = (b_stats['base_runs_conceded'] / np.maximum(1, b_stats['base_balls'])) * 6.0
    b_stats['base_dot_pct'] = (b_stats['base_dots'] / np.maximum(1, b_stats['base_balls'])) * 100.0
    b_stats['base_boundary_pct'] = (b_stats['base_boundaries_conceded'] / np.maximum(1, b_stats['base_balls'])) * 100.0
    b_stats['base_strike_rate'] = b_stats['base_balls'] / np.maximum(1, b_stats['base_wickets'])
    b_stats['base_average'] = b_stats['base_runs_conceded'] / np.maximum(1, b_stats['base_wickets'])

    # 3. Merge Pressure and Baseline Profiles
    bowl_profile = p_stats.merge(
        b_stats[['bowler_id', 'base_balls', 'base_runs_conceded', 'base_wickets', 'base_matches',
                 'base_economy', 'base_dot_pct', 'base_boundary_pct', 'base_strike_rate', 'base_average']],
        on='bowler_id',
        how='left'
    )

    # Impute missing baselines
    bowl_profile['base_balls'] = bowl_profile['base_balls'].fillna(0).astype(int)
    bowl_profile['base_runs_conceded'] = bowl_profile['base_runs_conceded'].fillna(0).astype(int)
    bowl_profile['base_wickets'] = bowl_profile['base_wickets'].fillna(0).astype(int)
    bowl_profile['base_matches'] = bowl_profile['base_matches'].fillna(0).astype(int)
    bowl_profile['base_economy'] = bowl_profile['base_economy'].fillna(bowl_profile['p_economy'])
    bowl_profile['base_dot_pct'] = bowl_profile['base_dot_pct'].fillna(bowl_profile['p_dot_pct'])
    bowl_profile['base_boundary_pct'] = bowl_profile['base_boundary_pct'].fillna(bowl_profile['p_boundary_pct'])
    bowl_profile['base_strike_rate'] = bowl_profile['base_strike_rate'].fillna(bowl_profile['p_strike_rate'])
    bowl_profile['base_average'] = bowl_profile['base_average'].fillna(bowl_profile['p_average'])

    # 4. Compute Delta Resilience Metrics
    # Note: Positive delta_economy is favorable (economy improves/drops under pressure!)
    bowl_profile['delta_economy'] = bowl_profile['base_economy'] - bowl_profile['p_economy']
    bowl_profile['delta_dot_pct'] = bowl_profile['p_dot_pct'] - bowl_profile['base_dot_pct']
    bowl_profile['delta_boundary_pct'] = bowl_profile['base_boundary_pct'] - bowl_profile['p_boundary_pct']

    # Rename bowler columns to standard player columns
    bowl_profile.rename(columns={'bowler_id': 'player_id', 'bowler_name': 'player_name'}, inplace=True)

    print(f"[BowlingAnalysis] Evaluated bowling profiles for {len(bowl_profile):,} players.")
    return bowl_profile
