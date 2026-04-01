# Legacy manuscript tables (historical reference only)

`GNNRank-main/paper_tables/` is a **legacy** location and is **not** the canonical source for current manuscript-facing numbers.

## Canonical source of truth

Use the canonical paper-artifact pipeline and outputs under `GNNRank-main/outputs/` (for example `GNNRank-main/outputs/paper_tables/` and `GNNRank-main/outputs/audits/`). Do not cite values from this legacy folder for current manuscript claims.

## What this folder contains

These files were historical CSV/LaTeX table exports (for example leaderboard, compute-matched, and missingness summaries) that were originally generated from leaderboard-style CSV inputs.

## Current policy

- Keep these files only for historical reference.
- Prefer regenerating manuscript artifacts from the canonical pipeline instead of editing or merging legacy table files by hand.
Use the tabulars inside a `table` (or `longtable`) environment and add `\caption{...}` and `\label{...}` as in the comments at the bottom of each file.

## ⚠️ Status: Legacy (superseded)

These files use **`/81` denominators** (including the extra `_AUTO/Basketball_temporal__1985adj` dataset
that is NOT part of the 80-dataset manuscript benchmark).

**For manuscript submission, use `GNNRank-main/outputs/paper_tables/` instead:**

| Legacy file (here) | Canonical replacement (path from repo root) |
|--------------------|-----------------------|
| table1_main_leaderboard.csv | `GNNRank-main/outputs/paper_tables/table4_full_suite.csv` |
| table2_compute_matched.csv | `GNNRank-main/outputs/paper_tables/table5_compute_matched.csv` |
| table3_missingness_audit.csv | `GNNRank-main/outputs/paper_tables/table6_missingness.csv` |

Additional corrections documented in `docs/audits/REPO_ORGANIZATION_AND_REPAIR_REPORT.md`:
- btl and davidScore values in early draft were swapped and numerically wrong
- Football n-range claim (20–107) was incorrect; n=20 for all 12 football instances
- All `GNNRank-main/outputs/paper_tables/` files are regenerated directly from
  `GNNRank-main/paper_csv/leaderboard_per_method.csv`

To regenerate (run from the repository root):
```bash
python GNNRank-main/scripts/paper/run_all_paper_artifacts.py
```

