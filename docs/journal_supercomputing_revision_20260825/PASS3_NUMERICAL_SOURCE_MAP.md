# Pass 3 Numerical Source Map

Date: 2026-08-25  
Canonical primary: `GNNRank-main/paper_csv/leaderboard_per_method.csv`  
Derived: `outputs/revision_analysis_20260824/runtime_coverage_final/*`,  
`outputs/revision_analysis_20260825/family_aware_baselines/*`,  
`outputs/revision_analysis_20260825/reviewer_ablation_scalability/*`

| Manuscript table/claim | Source file | Filter/config | Denominator | Metric direction | Completion rule | Stats |
|---|---|---|---|---|---|---|
| Suite 80 / loadable 78 / exclude `_AUTO` | `outputs/derived/dataset_inventory.csv` + robust loader | `in_80_suite`; missing ERO+HeadToHead | 80 intended; **78 loadable** | — | missing adj excluded | see `FINAL_DATASET_DENOMINATOR_AUDIT.md` |
| Table `tab:pairwise_quality_simple` | `f_pairwise_common_completion.csv` | metric=`upset_simple` | pairwise n=77 or 60 | ↓ better; Δ=OURS−base | both succeed | Holm from `j_formal_statistics.csv` where present |
| Table `tab:pairwise_quality_ratio` | same | metric=`upset_ratio` | same | ↓ better | same | W/T/L + med Δ |
| upset_naive narrative | same | metric=`upset_naive` | same | ↓ better | same | W/T/L |
| Family-aware narrative | `FAMILY_AWARE_BASELINE_ANALYSIS.md` + `equal_family_macro.csv`, `leave_one_family_out.csv`, `hierarchical_bootstrap.csv` | equal-family / LOFO | 7 families (Finance out) | ↓ better | OURS vs fixed configs | hierarchical CI |
| Table `tab:runtime_wtl` | `e1_runtime_wtl.csv` | OURS vs baseline | 77 classical / 60 GNN | ratio OURS/base | both succeed | Holm runtime in `j_formal_statistics.csv` |
| Coverage 77/78, 78/78, 61/78 | `e2_completion_matrix.csv` excluding ERO | method SUCCESS counts | **78 loadable** | — | success/timeout/N/A | — |
| Finance leaderboard timeout | `h_finance_stress_case.csv` | dataset=finance | 1 | — | TIMEOUT vs SUCCESS | — |
| FINANCE_A0/A2/A4/A6 algorithm/harness distinction | `analysis_summary.json` + `raw_runs.csv` + `RUNTIME_PROVENANCE_AUDIT.md` | FINANCE_* | 4 configs | algorithm seconds where phase columns exist; harness seconds only when explicitly labeled | SUCCESS / INTERNAL_TIME_LIMIT / TIMEOUT_HARD_WALLCLOCK | A0 algorithm 600.53s, harness 612.55s; A2/A4 algorithm 602.31/602.28s, harness 1214.76/1214.57s; A6 hard wall-clock timeout 1800.10s, no completed algorithm runtime |
| A4 non-Finance algorithm runtime ~0.01-0.83s med 0.38 | `structural_ablation.csv` config=A4 non-Finance, column `runtime_algorithm_sec` | A4 | 77 | runtime ↓ | complete | descriptive |
| Table `tab:ablation_primary` | `primary_pairwise_statistics.csv` | is_primary / listed pairs | 77 or 33 | as labeled | non-Finance paired | Wilcoxon + Holm |
| Sensitivity narrative | `zero_tol_sensitivity.csv`, `refinement_sensitivity.csv`, `legacy_pass_sensitivity.csv`, `mincut_budget_sensitivity.csv`, `cycle_selection_sensitivity.csv` | Layer-1 | 33 | various | complete | paired where present |
| Min-cut regime | `MINCUT_MANUSCRIPT_EVIDENCE_SYNTHESIS.md` | broad char | 39/40 | structural | protocol | — |
| Figures | generated from `structural_ablation*.csv` | Figure 1: A4 `runtime_algorithm_sec`; Figure 2: A0-A6 ablation metrics | non-Finance | — | complete | script `generate_pass3_figures.py` |
