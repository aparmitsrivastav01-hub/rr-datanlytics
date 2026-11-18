# SupeRR Selector Season 2 — Round 1: Pressure Reliability Index (PRI)

Data-driven analytics engine for **Unstop SupeRR Selector Season 2 (Round 1)**, focused on identifying the most reliable batters and bowlers under high-pressure match situations for Rajasthan Royals' IPL 2027 auction strategy.

---

## 1. Project Overview

Raw aggregate metrics (total runs scored, total wickets taken) fail to distinguish true clutch performers from volume accumulators. The **Pressure Reliability Index (PRI)** quantifies player performance under pressure relative to their baseline across 200,999 deliveries in IPL and T20Is between 2022 and 2026.

### Key Capabilities
- **Strict Zero-Leakage Dynamic Match State:** Prior cumulative state (RRR, balls remaining, wickets in hand) evaluated delivery-by-delivery without lookahead leakage.
- **Dynamic Context Classification:** Pressure identified across Super Overs, high-RRR chases ($10 \le RRR \le 24$), death-over finishes, chase collapses, top-order rebuilds, and death acceleration.
- **Resilience Delta Analysis:** Measures elevation/drop-off ($\Delta = Metric_{pressure} - Metric_{baseline}$).
- **Empirical Bayesian Shrinkage:** Regresses small samples toward cohort baselines to ensure statistical fairness.
- **Sensitivity Validation:** Rank stability verified across multiple parameter perturbations (Spearman $\rho > 0.90$).

---

## 2. Directory Structure

```text
SupeRR-Selector/
├── data/
│   ├── raw/                      # Raw source CSV files
│   └── processed/                # Preprocessed and enhanced data
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_pressure_analysis.ipynb
│   ├── 03_batting_analysis.ipynb
│   ├── 04_bowling_analysis.ipynb
│   └── 05_player_rankings.ipynb
├── src/
│   ├── data_loader.py            # Data loading and column validation
│   ├── preprocessing.py          # State cleaning and MCC law compliance
│   ├── pressure_detector.py      # Prior-state leverage calculation
│   ├── batting_analysis.py       # Batting metrics and delta computation
│   ├── bowling_analysis.py       # Bowling metrics and delta computation
│   ├── scoring_engine.py         # Bayesian shrinkage & PRI calculation
│   └── ranking_engine.py         # Top 10 selection & sensitivity analysis
├── outputs/
│   ├── data_quality_report.md
│   ├── pressure_methodology.md
│   ├── top_10_batters.csv
│   ├── top_10_bowlers.csv
│   ├── player_pressure_metrics.csv
│   └── pressure_analysis_summary.md
├── reports/
│   └── SupeRR_Selector_Round_1_Methodology_Report.pdf
├── tests/
│   └── test_pipeline.py
├── run_pipeline.py
├── generate_report_pdf.py
├── requirements.txt
└── README.md
```

---

## 3. How to Run the Pipeline

### Step 1: Install Requirements
```bash
pip install -r requirements.txt
```

### Step 2: Execute End-to-End Pipeline
```bash
python run_pipeline.py
```

### Step 3: Run Unit Tests
```bash
python -m unittest tests/test_pipeline.py
```

### Step 4: Generate Final Methodology Report PDF
```bash
python generate_report_pdf.py
```

### Step 5: Run Automated Consistency Verification
```bash
python verify_submission_consistency.py
```

---

## 4. Final Rankings Overview (Canonical Audited Results)

### Top 10 Batters Under Pressure (PRI-Bat)
*Eligibility: Minimum 120 pressure deliveries faced across at least 15 matches.*

