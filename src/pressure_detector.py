"""
Pressure Detector Module for SupeRR Selector Season 2
Evaluates delivery-level leverage and identifies high-pressure match situations
strictly prior to each ball being bowled (zero data leakage).
Handles multi-label condition overlaps and provides transparent categorization.
"""

import pandas as pd
import numpy as np


def detect_pressure_situations(
    bbb_df,
    rrr_min=10.0,
    rrr_max=24.0,
    death_balls_inn2=30,
    death_runs_inn2=60,
    death_balls_inn1=24,
    early_collapse_balls=48,
    early_collapse_wickets=3
):
    """
    Computes prior match state and flags high-pressure deliveries.
    Provides explicit individual condition flags, primary category hierarchy,
    and transparent multi-label overlap tracking.
    """
    df = bbb_df.copy()

    # Ensure clean chronological sorting by match, innings, and ball sequence
    df.sort_values(by=['match_id', 'innings', 'overid', 'over_ball_num'], inplace=True)
    df.reset_index(drop=True, inplace=True)

    grouped = df.groupby(['match_id', 'innings'])

    # Vectorized prior state calculation (strictly prior to current delivery)
    df['runs_before'] = grouped['total_ball_runs'].cumsum() - df['total_ball_runs']
    df['wickets_before'] = grouped['is_wicket'].cumsum() - df['is_wicket'].astype(int)
    df['legal_balls_before'] = grouped['is_legal'].cumsum() - df['is_legal'].astype(int)

    df['wickets_in_hand'] = np.maximum(0, 10 - df['wickets_before'])

    # Balls remaining & required rates per innings
    df['balls_remaining_inn1'] = np.maximum(0, df['max_balls_inn1'] - df['legal_balls_before'])
    df['balls_remaining_inn2'] = np.maximum(0, df['max_balls_inn2'] - df['legal_balls_before'])

    df['runs_needed'] = np.maximum(0, df['effective_target'] - df['runs_before'])

    # Required Run Rate for Innings 2 (only valid when balls remain and target is known)
    is_inn2 = df['innings'] == 2
    df['rrr'] = np.where(
        is_inn2 & (df['balls_remaining_inn2'] > 0),
        (df['runs_needed'] / df['balls_remaining_inn2']) * 6.0,
        np.nan
    )

    # 1. Individual Explicit Pressure Conditions
    # A. Super Overs (innings > 2)
    df['p_super_over'] = df['innings'] > 2

    # B. Innings 2: High RRR Escalation
    df['p_chase_high_rrr'] = (
        is_inn2 &
        (df['rrr'] >= rrr_min) &
        (df['rrr'] <= rrr_max) &
        (df['wickets_in_hand'] >= 2)
    )

    # C. Innings 2: Death Overs Close Chase
    df['p_chase_death_close'] = (
        is_inn2 &
        (df['balls_remaining_inn2'] <= death_balls_inn2) &
        (df['runs_needed'] <= death_runs_inn2) &
        (df['runs_needed'] > 0) &
        (df['rrr'] >= 7.0) &
        (df['rrr'] <= rrr_max)
    )

    # D. Innings 2: Chase Collapse
    df['p_chase_collapse'] = (
        is_inn2 &
        (df['wickets_in_hand'] <= 4) &
        (df['wickets_in_hand'] >= 1) &
        (df['runs_needed'] >= 25) &
        (df['rrr'] <= rrr_max)
    )

    # E. Innings 1: Top-Order Powerplay Rebuild
    is_inn1 = df['innings'] == 1
    df['p_target_early_collapse'] = (
        is_inn1 &
        (df['legal_balls_before'] <= early_collapse_balls) &
        (df['wickets_before'] >= early_collapse_wickets)
    )

    # F. Innings 1: Death Acceleration Climax
    df['p_target_death_accel'] = (
        is_inn1 &
        (df['balls_remaining_inn1'] <= death_balls_inn1) &
        (df['wickets_in_hand'] >= 3)
    )

    # Union boolean flag (strictly unique deliveries)
    df['is_pressure'] = (
        df['p_super_over'] |
        df['p_chase_high_rrr'] |
        df['p_chase_death_close'] |
        df['p_chase_collapse'] |
        df['p_target_early_collapse'] |
        df['p_target_death_accel']
    )

    # Number of concurrent pressure conditions satisfied
    cond_cols = [
        'p_super_over', 'p_chase_high_rrr', 'p_chase_death_close',
        'p_chase_collapse', 'p_target_early_collapse', 'p_target_death_accel'
    ]
    df['pressure_condition_count'] = df[cond_cols].sum(axis=1)

    # Hierarchical Primary Category Assignment (Rigorous Priority Order)
    # Priority: Super_Over > Chase_Death_Close > Chase_Collapse > Chase_High_RRR > Target_Early_Collapse > Target_Death_Accel
    df['primary_pressure_category'] = 'Normal'
    df.loc[df['p_target_death_accel'], 'primary_pressure_category'] = 'Target_Death_Acceleration'
    df.loc[df['p_target_early_collapse'], 'primary_pressure_category'] = 'Target_Early_Collapse'
    df.loc[df['p_chase_high_rrr'], 'primary_pressure_category'] = 'Chase_High_RRR'
    df.loc[df['p_chase_collapse'], 'primary_pressure_category'] = 'Chase_Collapse'
    df.loc[df['p_chase_death_close'], 'primary_pressure_category'] = 'Chase_Death_Close'
    df.loc[df['p_super_over'], 'primary_pressure_category'] = 'Super_Over'

    # Retain pressure_context for backward compatibility
    df['pressure_context'] = df['primary_pressure_category']

    # Transparent multi-label string listing all matching tags
    tags = []
    for _, row in df[df['is_pressure']][cond_cols].iterrows():
        active = [c.replace('p_', '') for c in cond_cols if row[c]]
        tags.append(';'.join(active))
    df['pressure_tags'] = 'Normal'
    df.loc[df['is_pressure'], 'pressure_tags'] = tags

    unique_pressure = df['is_pressure'].sum()
    sum_individual = df[cond_cols].sum().sum()
    pct = (unique_pressure / len(df)) * 100

    print(f"[PressureDetector] Processed {len(df):,} deliveries.")
    print(f"  - Unique High-Pressure Deliveries: {unique_pressure:,} ({pct:.2f}%)")
    print(f"  - Sum of Individual Category Activations: {sum_individual:,}")
    print(f"  - Net Overlapping Condition Activations: {sum_individual - unique_pressure:,}")

    return df
