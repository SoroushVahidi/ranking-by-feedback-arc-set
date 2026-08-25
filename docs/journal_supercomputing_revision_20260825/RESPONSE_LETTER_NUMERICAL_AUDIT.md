# Response Letter Numerical Audit

Date: 2026-08-25

**Comment provenance:** The JoS decision email is not preserved as a single verbatim file in this worktree. Point-by-point concerns are taken from the preserved revision evidence (`REVIEWER_TO_LATEX_CHANGE_MATRIX.md`, `REVIEWER_MASTER_MATRIX.md`, `NOVELTY_THEORY_REVIEWER_MAP.md`, `REVIEWER_TECHNICAL_AUDIT.md`, `REVIEWER_EXPERIMENT_RESPONSE_TEMPLATE.md`, and the user's structured R1–R4 outline). Comment boxes in the response letter are concise restatements of those preserved concerns, not invented issues.

| Reviewer / comment | Statement | Source | Denominator | Metric | Exact value |
|---|---|---|---|---|---|
| R1.2 / R3.1 | A0→A2 upset_simple W/T/L | `primary_pairwise_statistics.csv` | n=77 non-Finance | upset_simple ↓ | 76/0/1; med Δ −0.0166; Holm 2.4e−12 |
| R1.2 / R3.1 | A1→A2 upset_simple | same | n=33 | upset_simple ↓ | 32/0/1; med Δ −0.0159; Holm 1.5e−6 |
| R1.2 | A4 runtime range | `structural_ablation.csv` A4 non-Finance | n=77 | runtime_sec | ≈0.01–1.2 s; med ≈0.57 s; n≤602 |
| R1.2 / R2.8 | Finance boundary timings | `analysis_summary.json` finance[] | 4 configs | wall seconds | A0=612.55s SUCCESS; A2=1214.76s; A4=1214.57s INTERNAL_TIME_LIMIT; A6=1800.10s TIMEOUT_HARD_WALLCLOCK |
| R2.4 | Coverage | `e2_completion_matrix.csv` ∖ ERO | **78 loadable** | success | OURS 77/78; classical 78/78; GNN 61/78 |
| R2.3 / R3.3 | GNN runtime | `e1_runtime_wtl.csv` | n=60 | runtime ratio | 60/60 faster; med ≈0.12× (~8×) |
| R3.3 | Classical slower | `e1_runtime_wtl.csv` | n=77 | median ratio | syncRank 2.6× … PageRank 536× |
| R3.2 | SpringRank canonical median | `table4_full_suite.csv` | suite export | median upset_simple | 0.802724 |
| R4.7 | Cycle selection | `cycle_selection_sensitivity.csv` / ablation final | n=33 | upset_simple | |med Δ|≈1e−3 on A4 path |
| R1.2 | P2/P3 / zero_tol / refine | sensitivity CSVs + `REVIEWER_ABLATION_FINAL_ANALYSIS.md` | Layer-1 n=33 | various | P2/P3 inert; zero_tol STABLE; refine saturates |

All values also cross-listed in `PASS3_NUMERICAL_SOURCE_MAP.md` / `PASS3_NUMERICAL_CLAIM_AUDIT.md`.
