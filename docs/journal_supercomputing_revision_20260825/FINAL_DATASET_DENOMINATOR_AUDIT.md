# Final Dataset Denominator Audit

Date: 2026-08-25  
Branch: `jsuper-manuscript-major-revision-20260825`  
Checkpoint: `checkpoint-before-dataset-denominator-audit` (`35e77e7b`)

## Authoritative identity

```
INTENDED = 80
AVAILABLE / LOADABLE = 78
MISSING = [
  ERO/p5K5N350eta10styleuniform,
  Halo2BetaData/HeadToHead
]
EXCLUDED_EXTRA = [
  _AUTO/Basketball_temporal__1985adj
]
HALO_LOADABLE_MEMBER = Halo2BetaData
```

Provenance:

- Intended suite: `outputs/derived/dataset_inventory.csv` (`in_80_suite=True` → 80; extra `_AUTO` → False).
- Family counts match `docs/paper/PAPER_ARTIFACTS_README.md` (30+30+6+6+3+1+2+1+1 = 80).
- Loadability: robust loader (`_robust_load_real_data`) over the 80 IDs → **78 OK**, **2 FileNotFoundError** (ERO + HeadToHead).
- `_AUTO/...1985adj` loads and duplicates Basketball 1985 (`n=282`, `m=2904`) but is **outside** the 80-suite.

## Root cause of “80 − 2 = 79”

**Stale / arithmetically wrong prose**, not a second missing file.

The manuscript correctly named two missing adjacency IDs but incorrectly wrote “effective denominator of 79.”  
Correct arithmetic: \(80-2=78\).

A contributing confusion: archived `e2_completion_matrix.csv` has **79 rows** because it

1. **omits** loadable `Halo2BetaData`, and  
2. **includes** `Halo2BetaData/HeadToHead` (archived SUCCESS for classical/OURS under that label) **and** ERO (NOT_RUN),

so `e2_coverage_matrix.csv` set `intended=79`. That 79-row leaderboard slice is **not** “80 minus two missing files.” Coverage claims must use the loadable inventory (**78**), not the e2 row count.

## Status of special IDs

| ID | In intended 80? | File / loadable? | Role |
|---|---|---|---|
| `ERO/p5K5N350eta10styleuniform` | Yes | No adj; NOT_RUN in e2 | Missing / suite member |
| `Halo2BetaData/HeadToHead` | Yes | No resolvable `adj.npz` under robust loader | Missing suite ID |
| `Halo2BetaData` | Yes | Yes (`data/Halo2BetaData/adj.npz`) | Loadable Halo member used by OURS-Reach A4 |
| `_AUTO/Basketball_temporal__1985adj` | No | Yes (duplicate of 1985) | Excluded extra (raw count 81) |

## Coverage over loadable 78

Recomputed from `e2_completion_matrix.csv` after dropping ERO (78-row loadable proxy; Halo labeled `HeadToHead` in that archive):

| Method | Success | Fraction | Percent |
|---|---:|---|---:|
| OURS (archived / OURS-Reach completion) | 77 | 77/78 | 98.7% (Finance timeout) |
| SpringRank, BTL, PageRank, DavidScore, SVD_NRS, SerialRank, RankCentrality | 78 | 78/78 | 100% |
| SyncRank | 77 | 77/78 | 98.7% (Finance timeout) |
| DIGRAC / ib | 61 | 61/78 | 78.2% (primarily N/A, not timeout) |

### Were 77/79, 78/79, 61/79 correct?

| Claim | Verdict |
|---|---|
| 77/79 | **Incorrect denominator** (should be **77/78**) |
| 78/79 | **Incorrect denominator** (should be **78/78**) |
| 61/79 | **Incorrect denominator** (should be **61/78**) |

Numerators matched archived SUCCESS counts; the readable denominator was wrong.

## OURS-Reach vs headline tables

- Canonical A4 metrics: `a4_gnnrank_metrics.csv` → **77** complete datasets including `Halo2BetaData`, excluding Finance/ERO/HeadToHead.
- Pairwise quality/runtime tables use common-completion \(n=77\) (OURS vs classical) / \(n=60\) (vs GNN) — unchanged and consistent.
- Coverage prose now uses loadable **78**, distinct from pairwise \(n\).

## Family mapping

- Intended Halo family size in the 80-suite: **2** IDs; loadable Halo graphs: **1** (`Halo2BetaData`).
- ERO: `included_if_present` in family mapping; not loadable → absent from quality macros.
- `_AUTO` appears in `family_mapping.csv` as `included` but is **not** in equal-family result CSVs (mapping hygiene note only; not a manuscript denominator).
- Family-aware quality macros exclude Finance (unchanged).

## Full inventory table

See machine-oriented reconstruction: every `dataset_inventory.csv` row with loadability from the robust loader is summarized in the checker’s PASS output and in `FINAL_DATASET_DENOMINATOR_TABLE.csv` (generated alongside this audit).

## Required statuses

- `NO_DENOMINATOR_INCONSISTENCY` — after manuscript/response repair  
- `NO_UNTRACEABLE_COVERAGE_CLAIMS` — fractions tied to e2∖ERO and inventory  
- `DATASET_DENOMINATOR_CONSISTENCY = PASS` — `check_dataset_denominator_consistency.py`
