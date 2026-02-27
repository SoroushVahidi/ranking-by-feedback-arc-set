#!/usr/bin/env python3
"""
Build three leaderboard CSVs and a missingness audit for the manuscript.

Inputs:
  - paper_csv/results_from_result_arrays.csv (from tools/build_results_table_from_result_arrays.py)
  - full_833614_metrics_best.csv (optional fallback for datasets/methods not in result_arrays)

Outputs (all under paper_csv/):
  A) leaderboard_per_method.csv   — one row per (dataset, method) [no oracle]
  B) leaderboard_oracle_envelopes.csv — per-dataset best_classical / best_gnn with which method
  C) leaderboard_compute_matched.csv  — same schema as (A) filtered to runtime_sec <= time_budget_sec, + coverage
  D) missingness_audit.csv       — per-method: n_valid_metrics, n_valid_runtime, n_timeout, Finance_excluded

Run from repo root: python tools/build_leaderboard_csvs.py
"""

import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOLS = REPO_ROOT / "tools"
AGGREGATOR = TOOLS / "build_results_table_from_result_arrays.py"
RESULTS_CSV = REPO_ROOT / "paper_csv" / "results_from_result_arrays.csv"
FULL_METRICS_CSV = REPO_ROOT / "full_833614_metrics_best.csv"
PAPER_CSV = REPO_ROOT / "paper_csv"
UNIFIED_COMPARISON_CSV = PAPER_CSV / "unified_comparison.csv"

# Output paths
OUT_LEADERBOARD = PAPER_CSV / "leaderboard_per_method.csv"
OUT_ORACLE = PAPER_CSV / "leaderboard_oracle_envelopes.csv"
OUT_COMPUTE_MATCHED = PAPER_CSV / "leaderboard_compute_matched.csv"
OUT_MISSINGNESS = PAPER_CSV / "missingness_audit.csv"

# Method groups (must match build_unified_comparison / train.py naming)
CLASSICAL = [
    "SpringRank", "syncRank", "serialRank", "btl", "davidScore",
    "eigenvectorCentrality", "PageRank", "rankCentrality", "SVD_RS", "SVD_NRS",
]
GNN_METHODS = ["DIGRAC", "ib", "DIGRACib"]
OURS_METHODS = ["OURS_MFAS", "OURS_MFAS_INS1", "OURS_MFAS_INS2", "OURS_MFAS_INS3"]

# Time budget for compute-matched (seconds)
TIME_BUDGET_SEC = 1800.0
# Infer timeout: no runtime or runtime >= this
TIMEOUT_THRESHOLD_SEC = 1800.0

# Datasets we explicitly treat as excluded (e.g. Finance) when reporting
EXPLICIT_EXCLUSIONS = ["finance"]

# Dataset -> canonical dataset key that has runtime (for backfilling missing runtime)
# See docs/Missing_runtime_root_cause.md
DATASET_RUNTIME_ALIASES = {
    "Halo2BetaData": "Halo2BetaData/HeadToHead",
    "_AUTO/Basketball_temporal__1985adj": "Basketball_temporal/1985",
}


def ensure_aggregator_run():
    # Always refresh so new result_arrays runs are picked up.
    # This keeps the pipeline consistent after targeted re-runs (e.g., OURS-only verification).
    subprocess.check_call([sys.executable, str(AGGREGATOR)], cwd=str(REPO_ROOT))


def load_ra() -> pd.DataFrame:
    df = pd.read_csv(RESULTS_CSV)
    df = df[df["which"] == "upset"].copy()
    # Keep the paper suite stable: if unified_comparison.csv exists, restrict to its dataset list.
    if UNIFIED_COMPARISON_CSV.exists():
        try:
            suite = pd.read_csv(UNIFIED_COMPARISON_CSV)
            suite_datasets = set(suite["dataset"].astype(str).unique())
            df = df[df["dataset"].astype(str).isin(suite_datasets)].copy()
        except Exception:
            # If unified_comparison is malformed, fall back to all datasets.
            pass
    return df


