#!/usr/bin/env python3
"""
Compute per-metric Win/Tie/Loss (WTL) comparisons for OURS vs:
  - best classical baseline (per metric)
  - best GNN variant (single best variant per dataset, by upset_simple)

Inputs (assumed to be in the same directory as this script):
  - full_833614_metrics_best.csv
      columns: dataset, method,
               upset_simple_mean, upset_simple_std,
               upset_ratio_mean, upset_ratio_std,
               upset_naive_mean, upset_naive_std,
               runtime_sec_mean, runtime_sec_std
  - per_dataset_summary.csv
      provides dataset -> kind mapping for family breakdown.

Definitions:
  - OURS method: OURS_MFAS_INS3
  - Classical baselines (10):
      SpringRank, syncRank, serialRank, btl, davidScore,
      eigenvectorCentrality, PageRank, rankCentrality, SVD_RS, SVD_NRS
  - GNN variants:
      DIGRAC_dist, DIGRAC_proximal_baseline, ib_dist, ib_proximal_baseline

Per-dataset "best" values:
  - BEST_CLASSICAL for each metric (upset_simple, upset_naive, upset_ratio, runtime):
      min over classical baselines of that metric.
  - BEST_GNN: pick the GNN variant with minimum upset_simple_mean on that dataset,
      then use that same variant's upset_naive_mean, upset_ratio_mean, runtime_sec_mean.

Ties:
  - For loss metrics (upset_simple, upset_naive, upset_ratio):
      |ours - best| <= 1e-3
  - For runtime:
      |ours - best| <= 1e-6 OR (ours < 1e-3 and best < 1e-3)
  - Datasets with NaN for either side on a metric are excluded for that comparison.

Outputs:
  - wtl_by_metric.csv
      columns: comparison, metric, wins, ties, losses, total
      comparison in {OURS_vs_best_classical, OURS_vs_best_gnn}
      metric in {upset_simple, upset_naive, upset_ratio, runtime}
  - wtl_by_metric_family.csv
      columns: comparison, family, metric, wins, ties, losses, total
      family in {Basketball, Football, Faculty, Animal, Head-to-head, Finance, Other}

Run from inside GNNRank-main:
  python compute_wtl_by_metric.py
"""

import math
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
FULL_METRICS_CSV = HERE / "full_833614_metrics_best.csv"
PER_DATASET_SUMMARY_CSV = HERE / "per_dataset_summary.csv"

OURS_METHOD = "OURS_MFAS_INS3"

