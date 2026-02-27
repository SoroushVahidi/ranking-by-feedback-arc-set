# Deliverable: repository audit + leaderboard pipeline

## 1) Audit: where “best GNN” and “best classical” are computed

See **`docs/Repository_audit_best_gnn_classical.md`** for the full audit. Summary:

- **Load per-method/per-variant:** `tools/build_results_table_from_result_arrays.py` (lines 39–58, 109–185) → **paper_csv/results_from_result_arrays.csv**. `tools/build_unified_comparison.py` (46–53) loads that CSV and **full_833614_metrics_best.csv**.
- **Best classical:** `tools/build_unified_comparison.py` **83–100** — min of `upset_simple_mean` over `CLASSICAL` list per dataset.
- **Best GNN:** `tools/build_unified_comparison.py` **104–113** — `gnn_rows["upset_simple_mean"].idxmin()` over rows with `method in ["DIGRAC", "ib", "DIGRACib"]` from result_arrays only.
- **Aggregate for manuscript:** **paper_csv/unified_comparison.csv** (one row per dataset: ours + best_classical + best_gnn), produced in `build_unified_comparison.py` 56–134.

---

## 2) Files to edit / add (no edits to existing code; only new files)

| Action | Path |
|--------|------|
| **Add** | `docs/Repository_audit_best_gnn_classical.md` |
| **Add** | `tools/build_leaderboard_csvs.py` |
| **Add** | `paper_csv/README_leaderboard_outputs.md` |

No patches to existing files; the new pipeline is self-contained.

---

## 3) New CSV schemas and where they are written

| CSV | Path | Schema |
|-----|------|--------|
| **A) Per-method leaderboard** | `paper_csv/leaderboard_per_method.csv` | dataset, method, config, upset_simple, upset_naive, upset_ratio, kendall_tau, runtime_sec, timeout_flag, seed, trial_id, source |
| **B) Oracle envelopes** | `paper_csv/leaderboard_oracle_envelopes.csv` | dataset, best_classical_upset_simple, best_classical_upset_naive, best_classical_upset_ratio, best_classical_runtime_sec, best_classical_method, best_gnn_upset_simple, best_gnn_upset_naive, best_gnn_upset_ratio, best_gnn_runtime_sec, best_gnn_method, best_gnn_config |
| **C) Compute-matched** | `paper_csv/leaderboard_compute_matched.csv` | Same as (A), but only rows with runtime_sec ≤ 1800. |
| **C) Coverage** | `paper_csv/leaderboard_compute_matched_coverage.csv` | method, n_datasets_with_any_row, n_valid_upset_simple, n_valid_runtime, n_timeout, n_within_time_budget |
| **Missingness audit** | `paper_csv/missingness_audit.csv` | method, n_datasets_with_valid_metrics, n_datasets_with_valid_runtime, n_timeouts, finance_like_exclusions |

All under **GNNRank-main/paper_csv/**.

---

## 4) README snippet for manuscript

Use this (or adapt) in the paper or supplement:

```markdown
## Leaderboard and audit outputs

Per-method results (no oracle) are in `leaderboard_per_method.csv`: one row per (dataset, method) or (dataset, method, config) for all OURS variants, classical baselines, and each GNN variant. Oracle envelopes (best classical and best GNN per dataset, with the method that achieved each) are in `leaderboard_oracle_envelopes.csv`. For a shared time budget of 1800s, compute-matched results are in `leaderboard_compute_matched.csv`, with coverage and timeout counts in `leaderboard_compute_matched_coverage.csv`. Missingness is not silently dropped: `missingness_audit.csv` records per-method valid metrics, valid runtime, timeouts, and Finance-like exclusions (e.g. finance:no_data, finance:timeout). All CSVs are produced by `tools/build_leaderboard_csvs.py`.
```

---

## 5) How to run

From repo root (GNNRank-main):

```bash
python tools/build_leaderboard_csvs.py
```

This ensures **paper_csv/results_from_result_arrays.csv** exists (runs `build_results_table_from_result_arrays.py` if missing), then writes the five outputs above.
