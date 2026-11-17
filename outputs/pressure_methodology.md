# Pressure Reliability Index (PRI) Methodology Framework (Audited & Methodologically Refined)
**Project:** SupeRR Selector Season 2 — Round 1: Pressure Reliability Index (PRI)  
**Author:** Cricket Analytics & Data Science Team  
**Date:** November 2026  
**Status:** Certified Production Specification  

---

## 1. Theoretical Foundation & Philosophy

In high-stakes Twenty20 cricket—and particularly in auction modeling for the Rajasthan Royals ahead of IPL 2027—raw aggregate numbers (such as total runs scored or total wickets taken) conceal critical flaws. A player who scores heavily in lopsided games or low-intensity powerplays often wilts when match leverage peaks. Conversely, true match-winners display **resilience, boundary potency, and boundary suppression** when the margin for error is razor-thin.

The **Pressure Reliability Index (PRI)** is built upon three foundational tenets:
1. **Dynamic Match State Without Leakage:** Match leverage is calculated strictly **prior to each delivery** using only information known on the field. Future outcomes, future deliveries, and final results are never used to define the pressure of the current ball.
2. **Relative Performance vs. Normal Baseline:** A high aggregate performer is not necessarily a pressure performer. PRI compares a player's pressure execution against their own non-pressure baseline ($\Delta = Metric_{pressure} - Metric_{baseline}$).
3. **Statistical Fairness & Bayesian Credibility:** To avoid rewarding small-sample outliers, PRI incorporates empirical Bayesian shrinkage towards league and positional baselines, combined with rigorous volume eligibility criteria.

---

## 2. Dynamic Pressure Identification Framework

### 2.1 State Reconstruction Prior to Ball $i$
Let $m$ denote the match, $inn$ the innings, and $i$ the delivery index within the innings. Before delivery $i$ is bowled, the exact state is evaluated via rolling cumulative sums:

$$\text{Runs Before}_{m, inn, i} = \sum_{j=1}^{i-1} \text{TotalRuns}_{m, inn, j}$$

$$\text{Wickets Before}_{m, inn, i} = \sum_{j=1}^{i-1} \mathbb{I}(\text{IsWicket}_{m, inn, j})$$

$$\text{Legal Balls Bowled Before}_{m, inn, i} = \sum_{j=1}^{i-1} \mathbb{I}(\text{ExtrasType}_{m, inn, j} \notin \{\text{wide, Overstep, other}\})$$

From these cumulative quantities, dynamic context indicators are derived:
- **Wickets in Hand ($W_{hand}$):** $10 - \text{Wickets Before}$.
- **Scheduled Balls ($B_{sched}$):** 
  - For Innings 2: $\text{second\_inn\_revised\_overs}$ if revised; else 120.
  - For Innings 1: $\text{first\_inn\_revised\_overs}$ if revised; else 120.
- **Balls Remaining ($B_{rem}$):** $\max(0, B_{sched} - \text{Legal Balls Bowled Before})$.
- **Target ($T$):** 
  - For Innings 2: $\text{revised\_target}$ if present; else $\text{Innings 1 Total Runs} + 1$.
- **Runs Needed ($R_{need}$):** $\max(0, T - \text{Runs Before})$.
- **Required Run Rate ($RRR$):** 

$$RRR = \begin{cases} \left(\frac{R_{need}}{B_{rem}}\right) \times 6 & \text{if } B_{rem} > 0 \text{ and } inn = 2 \\ \text{undefined} & \text{otherwise} \end{cases}$$

### 2.2 Pressure Boundary Definitions & Multi-Label Overlap Accounting

A delivery is classified as a **High-Pressure Situation ($\text{IsPressure} = 1$)** if it meets any of the following criteria:

#### A. Super Overs (Innings 3 & 4)
- **Condition:** $inn > 2$ (38 deliveries).
- **Rationale:** Every single delivery in a Super Over is direct sudden-death leverage.

#### B. Innings 2: The Chase Under Escalation
- **Condition B1 (Steep Required Run Rate):** $RRR \ge 10.0 \text{ runs/over}$ AND $RRR \le 24.0 \text{ runs/over}$ AND $W_{hand} \ge 2$ (39,081 activations).
- **Condition B2 (Death Overs Clutch Chase):** $B_{rem} \le 30 \text{ balls}$ AND $R_{need} \le 60 \text{ runs}$ AND $R_{need} > 0$ AND $RRR \ge 7.0$ (9,168 activations).
- **Condition B3 (Resource Depletion / Collapse in Chase):** $W_{hand} \le 4$ AND $W_{hand} \ge 1$ AND $R_{need} \ge 25 \text{ runs}$ AND $RRR \le 24.0$ (7,914 activations).

#### C. Innings 1: Setting the Total Under Duress
- **Condition C1 (Top-Order Crisis / Powerplay Collapse):** $\text{Legal Balls Before} \le 48 \text{ balls}$ AND $\text{Wickets Before} \ge 3$ (5,154 activations).
- **Condition C2 (Death Overs Launch Phase):** $B_{rem} \le 24 \text{ balls}$ AND $W_{hand} \ge 3$ (18,742 activations).

#### Overlap Transparency Matrix:
Because tactical states co-occur (e.g. a chase requiring 12 rpo in the death overs satisfies both B1 and B2), the individual category activations sum to **80,097**, representing **66,769 unique deliveries** (33.22% of all deliveries) with **13,328 overlapping activations**. The pipeline tracks individual condition flags, exports multi-label tags (`pressure_tags`), and assigns a strict priority hierarchy for primary classification:
$$\text{Super\_Over} \succ \text{Chase\_Death\_Close} \succ \text{Chase\_Collapse} \succ \text{Chase\_High\_RRR} \succ \text{Target\_Early\_Collapse} \succ \text{Target\_Death\_Accel}$$

