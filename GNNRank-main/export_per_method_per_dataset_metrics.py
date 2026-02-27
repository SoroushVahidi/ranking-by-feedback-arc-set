#!/usr/bin/env python3
"""
Export a clean per-dataset, per-method CSV containing all loss metrics
and runtime for each method on each dataset.

Input (in this directory):
  - full_833614_metrics_best.csv
      columns: dataset, method,
               upset_simple_mean, upset_simple_std,
               upset_ratio_mean, upset_ratio_std,
               upset_naive_mean, upset_naive_std,
               runtime_sec_mean, runtime_sec_std

Output:
  - per_method_per_dataset_metrics.csv
      columns:
        dataset, method,
        upset_simple, upset_naive, upset_ratio, runtime_sec

This is essentially a slimmed-down view of full_833614_metrics_best.csv
with only the mean metrics kept, suitable for downstream analysis.

Run from inside GNNRank-main:
  python export_per_method_per_dataset_metrics.py
"""

from pathlib import Path

import pandas as pd


HERE = Path(__file__).resolve().parent
INPUT_CSV = HERE / "full_833614_metrics_best.csv"
OUT_CSV = HERE / "per_method_per_dataset_metrics.csv"


def main():
    df = pd.read_csv(INPUT_CSV)

    out = df[
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

    out.to_csv(OUT_CSV, index=False)


if __name__ == "__main__":
    main()

