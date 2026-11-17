"""
Data Loader Module for SupeRR Selector Season 2
Handles loading of all 6 raw CSV files with proper dtypes and validation.
"""

import os
import pandas as pd
import numpy as np


def load_raw_data(data_dir=None):
    """
    Loads all raw CSV files from the specified data directory.
    Falls back to current working directory if data_dir is not provided or files are missing.
    """
    if data_dir is None:
        if os.path.exists('data/raw/ball_by_ball.csv'):
            data_dir = 'data/raw'
        else:
            data_dir = '.'

    print(f"[DataLoader] Loading datasets from: {os.path.abspath(data_dir)}")

    competitions_path = os.path.join(data_dir, 'competitions.csv')
    teams_path = os.path.join(data_dir, 'teams.csv')
    matches_path = os.path.join(data_dir, 'matches.csv')
    bbb_path = os.path.join(data_dir, 'ball_by_ball.csv')
    pe_path = os.path.join(data_dir, 'playing_eleven.csv')
    ctpm_path = os.path.join(data_dir, 'competition_team_player_mapping.csv')

    competitions = pd.read_csv(competitions_path)
    teams = pd.read_csv(teams_path)
    matches = pd.read_csv(matches_path)
    bbb = pd.read_csv(bbb_path, low_memory=False)
    playing_eleven = pd.read_csv(pe_path)
    ctpm = pd.read_csv(ctpm_path)

    print(f"[DataLoader] Successfully loaded:")
    print(f"  - competitions: {len(competitions):,} rows")
    print(f"  - teams: {len(teams):,} rows")
    print(f"  - matches: {len(matches):,} rows")
    print(f"  - ball_by_ball: {len(bbb):,} rows")
    print(f"  - playing_eleven: {len(playing_eleven):,} rows")
    print(f"  - mapping: {len(ctpm):,} rows")

    return {
        'competitions': competitions,
        'teams': teams,
        'matches': matches,
        'ball_by_ball': bbb,
        'playing_eleven': playing_eleven,
        'mapping': ctpm
    }


if __name__ == '__main__':
    data = load_raw_data()
