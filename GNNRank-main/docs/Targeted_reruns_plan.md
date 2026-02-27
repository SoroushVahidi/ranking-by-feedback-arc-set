# Targeted re-run plan

Based on the coverage and missingness tables, this document lists **minimal** (dataset, method/config, seed) combinations and commands to fill obvious holes. Only re-run what is needed to remove inconsistent or missing data where it would affect the manuscript.

---

## 1) Gaps identified from coverage/missingness

### A) Runtime exists but upset_simple missing (or vice versa)

From `missingness_audit.csv`:

| Method | valid_metrics | valid_runtime | timeouts | Note |
|--------|----------------|---------------|----------|------|
| SVD_NRS | 81 | 80 | 1 | One dataset has valid metrics but valid_runtime is 80 → one row may have metrics and no runtime, or one timeout with no metrics. |
| SVD_RS | 81 | 80 | 1 | Same pattern. |
| SpringRank | 82 | 80 | 2 | Two more valid metric rows than runtime → two (dataset, config) with metrics and no runtime, or two timeouts. |
| syncRank | 79 | 78 | 2 | Two timeouts. |
| mvr | 17 | 16 | 2 | Two timeouts. |
| OURS_MFAS_INS1OURS_MFAS_INS2 | 1 | 0 | 1 | Single row has metrics but no runtime (composite method; low priority). |
| btlDIGRAC | 1 | 0 | 1 | Same (composite; low priority). |

**Action:** For **SVD_NRS**, **SVD_RS**, **SpringRank**: identify the (dataset, method) rows in `leaderboard_per_method.csv` where `runtime_sec` is missing but `upset_simple` is present (or the converse). Re-run those (dataset, method) with the same seed/trial as in the pipeline so that both runtime and metrics are written.

To list such rows from the repo root:
```bash
python -c "
import pandas as pd
from pathlib import Path
p = Path('paper_csv/leaderboard_per_method.csv')
df = pd.read_csv(p)
for m in ['SVD_NRS','SVD_RS','SpringRank']:
    sub = df[df['method']==m]
    no_rt = sub['runtime_sec'].isna()
    has_us = sub['upset_simple'].notna()
    bad = sub[(no_rt & has_us) | (no_rt & ~has_us)]
    if len(bad): print(m, bad[['dataset','method','upset_simple','runtime_sec']].to_string())
"
``` For **syncRank** and **mvr**, the two timeouts each are already recorded; optional re-runs with a longer timeout would only add data if desired.

### B) GNN coverage at 1800 s vs 7200 s

From `leaderboard_compute_matched_coverage.csv`:

- **DIGRAC**: n_within_time_budget = 156, n_timeout = 1.
- **ib**: n_within_time_budget = 155, n_timeout = 2.

So at 1800 s, GNN already has high coverage (155–156 runs within budget). The 1–2 timeouts are the only gap; they are likely on the same large dataset(s). No large “GNN low at 1800 but high at 7200” gap was found; optional re-runs at 7200 s would only fill 1–2 GNN runs.

### C) Finance and OURS

- **OURS** (all variants): **finance** is recorded as `finance:timeout` in `missingness_audit.csv`. So OURS on Finance hits the 1800 s limit and is excluded from compute-matched at 1800 s.
- **Action:** Either (1) **leave as-is** and state in the manuscript that Finance is excluded for OURS under the 1800 s budget, or (2) run OURS on Finance with a **longer timeout** (e.g. 3600 or 7200 s) and add that run to a separate “extended budget” table. No change to the main 1800 s compute-matched table is required unless you choose to extend the budget for Finance only.

---

## 2) Exact (dataset, method/config, seed) to re-run (minimal set)

Only the following are recommended as **targeted** re-runs to fix inconsistent metrics/runtime without re-running the full grid.

### Priority 1: Missing runtime for SVD_NRS, SVD_RS, SpringRank

Identified rows (runtime missing, upset_simple present):

| dataset | method |
|---------|--------|
| Halo2BetaData | SVD_NRS |
| Halo2BetaData | SVD_RS |
| Halo2BetaData | SpringRank |
| _AUTO/Basketball_temporal__1985adj | SpringRank |

**Update:** These four holes are **backfilled** in the pipeline: `build_leaderboard_csvs.py` uses `DATASET_RUNTIME_ALIASES` to fill runtime from the canonical dataset (Halo2BetaData/HeadToHead, Basketball_temporal/1985). See `docs/Missing_runtime_root_cause.md`. Re-runs for these four are no longer required for a consistent leaderboard.

**Example command** (syntax depends on your `train.py` / runner):

```bash
# From GNNRank-main (or repo root). Replace DATASET and METHOD.
python src/train.py --dataset DATASET --baseline METHOD
```

Example for one dataset and SVD_NRS:

```bash
python src/train.py --dataset <dataset_with_missing_runtime> --baseline SVD_NRS
```

Repeat for each (dataset, method) identified in step 1. Use the same `--seed` and trial setup as in the main experiments.

### Priority 2: Optional — OURS on Finance with extended timeout

If you want a single OURS result for Finance (not for the 1800 s table, but for an extended-budget or appendix table):

- **Dataset:** `finance`
- **Method:** `OURS_MFAS_INS3` (or all OURS variants)
- **Change:** Temporarily set the non-GNN timeout to 3600 or 7200 s for this run only.
- **Command:** Same as your normal OURS run for Finance, with the increased timeout.

No need to re-run other methods on Finance unless you want full consistency for that dataset.

### Priority 3: Optional — GNN timeouts (1 DIGRAC, 2 ib)

- Identify the (dataset, config) for which DIGRAC or ib timed out (runtime_sec ≥ 1800 or missing with timeout_flag True).
- Optionally re-run those with GNN timeout 7200 s and add the result to the leaderboard; the main 1800 s compute-matched table stays as-is.

---

## 3) Commands to reproduce full pipeline (for reference)

After any targeted re-runs, regenerate the leaderboard and tables so that the manuscript CSVs and tables are up to date:

```bash
# From repo root (GNNRank-main)
python tools/build_results_table_from_result_arrays.py   # if result_arrays changed
python tools/build_leaderboard_csvs.py
python tools/build_paper_tables.py
python tools/build_paper_figs.py
```

---

## 4) Summary

- **Minimal recommended:** Re-run only the (dataset, method) pairs where **runtime is missing but metrics exist** (or the reverse) for **SVD_NRS**, **SVD_RS**, and **SpringRank**, using the same seed/trial as in the main pipeline.
- **Finance:** Document as excluded for OURS at 1800 s; optionally add OURS-on-Finance with extended timeout for an appendix or extended table.
- **GNN:** Coverage at 1800 s is already high; 1–2 GNN timeouts are optional to fill.
- **Composite methods** (OURS_MFAS_INS1OURS_MFAS_INS2, btlDIGRAC): Low priority; can be left as-is or excluded from the main tables.

This keeps the re-run set small and focused on removing clear inconsistencies rather than re-running all experiments.