| Rank | Player Name | Player ID | PRI-Bat | Balls | Matches | Pressure SR | Base SR | $\Delta$ SR | Pressure Avg | Boundary % |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | **Tim David** | `6396` | **93.4** | 618 | 65 | 201.6 | 153.3 | +48.3 | 37.8 | 29.6% |
| **2** | **Shashank Singh** | `2756` | **92.0** | 329 | 29 | 190.3 | 120.8 | +69.5 | 69.6 | 27.1% |
| **3** | **Dinesh Karthik** | `143` | **86.1** | 446 | 51 | 185.7 | 124.9 | +60.8 | 27.6 | 28.3% |
| **4** | **Naman Dhir** | `37052` | **84.3** | 254 | 31 | 198.8 | 145.4 | +53.4 | 29.7 | 31.1% |
| **5** | **Donovan Ferreira** | `8182` | **81.2** | 187 | 19 | 192.5 | 129.5 | +63.0 | 27.7 | 27.8% |
| **6** | **Tristan Stubbs** | `20702` | **80.2** | 632 | 54 | 171.2 | 120.0 | +51.2 | 33.8 | 22.9% |
| **7** | **Ashutosh Sharma** | `8101` | **80.1** | 278 | 26 | 177.0 | 123.2 | +53.8 | 27.3 | 25.5% |
| **8** | **Reeza Hendricks** | `768` | **80.0** | 327 | 19 | 170.3 | 131.3 | +39.0 | 46.4 | 26.0% |
| **9** | **Rishabh Pant** | `4703` | **80.0** | 379 | 37 | 175.7 | 128.7 | +47.0 | 29.0 | 26.6% |
| **10** | **Glenn Maxwell** | `838` | **79.3** | 371 | 35 | 180.6 | 148.6 | +32.0 | 26.8 | 27.5% |

### Top 10 Bowlers Under Pressure (PRI-Bowl)
*Eligibility: Minimum 120 pressure legal balls bowled across at least 15 matches.*

| Rank | Player Name | Player ID | PRI-Bowl | Balls | Matches | Pressure Econ | $\Delta$ Econ | Wkts | Strike Rate | Dot % |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | **Mohammad Nawaz** | `2490` | **89.3** | 236 | 22 | 6.03 | +1.33 | 25 | 9.4 | 42.8% |
| **2** | **Mitchell Santner** | `4101` | **88.9** | 505 | 41 | 6.74 | +0.65 | 37 | 13.6 | 39.8% |
| **3** | **Rashid Khan** | `4722` | **86.1** | 921 | 87 | 7.67 | -0.50 | 73 | 12.6 | 37.8% |
| **4** | **Abrar Ahmed** | `5979` | **84.3** | 256 | 27 | 6.14 | +0.64 | 19 | 13.5 | 46.1% |
| **5** | **Haris Rauf** | `7364` | **82.8** | 410 | 41 | 8.40 | -0.05 | 38 | 10.8 | 41.7% |
| **6** | **Matheesha Pathirana** | `8661` | **82.4** | 537 | 43 | 7.93 | -0.29 | 53 | 10.1 | 37.2% |
| **7** | **Sufiyan Muqeem** | `34485` | **80.4** | 212 | 17 | 5.32 | +1.01 | 14 | 15.1 | 54.2% |
| **8** | **Ravi Bishnoi** | `7503` | **77.7** | 983 | 73 | 8.24 | -0.39 | 62 | 15.9 | 38.0% |
| **9** | **Mohammad Rishad Hossain** | `8380` | **77.2** | 241 | 24 | 8.29 | +0.08 | 21 | 11.5 | 38.2% |
| **10** | **Jacob Duffy** | `22920` | **77.0** | 334 | 30 | 8.35 | -0.04 | 28 | 11.9 | 46.1% |

---

## 5. Statistical Framework & Governance Note

- **85% Performance / 15% Exposure:** Performance-related dimensions (execution + resilience deltas) dictate 85% of PRI weight allocation; exposure credibility accounts for 15%.
- **Empirical Bayesian Shrinkage ($K=60$):** Applied to both absolute metrics and resilience deltas, stabilizing estimates for low-sample performers against cohort priors.
- **Single Source of Truth:** All published rankings across documentation, CSV exports, and the research methodology PDF are strictly synchronized with the canonical output of `run_pipeline.py`.

---
*Developed for Unstop SupeRR Selector Season 2.*
