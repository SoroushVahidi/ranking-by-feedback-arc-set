# Reviewer Experiment Response Template

Date: 2026-08-25
Branch: `jsuper-reviewer-ablation-scale-20260825`

Maps each reviewer experimental request to the experiment configuration
answering it and the output table that will answer it.

This is NOT the response letter — it is a planning document.

---

## Reviewer 1

### R1: Phase 1 only, Phase 1 + insertion/add-back, full algorithm

| Field | Value |
|---|---|
| Requested evidence | Show contribution of each pipeline stage: Phase A alone, Phase A + add-back, full pipeline |
| Experiment configuration | A0 (Phase A only), A1 (Phase A + legacy topo add-back), A3 (original full: topo + refine), A4 (reach + refine) |
| Output table | `structural_ablation.csv` — rows per (dataset, config) with upset_simple/ratio/naive, removed weight, runtime |
| Manuscript section | §Experiments (ablation table) |
| Response point | Table shows monotonic improvement from A0 → A2 (reachability) and A2 → A4 (refinement). Legacy A1 is near-random on upset_simple. |

### R1: Density/scale behavior

| Field | Value |
|---|---|
| Requested evidence | How does the algorithm behave across density/scale regimes? |
| Experiment configuration | A0, A2, A4, A6 on Layer 2 (all 78 feasible datasets) |
| Output table | `scaling_results.csv` — n, m, density, runtime by stage, completion |
| Manuscript section | §Experiments (scalability subsection) |
| Response point | Runtime scales with m·n; finance timeout is a known boundary; sparse/moderate-density graphs complete in <1s. |

### R1: Zero tolerance, insertion passes, refinement iterations

| Field | Value |
|---|---|
| Requested evidence | Sensitivity to numerical tolerances and iteration counts |
| Experiment configuration | Z12/Z15/Z18 (zero_tol grid on A4), P0–P3 (insertion passes), R0–R3 (refinement budget) |
| Output tables | `zero_tol_sensitivity.csv`, `legacy_pass_sensitivity.csv`, `refinement_sensitivity.csv` |
| Manuscript section | §Experiments (sensitivity analysis) or appendix |
| Response point | Zero tolerance is numerically inert. Insertion passes 2-3 contribute zero additional reinsertions. Refinement has diminishing returns beyond canonical setting. |

---

## Reviewer 2

### R2: Timeout/failure robustness

| Field | Value |
|---|---|
| Requested evidence | How are timeouts and failures handled? |
| Experiment configuration | Finance stress case (FINANCE_A0/A2/A4/A6 with 600s budget) + completion matrix across all datasets |
| Output table | `completion_matrix.csv`, `h_finance_stress_case` (within raw_runs.csv) |
| Manuscript section | §Experiments (coverage/timeout subsection) |
| Response point | 77/78 datasets complete for OURS; finance timeout acknowledged. No arbitrary penalty. |

### R2: Scalability qualification

| Field | Value |
|---|---|
| Requested evidence | Qualified scalability claim |
| Experiment configuration | Scaling results across all 78 datasets with n, m, density, stage runtimes |
| Output table | `scaling_results.csv` |
| Manuscript section | §Discussion, §Limitations |
| Response point | Scales to n≤602; finance (n=1315, dense) times out. O(mn+m²) confirmed empirically. |

---

## Reviewer 3

### R3: Add-back actually changing outcomes

| Field | Value |
|---|---|
| Requested evidence | Does add-back change the ranking, not just the edge count? |
| Experiment configuration | A0 vs A1 vs A2 — permutation distance, upset metric deltas |
| Output table | `structural_ablation.csv` with `permutation_distance_vs_p1` |
| Manuscript section | §Experiments (ablation) |
| Response point | Legacy topo add-back (A1) changes few rankings; reachability (A2) changes more and improves upset_simple in 74/78. |

### R3: Stronger replacement for ineffective INS1/2/3

| Field | Value |
|---|---|
| Requested evidence | INS1/2/3 are nearly identical — is there a better alternative? |
| Experiment configuration | P0–P3 (insertion pass sensitivity), A2 (reachability as replacement), A5/A6 (min-cut exchange as replacement) |
| Output table | `legacy_pass_sensitivity.csv`, `structural_ablation.csv` |
| Manuscript section | §Experiments (insertion-pass analysis) |
| Response point | P2/P3 add zero edges beyond P1. Reachability (A2) is the principled replacement. Min-cut exchange (A5) provides further structural gain. |

---

## Reviewer 4

### R4: Ablations of the MWFAS backbone

| Field | Value |
|---|---|
| Requested evidence | What does each algorithmic component contribute? |
| Experiment configuration | A0–A6 structural ablation |
| Output table | `structural_ablation.csv` |
| Manuscript section | §Experiments (ablation table) |
| Response point | Phase A contributes the base DAG. Reachability add-back improves upset_simple. Phase C improves upset_ratio. Min-cut exchange improves structural objective. |

### R4: Cycle-selection behavior

| Field | Value |
|---|---|
| Requested evidence | How does cycle selection affect results? |
| Experiment configuration | C0 (DFS first-found) vs C1 (DFS reverse-order) on A0 and A4 |
| Output table | `cycle_selection_sensitivity.csv` |
| Manuscript section | §Experiments or appendix |
| Response point | Two deterministic DFS variants compared. Cycle selection has minimal effect on final ranking quality. |

### R4: Scalability

| Field | Value |
|---|---|
| Requested evidence | Where does computational cost become limiting? |
| Experiment configuration | Layer 2 (all 78 datasets) for A0, A2, A4, A6 + finance stress |
| Output table | `scaling_results.csv` |
| Manuscript section | §Discussion |
| Response point | Empirical scaling characterization. Cost is dominated by Phase A (O(mn+m²)). Finance is the boundary case. |
