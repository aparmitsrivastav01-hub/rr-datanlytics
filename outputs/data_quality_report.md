# Data Quality and Preprocessing Audit Report (Audited Edition)
**Project:** SupeRR Selector Season 2 — Round 1: Pressure Reliability Index (PRI)  
**Author:** Sports Analytics & Cricket Data Science Team  
**Date:** November 2026  
**Status:** Validated, Audited & Certified  

---

## 1. Executive Summary

This report documents the end-to-end data profile, referential integrity audit, and anomaly log for the Unstop SupeRR Selector Season 2 dataset. Historical ball-by-ball records, match metadata, competition formats, team rosters, and playing XI structures from 2022 through 2026 were rigorously inspected and audited.

All findings are derived directly from the raw files without prior assumptions. Zero records have been silently dropped; every exclusion, correction, and edge-case handling is explicitly quantified and justified.

---

## 2. Dataset Overview & Dimensions

The dataset consists of 6 core CSV files spanning T20 cricket across the Indian Premier League (IPL) and official ICC T20 Internationals (T20I), plus Men's Emerging / Rising Stars T20 tournaments between **January 22, 2022** and **November 1, 2026**.

| File Name | Row Count | Column Count | Primary Key / Grain | Missing Cells (%) | Duplicate Rows |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `competitions.csv` | 141 | 4 | `comp_id` | 0.0% | 0 |
| `teams.csv` | 353 | 3 | `comp_id` + `team_id` | 0.0% | 0 |
| `matches.csv` | 883 | 22 | `match_id` | 27.5% (mostly revised target cols) | 0 |
| `ball_by_ball.csv` | 200,999 | 33 | `match_id` + `innings` + `innings_ball_num` | 16.5% (extras & dismissals) | 0 |
| `playing_eleven.csv` | 28,381 | 9 | `match_id` + `team_id` + `player_id` | 14.8% (captain/wk/order for non-players) | 0 |
| `competition_team_player_mapping.csv` | 6,413 | 6 | `comp_id` + `team_id` + `player_id` | 0.0% | 0 |

---

## 3. Competition & Match Profile

### 3.1 Format & Competition Breakdown
Cross-referencing `matches.csv` with `competitions.csv`:
- **IPL Matches:** 371 matches across 5 editions:
  - IPL 2022: 74 matches
  - IPL 2023: 74 matches
  - IPL 2024: 74 matches
  - IPL 2025: 75 matches
  - IPL 2026: 74 matches
- **T20I Matches:** 482 matches across 134 bilateral series, multi-nation tournaments, and ICC World Cups.
- **Other T20 Matches:** 30 matches (Mens T20 Emerging Teams Asia Cup 2024: 15 matches; Asia Cup Rising Stars 2025: 15 matches).
- **Total Matches in Metadata:** 883 matches.

### 3.2 Match Status & Ball-by-Ball Coverage Discrepancies
- **Matches with Ball-by-Ball Records:** 867 matches.
- **Matches without Ball-by-Ball Records:** 16 matches.
  - *Audit Finding:* All 16 missing matches carry `result: "Match Abandoned"` (e.g., Match IDs `31281`, `31284`, `31288`, `32610`, `32612`, `36564`, etc.). Because matches were called off before the toss or without a single ball bowled, zero deliveries were recorded. This accounts for 100% of the discrepancy between `matches.csv` and `ball_by_ball.csv`.
- **Incomplete Matches in Ball-by-Ball:**
  - **22 matches** contain only 1 innings (weather interrupted mid-match). Deliveries bowled in these innings represent legitimate play for individual player baselines, but Innings 2 chase pressure cannot be evaluated.
  - **6 matches** progressed to Super Overs (`innings` 3 and 4; 38 deliveries total).
  - **839 matches** contain exactly 2 completed/full innings.

### 3.3 Shortened Matches & Revised Targets (DLS)
- **23 matches** had revised targets and/or shortened overs.
- *Critical Data Definition Insight:* In `matches.csv`, `first_inn_revised_overs` and `second_inn_revised_overs` record the scheduled duration **in legal balls** (e.g., 114.0 balls = 19.0 overs; 90.0 balls = 15.0 overs in IPL 2023 final Match 21586).
- *Handling Rule:* In Innings 2, when `revised_target` is present, the target is `revised_target` and maximum scheduled balls is `second_inn_revised_overs`. When absent, target is `inn1_total_runs + 1` and maximum scheduled balls is 120 (20 overs).

---

## 4. Ball-by-Ball Integrity & Metric Definitions

### 4.1 Legal Ball Classification
A delivery is counted towards legal balls bowled and legal balls remaining if and only if it does **not** grant an extra ball:
- **Illegal Deliveries (re-bowled):**
  - `wide` (7,714 deliveries)
  - `Overstep` (576 deliveries — front-foot no-balls)
  - `other` (264 deliveries — waist-high full tosses and fielding restriction no-balls)
- **Legal Deliveries:**
  - Standard balls (189,167 deliveries)
  - `legbyes` (2,748 deliveries)
  - `byes` (529 deliveries)
  - `Penalty` (1 delivery — 5 penalty runs, Match `16753`)
- **Total Legal Deliveries:** 192,445 deliveries.

### 4.2 Batting vs Bowling Metric Assignment
- **Batter Balls Faced:** Deliveries where `extras_type != 'wide'`.
- **Batter Runs:** Strictly `runs`.
- **Bowler Runs Conceded:** `runs` + wide runs + no-ball penalties (`extras1_runs` for `wide`, `Overstep`, `other`). Byes, leg-byes, and penalties excluded per official MCC laws.
- **Bowler Wickets:** Wickets credited to the bowler (`Caught`: 7,557; `Bowled`: 1,775; `LBW`: 709; `Stump`: 214; `Hit Wicket`: 17; Total = 10,272). Run-outs (600), retired-outs (6), and obstructing the field (3) are excluded from bowler strike rates.

---

## 5. Player Identity & Referential Integrity Audit

### 5.1 Player Name Collisions (Disambiguation)
Three striker names and one bowler name correspond to **multiple distinct player IDs**:
- `Abdul Samad`: Player ID `7446` vs Player ID `6922`
- `Basil Hameed`: Player ID `8638` vs Player ID `39444`
- `Haider Ali`: Player ID `7338` vs Player ID `28756`
All aggregations strictly use `player_id` as the primary key.

### 5.2 Dismissed Player ID Imputation
Out of 10,881 wickets, exactly 1 record had `is_wicket == True` but `dismissed_player_id == NaN` (Match 40709, Innings 2, Over 19.5, Hardik Pandya `3330` retired out). Imputed with full sequence evidence.

---

## 6. Audit & Overlap Verification Summary

| Metric | Pre-Audit Value | Post-Audit Value | Audit Status |
| :--- | :---: | :---: | :---: |
| **Unique High-Pressure Deliveries** | 66,769 | 66,769 | **Verified (33.22%)** |
| **Sum of Category Activations** | 70,097 (reported) | 80,097 (actual sum) | **Corrected & Documented** |
| **Overlapping Deliveries** | Not reported | 13,328 activations | **Multi-Label Tagged** |
| **Shashank Singh Pressure Avg** | 69.6 | 69.56 (626 runs / 9 wkts) | **Independently Confirmed** |
| **Shashank Singh Pressure SR** | 190.3 | 190.27 (626 runs / 329 balls) | **Independently Confirmed** |
| **Bowling Strike Rate Integration** | Missing (0% weight) | Integrated (15% weight) | **Implemented & Rebalanced** |

---
*Report updated and certified by Independent Statistical Audit.*
