#!/usr/bin/env python3
"""
Export a CSV with all available methods on all datasets, including
classical baselines, OURS variants, and the best GNN method per
dataset (from per_dataset_summary.csv).

Inputs (in this directory):
  - full_833614_metrics_best.csv
      per-(dataset, method) mean metrics for classical + OURS (+ mvr)
  - per_dataset_summary.csv
      per-dataset summary including:
        best_gnn_method, best_gnn_upset_simple, best_gnn_runtime_sec

Output:
  - all_methods_including_gnn.csv
      columns:
        dataset, method,
        upset_simple, upset_naive, upset_ratio, runtime_sec

Notes:
  - For classical + OURS methods, all four metrics are taken from
    full_833614_metrics_best.csv (mean values).
  - For the GNN rows, we only have upset_simple and runtime_sec in
    per_dataset_summary.csv; upset_naive and upset_ratio are left
    empty (NA).

Run from inside GNNRank-main:
  python export_all_methods_including_gnn.py
"""

from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
FULL_CSV = HERE / "full_833614_metrics_best.csv"
SUMMARY_CSV = HERE / "per_dataset_summary.csv"
OUT_CSV = HERE / "all_methods_including_gnn.csv"


def main():
    # Base: all classical + OURS (+ any other methods present) from full_833614...
    base = pd.read_csv(FULL_CSV)
    base_out = base[
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

    # Per-dataset best GNN (one method per dataset).
    summ = pd.read_csv(SUMMARY_CSV)
    gmask = summ["best_gnn_method"].notna() & (summ["best_gnn_method"] != "")
    gnn_rows = []
    for _, r in summ[gmask].iterrows():
        gnn_rows.append(
            {
                "dataset": r["dataset"],
                "method": r["best_gnn_method"],
                "upset_simple": r.get("best_gnn_upset_simple", np.nan),
                "upset_naive": np.nan,  # not available in per_dataset_summary.csv
                "upset_ratio": np.nan,  # not available
                "runtime_sec": r.get("best_gnn_runtime_sec", np.nan),
            }
        )
    gnn_df = pd.DataFrame(gnn_rows)

    # Concatenate, avoiding duplicate (dataset, method) if somehow already present.
    combined = pd.concat([base_out, gnn_df], ignore_index=True)
    combined.drop_duplicates(subset=["dataset", "method"], inplace=True)

    combined.to_csv(OUT_CSV, index=False)


if __name__ == "__main__":
    main()

