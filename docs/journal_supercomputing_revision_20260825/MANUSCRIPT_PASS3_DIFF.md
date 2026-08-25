# Manuscript Pass 3 Diff Summary

Date: 2026-08-25  
Prior HEAD: `062c3e1b`

## Protocol rewrite
Consolidated Experimental Protocol: denominators 80/79/77/60, determinism vs GNN stochasticity, timeout budgets, completion rules, statistics, family-aware motivation, canonical CSV provenance.

## Baseline table corrections
Replaced submitted unpaired Table 4/5-style aggregates with pairwise common-completion W/T/L tables for `upset_simple` and `upset_ratio` (canonical `f_pairwise_common_completion.csv`).

## Statistics
Wilcoxon + Holm where exported (`j_formal_statistics.csv`); W/T/L + median Δ for all principal baselines.

## Family-aware
New subsection: equal-family, LOFO-fragile SpringRank, Basketball collapse, persistent BTL `upset_ratio` loss.

## Runtime correction
OURS slower than classical (2.6×–536× medians); 60/60 vs DIGRAC/ib at ~8× under trained end-to-end protocol; hardware caveat.

## Timeout/coverage
77/79 OURS; 78/79 classical typical; 61/79 GNN; Finance timeout; N/A vs timeout distinguished.

## Finance
Dedicated stress paragraph with FINANCE_A0/A2/A4/A6 terminal outcomes.

## Ablation / sensitivity / min-cut
Primary A0–A6 Holm table; compact sensitivity; regime-specific min-cut empirics; INS de-emphasized.

## Figures
`fig_runtime_vs_edges.pdf`, `fig_structural_ablation.pdf` from existing CSVs.

## Not changed
Abstract, Conclusion (still submitted text; TODO markers), response letter, title.
