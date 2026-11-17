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

---

## 4. Final Rankings Overview

### Top 10 Batters Under Pressure (PRI-Bat)
1. **Tim David** (PRI: 94.8 | SR: 201.6 | $\Delta$SR: +48.3 | Avg: 37.8)
2. **Shashank Singh** (PRI: 92.0 | SR: 190.3 | $\Delta$SR: +69.5 | Avg: 69.6)
3. **Dinesh Karthik** (PRI: 86.1 | SR: 185.7 | $\Delta$SR: +60.8 | Avg: 27.6)
4. **Naman Dhir** (PRI: 85.6 | SR: 198.8 | $\Delta$SR: +53.4 | Avg: 29.7)
5. **Donovan Ferreira** (PRI: 81.8 | SR: 192.5 | $\Delta$SR: +63.0 | Avg: 27.7)
6. **Tristan Stubbs** (PRI: 81.1 | SR: 171.2 | $\Delta$SR: +51.2 | Avg: 33.8)
7. **Glenn Maxwell** (PRI: 80.8 | SR: 180.6 | $\Delta$SR: +32.0 | Avg: 26.8)
8. **Reeza Hendricks** (PRI: 80.5 | SR: 170.3 | $\Delta$SR: +39.0 | Avg: 46.4)
9. **Ashutosh Sharma** (PRI: 80.5 | SR: 177.0 | $\Delta$SR: +53.8 | Avg: 27.3)
10. **Rishabh Pant** (PRI: 80.4 | SR: 175.7 | $\Delta$SR: +47.0 | Avg: 29.0)

### Top 10 Bowlers Under Pressure (PRI-Bowl)
1. **Mitchell Santner** (PRI: 93.0 | Econ: 6.74 | $\Delta$Econ: +0.65 | Dot%: 39.8% | Wkts: 37)
2. **Abrar Ahmed** (PRI: 89.8 | Econ: 6.14 | $\Delta$Econ: +0.64 | Dot%: 46.1% | Wkts: 19)
3. **Mohammad Nawaz** (PRI: 89.3 | Econ: 6.03 | $\Delta$Econ: +1.33 | Dot%: 42.8% | Wkts: 25)
4. **Sufiyan Muqeem** (PRI: 87.9 | Econ: 5.32 | $\Delta$Econ: +1.01 | Dot%: 54.2% | Wkts: 14)
5. **Sunil Narine** (PRI: 86.4 | Econ: 6.75 | $\Delta$Econ: +0.02 | Dot%: 38.2% | Wkts: 25)
6. **Rashid Khan** (PRI: 86.0 | Econ: 7.67 | $\Delta$Econ: -0.50 | Dot%: 37.8% | Wkts: 73)
7. **Ravi Bishnoi** (PRI: 83.2 | Econ: 8.24 | $\Delta$Econ: -0.39 | Dot%: 38.0% | Wkts: 62)
8. **Haris Rauf** (PRI: 81.3 | Econ: 8.40 | $\Delta$Econ: -0.05 | Dot%: 41.7% | Wkts: 38)
9. **Matheesha Pathirana** (PRI: 80.2 | Econ: 7.93 | $\Delta$Econ: -0.29 | Dot%: 37.2% | Wkts: 53)
10. **Deepak Chahar** (PRI: 79.6 | Econ: 8.31 | $\Delta$Econ: +0.59 | Dot%: 41.9% | Wkts: 17)

---
*Developed for Unstop SupeRR Selector Season 2.*
