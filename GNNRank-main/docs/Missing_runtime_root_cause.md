# Root cause: missing runtime where upset_simple is present

## Affected (dataset, method) pairs

| dataset | method | config |
|---------|--------|--------|
| Halo2BetaData | SVD_NRS, SVD_RS, SpringRank | trials1train_r100test_r100AllTrue |
| _AUTO/Basketball_temporal__1985adj | SpringRank | trials1train_r100test_r100AllTrue |

## Cause (result_arrays layout)

1. **Halo2BetaData**  
   - The aggregator discovers **two** dataset dirs: `result_arrays/Halo2BetaData/` and `result_arrays/Halo2BetaData/HeadToHead/`.  
   - Under **Halo2BetaData/** there is **upset/** (with SpringRank, SVD_NRS, SVD_RS and config `trials1train_r100test_r100AllTrue`) but **no runtime/** at all.  
   - Under **Halo2BetaData/HeadToHead/** there are both **upset/** and **runtime/** (with config `trials10train_r100test_r100AllTrue`).  
   - So rows for dataset key **"Halo2BetaData"** come from the parent dir and have **no matching runtime** (runtime dir is missing). Rows for **"Halo2BetaData/HeadToHead"** have runtime.  
   - **Root cause:** runtime was never written under `result_arrays/Halo2BetaData/` (only under `Halo2BetaData/HeadToHead/`). Config also differs (trials1 vs trials10), so it is not a simple file-name mismatch.

2. **_AUTO/Basketball_temporal__1985adj**  
   - There is `result_arrays/_AUTO/Basketball_temporal__1985adj/upset/SpringRank/` but **no runtime/** (or no matching runtime .npy) for that dataset dir.  
   - **Root cause:** runtime was never saved for this auto-generated dataset path, or the run did not write to `runtime/` for this key.

## Not a bug in

- **Aggregator** (`build_results_table_from_result_arrays.py`): It correctly looks for `dataset_dir / runtime_which / method / config.npy` and sets `runtime_sec_mean = np.nan` when the file is missing or the directory does not exist.  
- **Parsing:** CSV and .npy reads are consistent; NaN is from the aggregator when no runtime data is found.  
- **Method/config keys:** Method and config names match between upset and runtime where both exist; the issue is absence of runtime data for the above dataset keys.

## Fix options

1. **Backfill in pipeline:** When building the leaderboard, for rows with missing runtime, fill from a **canonical alias** dataset that has the same method (and optionally same or similar config). Example: for dataset `Halo2BetaData`, use runtime from `Halo2BetaData/HeadToHead` for the same method (e.g. mean over configs). Implemented in `build_leaderboard_csvs.py` via `DATASET_RUNTIME_ALIASES`.  
2. **Re-run and save:** Run the affected (dataset, method, config) and ensure runtime is written under the same dataset key (e.g. create `result_arrays/Halo2BetaData/runtime/SVD_NRS/...`).  
3. **Drop duplicate key:** Treat only `Halo2BetaData/HeadToHead` as the canonical dataset and do not emit rows for `Halo2BetaData` from the aggregator (e.g. filter in aggregator or leaderboard). That removes the hole by not reporting the incomplete key.
