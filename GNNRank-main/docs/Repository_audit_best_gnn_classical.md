# Repository audit: where “best GNN” and “best classical” are computed

(Experiments rewrite, no new runs yet.)

## 1) Where results are loaded

| Source | Script | Line range | What is loaded |
|--------|--------|------------|----------------|
| **result_arrays/** (recursive) | `tools/build_results_table_from_result_arrays.py` | 39–58 `find_dataset_dirs`, 60–106 agg, 109–185 main | All `result_arrays/**/upset/`, `**/upset_latest/`, `**/runtime/`, `**/runtime_latest/`; each `.npy` → one row with dataset, method, config, which, upset_*_mean/std, runtime_sec_mean/std, num_runs, num_nans |
| **results_from_result_arrays.csv** | `tools/build_unified_comparison.py` | 45–49 `load_from_result_arrays()` | Reads CSV; keeps `which == "upset"` only |
| **full_833614_metrics_best.csv** | `tools/build_unified_comparison.py` | 51–53 `load_full_metrics()` | Fallback for dataset/method not in result_arrays |
| **full_833614_metrics_best.csv** | `compute_wtl_by_metric.py` | 138–139 | Full CSV; expects also `per_dataset_summary.csv` for family (deleted in current repo) |
| **paper_csv/unified_comparison.csv** | `tools/compute_contribution_stats.py` | 65–66 | Reads unified CSV; uses only rows with `ours_upset_simple` present |

## 2) Where “best-of” across variants/methods is chosen

### Best classical (min upset_simple over classical baselines)

| Script | Line range | Definition |
|--------|------------|------------|
| **tools/build_unified_comparison.py** | 83–100 | For each dataset: loop over `CLASSICAL` methods; take **min** of `upset_simple_mean` (from ra then full); store `best_classical_upset_simple`, `best_classical_upset_ratio`, `best_classical_upset_naive`, `best_classical_runtime_sec` |
| **compute_wtl_by_metric.py** | 154–167 | `classical_df.groupby("dataset").agg(best_classical_upset_simple=("upset_simple_mean", "min"), ...)` — same idea, different input CSV |
| **delta_mode_a_vs_b.py** | 80–84 | `classical.groupby("dataset").agg(upset_simple_mean=("upset_simple_mean", "min"), ...).rename(..., best_classical_upset_simple=...)` |

### Best GNN candidate (min upset_simple across GNN variants)

| Script | Line range | Definition |
|--------|------------|------------|
| **tools/build_unified_comparison.py** | 104–113 | For each dataset: `gnn_rows = ra[(dataset) & method in GNN_METHODS]`; **`idx = gnn_rows["upset_simple_mean"].idxmin()`**; then `best_gnn_row = gnn_rows.loc[idx]` → best_gnn_upset_simple/ratio/naive/runtime. **GNN_METHODS = ["DIGRAC", "ib", "DIGRACib"]** (line 37). Only from **result_arrays**; full_833614_metrics_best has no GNN rows. |
| **compute_wtl_by_metric.py** | 174–191 | `gnn_df.groupby("dataset")`; for each dataset **`idx = valid["upset_simple_mean"].idxmin()`**; one row per dataset with best_gnn_* and **best_gnn_method**. Uses GNN_METHODS = DIGRAC_dist, DIGRAC_proximal_baseline, ib_dist, ib_proximal_baseline (different naming than result_arrays). |

## 3) Where results are aggregated into CSVs used for manuscript tables

| Output CSV | Produced by | Line range | Contents |
|------------|-------------|------------|----------|
| **paper_csv/results_from_result_arrays.csv** | `tools/build_results_table_from_result_arrays.py` | 176–186 | One row per (dataset, method, config, which); columns: upset_simple_mean, upset_simple_std, upset_ratio_mean, upset_ratio_std, upset_naive_mean, upset_naive_std, runtime_sec_mean, runtime_sec_std, num_runs, num_nans |
| **paper_csv/unified_comparison.csv** | `tools/build_unified_comparison.py` | 56–134, 132–134 | One row **per dataset**: ours_* (OURS_MFAS_INS3), best_classical_*, best_gnn_* (min over DIGRAC/ib/DIGRACib from ra only) |
| **paper_csv/contribution_stats.csv** | `tools/compute_contribution_stats.py` | (writes from stats dict) | Aggregated W/T/L and stats; **input** is unified_comparison.csv |
| **paper_csv/contribution_report.md** | `tools/compute_contribution_stats.py` | 245–315 | Human-readable report from same stats |

## 4) Summary

- **Load per-method/per-variant:** `build_results_table_from_result_arrays.py` (from disk) → `results_from_result_arrays.csv`; `build_unified_comparison.py` also loads `full_833614_metrics_best.csv`.
- **Choose best classical:** In `build_unified_comparison.py` (83–100): min of `upset_simple_mean` over `CLASSICAL` list; in `compute_wtl_by_metric.py` (154–167) and `delta_mode_a_vs_b.py` (80–84) similarly.
- **Choose best GNN:** In `build_unified_comparison.py` (104–113): `gnn_rows["upset_simple_mean"].idxmin()` over rows with `method in ["DIGRAC", "ib", "DIGRACib"]` from result_arrays only.
- **Aggregate for manuscript:** `unified_comparison.csv` is the main per-dataset table (ours + best_classical + best_gnn); `contribution_stats.csv` and `contribution_report.md` are derived from it.
