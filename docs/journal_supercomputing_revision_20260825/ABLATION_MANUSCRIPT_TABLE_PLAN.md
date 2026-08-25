# Ablation Manuscript Table Plan

Date: 2026-08-25
Branch: `jsuper-reviewer-ablation-scale-20260825`

Defines which tables should appear in the main manuscript vs appendix/supplement.

---

## Main Manuscript Tables

### Table: Structural Ablation (main text)

**Source**: `structural_ablation.csv` (aggregated to median/mean per config across Layer 1+2)
**Columns**: Config (A0–A6), n_datasets, median upset_simple, median upset_ratio, median upset_naive, median removed_weight, median runtime
**Rows**: A0, A1, A2, A3, A4, A5, A6
**Purpose**: Answers R1 (stage contributions), R3 (add-back effectiveness), R4 (component ablation)
**Size**: 7 rows — compact, high-impact

### Table: Primary Pairwise Statistics (main text)

**Source**: `primary_pairwise_statistics.csv`
**Columns**: Comparison (A0 vs A2, A1 vs A2, A2 vs A5, A4 vs A6, A0 vs A4), n_common, W/T/L, median delta, Wilcoxon p, Holm p, effect size
**Rows**: 6 predefined primary comparisons
**Purpose**: Answers R1/R4 (statistical significance of stage contributions)
**Size**: 6 rows

### Table: Scalability Summary (main text)

**Source**: `scaling_results.csv` (aggregated by density regime)
**Columns**: Density regime (sparse <0.05, medium 0.05-0.2, dense ≥0.2), n_datasets, median n, median m, median runtime, max runtime, completion rate
**Rows**: 3 density regimes × 4 main configs (A0, A2, A4, A6)
**Purpose**: Answers R2 (scalability qualification), R4 (scalability)
**Size**: 12 rows

### Table: Finance Stress Case (main text, small)

**Source**: `raw_runs.csv` (filtered to finance)
**Columns**: Config, status (SUCCESS/TIMEOUT), runtime, stage at timeout
**Rows**: 4 (FINANCE_A0, A2, A4, A6)
**Purpose**: Answers R2 (timeout robustness), honest limitation
**Size**: 4 rows

---

## Appendix/Supplement Tables

### Table: Legacy Insertion-Pass Sensitivity (appendix)

**Source**: `legacy_pass_sensitivity.csv`
**Columns**: Config (P0–P3), n_datasets, median edges restored, median upset_simple, median runtime
**Rows**: P0, P1, P2, P3
**Purpose**: Answers R1/R3 (INS1/2/3 ineffectiveness)
**Size**: 4 rows

### Table: Zero-Tolerance Sensitivity (appendix)

**Source**: `zero_tol_sensitivity.csv`
**Columns**: zero_tol, n_datasets, median removed_weight, median upset_simple, forced-progress count
**Rows**: 1e-12, 1e-15, 1e-18
**Purpose**: Answers R1 (numerical stability)
**Size**: 3 rows

### Table: Refinement Sensitivity (appendix)

**Source**: `refinement_sensitivity.csv`
**Columns**: Config (R0–R3), n_datasets, median upset_simple, median upset_ratio, median runtime
**Rows**: R0, R1, R2, R3
**Purpose**: Answers R1 (refinement iteration sensitivity)
**Size**: 4 rows

### Table: Min-Cut Budget Sensitivity (appendix)

**Source**: `mincut_budget_sensitivity.csv`
**Columns**: Budget (K=20, 50, 100), n_datasets, median attempts, median accepts, median gain, median runtime
**Rows**: 3
**Purpose**: Answers whether min-cut saturates quickly
**Size**: 3 rows

### Table: Cycle-Selection Sensitivity (appendix)

**Source**: `cycle_selection_sensitivity.csv`
**Columns**: Cycle rule (C0, C1), base config (A0, A4), n_datasets, median upset_simple
**Rows**: 4 (C0_A0, C0_A4, C1_A0, C1_A4)
**Purpose**: Answers R4 (cycle-selection behavior)
**Size**: 4 rows

### Table: Full Completion Matrix (supplement, large)

**Source**: `completion_matrix.csv`
**Columns**: Dataset, A0, A1, A2, A3, A4, A5, A6 (status per cell)
**Rows**: 78+1 datasets
**Purpose**: Answers R2 (coverage transparency)
**Size**: 79 rows — too large for main text

### Table: Family-Level Summary (appendix)

**Source**: `family_summary.csv`
**Columns**: Family, config, n_datasets, median upset_simple, median upset_ratio, median gain
**Rows**: 7 families × 7 structural configs = 49 rows
**Purpose**: Family-aware sensitivity
**Size**: 49 rows

---

## Table count summary

| Location | Tables | Total rows |
|---|---|---|
| Main manuscript | 4 | ~25 |
| Appendix | 6 | ~67 |
| Supplement | 1 | ~79 |
| **Total** | **11** | **~171** |