def load_full() -> pd.DataFrame:
    if not FULL_METRICS_CSV.exists():
        return pd.DataFrame()
    df = pd.read_csv(FULL_METRICS_CSV)
    # Keep paper suite stable (same filter as load_ra).
    if UNIFIED_COMPARISON_CSV.exists() and "dataset" in df.columns:
        try:
            suite = pd.read_csv(UNIFIED_COMPARISON_CSV)
            suite_datasets = set(suite["dataset"].astype(str).unique())
            df = df[df["dataset"].astype(str).isin(suite_datasets)].copy()
        except Exception:
            pass
    return df


def build_leaderboard_per_method(ra: pd.DataFrame, full: pd.DataFrame) -> pd.DataFrame:
    """One row per (dataset, method, config). No oracle."""
    rows = []
    # From result_arrays we have dataset, method, config, upset_*_mean, runtime_sec_mean
    for _, r in ra.iterrows():
        rt = float(r["runtime_sec_mean"]) if pd.notna(r["runtime_sec_mean"]) else np.nan
        timeout_flag = (
            True
            if (np.isnan(rt) or rt >= TIMEOUT_THRESHOLD_SEC)
            else False
        )
        rows.append({
            "dataset": r["dataset"],
            "method": r["method"],
            "config": r["config"] if pd.notna(r["config"]) else "",
            "upset_simple": float(r["upset_simple_mean"]),
            "upset_naive": float(r["upset_naive_mean"]),
            "upset_ratio": float(r["upset_ratio_mean"]),
            "kendall_tau": np.nan,  # not in current aggregator
            "runtime_sec": rt,
            "timeout_flag": timeout_flag,
            "seed": np.nan,
            "trial_id": np.nan,
            "source": "result_arrays",
        })
    # Add any (dataset, method) from full that are not already in ra
    keys_ra = set(zip(ra["dataset"].astype(str), ra["method"].astype(str)))
    if not full.empty:
        for _, r in full.iterrows():
            ds, m = str(r["dataset"]), str(r["method"])
            if (ds, m) in keys_ra:
                continue
            keys_ra.add((ds, m))
            us = float(r["upset_simple_mean"]) if pd.notna(r.get("upset_simple_mean")) else np.nan
            un = float(r["upset_naive_mean"]) if pd.notna(r.get("upset_naive_mean")) else np.nan
            ur = float(r["upset_ratio_mean"]) if pd.notna(r.get("upset_ratio_mean")) else np.nan
            rt = float(r["runtime_sec_mean"]) if pd.notna(r.get("runtime_sec_mean")) else np.nan
            timeout_flag = True if (np.isnan(rt) or rt >= TIMEOUT_THRESHOLD_SEC) else False
            rows.append({
                "dataset": ds,
                "method": m,
                "config": "",
                "upset_simple": us,
                "upset_naive": un,
                "upset_ratio": ur,
                "kendall_tau": np.nan,
                "runtime_sec": rt,
                "timeout_flag": timeout_flag,
                "seed": np.nan,
                "trial_id": np.nan,
                "source": "full_metrics",
            })
    df = pd.DataFrame(rows)
    # Backfill missing runtime from alias dataset (same method)
    df = _backfill_runtime_from_aliases(df, ra)
    return df


def _backfill_runtime_from_aliases(lb: pd.DataFrame, ra: pd.DataFrame) -> pd.DataFrame:
    """Fill runtime_sec when missing using same-method runtime from alias dataset."""
    lb = lb.copy()
    # Build (alias_ds, method) -> mean runtime from ra
    alias_runtime = {}
    for _, r in ra.iterrows():
        ds, m = str(r["dataset"]), str(r["method"])
        rt = r.get("runtime_sec_mean")
        if pd.isna(rt) or not np.isfinite(rt):
            continue
        for short_ds, canonical_ds in DATASET_RUNTIME_ALIASES.items():
            if ds == canonical_ds:
                key = (short_ds, m)
                if key not in alias_runtime:
                    alias_runtime[key] = []
                alias_runtime[key].append(float(rt))
    for key in alias_runtime:
        alias_runtime[key] = float(np.mean(alias_runtime[key]))
    # Apply backfill
    for idx, row in lb.iterrows():
        if pd.notna(row.get("runtime_sec")) and np.isfinite(row["runtime_sec"]):
            continue
        if pd.isna(row.get("upset_simple")):
            continue
        ds, m = str(row["dataset"]), str(row["method"])
        if ds not in DATASET_RUNTIME_ALIASES:
            continue
        key = (ds, m)
        if key in alias_runtime:
            lb.at[idx, "runtime_sec"] = alias_runtime[key]
            lb.at[idx, "timeout_flag"] = alias_runtime[key] >= TIMEOUT_THRESHOLD_SEC
    return lb


