# Reviewer Experiment Response Template

Date: 2026-08-25
Branch: `jsuper-reviewer-ablation-scale-20260825`

Maps each reviewer experimental request to the experiment configuration
answering it and the output table that will answer it.

Status legend: `RESOLVED_BY_COMPLETED_RUN` | `PARTIAL` | `FAILED_TO_COLLECT` | `NOT_APPLICABLE`

---

## Reviewer 1

### R1: Phase 1 only, Phase 1 + insertion/add-back, full algorithm

| Field | Value |
|---|---|
| Requested evidence | Show contribution of each pipeline stage: Phase A alone, Phase A + add-back, full pipeline |
| Experiment configuration | A0 (Phase A only), A1 (Phase A + legacy topo add-back), A3 (original full: topo + refine), A4 (reach + refine) |
| Output table | `structural_ablation.csv`, `primary_pairwise_statistics.csv` |
| Status | **RESOLVED_BY_COMPLETED_RUN** (non-finance complete; paired A0→A2 / A0→A4 significant) |
| Response point | Reachability (A2) beats Phase A and topo proxy (A1). Full A4 improves upset_ratio vs A2. |

### R1: Density/scale behavior

| Field | Value |
|---|---|
| Requested evidence | How does the algorithm behave across density/scale regimes? |
| Experiment configuration | A0, A2, A4, A6 on Layer 2 (all 78 feasible datasets) |
| Output table | `scaling_results.csv` |
| Status | **RESOLVED_BY_COMPLETED_RUN** (non-finance); finance stress **PARTIAL** until FINANCE_A6 terminal |
| Response point | n≤602 completes in ≲1–4s median depending on config; finance is the boundary. |

### R1: Zero tolerance, insertion passes, refinement iterations

| Field | Value |
|---|---|
| Requested evidence | Sensitivity to numerical tolerances and iteration counts |
| Experiment configuration | Z12/Z15/Z18, P0–P3, R0–R3 |
| Output tables | `zero_tol_sensitivity.csv`, `legacy_pass_sensitivity.csv`, `refinement_sensitivity.csv` |
| Status | **RESOLVED_BY_COMPLETED_RUN** |
| Response point | zero_tol STABLE; P2/P3 nearly inert vs P1; refinement saturates by R1/R2. |

---

## Reviewer 2

### R2: Timeout/failure robustness

| Field | Value |
|---|---|
| Requested evidence | How are timeouts and failures handled? |
| Experiment configuration | Finance stress + completion matrix |
| Output table | `completion_matrix.csv`, finance rows in `raw_runs.csv` |
| Status | **PARTIAL** — A0/A2/A4 collected; FINANCE_A6 hard-wallclock resume in flight (timeout itself is valid evidence) |
| Response point | Explicit INTERNAL_TIME_LIMIT on finance A2/A4; no fabricated penalties. |

### R2: Scalability qualification

| Field | Value |
|---|---|
| Requested evidence | Qualified scalability claim |
| Experiment configuration | Scaling + finance |
| Output table | `scaling_results.csv` |
| Status | **RESOLVED_BY_COMPLETED_RUN** for suite; finance boundary **PARTIAL** pending A6 |
| Response point | Suite scales; finance dense n=1315 is the stress boundary. |

---

## Reviewer 3

### R3: Add-back actually changing outcomes

| Field | Value |
|---|---|
| Requested evidence | Does add-back change the ranking, not just the edge count? |
| Experiment configuration | A0 vs A1 vs A2 — permutation distance, upset deltas |
| Output table | `structural_ablation.csv` with `permutation_distance_vs_p1` |
| Status | **RESOLVED_BY_COMPLETED_RUN** |
| Response point | A2 improves upset_simple vs A0 on 76/77; topo A1 loses to A2 on 32/33. |

### R3: Stronger replacement for ineffective INS1/2/3

| Field | Value |
|---|---|
| Requested evidence | INS1/2/3 nearly identical — better alternative? |
| Experiment configuration | P0–P3, A2, A5/A6 |
| Output table | `legacy_pass_sensitivity.csv`, `structural_ablation.csv` |
| Status | **RESOLVED_BY_COMPLETED_RUN** |
| Response point | P2/P3 add almost no ranking value beyond P1. Reachability + min-cut are the replacements. |

---

## Reviewer 4

### R4: Ablations of the MWFAS backbone

| Field | Value |
|---|---|
| Requested evidence | What does each algorithmic component contribute? |
| Experiment configuration | A0–A6 |
| Output table | `structural_ablation.csv`, `primary_pairwise_statistics.csv` |
| Status | **RESOLVED_BY_COMPLETED_RUN** |
| Response point | Phase A base; reachability ranking gain; refinement ratio gain; min-cut structural gain. |

### R4: Cycle-selection behavior

| Field | Value |
|---|---|
| Requested evidence | How does cycle selection affect results? |
| Experiment configuration | C0 vs C1 on A0 and A4 |
| Output table | `cycle_selection_sensitivity.csv` |
| Status | **RESOLVED_BY_COMPLETED_RUN** |
| Response point | MATERIALLY_SENSITIVE under A4 (small significant Δ); disclose rather than claim inertness. |

### R4: Scalability

| Field | Value |
|---|---|
| Requested evidence | Where does computational cost become limiting? |
| Experiment configuration | Layer 2 + finance |
| Output table | `scaling_results.csv` |
| Status | **PARTIAL** until FINANCE_A6 terminal; suite evidence complete |
| Response point | Cost dominated by Phase A / min-cut; finance is the limiting stress case. |
