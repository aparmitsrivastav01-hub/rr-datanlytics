"""
Batting Analysis Module for SupeRR Selector Season 2
Computes pressure and baseline batting metrics, delta resilience, and competition splits.
"""

import pandas as pd
import numpy as np


def analyze_batting_performance(df_bbb):
    """
    Aggregates delivery-level records into player-level batting profiles,
    comparing pressure performance against normal baseline performance.
    """
    df = df_bbb.copy()

    # Batter balls faced are deliveries where extras_type is NOT 'wide'
    batter_balls = df[df['is_batter_ball']].copy()

    # 1. Aggregate Pressure Batting Metrics
    p_df = batter_balls[batter_balls['is_pressure']]
    p_stats = p_df.groupby(['striker_id', 'striker_name']).agg(
        p_balls=('runs', 'count'),
        p_runs=('runs', 'sum'),
        p_fours=('is_four', 'sum'),
        p_sixes=('is_six', 'sum'),
        p_boundaries=('is_boundary', 'sum'),
        p_dots=('runs', lambda x: (x == 0).sum()),
        p_matches=('match_id', 'nunique'),
        p_ipl_balls=('is_ipl', lambda x: x.sum()),
        p_t20i_balls=('competition_type', lambda x: (x == 'T20I').sum())
    ).reset_index()

    # Track dismissals under pressure by dismissed_player_id
    p_wickets = df[df['is_pressure'] & df['is_wicket']]['dismissed_player_id'].value_counts().rename('p_dismissals')
    p_stats = p_stats.merge(p_wickets, left_on='striker_id', right_index=True, how='left')
    p_stats['p_dismissals'] = p_stats['p_dismissals'].fillna(0).astype(int)

    p_stats['p_strike_rate'] = (p_stats['p_runs'] / np.maximum(1, p_stats['p_balls'])) * 100.0
    p_stats['p_boundary_pct'] = (p_stats['p_boundaries'] / np.maximum(1, p_stats['p_balls'])) * 100.0
    p_stats['p_dot_pct'] = (p_stats['p_dots'] / np.maximum(1, p_stats['p_balls'])) * 100.0
    p_stats['p_average'] = p_stats['p_runs'] / np.maximum(1, p_stats['p_dismissals'])

    # 2. Aggregate Normal (Baseline) Batting Metrics
    b_df = batter_balls[~batter_balls['is_pressure']]
    b_stats = b_df.groupby(['striker_id', 'striker_name']).agg(
        base_balls=('runs', 'count'),
        base_runs=('runs', 'sum'),
        base_fours=('is_four', 'sum'),
        base_sixes=('is_six', 'sum'),
        base_boundaries=('is_boundary', 'sum'),
        base_dots=('runs', lambda x: (x == 0).sum()),
        base_matches=('match_id', 'nunique')
    ).reset_index()

    b_wickets = df[(~df['is_pressure']) & df['is_wicket']]['dismissed_player_id'].value_counts().rename('base_dismissals')
    b_stats = b_stats.merge(b_wickets, left_on='striker_id', right_index=True, how='left')
    b_stats['base_dismissals'] = b_stats['base_dismissals'].fillna(0).astype(int)

    b_stats['base_strike_rate'] = (b_stats['base_runs'] / np.maximum(1, b_stats['base_balls'])) * 100.0
    b_stats['base_boundary_pct'] = (b_stats['base_boundaries'] / np.maximum(1, b_stats['base_balls'])) * 100.0
    b_stats['base_dot_pct'] = (b_stats['base_dots'] / np.maximum(1, b_stats['base_balls'])) * 100.0
    b_stats['base_average'] = b_stats['base_runs'] / np.maximum(1, b_stats['base_dismissals'])

    # 3. Merge Pressure and Baseline Profiles
    bat_profile = p_stats.merge(
        b_stats[['striker_id', 'base_balls', 'base_runs', 'base_dismissals', 'base_matches',
                 'base_strike_rate', 'base_boundary_pct', 'base_dot_pct', 'base_average']],
        on='striker_id',
        how='left'
    )

    # Impute missing baselines for rare single-match players
    bat_profile['base_balls'] = bat_profile['base_balls'].fillna(0).astype(int)
    bat_profile['base_runs'] = bat_profile['base_runs'].fillna(0).astype(int)
    bat_profile['base_dismissals'] = bat_profile['base_dismissals'].fillna(0).astype(int)
    bat_profile['base_matches'] = bat_profile['base_matches'].fillna(0).astype(int)
    bat_profile['base_strike_rate'] = bat_profile['base_strike_rate'].fillna(bat_profile['p_strike_rate'])
    bat_profile['base_boundary_pct'] = bat_profile['base_boundary_pct'].fillna(bat_profile['p_boundary_pct'])
    bat_profile['base_dot_pct'] = bat_profile['base_dot_pct'].fillna(bat_profile['p_dot_pct'])
    bat_profile['base_average'] = bat_profile['base_average'].fillna(bat_profile['p_average'])

    # 4. Compute Delta Resilience Metrics
    bat_profile['delta_strike_rate'] = bat_profile['p_strike_rate'] - bat_profile['base_strike_rate']
    bat_profile['delta_boundary_pct'] = bat_profile['p_boundary_pct'] - bat_profile['base_boundary_pct']
    bat_profile['delta_average'] = bat_profile['p_average'] - bat_profile['base_average']

    # Rename striker columns to standard player columns
    bat_profile.rename(columns={'striker_id': 'player_id', 'striker_name': 'player_name'}, inplace=True)

    print(f"[BattingAnalysis] Evaluated batting profiles for {len(bat_profile):,} players.")
    return bat_profile
