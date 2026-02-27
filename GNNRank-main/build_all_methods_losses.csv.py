#!/usr/bin/env python3
"""
Build a per-dataset, per-method CSV with ALL three losses for all methods,
including GNNRank, ignoring runtime.

Outputs: all_methods_losses.csv with columns
  - dataset
  - method
  - upset_simple_mean, upset_simple_std
  - upset_naive_mean,  upset_naive_std
  - upset_ratio_mean,  upset_ratio_std

Sources:
  - full_833614_metrics_best.csv
      (parsed from full_833614.out; contains all non-GNN methods + OURS + mvr)
  - paper_csv/results_table.csv
      (per-dataset aggregated metrics for DIGRACib; we use rows with which == "upset")
"""

from pathlib import Path

import pandas as pd


HERE = Path(__file__).resolve().parent


def main():
    best_path = HERE / "full_833614_metrics_best.csv"
    rt_path = HERE / "paper_csv" / "results_table.csv"

    df_best = pd.read_csv(best_path)
    df_rt = pd.read_csv(rt_path)

    # Start from the best-metrics table for all non-GNN methods.
    rows = []
    for _, r in df_best.iterrows():
        rows.append(
            {
                "dataset": r["dataset"],
                "method": r["method"],
                "upset_simple_mean": r["upset_simple_mean"],
                "upset_simple_std": r["upset_simple_std"],
                "upset_naive_mean": r["upset_naive_mean"],
                "upset_naive_std": r["upset_naive_std"],
                "upset_ratio_mean": r["upset_ratio_mean"],
                "upset_ratio_std": r["upset_ratio_std"],
            }
        )

    # Add GNNRank (DIGRACib) using results_table.csv (which has all three losses).
    df_gnn = df_rt[(df_rt["method"] == "DIGRACib") & (df_rt["which"] == "upset")].copy()

    for _, r in df_gnn.iterrows():
        ds = r["dataset"]
        method = r["method"]

        # Skip if already present (it is not, but we keep this guard to be safe).
        if any((row["dataset"] == ds and row["method"] == method) for row in rows):
            continue

        rows.append(
            {
                "dataset": ds,
                "method": method,
                "upset_simple_mean": r["upset_simple_mean"],
                "upset_simple_std": r["upset_simple_std"],
                "upset_naive_mean": r["upset_naive_mean"],
                "upset_naive_std": r["upset_naive_std"],
                "upset_ratio_mean": r["upset_ratio_mean"],
                "upset_ratio_std": r["upset_ratio_std"],
            }
        )

    out_df = pd.DataFrame(rows)
    out_df.sort_values(["dataset", "method"], inplace=True)

    out_path = HERE / "all_methods_losses.csv"
    out_df.to_csv(out_path, index=False)
    print(f"Wrote {len(out_df)} rows to {out_path}")


if __name__ == "__main__":
    main()

