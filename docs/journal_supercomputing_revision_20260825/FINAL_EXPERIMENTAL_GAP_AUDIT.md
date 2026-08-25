# Final Experimental Gap Audit


> **SUPERSEDED NOTE (2026-08-25, runtime-provenance fix):** the raw `1214.76`/`1214.57` Finance timings cited below are per-run harness-timer readings, not single-invocation `OURS-Reach` algorithm cost -- each contains a diagnostic Phase-A-only rerun (used only to compute a permutation-distance sensitivity statistic) that inflates the reading by roughly one extra Phase-A execution (~612s on Finance). The corrected algorithm-only Finance timings are ~600.5s (A0), ~602.3s (A2/A4); `1800.10s` (A6, hard-wallclock timeout without a finished ranking) is unaffected. See `RUNTIME_PROVENANCE_AUDIT.md` for the full analysis.
Date: 2026-08-25  
Branch: `jsuper-final-experimental-gaps-20260825`  
Base SHA: `d38244d61aa511183fab58c4ca5cbf4e8ca0f9b4`  
Integrated evidence SHAs:
- reviewer ablation finalize: `d38244d6`
- runtime/coverage final: `981dc22117320b1d3b6887ffa2dc9cc998445442`
- min-cut characterization: `904332b2f0abae90dbc4d2ce11b96e49644deb58`
- manuscript-prep (prose only; not merged): `1af67628`

This audit covers **experimentally testable** reviewer concerns only.
No manuscript rewriting was performed in this task.

---

## Status legend

RESOLVED | RESOLVED_WITH_NEGATIVE_RESULT | RESOLVED_BY_EXISTING_EVIDENCE |
PARTIAL | UNRESOLVED | NOT_EXPERIMENTAL

---

## Reviewer experimental matrix

| ID | Concern | Status | Evidence |
|---|---|---|---|
| R1 stage ablation | RESOLVED | Ablation A0–A6; 1009/1009; aggregates committed |
| R1 density/scale | RESOLVED | Layer2 + scaling_results; finance boundary |
| R1 zero_tol | RESOLVED | STABLE grid |
| R1 insertion passes | RESOLVED_WITH_NEGATIVE_RESULT | P2/P3 weak |
| R1 refinement | RESOLVED | saturates |
| R2 timeout/coverage | RESOLVED | completion matrix + finance classes |
| R2 classical runtime W/T/L | RESOLVED_BY_EXISTING_EVIDENCE | `CLASSICAL_RUNTIME_FINAL.md` / e1 |
| R2 statistics/Holm | RESOLVED_BY_EXISTING_EVIDENCE | runtime-coverage final |
| R2 Basketball independence | RESOLVED_WITH_NEGATIVE_RESULT | family-aware analysis; SpringRank claims weakened |
| R2 GNN ~8× fairness | RESOLVED_BY_EXISTING_EVIDENCE | accounting audit verdict **B** (qualify; no rerun) |
| R2 scalability wording | RESOLVED | finance A0/A2/A4 limits + A6 hard wall-clock timeout |
| R3 INS ineffective | RESOLVED_WITH_NEGATIVE_RESULT | P-grid |
| R3 stronger mechanism | RESOLVED | reachability + min-cut structural gains |
| R3 classical head-to-head | RESOLVED_BY_EXISTING_EVIDENCE | runtime-coverage / classical finals |
| R4 backbone ablation | RESOLVED | A0–A6 |
| R4 cycle selection | RESOLVED_WITH_NEGATIVE_RESULT | small but significant under A4 |
| R4 scalability | RESOLVED | suite + finance hard failures |
| Weighted-FAS full-table all baselines | PARTIAL | min-cut weighted gains for OURS variants; not full 12-baseline weighted table |
| Per-edge attribution | NOT_EXPERIMENTAL / low priority | stage-level ablation answers component question |
| OURS repeat-trial variance | NOT_EXPERIMENTAL | deterministic method |
| Exact GPU model ledger for archived GNN runs | PARTIAL | README CUDA capability; no locked GPU serial for archived arrays — mitigated by qualification, not blocking |

---

## E1 FINANCE_A6

| Field | Value |
|---|---|
| Status | **TIMEOUT_HARD_WALLCLOCK** |
| Runtime | 1800.10 s hard wall-clock timeout (no completed algorithm runtime) |
| Campaign | **1009/1009** terminal |
| Non-finance aggregates changed? | **No** (primary pairwise identical to 1008 snapshot) |

---

## E2 family-aware

Completed with frozen mapping, equal-family, LOFO, Basketball collapse,
hierarchical bootstrap. Principal quality conclusions **partially survive**;
SpringRank/davidScore claims must be weakened; BTL upset_ratio loss persists.

---

## E3 GNN timing

Verdict **B** — no targeted rerun launched.

---

## Closure declaration

Weighted-FAS comparison across all baselines remains only partially filled
(min-cut branch covers OURS-side weighted gains). That item is **scientific
nice-to-have / partial**, already documented on prior branches, and is **not**
an unfinished launched experiment.

For the originally scoped experimental campaign of this revision (ablation,
finance stress, family-aware sensitivity, runtime accounting qualification):

**NO_REMAINING_EXPERIMENTAL_GAPS**

Optional future work (not blocking): controlled GNN stage-timing study with
hardware manifest; full weighted-FAS table for all baselines.
