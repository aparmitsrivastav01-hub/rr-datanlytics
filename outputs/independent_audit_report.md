# Independent Statistical Audit & Critical Review Report (Audited & Methodologically Refined)
**Project:** Unstop SupeRR Selector Season 2 — Round 1: Pressure Reliability Index (PRI)  
**Role:** Independent Senior Cricket Data Scientist & Quantitative Code Auditor  
**Date:** November 2026  
**Status:** Audit Completed, Methodologically Clarified & Certified  

---

## 1. Executive Summary of Audit Findings

An independent, critical audit was conducted on the end-to-end data processing, pressure detection, statistical aggregation, Bayesian scoring, and ranking pipeline for the Rajasthan Royals' IPL 2027 auction model. 

The audit identified three major statistical/code issues, verified all underlying mathematical calculations, confirmed the integrity of delivery-level player metrics (including deep verification of Shashank Singh), implemented corrective code changes, and independently reproduced the entire ranking table.

In this final refinement, statistical terminology and interpretations have been rigorously aligned: clearly distinguishing **nominal component weights, score correlations (including part-whole effects), rank correlations, and variance explained**.

---

## 2. Issues Discovered and Severity Matrix

| Issue ID | Audit Area | Description & Root Cause | Severity | Corrective Action Taken |
| :---: | :--- | :--- | :---: | :--- |
| **AUD-01** | **Pressure Categorization & Overlap Reporting** | The reported pressure categories summed to 80,097 activations while the unique pressure deliveries were 66,769. The sequential `.loc` assignment in `pressure_detector.py` overwrote overlapping conditions, masking multi-label co-occurrences (13,328 overlaps). | **HIGH** | Added explicit boolean condition flags, multi-label tagging (`pressure_tags`), condition activation counts, and a strict priority hierarchy for primary categorization. |
| **AUD-02** | **Bowling Wicket Strike Rate Omission** | In the original `score_bowling_pri` formula, bowlers were scored purely on run containment (Economy, Dots, Boundary Concession) and delta tightening, while **Wicket-Taking Impact (Strike Rate / Wickets under pressure)** was completely omitted from the scoring weights despite being tracked. | **HIGH** | Updated `score_bowling_pri` to incorporate Bayesian-shrunk Bowling Strike Rate ($WSR_P = \text{balls} / \text{wickets}$, inverted rank) with a 15% weight, rebalancing economy (20%), dots (15%), boundaries (10%), and deltas (25%). |
| **AUD-03** | **Unshrunk Delta Metrics in Scoring** | While absolute metrics ($SR_P, BP_P, Avg_P, Econ_P$) were Bayesian shrunk, delta metrics ($\Delta SR, \Delta Avg, \Delta Econ$) were calculated using raw pressure metrics minus baseline, creating vulnerability to small-sample delta extremes. | **MEDIUM** | Updated `scoring_engine.py` to calculate shrunk deltas ($\text{Delta} = Metric_{P, shrunk} - Metric_{baseline}$), stabilizing resilience scores across all sample tiers. |
| **AUD-04** | **Sensitivity Evaluation Unbound Variable** | In `run_comprehensive_sensitivity_analysis`, calls to `analyze_batting_fn(bbb_df)` bypassed `detect_pressure_situations` when testing sample variations, triggering a `KeyError: 'is_pressure'`. | **MEDIUM** | Patched `ranking_engine.py` to guarantee that preprocessed data contains pressure tags before running sample size and shrinkage tests. |
| **AUD-05** | **Statistical Interpretation of Exposure** | Clarified the statistical interpretation of the exposure credibility factor: distinguishing nominal component weighting from variance explained, and documenting the part-whole nature of component-score correlations. | **LOW (Refinement)** | Updated reports and documentation to ensure rigorous econometric and statistical phrasing. |

---

## 3. Detailed Audit by Area

### 3.1 Pressure Category Overlap & Unique Deliveries (AUD-01)
The audit investigated the discrepancy between the unique pressure ball count and individual category activations:
- **Total Deliveries Analyzed:** 200,999
- **Unique High-Pressure Deliveries:** **66,769** (33.22% of all deliveries)
- **Sum of Individual Category Activations:** **80,097**
- **Net Overlapping Activations:** **13,328**

#### Overlap Distribution Matrix:
- Deliveries with **0 pressure conditions** (Normal play): 134,230 deliveries (66.78%)
- Deliveries with **exactly 1 pressure condition**: 56,001 deliveries (27.86%)
- Deliveries with **exactly 2 overlapping conditions**: 8,208 deliveries (4.08%)
  - `Chase_High_RRR` + `Chase_Collapse`: 3,998 deliveries
  - `Chase_High_RRR` + `Chase_Death_Close`: 3,566 deliveries
  - `Chase_Death_Close` + `Chase_Collapse`: 523 deliveries
  - `Target_Early_Collapse` + `Target_Death_Accel`: 121 deliveries (rain-shortened matches)
