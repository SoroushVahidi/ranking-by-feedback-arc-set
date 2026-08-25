# Introduction Consistency Check

Date: 2026-08-25

## Forbidden / unsafe wording scan (rewritten Intro + contributions only)

| Term | Intro uses? | Verdict |
|---|---|---|
| scalable (our method, unqualified) | No | Pass |
| Scalability (qualified) | Yes — sparse/moderate; Finance boundary | Pass |
| novel / novelty | Only to deny dataset expansion as primary novelty | Pass |
| new (algorithm) | Only in “does not propose a new general approximation algorithm” | Pass |
| approximation guarantee | Explicit non-inheritance under early termination | Pass |
| faster | Only vs trained GNN end-to-end; classical = slower | Pass |
| state-of-the-art | Absent | Pass |
| outperforms | Absent | Pass |
| robust | Absent in rewritten block | Pass |
| 80 datasets | Absent as boast | Pass |
| INS | Removed from Intro contribution framing | Pass |

## Evidence trace for numerical / directional Intro claims

| Claim | Authoritative source |
|---|---|
| Slower than lightweight classical | `CLASSICAL_RUNTIME_FINAL.md` (OURS slower on majority vs SpringRank/BTL/…) |
| Faster than trained GNN end-to-end | `GNN_RUNTIME_ACCOUNTING_AUDIT.md` + classical runtime GNN ratios |
| Competitive vs SpringRank/davidScore/SVD_NRS | `FAMILY_AWARE_BASELINE_ANALYSIS.md` |
| BTL stronger on upset_ratio | Same (7/7 families) |
| Reachability fidelity matters | `REVIEWER_ABLATION_FINAL_ANALYSIS.md` (A0→A2 / A1→A2) |
| Finance dense boundary | Runtime/coverage + ablation Finance rows |
| No unconditional DF03 transfer under timeout | `APPROXIMATION_GUARANTEE_AUDIT.md` |
| Prior add-back / local-ratio lineage | `PRIOR_ADDBACK_LINEAGE.md`, `REVISED_CONTRIBUTION_POSITIONING.md` |

## Residual inconsistency (expected; deferred)

Framework § opening still contains submitted oversell (“practical, scalable… multi-pass add-back”) — **not edited in this pass** per task O.