def build_oracle_envelopes(lb: pd.DataFrame) -> pd.DataFrame:
    """Per-dataset: best_classical_* and best_gnn_* with which method achieved it."""
    classical_set = set(CLASSICAL)
    gnn_set = set(GNN_METHODS)
    records = []
    for dataset in sorted(lb["dataset"].unique()):
        sub = lb[lb["dataset"] == dataset]
        # Best classical (min upset_simple)
        cl = sub[sub["method"].isin(classical_set)].dropna(subset=["upset_simple"])
        if len(cl):
            idx = cl["upset_simple"].idxmin()
            row_cl = cl.loc[idx]
            best_classical_upset_simple = float(row_cl["upset_simple"])
            best_classical_upset_naive = float(row_cl["upset_naive"])
            best_classical_upset_ratio = float(row_cl["upset_ratio"])
            best_classical_runtime_sec = float(row_cl["runtime_sec"]) if pd.notna(row_cl["runtime_sec"]) else np.nan
            best_classical_method = str(row_cl["method"])
        else:
            best_classical_upset_simple = best_classical_upset_naive = best_classical_upset_ratio = np.nan
            best_classical_runtime_sec = np.nan
            best_classical_method = ""
        # Best GNN (min upset_simple)
        gnn = sub[sub["method"].isin(gnn_set)].dropna(subset=["upset_simple"])
        if len(gnn):
            idx = gnn["upset_simple"].idxmin()
            row_gnn = gnn.loc[idx]
            best_gnn_upset_simple = float(row_gnn["upset_simple"])
            best_gnn_upset_naive = float(row_gnn["upset_naive"])
            best_gnn_upset_ratio = float(row_gnn["upset_ratio"])
            best_gnn_runtime_sec = float(row_gnn["runtime_sec"]) if pd.notna(row_gnn["runtime_sec"]) else np.nan
            best_gnn_method = str(row_gnn["method"])
            best_gnn_config = str(row_gnn["config"]) if pd.notna(row_gnn["config"]) else ""
        else:
            best_gnn_upset_simple = best_gnn_upset_naive = best_gnn_upset_ratio = np.nan
            best_gnn_runtime_sec = np.nan
            best_gnn_method = ""
            best_gnn_config = ""
        records.append({
            "dataset": dataset,
            "best_classical_upset_simple": best_classical_upset_simple,
            "best_classical_upset_naive": best_classical_upset_naive,
            "best_classical_upset_ratio": best_classical_upset_ratio,
            "best_classical_runtime_sec": best_classical_runtime_sec,
            "best_classical_method": best_classical_method,
            "best_gnn_upset_simple": best_gnn_upset_simple,
            "best_gnn_upset_naive": best_gnn_upset_naive,
            "best_gnn_upset_ratio": best_gnn_upset_ratio,
            "best_gnn_runtime_sec": best_gnn_runtime_sec,
            "best_gnn_method": best_gnn_method,
            "best_gnn_config": best_gnn_config,
        })
    return pd.DataFrame(records)


