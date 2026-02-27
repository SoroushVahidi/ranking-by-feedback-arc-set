#!/usr/bin/env python3
"""
Regenerate the overall leaderboard (tab:overall_leaderboard_simple)
from full_833614_metrics_best.csv, restricted to the manuscript
method list and ordered as specified.

For each method, we aggregate across datasets and compute:
  - Count of datasets
  - mean ± std of upset_simple_mean
  - mean ± std of upset_naive_mean
  - mean ± std of upset_ratio_mean

Outputs:
  - overall_leaderboard_simple.csv  (aggregated stats)
  - overall_leaderboard_simple.tex  (LaTeX table body)

Run from inside GNNRank-main:
  python compute_overall_leaderboard_simple.py
"""

import math
from pathlib import Path

import pandas as pd


HERE = Path(__file__).resolve().parent
INPUT_CSV = HERE / "full_833614_metrics_best.csv"
OUT_CSV = HERE / "overall_leaderboard_simple.csv"
OUT_TEX = HERE / "overall_leaderboard_simple.tex"


METHOD_ORDER = [
    "OURS_MFAS",
    "OURS_MFAS_INS1",
    "OURS_MFAS_INS2",
    "OURS_MFAS_INS3",
    "SpringRank",
    "syncRank",
    "serialRank",
    "btl",
    "davidScore",
    "eigenvectorCentrality",
    "PageRank",
    "rankCentrality",
    "SVD_RS",
    "SVD_NRS",
]


def agg_mean_std(series: pd.Series):
    """Return (mean, std) ignoring NaNs, with population std (ddof=0)."""
    s = series.dropna()
    if s.empty:
        return math.nan, math.nan
    mean = float(s.mean())
    std = float(s.std(ddof=0))
    return mean, std


def main():
    df = pd.read_csv(INPUT_CSV)

    # Filter to the exact set of methods (exclude mvr and any others).
    df = df[df["method"].isin(METHOD_ORDER)].copy()

    rows = []
    for method in METHOD_ORDER:
        sub = df[df["method"] == method]
        if sub.empty:
            # Keep the row with NaNs so the LaTeX ordering is preserved.
            rows.append(
                {
                    "method": method,
                    "count": 0,
                    "upset_simple_mean": math.nan,
                    "upset_simple_std": math.nan,
                    "upset_naive_mean": math.nan,
                    "upset_naive_std": math.nan,
                    "upset_ratio_mean": math.nan,
                    "upset_ratio_std": math.nan,
                }
            )
            continue

        n = int(sub.shape[0])
        us_mean, us_std = agg_mean_std(sub["upset_simple_mean"])
        un_mean, un_std = agg_mean_std(sub["upset_naive_mean"])
        ur_mean, ur_std = agg_mean_std(sub["upset_ratio_mean"])

        rows.append(
            {
                "method": method,
                "count": n,
                "upset_simple_mean": us_mean,
                "upset_simple_std": us_std,
                "upset_naive_mean": un_mean,
                "upset_naive_std": un_std,
                "upset_ratio_mean": ur_mean,
                "upset_ratio_std": ur_std,
            }
        )

    out_df = pd.DataFrame(rows)
    out_df.to_csv(OUT_CSV, index=False)

    # LaTeX table body: one row per method, in the specified order.
    # Format: Method & Count & u_simple mean±std & u_naive mean±std & u_ratio mean±std \\
    lines = []
    for _, r in out_df.iterrows():
        method = str(r["method"])
        method_tex = method.replace("_", r"\_")
        n = int(r["count"])

        def fmt_pair(mean, std, decimals=3):
            if math.isnan(mean) or math.isnan(std):
                return "--"
            return f"{mean:.{decimals}f} $\\pm$ {std:.{decimals}f}"

        us = fmt_pair(r["upset_simple_mean"], r["upset_simple_std"])
        un = fmt_pair(r["upset_naive_mean"], r["upset_naive_std"])
        ur = fmt_pair(r["upset_ratio_mean"], r["upset_ratio_std"])

        lines.append(f"{method_tex} & {n} & {us} & {un} & {ur} \\\\")

    tex_body = "\n".join(lines) + "\n"
    OUT_TEX.write_text(tex_body)


if __name__ == "__main__":
    main()

