#!/usr/bin/env python3
"""
Export per-dataset, per-method metrics with FULL fields for:
  - all classical baselines
  - all OURS variants
  - the selected GNNRank method per dataset (best_gnn_method)

For GNNRank, we fill all three losses and runtime by combining:
  - per_dataset_summary.csv: best_gnn_method, best_gnn_upset_simple, best_gnn_runtime_sec
  - paper_csv/results_table_clean.csv: per-config upset_simple_mean, upset_ratio_mean,
    upset_naive_mean for DIGRACib, from which we recover the specific config that
    matches best_gnn_upset_simple for each dataset.

We do NOT rely on the previously generated helper CSVs; this script
builds everything from the original pipeline outputs.

Inputs (relative to repo root inside GNNRank-main):
  - full_833614_metrics_best.csv
  - per_dataset_summary.csv
  - paper_csv/results_table_clean.csv

Output:
  - all_methods_with_gnn_full.csv
      columns:
        dataset, method,
        upset_simple, upset_naive, upset_ratio, runtime_sec

Notes on missing values:
  - For classical + OURS methods: all four fields are present from
    full_833614_metrics_best.csv.
  - For GNNRank rows:
      - upset_simple and runtime_sec come from per_dataset_summary.csv.
      - upset_naive and upset_ratio are taken from the specific DIGRACib
        config in results_table_clean whose upset_simple_mean is closest
        to best_gnn_upset_simple for that dataset. If no reasonably close
        match is found (within a small tolerance), these remain empty.
"""

from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
FULL_METRICS_CSV = HERE / "full_833614_metrics_best.csv"
PER_DATASET_SUMMARY_CSV = HERE / "per_dataset_summary.csv"
RESULTS_TABLE_CLEAN_CSV = HERE / "paper_csv" / "results_table_clean.csv"
OUT_CSV = HERE / "all_methods_with_gnn_full.csv"


def build_base_methods() -> pd.DataFrame:
    """
    Build per-(dataset, method) metrics for classical + OURS (and mvr)
    from full_833614_metrics_best.csv.
    """
    df = pd.read_csv(FULL_METRICS_CSV)
    base = df[
        [
            "dataset",
            "method",
            "upset_simple_mean",
            "upset_naive_mean",
            "upset_ratio_mean",
            "runtime_sec_mean",
        ]
    ].rename(
        columns={
            "upset_simple_mean": "upset_simple",
            "upset_naive_mean": "upset_naive",
            "upset_ratio_mean": "upset_ratio",
            "runtime_sec_mean": "runtime_sec",
        }
    )
    return base


def build_gnn_rows() -> pd.DataFrame:
    """
    Build per-dataset GNNRank rows using per_dataset_summary + results_table_clean.

    For each dataset where best_gnn_method is defined, we:
      - Take upset_simple and runtime_sec from per_dataset_summary.
      - Look up rows in results_table_clean with:
            dataset == this dataset
            method  == "DIGRACib"
            which   == "upset"
        and pick the config whose upset_simple_mean is closest to
        best_gnn_upset_simple.
      - Use that config's upset_ratio_mean and upset_naive_mean.
    """
    summary = pd.read_csv(PER_DATASET_SUMMARY_CSV)
    clean = pd.read_csv(RESULTS_TABLE_CLEAN_CSV)

    # Only GNN-related rows in per-dataset summary.
    mask = summary["best_gnn_method"].notna() & (summary["best_gnn_method"] != "")
    gnn_summary = summary[mask].copy()

    # We only need DIGRACib / GNN configs from the clean table.
    clean_gnn = clean[
        (clean["method"] == "DIGRACib") & (clean["which"] == "upset")
    ].copy()

    rows = []
    for _, r in gnn_summary.iterrows():
        ds = r["dataset"]
        method_name = r["best_gnn_method"]
        target_us = float(r["best_gnn_upset_simple"])
        runtime = float(r["best_gnn_runtime_sec"])

        # Find candidate configs for this dataset.
        cand = clean_gnn[clean_gnn["dataset"] == ds]
        upset_naive = np.nan
        upset_ratio = np.nan

        if not cand.empty:
            # Choose config with closest upset_simple_mean to the target.
            diffs = (cand["upset_simple_mean"] - target_us).abs()
            idx_min = diffs.idxmin()
            best_row = cand.loc[idx_min]
            best_diff = float(diffs.loc[idx_min])

            # Tolerance: allow small numeric differences due to rounding.
            # If it's too far off, we consider it unreliable and leave NA.
            if best_diff <= 1e-3:
                upset_naive = float(best_row["upset_naive_mean"])
                upset_ratio = float(best_row["upset_ratio_mean"])

        rows.append(
            {
                "dataset": ds,
                "method": method_name,
                "upset_simple": target_us,
                "upset_naive": upset_naive,
                "upset_ratio": upset_ratio,
                "runtime_sec": runtime,
            }
        )

    return pd.DataFrame(rows)


def main():
    base = build_base_methods()
    gnn = build_gnn_rows()

    # Combine, avoiding accidental duplicates if any dataset/method pair overlaps.
    combined = pd.concat([base, gnn], ignore_index=True)
    combined.drop_duplicates(subset=["dataset", "method"], inplace=True)

    # Sort for readability.
    combined.sort_values(["dataset", "method"], inplace=True)

    combined.to_csv(OUT_CSV, index=False)


if __name__ == "__main__":
    main()