def build_compute_matched(lb: pd.DataFrame) -> tuple:
    """Filter to runtime_sec <= TIME_BUDGET_SEC; return (filtered df, coverage dict)."""
    within = lb.dropna(subset=["runtime_sec"]).copy()
    within = within[within["runtime_sec"] <= TIME_BUDGET_SEC]
    # Coverage: per method, how many datasets have valid metrics / valid runtime / timeout
    all_methods = lb["method"].unique()
    coverage = []
    for m in all_methods:
        sub = lb[lb["method"] == m]
        n_valid_metrics = sub.dropna(subset=["upset_simple"]).shape[0]
        n_valid_runtime = sub.dropna(subset=["runtime_sec"]).shape[0]
        n_timeout = (sub["timeout_flag"] == True).sum()
        n_within_budget = within[within["method"] == m].shape[0]
        n_datasets_total = sub["dataset"].nunique()
        coverage.append({
            "method": m,
            "n_datasets_with_any_row": n_datasets_total,
            "n_valid_upset_simple": int(n_valid_metrics),
            "n_valid_runtime": int(n_valid_runtime),
            "n_timeout": int(n_timeout),
            "n_within_time_budget": int(n_within_budget),
        })
    return within, pd.DataFrame(coverage)


def build_missingness_audit(lb: pd.DataFrame, coverage_df: pd.DataFrame) -> pd.DataFrame:
    """Per-method: valid metrics, valid runtime, timeouts; Finance exclusions explicitly recorded."""
    audit = []
    for m in lb["method"].unique():
        sub = lb[lb["method"] == m]
        n_valid_metrics = sub.dropna(subset=["upset_simple"]).shape[0]
        n_valid_runtime = sub.dropna(subset=["runtime_sec"]).shape[0]
        n_timeout = (sub["timeout_flag"] == True).sum()
        # Datasets with at least one row for this method
        datasets = set(sub["dataset"].unique())
        # Finance(-like) exclusions: datasets in EXPLICIT_EXCLUSIONS that appear in global dataset list but missing or timeout for this method
        finance_like = [d for d in EXPLICIT_EXCLUSIONS if d in lb["dataset"].unique()]
        excluded_finance = []
        for d in finance_like:
            sub_d = sub[sub["dataset"] == d]
            if sub_d.empty:
                excluded_finance.append(f"{d}:no_data")
            elif (sub_d["timeout_flag"] == True).all():
                excluded_finance.append(f"{d}:timeout")
            else:
                excluded_finance.append(f"{d}:included")
        audit.append({
            "method": m,
            "n_datasets_with_valid_metrics": int(n_valid_metrics),
            "n_datasets_with_valid_runtime": int(n_valid_runtime),
            "n_timeouts": int(n_timeout),
            "finance_like_exclusions": ";".join(excluded_finance) if excluded_finance else "",
        })
    return pd.DataFrame(audit)


def main():
    ensure_aggregator_run()
    ra = load_ra()
    full = load_full()

    PAPER_CSV.mkdir(parents=True, exist_ok=True)

    # A) Per-method leaderboard (no oracle)
    lb = build_leaderboard_per_method(ra, full)
    lb.to_csv(OUT_LEADERBOARD, index=False)
    print(f"Wrote {OUT_LEADERBOARD} ({len(lb)} rows)")

    # B) Oracle envelopes
    oracle = build_oracle_envelopes(lb)
    oracle.to_csv(OUT_ORACLE, index=False)
    print(f"Wrote {OUT_ORACLE} ({len(oracle)} rows)")

    # C) Compute-matched + coverage
    within, coverage_df = build_compute_matched(lb)
    within.to_csv(OUT_COMPUTE_MATCHED, index=False)
    print(f"Wrote {OUT_COMPUTE_MATCHED} ({len(within)} rows, time_budget_sec={TIME_BUDGET_SEC})")
    coverage_path = PAPER_CSV / "leaderboard_compute_matched_coverage.csv"
    coverage_df.to_csv(coverage_path, index=False)
    print(f"Wrote {coverage_path}")

    # D) Missingness audit
    audit_df = build_missingness_audit(lb, coverage_df)
    audit_df.to_csv(OUT_MISSINGNESS, index=False)
    print(f"Wrote {OUT_MISSINGNESS}")

    return OUT_LEADERBOARD, OUT_ORACLE, OUT_COMPUTE_MATCHED, OUT_MISSINGNESS


if __name__ == "__main__":
    main()