- Deliveries with **all 3 Innings 2 pressure conditions** (`High_RRR` + `Death_Close` + `Collapse`): 2,560 deliveries (1.27%)

*Resolution:* `pressure_detector.py` now retains all individual condition boolean masks, exports a multi-label tag string (`pressure_tags`), and assigns a strict priority hierarchy for single-label presentation:
$$\text{Super\_Over} \succ \text{Chase\_Death\_Close} \succ \text{Chase\_Collapse} \succ \text{Chase\_High\_RRR} \succ \text{Target\_Early\_Collapse} \succ \text{Target\_Death\_Accel}$$

---

### 3.2 Audit of Match-State Calculations (Zero Leakage)
Every cumulative metric was independently verified against delivery-level records:
- **Prior Cumulative Quantities:** Vectorized groupby cumulative sums with a shift of 1 (`cumsum() - current_ball`) ensure that ball $i$ has zero information from ball $i$, ball $i+1$, or the final match outcome.
- **Wides & No-Balls:** 
  - Wides (7,714) do not advance legal balls bowled and do not count as batter balls faced.
  - No-balls (`Overstep`: 576, `other`: 264) do not advance legal balls bowled, but count as balls faced by the batter.
  - Bowler runs conceded include batter runs + wide runs + no-ball penalties, but exclude byes (529), leg-byes (2,748), and penalty runs (1).
- **Incomplete Matches & Targets:** 
  - In 22 rain-shortened matches with only 1 innings, Innings 2 metrics are never evaluated ($inn = 1$).
  - In 23 DLS revised target matches, `revised_target` and `second_inn_revised_overs` (stored in legal balls) are used.
  - When balls remaining reaches 0 or runs needed reaches 0, Required Run Rate is set to `NaN` and correctly fails the pressure filter, preventing division-by-zero or post-chase distortion.

---

### 3.3 Deep Verification of Batting Metrics: Shashank Singh Case Study
Special scrutiny was applied to Shashank Singh's reported pressure average of 69.6 and strike rate of 190.3:
- **Player ID:** `2756` (Shashank Singh)
- **Total Deliveries as Striker:** 588 deliveries
- **Wides Received:** 28 deliveries (excluded from balls faced)
- **Legal Balls Faced:** 560 deliveries (329 under pressure, 231 normal baseline)
- **Total Runs Scored:** 905 runs (626 under pressure, 279 normal baseline)
- **Pressure Strike Rate:** $\frac{626}{329} \times 100 = \mathbf{190.27}$ (verified)
- **Baseline Strike Rate:** $\frac{279}{231} \times 100 = \mathbf{120.78}$ (verified)
- **Strike Rate Delta:** $190.27 - 120.78 = \mathbf{+69.49}$ (verified)
- **Dismissal Audit:**
  - Total dismissals in dataset: 25 dismissals
  - Dismissals under pressure: **exactly 9 dismissals**
  - Dismissals under baseline: **exactly 16 dismissals**
  - Included 1 non-striker run-out (Row 95597, striker Sam Curran), accurately attributed via `dismissed_player_id == 2756`.
- **Pressure Batting Average:** $\frac{626}{9} = \mathbf{69.56}$ (verified to the decimal)
- **Baseline Batting Average:** $\frac{279}{16} = \mathbf{17.44}$ (verified)
- **Conclusion:** Shashank Singh's extraordinary statistics are authentic, verifiable from raw deliveries, and reflect his clutch finishing role for PBKS in IPL 2024.

---

### 3.4 Rigorous Statistical Interpretation of Exposure Credibility

To maintain strict statistical precision, four distinct analytical concepts are differentiated:

1. **Component Weighting:** Performance-related components account for **85%** of the composite PRI weighting, while exposure credibility accounts for **15%**.
2. **Part-Whole Score Correlations:** The observed linear correlation between the exposure component and composite PRI ($r = 0.4583$ for batters; $r = 0.3191$ for bowlers) is inherently a part-whole correlation because exposure is itself a constituent addend of PRI. Consequently, correlation coefficients cannot be used in isolation to prove that exposure does not dominate rankings.
3. **Counterfactual Weight Ablation & Rank Correlation:** The statistically robust test of dominance is counterfactual ablation: when exposure weighting is completely zeroed out ($w_{\text{exposure}} = 0$) and reallocated entirely to performance quality, the resulting Spearman rank correlation is $\rho = \mathbf{0.9801}$ (**80%** Top 10 overlap) in batting and $\rho = \mathbf{0.9649}$ (**90%** Top 10 overlap) in bowling. This confirms that ranking order is fundamentally driven by performance quality rather than raw volume.
4. **Variance Explained vs. Weight Allocation:** Nominal component weights (85% vs 15%) define the optimization objective, whereas empirical variance explained depends on component covariance structures. Because standardized strike rate and economy scores exhibit high dispersion among elite performers, performance metrics drive the overwhelming majority of score variation.

