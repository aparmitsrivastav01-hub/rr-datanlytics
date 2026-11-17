"""
Scoring Engine Module for SupeRR Selector Season 2
Implements empirical Bayesian shrinkage, percentile standardization,
and composite PRI index computation for batters and bowlers.
Updated to incorporate Wicket Strike Rate for bowlers and shrunk delta metrics.
"""

import numpy as np
import pandas as pd
from scipy.stats import rankdata


def percentile_rank(series):
    """
    Computes strict percentile ranks scaled 0 to 100.
    Handles single-value or identical arrays safely.
    """
    n = len(series)
    if n <= 1:
        return pd.Series(50.0, index=series.index)
    ranks = rankdata(series, method='average')
    return ((ranks - 1.0) / (n - 1.0)) * 100.0


def score_batting_pri(
    bat_df,
    min_balls=120,
    min_matches=15,
    k_shrink=60.0,
    weights=None
):
    """
    Computes Batting Pressure Reliability Index (PRI-Bat) on 0-100 scale.
    Uses Bayesian-shrunk execution metrics and shrunk resilience deltas.
    """
    if weights is None:
        weights = {
            'w_sr': 0.25,
            'w_bp': 0.15,
            'w_avg': 0.10,
            'w_delta_sr': 0.20,
            'w_delta_avg': 0.15,
            'w_exposure': 0.15
        }

    # Filter eligible pool
    df = bat_df[(bat_df['p_balls'] >= min_balls) & (bat_df['p_matches'] >= min_matches)].copy()
    if df.empty:
        raise ValueError("[ScoringEngine] No batters meet the eligibility criteria.")

    # Cohort means for Bayesian shrinkage
    cohort_sr = (df['p_runs'].sum() / df['p_balls'].sum()) * 100.0
    cohort_bp = (df['p_boundaries'].sum() / df['p_balls'].sum()) * 100.0
    cohort_avg = df['p_runs'].sum() / np.maximum(1, df['p_dismissals'].sum())

    # Bayesian shrinkage factor based on sample size
    w_cred = df['p_balls'] / (df['p_balls'] + k_shrink)
    df['shrunk_sr'] = w_cred * df['p_strike_rate'] + (1 - w_cred) * cohort_sr
    df['shrunk_bp'] = w_cred * df['p_boundary_pct'] + (1 - w_cred) * cohort_bp
    df['shrunk_avg'] = w_cred * df['p_average'] + (1 - w_cred) * cohort_avg

    # Shrunk resilience deltas (protects against small-sample extreme deltas)
    df['shrunk_delta_sr'] = df['shrunk_sr'] - df['base_strike_rate']
    df['shrunk_delta_avg'] = df['shrunk_avg'] - df['base_average']

    # Component standardization (0-100)
    df['score_sr'] = percentile_rank(df['shrunk_sr'])
    df['score_bp'] = percentile_rank(df['shrunk_bp'])
    df['score_avg'] = percentile_rank(df['shrunk_avg'])
    df['score_delta_sr'] = percentile_rank(df['shrunk_delta_sr'])
    df['score_delta_avg'] = percentile_rank(df['shrunk_delta_avg'])

    # Exposure factor: combined balls and distinct matches
    exposure_raw = df['p_balls'] * np.sqrt(df['p_matches'])
    df['score_exposure'] = percentile_rank(exposure_raw)

    # Composite PRI-Bat
    df['pri_score'] = (
        weights['w_sr'] * df['score_sr'] +
        weights['w_bp'] * df['score_bp'] +
        weights['w_avg'] * df['score_avg'] +
        weights['w_delta_sr'] * df['score_delta_sr'] +
        weights['w_delta_avg'] * df['score_delta_avg'] +
        weights['w_exposure'] * df['score_exposure']
    )

    df.sort_values(by='pri_score', ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)
    df['rank'] = df.index + 1

    return df


def score_bowling_pri(
    bowl_df,
    min_balls=120,
    min_matches=15,
    k_shrink=60.0,
    weights=None
):
    """
    Computes Bowling Pressure Reliability Index (PRI-Bowl) on 0-100 scale.
    Statistically complete: incorporates Economy, Dot %, Boundary %, Wicket Strike Rate,
    Economy Delta, Dot Delta, and Exposure Credibility.
    """
    if weights is None:
        weights = {
            'w_econ': 0.20,
            'w_dot': 0.15,
            'w_bcr': 0.10,
            'w_sr': 0.15,
            'w_delta_econ': 0.15,
            'w_delta_dot': 0.10,
            'w_exposure': 0.15
        }

    # Filter eligible pool
    df = bowl_df[(bowl_df['p_balls'] >= min_balls) & (bowl_df['p_matches'] >= min_matches)].copy()
    if df.empty:
        raise ValueError("[ScoringEngine] No bowlers meet the eligibility criteria.")

    # Cohort means for Bayesian shrinkage
    cohort_econ = (df['p_runs_conceded'].sum() / df['p_balls'].sum()) * 6.0
    cohort_dot = (df['p_dots'].sum() / df['p_balls'].sum()) * 100.0
    cohort_bcr = (df['p_boundaries_conceded'].sum() / df['p_balls'].sum()) * 100.0
    cohort_sr = df['p_balls'].sum() / np.maximum(1, df['p_wickets'].sum())

    # Bayesian shrinkage factor based on sample size
    w_cred = df['p_balls'] / (df['p_balls'] + k_shrink)
    df['shrunk_econ'] = w_cred * df['p_economy'] + (1 - w_cred) * cohort_econ
    df['shrunk_dot'] = w_cred * df['p_dot_pct'] + (1 - w_cred) * cohort_dot
    df['shrunk_bcr'] = w_cred * df['p_boundary_pct'] + (1 - w_cred) * cohort_bcr
    df['shrunk_sr'] = w_cred * df['p_strike_rate'] + (1 - w_cred) * cohort_sr

    # Shrunk resilience deltas
    df['shrunk_delta_econ'] = df['base_economy'] - df['shrunk_econ']
    df['shrunk_delta_dot'] = df['shrunk_dot'] - df['base_dot_pct']

    # Component standardization (0-100)
    # Lower economy, boundary concession, and balls per wicket are superior -> inverted percentile rank
    df['score_econ'] = 100.0 - percentile_rank(df['shrunk_econ'])
    df['score_dot'] = percentile_rank(df['shrunk_dot'])
    df['score_bcr'] = 100.0 - percentile_rank(df['shrunk_bcr'])
    df['score_sr'] = 100.0 - percentile_rank(df['shrunk_sr'])  # Lower balls/wicket is better
    df['score_delta_econ'] = percentile_rank(df['shrunk_delta_econ'])
    df['score_delta_dot'] = percentile_rank(df['shrunk_delta_dot'])

    # Exposure factor
    exposure_raw = df['p_balls'] * np.sqrt(df['p_matches'])
    df['score_exposure'] = percentile_rank(exposure_raw)

    # Composite PRI-Bowl
    df['pri_score'] = (
        weights['w_econ'] * df['score_econ'] +
        weights['w_dot'] * df['score_dot'] +
        weights['w_bcr'] * df['score_bcr'] +
        weights['w_sr'] * df['score_sr'] +
        weights['w_delta_econ'] * df['score_delta_econ'] +
        weights['w_delta_dot'] * df['score_delta_dot'] +
        weights['w_exposure'] * df['score_exposure']
    )

    df.sort_values(by='pri_score', ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)
    df['rank'] = df.index + 1

    return df
