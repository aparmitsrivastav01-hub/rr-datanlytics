# Pressure Analysis & PRI Results Summary (Audited)

## 1. Executive Overview
Across 200,999 deliveries bowled between 2022 and 2026, **66,769 unique deliveries (33.22%)** were evaluated as high-pressure contexts. The Pressure Reliability Index (PRI) combines Bayesian-shrunk execution metrics, delta resilience against normal baseline, and exposure credibility.

### Pressure Categorization & Overlap Transparency
- **Super Overs:** 38 deliveries
- **Chase High RRR:** 39,081 deliveries
- **Chase Death Close:** 9,168 deliveries
- **Chase Collapse:** 7,914 deliveries
- **Target Early Collapse:** 5,154 deliveries
- **Target Death Acceleration:** 18,742 deliveries
- **Sum of Category Activations:** 80,097
- **Unique High-Pressure Deliveries:** 66,769
- **Net Overlapping Deliveries:** 13,328 (Explicitly documented; multi-label tagged).

## 2. Audited Top 10 Batters Under Pressure

| Rank | Player Name | Player ID | PRI Score | Pressure Balls | Matches | Pressure SR | Base SR | Delta SR | Pressure Avg | Boundary % |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **Tim David** | 6396 | **93.38** | 618 | 65 | 201.62 | 153.29 | +48.33 | 37.76 | 29.6% |
| 2 | **Shashank Singh** | 2756 | **91.95** | 329 | 29 | 190.27 | 120.78 | +69.49 | 69.56 | 27.1% |
| 3 | **Dinesh Karthik** | 143 | **86.09** | 446 | 51 | 185.65 | 124.87 | +60.78 | 27.60 | 28.3% |
| 4 | **Naman Dhir** | 37052 | **84.29** | 254 | 31 | 198.82 | 145.37 | +53.45 | 29.71 | 31.1% |
| 5 | **Donovan Ferreira** | 8182 | **81.20** | 187 | 19 | 192.51 | 129.49 | +63.03 | 27.69 | 27.8% |
| 6 | **Tristan Stubbs** | 20702 | **80.19** | 632 | 54 | 171.20 | 120.00 | +51.20 | 33.81 | 22.9% |
| 7 | **Ashutosh Sharma** | 8101 | **80.08** | 278 | 26 | 176.98 | 123.19 | +53.79 | 27.33 | 25.5% |
| 8 | **Reeza Hendricks** | 768 | **80.00** | 327 | 19 | 170.34 | 131.30 | +39.04 | 46.42 | 26.0% |
| 9 | **Rishabh Pant** | 4703 | **79.96** | 379 | 37 | 175.73 | 128.69 | +47.04 | 28.96 | 26.6% |
| 10 | **Glenn Maxwell** | 838 | **79.29** | 371 | 35 | 180.59 | 148.55 | +32.04 | 26.80 | 27.5% |

## 3. Audited Top 10 Bowlers Under Pressure

| Rank | Player Name | Player ID | PRI Score | Pressure Balls | Matches | Pressure Econ | Base Econ | Delta Econ | Wickets | Bowling SR | Dot % | Boundary Conceded % |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **Mohammad Nawaz** | 2490 | **89.33** | 236 | 22 | 6.03 | 7.35 | +1.33 | 25 | 9.4 | 42.8% | 9.3% |
| 2 | **Mitchell Santner** | 4101 | **88.85** | 505 | 41 | 6.74 | 7.39 | +0.65 | 37 | 13.6 | 39.8% | 11.7% |
| 3 | **Rashid Khan** | 4722 | **86.07** | 921 | 87 | 7.67 | 7.16 | -0.50 | 73 | 12.6 | 37.8% | 14.5% |
| 4 | **Abrar Ahmed** | 5979 | **84.31** | 256 | 27 | 6.14 | 6.78 | +0.64 | 19 | 13.5 | 46.1% | 10.5% |
| 5 | **Haris Rauf** | 7364 | **82.81** | 410 | 41 | 8.40 | 8.35 | -0.05 | 38 | 10.8 | 41.7% | 18.0% |
| 6 | **Matheesha Pathirana** | 8661 | **82.41** | 537 | 43 | 7.93 | 7.64 | -0.29 | 53 | 10.1 | 37.2% | 16.0% |
| 7 | **Sufiyan Muqeem** | 34485 | **80.44** | 212 | 17 | 5.32 | 6.33 | +1.01 | 14 | 15.1 | 54.2% | 10.4% |
| 8 | **Ravi Bishnoi** | 7503 | **77.70** | 983 | 73 | 8.24 | 7.85 | -0.39 | 62 | 15.9 | 38.0% | 18.3% |
| 9 | **Mohammad Rishad Hossain** | 8380 | **77.19** | 241 | 24 | 8.29 | 8.37 | +0.08 | 21 | 11.5 | 38.2% | 17.4% |
| 10 | **Jacob Duffy** | 22920 | **76.96** | 334 | 30 | 8.35 | 8.31 | -0.04 | 28 | 11.9 | 46.1% | 21.6% |

## 4. Comprehensive Sensitivity & Stability Analysis

| Sensitivity Test Dimension | Batting Spearman ρ | Batting Top 10 Overlap | Bowling Spearman ρ | Bowling Top 10 Overlap |
| :--- | :---: | :---: | :---: | :---: |
| Strict Threshold (RRR ≥ 11, Death ≤ 24) | 0.8929 | 70% | 0.9100 | 70% |
| Relaxed Threshold (RRR ≥ 9, Death ≤ 36) | 0.9308 | 70% | 0.8934 | 70% |
| Sample Size Cutoff = 100 Balls | 0.9997 | 100% | 0.9999 | 100% |
| Sample Size Cutoff = 150 Balls | 0.9991 | 100% | 0.9994 | 100% |
| Bayesian Shrinkage K = 40 | 0.9995 | 100% | 0.9992 | 100% |
| Bayesian Shrinkage K = 80 | 0.9993 | 100% | 0.9996 | 100% |

