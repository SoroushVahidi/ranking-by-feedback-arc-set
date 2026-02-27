#!/usr/bin/env python3
"""
Build a per-dataset, per-method CSV with:

  - upset_simple_mean, upset_simple_std
  - upset_naive_mean,  upset_naive_std
  - upset_ratio_mean,  upset_ratio_std
  - runtime_sec_mean,  runtime_sec_std

for:
  - All classical baselines
  - All OURS variants
  - The GNNRank method (DIGRACib) from the original GNNRank pipeline.

Inputs (relative to this directory):
  - full_833614_metrics_best.csv        (parsed from full_833614.out)
  - paper_csv/results_table.csv         (per-dataset aggregated metrics incl. DIGRACib)

Output:
  - all_methods_metrics.csv

Notes:
  - For non-GNN methods, everything (including runtime) comes from
    full_833614_metrics_best.csv.
  - For GNNRank (method == "DIGRACib"), we take losses from
    paper_csv/results_table.csv (rows with which == "upset").
    That file does not contain runtime_sec_mean / std, so those
    columns are left empty for DIGRACib.
"""

from pathlib import Path

import pandas as pd


HERE = Path(__file__).resolve().parent


def main():
    best_path = HERE / "full_833614_metrics_best.csv"
    rt_path = HERE / "paper_csv" / "results_table.csv"

    df_best = pd.read_csv(best_path)
    df_rt = pd.read_csv(rt_path)

    # Start from the best-metrics table: classical + OURS (+ mvr).
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
                "runtime_sec_mean": r.get("runtime_sec_mean", ""),
                "runtime_sec_std": r.get("runtime_sec_std", ""),
            }
        )

    # Add GNNRank (DIGRACib) using results_table.csv (which has all three losses).
    # We only use rows with which == "upset".
    df_gnn = df_rt[(df_rt["method"] == "DIGRACib") & (df_rt["which"] == "upset")].copy()

    for _, r in df_gnn.iterrows():
        ds = r["dataset"]
        method = r["method"]

        # Skip if already present (should not happen, but be safe).
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
                # runtime columns are not present in results_table.csv; leave blank.
                "runtime_sec_mean": "",
                "runtime_sec_std": "",
            }
        )

    out_df = pd.DataFrame(rows)
    out_df.sort_values(["dataset", "method"], inplace=True)

    out_path = HERE / "all_methods_metrics.csv"
    out_df.to_csv(out_path, index=False)
    print(f"Wrote {len(out_df)} rows to {out_path}")


if __name__ == "__main__":
    main()