---

## 3. Batting Pressure Reliability Index (PRI-Bat)

### 3.1 Core Batting Dimensions
For each batter with pressure balls faced $N_{P} \ge 120$ and baseline balls faced $N_{B} \ge 1$:
1. **Pressure Strike Rate ($SR_P$):** $\frac{\text{Runs}_P}{\text{Balls Faced}_P} \times 100$
2. **Pressure Boundary Percentage ($BP_P$):** $\frac{\text{Fours}_P + \text{Sixes}_P}{\text{Balls Faced}_P} \times 100$
3. **Pressure Average ($Avg_P$):** $\frac{\text{Runs}_P}{\max(1, \text{Dismissals}_P)}$
4. **Shrunk Strike Rate Delta ($\Delta SR_s$):** $SR_{P, s} - SR_{base}$
5. **Shrunk Average Delta ($\Delta Avg_s$):** $Avg_{P, s} - Avg_{base}$

### 3.2 Bayesian Shrinkage & Shrunk Deltas
Observed metrics are shrunk toward cohort baselines using credibility factor $w = \frac{N_P}{N_P + 60}$:
$$SR_{P, s} = w \cdot SR_P + (1 - w) \cdot \mu_{SR}$$
$$Avg_{P, s} = w \cdot Avg_P + (1 - w) \cdot \mu_{Avg}$$

### 3.3 Composite PRI-Bat Weights
$$\text{PRI}_{Bat} = 0.25 S(SR_{P, s}) + 0.15 S(BP_{P, s}) + 0.10 S(Avg_{P, s}) + 0.20 S(\Delta SR_s) + 0.15 S(\Delta Avg_s) + 0.15 S(\text{Exposure})$$
*Note on Weighting:* Performance-related components account for **85%** of the composite PRI weighting, while exposure credibility accounts for **15%**.

---

## 4. Bowling Pressure Reliability Index (PRI-Bowl)

### 4.1 Core Bowling Dimensions & Wicket Integration
PRI-Bowl integrates **Wicket Strike Rate ($WSR_P$)** to balance run containment with wicket breakthroughs:
1. **Pressure Economy ($Econ_P$):** $\frac{\text{Runs Conceded}_P}{B_P / 6}$ (Inverted percentile)
2. **Pressure Dot Ball % ($Dot\%_P$):** $\frac{\text{Dots}_P}{B_P} \times 100$
3. **Pressure Boundary Concession % ($BCR_P$):** $\frac{\text{Boundaries Conceded}_P}{B_P} \times 100$ (Inverted percentile)
4. **Pressure Wicket Strike Rate ($WSR_P$):** $\frac{B_P}{\max(1, \text{Wickets}_P)}$ (Inverted percentile)
5. **Shrunk Economy Delta ($\Delta Econ_s$):** $Econ_{base} - Econ_{P, s}$ (Positive = tightening under pressure)
6. **Shrunk Dot Ball Delta ($\Delta Dot\%_s$):** $Dot\%_{P, s} - Dot\%_{base}$

### 4.2 Composite PRI-Bowl Weights
$$\text{PRI}_{Bowl} = 0.20 S(\text{Inv } Econ_{P, s}) + 0.15 S(Dot\%_{P, s}) + 0.10 S(\text{Inv } BCR_{P, s}) + 0.15 S(\text{Inv } WSR_{P, s}) + 0.15 S(\Delta Econ_s) + 0.10 S(\Delta Dot\%_s) + 0.15 S(\text{Exposure})$$
*Note on Weighting:* Performance-related components account for **85%** of the composite PRI weighting, while exposure credibility accounts for **15%**.

---

## 5. Statistical Clarification: Exposure, Correlations, and Weighting

To maintain econometric and statistical precision:
1. **Distinction of Concepts:**
   - **Nominal Component Weights:** Prescribed model parameters (85% performance vs. 15% exposure credibility).
   - **Score Correlations (Pearson $r$):** The linear association between exposure scores and composite PRI ($r = 0.4583$ for batters; $r = 0.3191$ for bowlers). Because exposure is an additive constituent of the PRI score, this correlation is partly a **part-whole correlation**. It cannot be used alone to prove that exposure does not dominate rankings.
   - **Rank Correlations (Spearman $\rho$):** The monotonic stability of player rankings under counterfactual weight perturbations. Setting exposure weight to 0% yields rank correlations of $\rho = \mathbf{0.9801}$ (batting) and $\rho = \mathbf{0.9649}$ (bowling), demonstrating that player order is structurally determined by performance quality rather than raw volume.
   - **Variance Explained:** The empirical share of composite variance attributable to underlying components, which depends on component variances and cross-covariances. Standardized performance metrics possess substantial variance, ensuring that execution quality drives the final rank separation.

---

## 6. Statistical Safeguards & Eligibility Filters

1. **Eligibility Gates:** Minimum 120 pressure deliveries faced/bowled across at least 15 distinct matches.
2. **Empirical Bayesian Shrinkage:** $K = 60$ legal balls protects against low-volume distortions.
3. **Multi-Dimensional Sensitivity:** Tested across Strict ($RRR \ge 11$), Baseline ($RRR \ge 10$), and Relaxed ($RRR \ge 9$) thresholds, sample gates (100–150 balls), and shrinkage constants ($K = 40\text{--}80$), showing Spearman rank correlations $> 0.89\text{--}0.99$.

---
*Methodology refined and certified.*
