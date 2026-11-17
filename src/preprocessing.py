"""
Preprocessing Pipeline for SupeRR Selector Season 2
Cleans, validates, and enhances raw match and ball-by-ball data without data leakage.
"""

import pandas as pd
import numpy as np


def preprocess_data(data_dict):
    """
    Cleans and enhances ball_by_ball data, merges match metadata, and validates integrity.
    """
    matches = data_dict['matches'].copy()
    bbb = data_dict['ball_by_ball'].copy()
    comp = data_dict['competitions'].copy()

    # 1. Clean competitions & merge into matches
    matches = matches.merge(comp[['comp_id', 'comp_name', 'match_format', 'season']], on='comp_id', how='left')
    matches['is_ipl'] = matches['comp_name'].str.contains('IPL', case=False, na=False)
    matches['competition_type'] = np.where(matches['is_ipl'], 'IPL',
                                  np.where(matches['match_format'] == 'T20I', 'T20I', 'Other_T20'))

    # 2. Impute known edge case for dismissed_player_id (Hardik Pandya retire out)
    retire_out_mask = (bbb['is_wicket'] == True) & (bbb['dismissed_player_id'].isnull()) & (bbb['dismissal_type'] == 'Retire Out')
    if retire_out_mask.any():
        bbb.loc[retire_out_mask, 'dismissed_player_id'] = bbb.loc[retire_out_mask, 'striker_id']
        print(f"[Preprocessing] Imputed {retire_out_mask.sum()} missing dismissed_player_id for Retire Out.")

    # 3. Runs and extras calculations
    bbb['extras1_runs'] = bbb['extras1_runs'].fillna(0).astype(int)
    bbb['extras_2_runs'] = bbb['extras_2_runs'].fillna(0).astype(int)
    bbb['total_ball_runs'] = bbb['runs'] + bbb['extras1_runs'] + bbb['extras_2_runs']

    # 4. Ball classification
    # Re-bowled illegal deliveries: wide, Overstep (front-foot no ball), other (full-toss/fielding no ball)
    bbb['is_illegal'] = bbb['extras_type'].isin(['wide', 'Overstep', 'other'])
    bbb['is_legal'] = ~bbb['is_illegal']

    # Batter balls faced: wide is NOT faced by batter; no-balls and byes/leg-byes ARE faced
    bbb['is_batter_ball'] = bbb['extras_type'] != 'wide'

    # Bowler runs conceded: batter runs + wide runs + no-ball penalty extras; byes/leg-byes/penalties excluded
    illegal_extras = np.where(bbb['extras_type'].isin(['wide', 'Overstep', 'other']), bbb['extras1_runs'], 0)
    bbb['bowler_runs_conceded'] = bbb['runs'] + illegal_extras

    # Bowler wickets: exclude RunOut, Retire Out, and Obstructing the field
    non_bowler_dismissals = ['RunOut', 'Retire Out', 'Obstracting the field', 'Obstructing the field']
    bbb['is_bowler_wicket'] = bbb['is_wicket'] & (~bbb['dismissal_type'].isin(non_bowler_dismissals))

    # Dot balls from bowler perspective
    bbb['is_bowler_dot'] = bbb['is_legal'] & (bbb['bowler_runs_conceded'] == 0)

    # Boundaries
    bbb['is_boundary'] = bbb['is_four'] | bbb['is_six']

    # 5. Calculate Innings 1 total runs per match
    inn1_totals = bbb[bbb['innings'] == 1].groupby('match_id')['total_ball_runs'].sum().rename('inn1_total_runs')
    matches = matches.merge(inn1_totals, on='match_id', how='left')

    # 6. Target and scheduled balls calculation
    # For Innings 2: revised_target if present, else inn1_total_runs + 1
    matches['effective_target'] = np.where(
        matches['revised_target'].notnull(),
        matches['revised_target'],
        matches['inn1_total_runs'] + 1
    )

    matches['max_balls_inn2'] = np.where(
        matches['second_inn_revised_overs'].notnull(),
        matches['second_inn_revised_overs'],
        120
    ).astype(int)

    matches['max_balls_inn1'] = np.where(
        matches['first_inn_revised_overs'].notnull(),
        matches['first_inn_revised_overs'],
        120
    ).astype(int)

    # 7. Merge match attributes onto ball_by_ball
    match_cols_to_merge = [
        'match_id', 'comp_id', 'comp_name', 'season', 'match_date', 'competition_type', 'is_ipl',
        'knock_out', 'stage', 'effective_target', 'max_balls_inn1', 'max_balls_inn2'
    ]
    bbb = bbb.merge(matches[match_cols_to_merge], on='match_id', how='left')

    # 8. Chronological sorting
    bbb.sort_values(by=['match_id', 'innings', 'overid', 'over_ball_num'], inplace=True)
    bbb.reset_index(drop=True, inplace=True)

    print(f"[Preprocessing] Preprocessing completed. {len(bbb):,} deliveries processed and ordered.")
    return bbb, matches
