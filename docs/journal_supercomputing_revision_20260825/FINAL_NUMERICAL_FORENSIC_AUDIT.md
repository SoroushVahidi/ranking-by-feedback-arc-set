# Final Numerical Forensic Audit

Date: 2026-08-25

## Classification

**NO_UNTRACEABLE_NUMERICAL_CLAIMS**

Sources: `PASS3_NUMERICAL_SOURCE_MAP.md`, `PASS3_NUMERICAL_CLAIM_AUDIT.md`, `RESPONSE_LETTER_NUMERICAL_AUDIT.md`, canonical CSVs under `outputs/revision_analysis_20260824/runtime_coverage_final/` and `outputs/revision_analysis_20260825/reviewer_ablation_scalability/`.

## Critical checks

| Claim | Value | Source | Status |
|---|---|---|---|
| Intended suite | 80 | protocol + inventory | Pass |
| Readable | 79 | missing ERO + Halo files | Pass |
| Exclude `_AUTO/Basketball_temporal__1985adj` | excluded | protocol | Pass |
| OURS/classical common | 77 | pairwise CSV | Pass |
| OURS/GNN common | 60 | pairwise/runtime CSV | Pass |
| OURS coverage | 77/79 | e2 coverage | Pass |
| GNN coverage | 61/79 | e2 / narrative | Pass |
| Classical typical coverage | 78/79 | narrative | Pass |
| SpringRank median upset_simple (full-suite export) | 0.802724 | `table4_full_suite.csv` | Pass |
| Stale SpringRank 1.675 | absent | rg scan | Pass |
| BTL upset_simple W/T/L | 73/0/4 | pairwise | Pass |
| BTL upset_ratio W/T/L | 1/0/76 | pairwise | Pass |
| A0→A2 upset_simple | 76/0/1 n=77 Holm 2.4e−12 | primary_pairwise | Pass |
| A1→A2 | 32/0/1 n=33 | same | Pass |
| A2→A5 removed weight | 26/7/0 med −47 | same | Pass |
| A4→A6 removed weight | 66/11/0 med −57 | same | Pass |
| A0→A4 | 76/0/1 | same | Pass |
| zero_tol | STABLE | sensitivity | Pass |
| refinement | R1≈R2 saturates | sensitivity | Pass |
| P0–P3 | P2/P3 nearly inert | sensitivity | Pass |
| K20/K50/K100 | K50→K100 flat | sensitivity | Pass |
| Finance A0/A2/A4/A6 | 612.55; 1214.76 INTERNAL; 1214.57 INTERNAL; 1800.10 HARD | analysis_summary.json | Pass |
| Classical median ratios | SyncRank 2.6× … PageRank 536× | e1_runtime_wtl | Pass |
| GNN ~8× | DIGRAC/ib med ratio ≈0.12; 60/60 | e1 | Pass |
| A4 non-Finance runtime | ~0.01–1.2s med ≈0.57s | structural | Pass |
| SpringRank family LOFO-fragile | narrative | family-aware docs | Pass |

## Fixes this pass

None numerical removed; Abstract/Conclusion clarified that Tables 4–6 use archived `OURS_MFAS` while ablation quantifies reachability.
