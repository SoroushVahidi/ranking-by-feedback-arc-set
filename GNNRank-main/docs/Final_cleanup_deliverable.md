# Final cleanup + sanity checks — deliverable

## 1) Root cause (missing runtime)

**Doc:** `docs/Missing_runtime_root_cause.md`

- **Halo2BetaData (SVD_NRS, SVD_RS, SpringRank):** `result_arrays/Halo2BetaData/` has **upset/** but **no runtime/**; runtime exists only under `Halo2BetaData/HeadToHead/`. So the aggregator correctly outputs NaN for runtime for dataset key `"Halo2BetaData"`. Not a parsing bug; runtime was never written for that key.
- **_AUTO/Basketball_temporal__1985adj (SpringRank):** Same: no **runtime/** (or no matching .npy) for that dataset dir.

## 2) Patches / changes

### tools/build_leaderboard_csvs.py

- **Added** `DATASET_RUNTIME_ALIASES`: map `Halo2BetaData` → `Halo2BetaData/HeadToHead`, `_AUTO/Basketball_temporal__1985adj` → `Basketball_temporal/1985`.
- **Added** `_backfill_runtime_from_aliases(lb, ra)`: for rows with missing runtime and valid upset_simple, fill `runtime_sec` from the canonical alias dataset (same method, mean over configs). Called after building the leaderboard DataFrame.
- **Effect:** The four previously missing-runtime rows (Halo2BetaData x3, _AUTO x1) now get runtime from the alias; compute_matched row count increases (e.g. 1436 → 1440).

### tools/validate_paper_artifacts.py (new)

- **Check 1 — Missing runtime:** Fail if any row has `upset_simple` and missing `runtime_sec` unless (dataset, method) or method is in the whitelist (finance timeouts, Dryad GNN, composite methods).
- **Check 2 — Coverage mismatch:** Fail if table1 coverage total ≠ leaderboard unique dataset count.
- **Check 3 — Oracle guardrail:** Fail if table1/table2 have best_* columns but no `method` column (oracle used as main table).
- **Check 4 — Determinism:** Fail if `results_from_result_arrays.csv` has `num_runs==1` and `upset_simple_std > 0`.
- Writes **docs/Artifact_validation_report.md** and exits with code 1 on any failure.

### tools/build_all_paper_artifacts.sh (new)

- Runs in order: `build_leaderboard_csvs.py` → `validate_paper_artifacts.py` → `build_paper_tables.py` → `build_paper_figs.py` → `validate_paper_artifacts.py`.
- Idempotent; prints output paths at the end.
- Usage: `bash tools/build_all_paper_artifacts.sh` from repo root.

### docs/Missing_runtime_root_cause.md (new)

- Describes affected (dataset, method) pairs, cause (result_arrays layout), and fix options (backfill, re-run, drop key).

### docs/Targeted_reruns_plan.md (updated)

- Notes that the four Halo2BetaData / _AUTO holes are fixed by backfill; re-runs for those four no longer required.

## 3) Validator report

Generated at **docs/Artifact_validation_report.md** (overwritten each run). Sections: Missing runtime, Coverage mismatch, Oracle guardrail, Determinism, Overall PASSED/FAILED.

## 4) How to run

```bash
cd GNNRank-main
bash tools/build_all_paper_artifacts.sh
```

Or step by step:

```bash
python tools/build_leaderboard_csvs.py
python tools/validate_paper_artifacts.py
python tools/build_paper_tables.py
python tools/build_paper_figs.py
python tools/validate_paper_artifacts.py
```
