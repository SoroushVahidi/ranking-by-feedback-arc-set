# Post-Ablation Remaining Gaps

Date: 2026-08-25
Branch: `jsuper-reviewer-ablation-scale-20260825`

Identifies any reviewer experiment request that this ablation campaign
does NOT fully close after the raw run + analysis pass.

Status legend: `RESOLVED_BY_COMPLETED_RUN` | `PARTIAL` | `FAILED_TO_COLLECT` | `NOT_APPLICABLE`

---

## Covered by this experiment

| Reviewer | Request | Status |
|---|---|---|
| R1 | Phase 1 only vs full | RESOLVED_BY_COMPLETED_RUN |
| R1 | Density/scale behavior | RESOLVED_BY_COMPLETED_RUN (suite); finance PARTIAL until A6 terminal |
| R1 | Zero tolerance | RESOLVED_BY_COMPLETED_RUN (STABLE) |
| R1 | Insertion passes | RESOLVED_BY_COMPLETED_RUN (P2/P3 weak) |
| R1 | Refinement iterations | RESOLVED_BY_COMPLETED_RUN (saturates) |
| R2 | Timeout/failure robustness | PARTIAL (A0/A2/A4 done; A6 hard-wallclock pending) |
| R2 | Scalability qualification | PARTIAL until FINANCE_A6 terminal (suite done) |
| R3 | Add-back changing outcomes | RESOLVED_BY_COMPLETED_RUN |
| R3 | Replacement for INS1/2/3 | RESOLVED_BY_COMPLETED_RUN |
| R4 | MWFAS backbone ablation | RESOLVED_BY_COMPLETED_RUN |
| R4 | Cycle-selection behavior | RESOLVED_BY_COMPLETED_RUN (material on A4; disclosed) |
| R4 | Scalability | PARTIAL until FINANCE_A6 terminal |

## NOT covered / residual gaps

| # | Reviewer | Request | Why not covered | Status |
|---|---|---|---|---|
| 1 | R3 | Classical comparisons (head-to-head) | Already on runtime-coverage branch | NOT_APPLICABLE here (resolved elsewhere) |
| 2 | R4 | Per-edge component attribution | Stage-level ablation only | NOT_APPLICABLE / low priority |
| 3 | General | Weighted-FAS full-table vs all baselines | Min-cut gains for OURS variants only | PARTIAL (elsewhere) |
| 4 | General | Family-stratified Wilcoxon | n per family too small | NOT_APPLICABLE |
| 5 | R2 | Repeat-trial variance for OURS | OURS deterministic | NOT_APPLICABLE |
| 6 | R2 | FINANCE_A6 terminal class | Resume with 1800s hard wall-clock in flight | PARTIAL → becomes RESOLVED when row written (SUCCESS or TIMEOUT_HARD_WALLCLOCK both valid) |

---

## Summary

- Core non-finance experimental requests: **RESOLVED_BY_COMPLETED_RUN**.
- Remaining experimental gap: **FINANCE_A6 terminal row** (hard timeout counts as collected scalability evidence).
- After FINANCE_A6 lands: re-run `analyze_reviewer_ablation.py` once; update finance table; no campaign relaunch.
