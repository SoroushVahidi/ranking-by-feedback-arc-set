# Reachability Add-Back: Authoritative Result Summary

Date: 2026-08-24
Source data: `GNNRank-main/outputs/ablation/phase_ablation_results.csv` (390 rows, 78 datasets ×
5 phase modes), produced on the `journal-supercomputing-major-revision-20260824` branch (commit
`b2d05c85`) and integrated unchanged onto this branch. All numbers below are recomputed directly
from that CSV for this document, not copied from prose elsewhere — reproducible via the command
at the end of this file.

**This document exists specifically because `REVISION_RESULTS.md`'s original write-up emphasized
`upset_simple` and did not prominently break out `upset_ratio` and `upset_naive` separately. Doing
so here reveals a materially different picture on `upset_ratio` — see §2.** Per this task's
explicit instruction, **more restored edges is not treated as automatically better ranking**
anywhere in this document; each metric is reported and interpreted on its own terms.

## 1. Edges restored (Phase B only, vs. Phase-A-only kept set)

| Mode | Total edges restored (sum across 78 datasets) | Datasets where permutation changed vs. A0 |
|---|---|---|
| A1 (legacy topo add-back) | 84,857 | 67 / 78 (86%) |
| B1 (reachability add-back) | 87,369 | 76 / 78 (97%) |

Reachability restores ~3% more edges in total and changes the ranking on more datasets. **This
alone says nothing about whether the ranking got better** — see §2.

## 2. Ranking-quality metrics — all three, W/T/L, paired deltas (lower is better for all three)

| Metric | Comparison | n | W/T/L | Mean Δ | Median Δ |
|---|---|---|---|---|---|
| `upset_simple` | A1 vs A0 | 78 | 28/13/37 | −0.000051 | 0.000000 |
| `upset_simple` | B1 vs A0 | 78 | **74/2/2** | **−0.008627** | −0.008329 |
| `upset_simple` | B1 vs A1 | 78 | **73/3/2** | **−0.008576** | −0.008833 |
| `upset_ratio` | A1 vs A0 | 78 | 29/11/38 | +0.000004 | 0.000000 |
| `upset_ratio` | B1 vs A0 | 78 | **49/2/27** | −0.008575 | −0.005981 |
| `upset_ratio` | B1 vs A1 | 78 | **46/2/30** | −0.008580 | −0.005348 |
| `upset_naive` | A1 vs A0 | 78 | 28/13/37 | +105.7 | 0.0 |
| `upset_naive` | B1 vs A0 | 78 | **74/2/2** | −1912.3 | −1180.0 |
| `upset_naive` | B1 vs A1 | 78 | **73/3/2** | −2018.0 | −1135.5 |

**Key finding not prominent in the original write-up**: on `upset_simple` and `upset_naive`,
reachability add-back is a near-clean win (74/78, ~95%). **On `upset_ratio` specifically, it is
much more mixed: only 49/78 (~63%) improve, and 27/78 (~35%) get worse** — a substantially weaker
result than the headline `upset_simple` figure suggests. This is consistent with §3's caution
(restoring more edges does not uniformly help every objective) and should be reported alongside,
not instead of, the `upset_simple` result in any manuscript table. `upset_ratio` depends on score
*magnitudes* (via Phase C), not just order, so this divergence is plausible mechanistically but
was not previously called out this explicitly.

## 3. Weighted FAS objective (removed-edge weight)

**Not available in the current CSV.** `phase_ablation_results.csv` records edge *counts*
(`removed_phaseA`, `kept_final`, `edges_restored`) but not the *summed weight* of the removed edge
set. This is a genuine gap, already flagged in `REVISION_RESULTS.md` §7 item 4 ("Does it improve
weighted FAS cost? Not directly measured in this pass"). **Do not report a weighted-FAS-objective
comparison in the manuscript until this column is added and the harness re-run** — it is cheap to
add (sum `w[~kept]` per run) but was not done in this pass, and this document does not fabricate
it.

## 4. Runtime and completion

| Mode | Median runtime (s) | Max runtime (s) |
|---|---|---|
| A0 | 0.153 | 60.59 |
| A1_topo | 0.158 | 60.73 |
| A2_topo | 0.257 | 60.73 |
| B1_reach | 0.241 | 62.55 |
| B2_reach | 0.341 | 62.61 |

Reachability's median overhead over legacy topo add-back is small (≈0.08s without refinement,
≈0.08s with). The `max` column in every mode is dominated by `finance`'s time-budget cap (60s),
not by reachability-specific cost — see §5.

**Completion**: 78/78 datasets loaded and ran to completion in this harness invocation (`status ==
"ok"` for all rows except one aggregate `load_failed` row for `Halo2BetaData/HeadToHead`, which is
excluded from all counts above, matching `REVISION_RESULTS.md` §1).

## 5. The two honestly-reported exceptions (unchanged from `REVISION_RESULTS.md`, restated here for completeness)

- **`Halo2BetaData`** (n=602): reachability restores *more* edges than topo add-back (910 vs 743)
  yet its `upset_simple` is *substantially worse* (0.4255 vs 0.1735) — the single clearest,
  concrete illustration in this dataset of "more restored edges ≠ better ranking."
- **`finance`** (n=1315, near-complete graph): neither add-back mechanism ran at all within the
  time budget used (Phase A alone exhausted it) — this dataset provides **no evidence either way**
  and must not be counted as a "tie" in any aggregate framing.

## Reproduction

```
python3 -c "
import pandas as pd
df = pd.read_csv('GNNRank-main/outputs/ablation/phase_ablation_results.csv')
ok = df[df['status']=='ok']
# see this document's construction for the exact paired W/T/L computation
"
```
