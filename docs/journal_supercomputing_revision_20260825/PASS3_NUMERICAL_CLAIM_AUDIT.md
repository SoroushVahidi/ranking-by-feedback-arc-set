# Pass 3 Numerical Claim Audit

Date: 2026-08-25

## Cross-checked against CSV (programmatic)

| Claim in LaTeX | Verified value | Source |
|---|---|---|
| BTL upset_simple 73/0/4 | Pass | `f_pairwise_common_completion.csv` |
| BTL upset_ratio 1/0/76 | Pass | same |
| DIGRAC runtime 60/60 faster | Pass | `e1_runtime_wtl.csv` |
| DIGRAC median ratio ≈0.123 | Pass | same |
| A0→A2 upset_simple 76/0/1 med −0.0166 | Pass | `primary_pairwise_statistics.csv` |
| A1→A2 32/0/1 | Pass | same |
| A2→A5 removed 26/7/0 med −47 | Pass | same |
| A4→A6 removed 66/11/0 med −57 | Pass | same |
| A0→A4 76/0/1 | Pass | same |
| OURS coverage 77/79 | Pass | `e2_coverage_matrix.csv` / docs |
| A4 med runtime ≈0.57s | Pass | structural summary / ablation CSV |
| Finance A0 ≈612.55s | Pass | raw_runs / analysis_summary |
| Finance A6 hard timeout ≈1800.10s | Pass | same |

## Forbidden claims scan (Results section)

| Pattern | Status |
|---|---|
| OURS faster than classical | Absent (explicitly slower) |
| Universal quality superiority | Absent (“do not claim universal dominance”) |
| Oracle as deployable method | Absent (explicitly not headline) |
| DF03 under timeout | Not reintroduced in Results |
| 10.16× GNN speedup | Absent (uses ~8× from median ratio ≈0.12) |

## Table 4/5 inconsistency

Submitted unpaired aggregates superseded by pairwise common-completion tables from one canonical leaderboard-derived export. INS3≡OURS_MFAS duplicate labeling disclosed.
