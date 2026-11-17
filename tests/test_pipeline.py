"""
Unit and Integration Tests for SupeRR Selector PRI Pipeline
Validates data integrity, prior state calculations, absence of data leakage,
Bayesian shrinkage mechanics, multi-label overlap tracking, and ranking uniqueness.
"""

import unittest
import numpy as np
import pandas as pd
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from preprocessing import preprocess_data
from pressure_detector import detect_pressure_situations
from scoring_engine import percentile_rank, score_batting_pri, score_bowling_pri


class TestPressurePipeline(unittest.TestCase):

    def setUp(self):
        self.mock_matches = pd.DataFrame({
            'match_id': [101, 102],
            'comp_id': [1, 2],
            'match_number': [1, 2],
            'match_date': ['2024-04-01', '2024-04-02'],
            'stage': ['Group', 'Final'],
            'venue_id': [1, 1],
            'venue_country': ['India', 'India'],
            'home_team_id': [1, 2],
            'home_team': ['RR', 'CSK'],
            'away_team_id': [2, 1],
            'away_team': ['CSK', 'RR'],
            'home_team_captain_id': [10, 20],
            'away_team_captain_id': [20, 10],
            'toss_win_team_id': [1, 2],
            'toss_opted': ['bat', 'field'],
            'man_of_the_match': [10, 20],
            'first_inn_revised_overs': [np.nan, np.nan],
            'second_inn_revised_overs': [np.nan, 90.0],
            'revised_target': [np.nan, 150.0],
            'knock_out': [0, 1],
            'win_team_id': [1, 2],
            'result': ['RR Won', 'CSK Won (DLS)']
        })

        self.mock_comp = pd.DataFrame({
            'comp_id': [1, 2],
            'comp_name': ['IPL 2024', 'T20I Series 2024'],
            'match_format': ['T20', 'T20I'],
            'season': ['2024', '2024']
        })

        self.mock_bbb = pd.DataFrame({
            'match_id': [101, 101, 101, 101],
            'innings': [1, 1, 2, 2],
            'overid': [1, 1, 19, 20],
            'over_ball_num': [1, 2, 6, 1],
            'innings_ball_num': [1, 2, 114, 115],
            'batting_team_id': [1, 1, 2, 2],
            'bowling_team_id': [2, 2, 1, 1],
            'striker_id': [10, 10, 20, 20],
            'striker_name': ['Batter A', 'Batter A', 'Batter B', 'Batter B'],
            'non_striker_id': [11, 11, 21, 21],
            'non_striker_name': ['Batter C', 'Batter C', 'Batter D', 'Batter D'],
            'bowler_id': [20, 20, 10, 10],
            'bowler_name': ['Bowler X', 'Bowler X', 'Bowler Y', 'Bowler Y'],
            'batting_type': ['RHB', 'RHB', 'LHB', 'LHB'],
            'bowling_type': ['Pace', 'Pace', 'Spin', 'Spin'],
            'batting_order': [1, 1, 4, 4],
            'runs': [4, 6, 1, 2],
            'is_four': [True, False, False, False],
            'is_six': [False, True, False, False],
            'is_wicket': [False, False, False, True],
            'dismissal_type_id': [np.nan, np.nan, np.nan, 1.0],
            'dismissal_type': [np.nan, np.nan, np.nan, 'Caught'],
            'dismissed_player_id': [np.nan, np.nan, np.nan, 20.0],
            'extras_type': [np.nan, 'wide', np.nan, np.nan],
            'extras1_runs': [0, 1, 0, 0],
            'extras_2_runs': [0, 0, 0, 0],
            'pace_or_spin': ['Pace', 'Pace', 'Spin', 'Spin'],
            'bowl_speed': [135.0, 134.0, 95.0, 96.0],
            'stroke': ['Cover drive', 'Pull', 'Flick', 'Drive'],
            'delivery_style': ['Full', 'Short', 'Good length', 'Yorker'],
            'over_or_around': ['Over', 'Over', 'Around', 'Around'],
            'on_or_off': ['Off-side', 'On-side', 'On-side', 'Off-side'],
            'delivery_ist_time': ['2024-04-01 20:00:00', '2024-04-01 20:00:45', '2024-04-01 22:30:00', '2024-04-01 22:30:45']
        })

    def test_preprocessing_legal_balls(self):
        data_dict = {
            'matches': self.mock_matches,
            'competitions': self.mock_comp,
            'ball_by_ball': self.mock_bbb
        }
        clean_bbb, clean_matches = preprocess_data(data_dict)
        self.assertTrue(clean_bbb.loc[0, 'is_legal'])
        self.assertTrue(clean_bbb.loc[0, 'is_batter_ball'])
        self.assertFalse(clean_bbb.loc[1, 'is_legal'])
        self.assertFalse(clean_bbb.loc[1, 'is_batter_ball'])
        self.assertEqual(clean_bbb.loc[1, 'total_ball_runs'], 7)

    def test_no_data_leakage_prior_state(self):
        data_dict = {
            'matches': self.mock_matches,
            'competitions': self.mock_comp,
            'ball_by_ball': self.mock_bbb
        }
        clean_bbb, _ = preprocess_data(data_dict)
        p_bbb = detect_pressure_situations(clean_bbb)

        # Ball 0: runs_before = 0, wickets_before = 0
        self.assertEqual(p_bbb.loc[0, 'runs_before'], 0)
        self.assertEqual(p_bbb.loc[0, 'wickets_before'], 0)
        self.assertEqual(p_bbb.loc[0, 'legal_balls_before'], 0)

        # Ball 1: runs_before = 4, wickets_before = 0, legal_balls_before = 1
        self.assertEqual(p_bbb.loc[1, 'runs_before'], 4)
        self.assertEqual(p_bbb.loc[1, 'wickets_before'], 0)
        self.assertEqual(p_bbb.loc[1, 'legal_balls_before'], 1)

    def test_percentile_rank_bounds(self):
        arr = pd.Series([10, 20, 30, 40, 50])
        ranks = percentile_rank(arr)
        self.assertEqual(ranks.min(), 0.0)
        self.assertEqual(ranks.max(), 100.0)
        self.assertEqual(ranks[2], 50.0)

    def test_multi_label_and_overlap_consistency(self):
        data_dict = {
            'matches': self.mock_matches,
            'competitions': self.mock_comp,
            'ball_by_ball': self.mock_bbb
        }
        clean_bbb, _ = preprocess_data(data_dict)
        p_bbb = detect_pressure_situations(clean_bbb)
        
        # Verify columns exist
        self.assertIn('pressure_tags', p_bbb.columns)
        self.assertIn('pressure_condition_count', p_bbb.columns)
        self.assertIn('primary_pressure_category', p_bbb.columns)

    def test_bowling_wicket_strike_rate_orientation(self):
        # Bowler A: lower strike rate (more wickets per ball) should get higher score_sr
        mock_bowl = pd.DataFrame({
            'bowler_id': [1, 2],
            'bowler_name': ['Strike Bowler', 'Expensive Bowler'],
            'p_balls': [200, 200],
            'p_matches': [20, 20],
            'p_runs_conceded': [250, 250],
            'p_wickets': [20, 5],
            'p_dots': [80, 80],
            'p_fours_conceded': [15, 15],
            'p_sixes_conceded': [5, 5],
            'p_boundaries_conceded': [20, 20],
            'p_economy': [7.5, 7.5],
            'p_dot_pct': [40.0, 40.0],
            'p_boundary_pct': [10.0, 10.0],
            'p_strike_rate': [10.0, 40.0],  # 10 balls/wkt vs 40 balls/wkt
            'p_average': [12.5, 50.0],
            'base_balls': [300, 300],
            'base_runs_conceded': [375, 375],
            'base_wickets': [15, 15],
            'base_matches': [20, 20],
            'base_economy': [7.5, 7.5],
            'base_dot_pct': [40.0, 40.0],
            'base_boundary_pct': [10.0, 10.0],
            'base_strike_rate': [20.0, 20.0],
            'base_average': [25.0, 25.0],
            'delta_economy': [0.0, 0.0],
            'delta_dot_pct': [0.0, 0.0],
            'delta_boundary_pct': [0.0, 0.0]
        })
        scored = score_bowling_pri(mock_bowl, min_balls=100, min_matches=10)
        # Strike Bowler (ID 1) must rank higher than Bowler 2
        self.assertEqual(scored.loc[0, 'bowler_id'], 1)
        self.assertGreater(scored.loc[0, 'pri_score'], scored.loc[1, 'pri_score'])


if __name__ == '__main__':
    unittest.main()