CLASSICAL_METHODS = [
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

GNN_METHODS = [
    "DIGRAC_dist",
    "DIGRAC_proximal_baseline",
    "ib_dist",
    "ib_proximal_baseline",
]


def family(kind: str) -> str:
    """Map fine-grained kind into the paper's family name."""
    if not kind:
        return "Other"
    if kind == "basketball_temporal":
        return "Basketball"
    if kind == "football_temporal":
        return "Football"
    if kind in ("faculty_business", "faculty_cs", "faculty_history"):
        return "Faculty"
    if kind == "animal_static":
        return "Animal"
    if kind == "headtohead_static":
        return "Head-to-head"
    if kind == "finance_static":
        return "Finance"
    return kind


def compare_values(ours: float, best: float, metric_kind: str):
    """
    Compare OURS vs best for a single metric.

    Returns:
      "win" | "tie" | "loss" | None   (None => skip / insufficient data)
    """
    if ours is None or best is None:
        return None
    if not (math.isfinite(ours) and math.isfinite(best)):
        return None

    diff = ours - best

    if metric_kind == "runtime":
        # Runtime tie rule.
        if abs(diff) <= 1e-6 or (ours < 1e-3 and best < 1e-3):
            return "tie"
    else:
        # Loss metrics tie rule.
        if abs(diff) <= 1e-3:
            return "tie"

    # Lower is better in all metrics we consider.
    if ours < best:
        return "win"
    if ours > best:
        return "loss"
    # Exact equality but outside tolerance (should be very rare).
    return "tie"


def main():
    # Load data.
    df = pd.read_csv(FULL_METRICS_CSV)
    per_ds = pd.read_csv(PER_DATASET_SUMMARY_CSV)

    # Dataset -> family mapping via kind.
    kind_map = dict(zip(per_ds["dataset"], per_ds["kind"]))

    # Keep only methods we care about.
    relevant_methods = {OURS_METHOD} | set(CLASSICAL_METHODS) | set(GNN_METHODS)
    df = df[df["method"].isin(relevant_methods)].copy()

    # OURS rows (one per dataset).
    ours_df = df[df["method"] == OURS_METHOD].set_index("dataset")

    # Classical baselines: best per metric (min over methods) for each dataset.
    classical_df = df[df["method"].isin(CLASSICAL_METHODS)].copy()
    if not classical_df.empty:
        classical_best = (
            classical_df.groupby("dataset")
            .agg(
                best_classical_upset_simple=("upset_simple_mean", "min"),
                best_classical_upset_naive=("upset_naive_mean", "min"),
                best_classical_upset_ratio=("upset_ratio_mean", "min"),
                best_classical_runtime=("runtime_sec_mean", "min"),
            )
        )
    else:
        classical_best = pd.DataFrame(
            columns=[
                "best_classical_upset_simple",
                "best_classical_upset_naive",
                "best_classical_upset_ratio",
                "best_classical_runtime",
            ]
        )

    # GNN variants: choose single best variant per dataset by upset_simple_mean.
    gnn_df = df[df["method"].isin(GNN_METHODS)].copy()
    gnn_records = []
    for dataset, group in gnn_df.groupby("dataset"):
        valid = group.dropna(subset=["upset_simple_mean"])
        if valid.empty:
            continue
        idx = valid["upset_simple_mean"].idxmin()
        row = valid.loc[idx]
        gnn_records.append(
            {
                "dataset": dataset,
                "best_gnn_method": row["method"],
                "best_gnn_upset_simple": row["upset_simple_mean"],
                "best_gnn_upset_naive": row["upset_naive_mean"],
                "best_gnn_upset_ratio": row["upset_ratio_mean"],
                "best_gnn_runtime": row["runtime_sec_mean"],
            }
        )
    if gnn_records:
        gnn_best = pd.DataFrame(gnn_records).set_index("dataset")
    else:
        gnn_best = pd.DataFrame(
            columns=[
                "best_gnn_method",
                "best_gnn_upset_simple",
                "best_gnn_upset_naive",
                "best_gnn_upset_ratio",
                "best_gnn_runtime",
            ]
        )

    # Build per-dataset summary (restricted to datasets where OURS exists).
    datasets = sorted(ours_df.index.unique())
    records = []
    for ds in datasets:
        ours_row = ours_df.loc[ds]
        c_row = classical_best.loc[ds] if ds in classical_best.index else None
        g_row = gnn_best.loc[ds] if ds in gnn_best.index else None

        kind = kind_map.get(ds, "")
        fam = family(kind)

        records.append(
            {
                "dataset": ds,
                "family": fam,
                "ours_upset_simple": float(ours_row["upset_simple_mean"]),
                "ours_upset_naive": float(ours_row["upset_naive_mean"]),
                "ours_upset_ratio": float(ours_row["upset_ratio_mean"]),
                "ours_runtime": float(ours_row["runtime_sec_mean"]),
                "best_classical_upset_simple": float(c_row["best_classical_upset_simple"]) if c_row is not None else math.nan,
                "best_classical_upset_naive": float(c_row["best_classical_upset_naive"]) if c_row is not None else math.nan,
                "best_classical_upset_ratio": float(c_row["best_classical_upset_ratio"]) if c_row is not None else math.nan,
                "best_classical_runtime": float(c_row["best_classical_runtime"]) if c_row is not None else math.nan,
                "best_gnn_upset_simple": float(g_row["best_gnn_upset_simple"]) if g_row is not None else math.nan,
                "best_gnn_upset_naive": float(g_row["best_gnn_upset_naive"]) if g_row is not None else math.nan,
                "best_gnn_upset_ratio": float(g_row["best_gnn_upset_ratio"]) if g_row is not None else math.nan,
                "best_gnn_runtime": float(g_row["best_gnn_runtime"]) if g_row is not None else math.nan,
            }
        )

    ds_df = pd.DataFrame(records)

    comparisons = ["OURS_vs_best_classical", "OURS_vs_best_gnn"]
    metrics = [
        ("upset_simple", "loss"),
        ("upset_naive", "loss"),
        ("upset_ratio", "loss"),
        ("runtime", "runtime"),
    ]

    # Global WTL counts.
    global_counts = {
        comp: {m[0]: {"win": 0, "tie": 0, "loss": 0} for m in metrics}
        for comp in comparisons
    }

    # Family-wise WTL counts.
    family_counts = {
        comp: defaultdict(lambda: {m[0]: {"win": 0, "tie": 0, "loss": 0} for m in metrics})
        for comp in comparisons
    }

    for _, row in ds_df.iterrows():
        fam = row["family"]
        for metric_name, metric_kind in metrics:
            ours_val = float(row[f"ours_{metric_name}"])

            # Classical comparison.
            best_c = row.get(f"best_classical_{metric_name}", math.nan)
            res_c = compare_values(ours_val, best_c, metric_kind)
            if res_c is not None:
                global_counts["OURS_vs_best_classical"][metric_name][res_c] += 1
                family_counts["OURS_vs_best_classical"][fam][metric_name][res_c] += 1

            # GNN comparison.
            best_g = row.get(f"best_gnn_{metric_name}", math.nan)
            res_g = compare_values(ours_val, best_g, metric_kind)
            if res_g is not None:
                global_counts["OURS_vs_best_gnn"][metric_name][res_g] += 1
                family_counts["OURS_vs_best_gnn"][fam][metric_name][res_g] += 1

    # Write wtl_by_metric.csv
    rows_global = []
    for comp in comparisons:
        for metric_name, _ in metrics:
            c = global_counts[comp][metric_name]
            total = c["win"] + c["tie"] + c["loss"]
            rows_global.append(
                {
                    "comparison": comp,
                    "metric": metric_name,
                    "wins": c["win"],
                    "ties": c["tie"],
                    "losses": c["loss"],
                    "total": total,
                }
            )

    wtl_global_df = pd.DataFrame(rows_global)
    wtl_global_df.to_csv(HERE / "wtl_by_metric.csv", index=False)

    # Write wtl_by_metric_family.csv
    fam_rows = []
    fam_order = ["Basketball", "Football", "Faculty", "Animal", "Head-to-head", "Finance", "Other"]

    for comp in comparisons:
        fam_dict = family_counts[comp]
        for fam in fam_order:
            metric_dict = fam_dict.get(fam, None)
            if metric_dict is None:
                # No datasets for this family/comparison; still emit zeros for completeness.
                metric_dict = {m[0]: {"win": 0, "tie": 0, "loss": 0} for m in metrics}
            for metric_name, _ in metrics:
                c = metric_dict[metric_name]
                total = c["win"] + c["tie"] + c["loss"]
                fam_rows.append(
                    {
                        "comparison": comp,
                        "family": fam,
                        "metric": metric_name,
                        "wins": c["win"],
                        "ties": c["tie"],
                        "losses": c["loss"],
                        "total": total,
                    }
                )

    wtl_fam_df = pd.DataFrame(fam_rows)
    wtl_fam_df.to_csv(HERE / "wtl_by_metric_family.csv", index=False)


if __name__ == "__main__":
    main()