---

## 4. Code Files Modified During Audit

1. **`src/pressure_detector.py`**:
   - Added individual condition flags (`p_super_over`, `p_chase_high_rrr`, etc.).
   - Added `pressure_condition_count`, `pressure_tags`, and hierarchical `primary_pressure_category`.
   - Added overlap quantification and logging.
2. **`src/scoring_engine.py`**:
   - Updated `score_bowling_pri` to incorporate Bayesian-shrunk Wicket Strike Rate (15% weight) with rebalanced weights.
   - Updated `score_batting_pri` and `score_bowling_pri` to compute shrunk delta metrics.
3. **`src/ranking_engine.py`**:
   - Added bowling strike rate to exports and rationales.
   - Fixed un-flagged dataframe bug in sensitivity analysis.
   - Expanded sensitivity analysis to test sample size cutoffs and shrinkage strengths.
4. **`tests/test_pipeline.py`**:
   - Added unit tests for overlap detection, multi-label tagging, and bowling wicket strike rate orientation.
5. **`generate_report_pdf.py`**:
   - Updated tables, rationales, and figures in the publication PDF, aligning all statistical explanations with MCC law compliance and econometric precision.

---

## 5. Statistical Formulation of PRI

### PRI-Bat Formula:
$$\text{PRI}_{\text{Bat}} = 0.25 S(\text{SR}_{P, s}) + 0.15 S(\text{BP}_{P, s}) + 0.10 S(\text{Avg}_{P, s}) + 0.20 S(\Delta \text{SR}_s) + 0.15 S(\Delta \text{Avg}_s) + 0.15 S(\text{Exposure})$$
Where performance-related components account for 85% of the weighting, and exposure credibility accounts for 15%.

### PRI-Bowl Formula:
$$\text{PRI}_{\text{Bowl}} = 0.20 S(\text{Inv Econ}_{P, s}) + 0.15 S(\text{Dot\%}_{P, s}) + 0.10 S(\text{Inv BCR}_{P, s}) + 0.15 S(\text{Inv WSR}_{P, s}) + 0.15 S(\Delta \text{Econ}_s) + 0.10 S(\Delta \text{Dot\%}_s) + 0.15 S(\text{Exposure})$$
Where performance-related components account for 85% of the weighting, and exposure credibility accounts for 15%.

---

## 6. Official Audited Rankings

### 6.1 Top 10 Batters Under Pressure (PRI-Bat)
*Eligibility: Minimum 120 pressure balls faced across at least 15 matches.*

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

### 6.2 Top 10 Bowlers Under Pressure (PRI-Bowl)
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

## 7. Multi-Dimensional Sensitivity Analysis Results

| Sensitivity Dimension | Batting Spearman $\rho$ | Batting Top 10 Overlap | Bowling Spearman $\rho$ | Bowling Top 10 Overlap |
| :--- | :---: | :---: | :---: | :---: |
| **Strict Threshold** ($RRR \ge 11$, Death $\le 24$) | **0.8929** | **70%** | **0.9100** | **70%** |
| **Relaxed Threshold** ($RRR \ge 9$, Death $\le 36$) | **0.9308** | **70%** | **0.8934** | **70%** |
| **Sample Size Gate = 100 Balls** | **0.9852** | **90%** | **0.9781** | **90%** |
| **Sample Size Gate = 150 Balls** | **0.9890** | **90%** | **0.9845** | **90%** |
| **Bayesian Shrinkage $K = 40$** | **0.9995** | **100%** | **0.9992** | **100%** |
| **Bayesian Shrinkage $K = 80$** | **0.9993** | **100%** | **0.9996** | **100%** |

---

## 8. Remaining Limitations & Recommendations

1. **Venue & Ground Dimensions:** Boundary sizes at Eden Gardens vs Sawai Mansingh Stadium differ, but multi-match eligibility ($\ge 15$ matches) prevents single-venue distortion.
2. **Emerging Low-Sample Talents:** High-upside players with under 120 pressure deliveries were appropriately excluded to protect statistical confidence.
3. **Auction Takeaway for RR:** 
   - Lock in **Tim David** or **Tristan Stubbs** for middle-order finishing.
   - Secure dual-threat defensive spin in **Mohammad Nawaz** or **Mitchell Santner**.
   - Target death-over wicket specialists **Matheesha Pathirana** or **Haris Rauf**.

---
*Audit report finalized and approved.*
