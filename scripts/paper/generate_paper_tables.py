"""
generate_paper_tables.py
========================
Generates all canonical paper tables for:
  "Scalable and Training-Free Ranking from Pairwise Comparisons
   via Acyclic Graph Construction"

Source of truth: GNNRank-main/paper_csv/leaderboard_per_method.csv  (1468 rows)
Canonical outputs: outputs/paper_tables/

Run from the repository root:
    python scripts/paper/generate_paper_tables.py

Design notes
------------
- The 80-dataset suite excludes _AUTO/Basketball_temporal__1985adj.
- Table 4  = full 80-dataset suite, trials10 config, best config per dataset.
- Table 5  = compute-matched subset (ERO excluded because it times out → 79 datasets),
             sourced from leaderboard_compute_matched.csv (already filtered).
- For GNN methods (DIGRAC, ib) multiple K configs exist; we select the config with
  minimum upset_simple per (method, dataset).
- All aggregate statistics (median, mean) are computed *across datasets* (one value
  per dataset after picking best config).
"""

from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.sparse as sp

# ---------------------------------------------------------------------------
# Paths (all relative to repo root)
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
CSV_DIR = REPO_ROOT / "GNNRank-main" / "paper_csv"
DATA_DIR = REPO_ROOT / "GNNRank-main" / "data"
OUT_DIR = REPO_ROOT / "outputs" / "paper_tables"
DERIVED_DIR = REPO_ROOT / "outputs" / "derived"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
AUTO_DATASET = "_AUTO/Basketball_temporal__1985adj"

METHODS_TABLE4 = [
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
    "DIGRAC",
    "ib",
]

GNN_METHODS = {"DIGRAC", "ib"}

DATASET_FAMILIES = {
    "Basketball_coarse": lambda d: d.startswith("Basketball_temporal/") and "/finer" not in d,
    "Basketball_finer": lambda d: "Basketball_temporal/finer" in d,
    "Football_coarse": lambda d: d.startswith("Football_data_England_Premier_League/England_"),
    "Football_finer": lambda d: "Football_data_England_Premier_League/finer" in d,
    "Faculty": lambda d: d.startswith("FacultyHiringNetworks/"),
    "Animal": lambda d: d == "Dryad_animal_society",
    "Halo": lambda d: d.startswith("Halo2BetaData"),
    "Finance": lambda d: d == "finance",
    "ERO": lambda d: d.startswith("ERO/"),
    "_AUTO": lambda d: d.startswith("_AUTO/"),
}


def assign_family(dataset: str) -> str:
    for family, predicate in DATASET_FAMILIES.items():
        if predicate(dataset):
            return family
    return "Unknown"


# ---------------------------------------------------------------------------
# Data loading helpers
# ---------------------------------------------------------------------------

def load_leaderboard() -> pd.DataFrame:
    """Load and return the canonical leaderboard CSV."""
    path = CSV_DIR / "leaderboard_per_method.csv"
    if not path.exists():
        raise FileNotFoundError(f"Canonical source not found: {path}")
    df = pd.read_csv(path)
    print(f"Loaded leaderboard: {len(df)} rows, {df['dataset'].nunique()} datasets")
    return df


def load_compute_matched() -> pd.DataFrame:
    """Load and return the compute-matched leaderboard CSV."""
    path = CSV_DIR / "leaderboard_compute_matched.csv"
    if not path.exists():
        raise FileNotFoundError(f"Compute-matched CSV not found: {path}")
    df = pd.read_csv(path)
    print(f"Loaded compute_matched: {len(df)} rows, {df['dataset'].nunique()} datasets")
    return df


def load_missingness_audit() -> pd.DataFrame:
    path = CSV_DIR / "missingness_audit.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def load_contribution_stats() -> pd.DataFrame:
    path = CSV_DIR / "contribution_stats.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def load_unified_comparison() -> pd.DataFrame:
    path = CSV_DIR / "unified_comparison.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


# ---------------------------------------------------------------------------
# Core aggregation helpers
# ---------------------------------------------------------------------------

def filter_80_suite(df: pd.DataFrame) -> pd.DataFrame:
    """Remove the extra _AUTO dataset to get the 80-dataset suite."""
    return df[df["dataset"] != AUTO_DATASET].copy()


def filter_trials10(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only rows whose config contains 'trials10'."""
    return df[df["config"].str.contains("trials10", na=False)].copy()


def pick_best_per_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each (method, dataset) pair, select the row with the *lowest* upset_simple.
    This handles GNN methods (multiple K configs) and ensures non-GNN methods
    (one config per dataset) are also handled uniformly.
    NaN rows are kept only when *all* configs produce NaN.
    """
    df_sorted = df.sort_values(
        ["method", "dataset", "upset_simple"],
        na_position="last",
    )
    best = df_sorted.groupby(["method", "dataset"], as_index=False).first()
    return best


def aggregate_method_stats(
    best: pd.DataFrame,
    denominator: int,
    methods: list[str],
) -> pd.DataFrame:
    """
    Compute per-method summary statistics (median & mean across datasets).

    Parameters
    ----------
    best : DataFrame with one row per (method, dataset)
    denominator : total number of datasets in the suite (for coverage string)
    methods : ordered list of methods to include

    Returns
    -------
    DataFrame with one row per method
    """
    rows = []
    for method in methods:
        grp = best[best["method"] == method]
        n_valid = int(grp["upset_simple"].notna().sum())
        row: dict = {
            "method": method,
            "n_datasets": n_valid,
            "coverage": f"{n_valid}/{denominator}",
            "median_upset_simple": grp["upset_simple"].median(),
            "mean_upset_simple": grp["upset_simple"].mean(),
            "median_upset_ratio": grp["upset_ratio"].median(),
            "mean_upset_ratio": grp["upset_ratio"].mean(),
            "median_upset_naive": grp["upset_naive"].median(),
            "mean_upset_naive": grp["upset_naive"].mean(),
            "median_runtime_sec": grp["runtime_sec"].median(),
            "mean_runtime_sec": grp["runtime_sec"].mean(),
        }
        rows.append(row)

    result = pd.DataFrame(rows)
    # Sort by mean upset_simple ascending (lower = better)
    result = result.sort_values("mean_upset_simple", ascending=True).reset_index(drop=True)
    return result


# ---------------------------------------------------------------------------
# Table 4: Full 80-dataset suite
# ---------------------------------------------------------------------------

def build_table4(df: pd.DataFrame) -> pd.DataFrame:
    """
    Table 4 — Full suite (80 datasets, trials10 config).
    """
    df80 = filter_80_suite(df)
    df_t10 = filter_trials10(df80)
    best = pick_best_per_dataset(df_t10)

    # Report coverage reality check
    n_datasets_in_suite = df80["dataset"].nunique()
    assert n_datasets_in_suite == 80, (
        f"Expected 80 datasets in suite, got {n_datasets_in_suite}"
    )

    table = aggregate_method_stats(best, denominator=80, methods=METHODS_TABLE4)
    print(f"Table 4: {len(table)} methods, denominator=80")
    return table


# ---------------------------------------------------------------------------
# Table 5: Compute-matched suite
# ---------------------------------------------------------------------------

def build_table5(df_cm: pd.DataFrame) -> pd.DataFrame:
    """
    Table 5 — Compute-matched suite.
    Uses leaderboard_compute_matched.csv which already excludes timed-out
    method-dataset pairs and the ERO dataset (timeout). We further exclude
    the _AUTO dataset to arrive at the 79-dataset compute-matched suite.
    """
    df79 = filter_80_suite(df_cm)  # removes _AUTO → should be 79 datasets
    df_t10 = filter_trials10(df79)
    best = pick_best_per_dataset(df_t10)

    n_datasets = df79["dataset"].nunique()
    print(f"Table 5: compute-matched suite has {n_datasets} datasets (expected 79)")

    table = aggregate_method_stats(best, denominator=n_datasets, methods=METHODS_TABLE4)
    print(f"Table 5: {len(table)} methods, denominator={n_datasets}")
    return table


# ---------------------------------------------------------------------------
# Table 6: Missingness audit
# ---------------------------------------------------------------------------

def build_table6(df_miss: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
    """
    Table 6 — Per-method missingness / coverage summary.
    Falls back to computing from leaderboard if missingness_audit.csv is absent.
    """
    if not df_miss.empty:
        return df_miss

    # Fallback: compute from leaderboard
    df80 = filter_80_suite(df)
    df_t10 = filter_trials10(df80)
    best = pick_best_per_dataset(df_t10)

    rows = []
    for method in METHODS_TABLE4:
        grp = best[best["method"] == method]
        n_valid = int(grp["upset_simple"].notna().sum())
        n_timeout = int((grp["timeout_flag"] == True).sum())  # noqa: E712
        rows.append(
            {
                "method": method,
                "n_datasets_with_valid_metrics": n_valid,
                "n_timeouts": n_timeout,
                "coverage_80": f"{n_valid}/80",
            }
        )
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Table 7: Best-in-suite comparison
# ---------------------------------------------------------------------------

def build_table7(df_unified: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
    """
    Table 7 — Per-dataset OURS vs best-classical and best-GNN.

    Always recomputed from the canonical leaderboard (``df``) using the
    trials10 config, so that:
    - Only the 80-dataset paper suite is included (all _AUTO datasets removed).
    - GNN best-in-suite is derived from trials10 configs only, consistent with
      Table 4 and Table 5.

    For each comparator group (classical, GNN), "best" means the single
    method with the lowest ``upset_simple``; all its metrics are then
    reported together.  This "same-method" convention is semantically
    coherent: we compare OURS against whichever competitor a practitioner
    would choose on the primary metric, and then report all that
    competitor's metrics side-by-side.

    ``df_unified`` is accepted for API compatibility but is NOT used.
    """
    # Always derive from the canonical leaderboard with consistent filters.
    df80 = filter_80_suite(df)
    df_t10 = filter_trials10(df80)
    best = pick_best_per_dataset(df_t10)

    ours_methods = [m for m in METHODS_TABLE4 if m.startswith("OURS_")]
    classical_methods = [
        m for m in METHODS_TABLE4 if not m.startswith("OURS_") and m not in GNN_METHODS
    ]
    gnn_methods = [m for m in METHODS_TABLE4 if m in GNN_METHODS]

    def _best_row(sub: pd.DataFrame, methods: list[str]) -> pd.Series:
        """Return the row of the method with lowest upset_simple, or all-NaN."""
        group = sub[sub["method"].isin(methods)].dropna(subset=["upset_simple"])
        if group.empty:
            return pd.Series({"upset_simple": float("nan"),
                              "upset_ratio":  float("nan"),
                              "upset_naive":  float("nan"),
                              "runtime_sec":  float("nan")})
        return group.loc[group["upset_simple"].idxmin()]

    rows = []
    for dataset in sorted(best["dataset"].unique()):
        sub = best[best["dataset"] == dataset]
        ours_sub = sub[sub["method"].isin(ours_methods)]

        # OURS: best upset_simple variant; runtime from the canonical OURS_MFAS entry
        ours_valid = ours_sub.dropna(subset=["upset_simple"])
        if not ours_valid.empty:
            ours_row = ours_valid.loc[ours_valid["upset_simple"].idxmin()]
            ours_upset_simple = float(ours_row["upset_simple"])
            ours_upset_ratio  = float(ours_row["upset_ratio"])  if pd.notna(ours_row["upset_ratio"])  else float("nan")
            ours_upset_naive  = float(ours_row["upset_naive"])  if pd.notna(ours_row["upset_naive"])  else float("nan")
        else:
            ours_upset_simple = ours_upset_ratio = ours_upset_naive = float("nan")
        mfas_rows = ours_sub[ours_sub["method"] == "OURS_MFAS"]
        ours_runtime = float(mfas_rows["runtime_sec"].iloc[0]) if (len(mfas_rows) > 0 and pd.notna(mfas_rows["runtime_sec"].iloc[0])) else float("nan")

        cl_row  = _best_row(sub, classical_methods)
        gnn_row = _best_row(sub, gnn_methods)

        rows.append(
            {
                "dataset": dataset,
                "ours_upset_simple": ours_upset_simple,
                "ours_upset_ratio":  ours_upset_ratio,
                "ours_upset_naive":  ours_upset_naive,
                "ours_runtime_sec":  ours_runtime,
                "best_classical_upset_simple": float(cl_row["upset_simple"])  if pd.notna(cl_row["upset_simple"])  else float("nan"),
                "best_classical_upset_ratio":  float(cl_row["upset_ratio"])   if pd.notna(cl_row["upset_ratio"])   else float("nan"),
                "best_classical_upset_naive":  float(cl_row["upset_naive"])   if pd.notna(cl_row["upset_naive"])   else float("nan"),
                "best_classical_runtime_sec":  float(cl_row["runtime_sec"])   if pd.notna(cl_row["runtime_sec"])   else float("nan"),
                "best_gnn_upset_simple": float(gnn_row["upset_simple"])  if pd.notna(gnn_row["upset_simple"])  else float("nan"),
                "best_gnn_upset_ratio":  float(gnn_row["upset_ratio"])   if pd.notna(gnn_row["upset_ratio"])   else float("nan"),
                "best_gnn_upset_naive":  float(gnn_row["upset_naive"])   if pd.notna(gnn_row["upset_naive"])   else float("nan"),
                "best_gnn_runtime_sec":  float(gnn_row["runtime_sec"])   if pd.notna(gnn_row["runtime_sec"])   else float("nan"),
                "family": assign_family(dataset),
            }
        )
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Table 8: Runtime trade-off
# ---------------------------------------------------------------------------

def build_table8(df_contrib: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
    """
    Table 8 — Speedup and Pareto statistics (OURS vs best-GNN).

    Always recomputed from the canonical leaderboard (``df``) using trials10
    configs, so that GNN envelopes are consistent with Tables 4, 5, and 7.
    Uses ``build_table7`` internally so that the "best-by-upset_simple,
    then all its metrics" convention is applied identically.
    ``df_contrib`` is accepted for API compatibility but is NOT used.
    """
    # Re-use Table7 data as the per-dataset comparison base.
    comp = build_table7(pd.DataFrame(), df)

    # Rename columns to match the computation below
    comp = comp.rename(columns={
        "ours_upset_simple":            "ours_upset_simple",
        "ours_upset_ratio":             "ours_upset_ratio",
        "ours_runtime_sec":             "ours_runtime_sec",
        "best_classical_upset_simple":  "cl_best_upset_simple",
        "best_classical_upset_ratio":   "cl_best_upset_ratio",
        "best_classical_runtime_sec":   "cl_best_runtime",
        "best_gnn_upset_simple":        "gnn_best_upset_simple",
        "best_gnn_upset_ratio":         "gnn_best_upset_ratio",
        "best_gnn_runtime_sec":         "gnn_best_runtime",
    })

    def _wtl(series_a: pd.Series, series_b: pd.Series, tol: float) -> tuple[int, int, int]:
        nn = pd.concat([series_a, series_b], axis=1).dropna()
        a, b = nn.iloc[:, 0], nn.iloc[:, 1]
        w = int((a < b - tol).sum())
        t = int((abs(a - b) <= tol).sum())
        l = int((a > b + tol).sum())
        return w, t, l

    # ------------------------------------------------------------------ #
    # Section A: OURS vs best-classical                                   #
    # ------------------------------------------------------------------ #
    w_cl_s, t_cl_s, l_cl_s = _wtl(comp["ours_upset_simple"], comp["cl_best_upset_simple"], 1e-6)
    w_cl_r, t_cl_r, l_cl_r = _wtl(comp["ours_upset_ratio"], comp["cl_best_upset_ratio"], 1e-6)

    gap_simple = (comp["cl_best_upset_simple"] - comp["ours_upset_simple"]).dropna()
    rel_gap_s = (
        ((comp["cl_best_upset_simple"] - comp["ours_upset_simple"]) / comp["cl_best_upset_simple"])
        .dropna()
    )
    gap_ratio = (comp["cl_best_upset_ratio"] - comp["ours_upset_ratio"]).dropna()
    rel_gap_r = (
        ((comp["cl_best_upset_ratio"] - comp["ours_upset_ratio"]) / comp["cl_best_upset_ratio"])
        .dropna()
    )

    within_simple_1pct = int((gap_simple.abs() <= 0.01).sum())
    within_simple_5pct = int((gap_simple.abs() <= 0.05).sum())
    within_simple_10pct = int((gap_simple.abs() <= 0.10).sum())

    # ------------------------------------------------------------------ #
    # Section B: OURS vs best-GNN                                         #
    # ------------------------------------------------------------------ #
    w_gnn_s, t_gnn_s, l_gnn_s = _wtl(comp["ours_upset_simple"], comp["gnn_best_upset_simple"], 1e-6)
    w_gnn_r, t_gnn_r, l_gnn_r = _wtl(comp["ours_upset_ratio"], comp["gnn_best_upset_ratio"], 1e-6)

    gap_simple_g = (comp["gnn_best_upset_simple"] - comp["ours_upset_simple"]).dropna()
    rel_gap_sg = (
        ((comp["gnn_best_upset_simple"] - comp["ours_upset_simple"]) / comp["gnn_best_upset_simple"])
        .dropna()
    )
    gap_ratio_g = (comp["gnn_best_upset_ratio"] - comp["ours_upset_ratio"]).dropna()

    within_gnn_simple_1pct = int((gap_simple_g.abs() <= 0.01).sum())
    within_gnn_simple_5pct = int((gap_simple_g.abs() <= 0.05).sum())
    within_gnn_simple_10pct = int((gap_simple_g.abs() <= 0.10).sum())

    # ------------------------------------------------------------------ #
    # Section D: Speedup and Pareto                                        #
    # ------------------------------------------------------------------ #
    speedup_df = comp.dropna(subset=["ours_runtime_sec", "gnn_best_runtime"])
    speedup_df = speedup_df[speedup_df["ours_runtime_sec"] > 0].copy()
    speedup_df["speedup"] = speedup_df["gnn_best_runtime"] / speedup_df["ours_runtime_sec"]

    pareto_df = comp.dropna(subset=["ours_upset_simple", "gnn_best_upset_simple",
                                     "ours_runtime_sec", "gnn_best_runtime"])
    pareto_df = pareto_df[pareto_df["ours_runtime_sec"] > 0].copy()
    pb_fast = int(
        ((pareto_df["ours_upset_simple"] < pareto_df["gnn_best_upset_simple"]) &
         (pareto_df["ours_runtime_sec"] < pareto_df["gnn_best_runtime"])).sum()
    )
    pb_slow = int(
        ((pareto_df["ours_upset_simple"] < pareto_df["gnn_best_upset_simple"]) &
         (pareto_df["ours_runtime_sec"] >= pareto_df["gnn_best_runtime"])).sum()
    )
    pw_fast = int(
        ((pareto_df["ours_upset_simple"] >= pareto_df["gnn_best_upset_simple"]) &
         (pareto_df["ours_runtime_sec"] < pareto_df["gnn_best_runtime"])).sum()
    )
    pw_slow = int(
        ((pareto_df["ours_upset_simple"] >= pareto_df["gnn_best_upset_simple"]) &
         (pareto_df["ours_runtime_sec"] >= pareto_df["gnn_best_runtime"])).sum()
    )

    rows = [
        # Section A
        {"section": "A", "metric": "vs_classical_upset_simple_W_1e6", "value": w_cl_s},
        {"section": "A", "metric": "vs_classical_upset_simple_T_1e6", "value": t_cl_s},
        {"section": "A", "metric": "vs_classical_upset_simple_L_1e6", "value": l_cl_s},
        {"section": "A", "metric": "vs_classical_upset_simple_W_1e3", "value": w_cl_s},
        {"section": "A", "metric": "vs_classical_upset_simple_T_1e3", "value": t_cl_s},
        {"section": "A", "metric": "vs_classical_upset_simple_L_1e3", "value": l_cl_s},
        {"section": "A", "metric": "gap_simple_vs_cl_median",   "value": float(gap_simple.median())},
        {"section": "A", "metric": "gap_simple_vs_cl_mean",     "value": float(gap_simple.mean())},
        {"section": "A", "metric": "gap_simple_vs_cl_P25",      "value": float(gap_simple.quantile(0.25))},
        {"section": "A", "metric": "gap_simple_vs_cl_P75",      "value": float(gap_simple.quantile(0.75))},
        {"section": "A", "metric": "gap_simple_vs_cl_P90",      "value": float(gap_simple.quantile(0.90))},
        {"section": "A", "metric": "gap_simple_vs_cl_max",      "value": float(gap_simple.max())},
        {"section": "A", "metric": "rel_gap_simple_vs_cl_median", "value": float(rel_gap_s.median())},
        {"section": "A", "metric": "rel_gap_simple_vs_cl_mean",   "value": float(rel_gap_s.mean())},
        {"section": "A", "metric": "rel_gap_simple_vs_cl_P25",    "value": float(rel_gap_s.quantile(0.25))},
        {"section": "A", "metric": "rel_gap_simple_vs_cl_P75",    "value": float(rel_gap_s.quantile(0.75))},
        {"section": "A", "metric": "rel_gap_simple_vs_cl_P90",    "value": float(rel_gap_s.quantile(0.90))},
        {"section": "A", "metric": "rel_gap_simple_vs_cl_max",    "value": float(rel_gap_s.max())},
        {"section": "A", "metric": "vs_classical_within_1pct",  "value": within_simple_1pct},
        {"section": "A", "metric": "vs_classical_within_5pct",  "value": within_simple_5pct},
        {"section": "A", "metric": "vs_classical_within_10pct", "value": within_simple_10pct},
        {"section": "A", "metric": "vs_classical_ours_better",  "value": w_cl_s},
        {"section": "A", "metric": "vs_classical_upset_ratio_W_1e6", "value": w_cl_r},
        {"section": "A", "metric": "vs_classical_upset_ratio_T_1e6", "value": t_cl_r},
        {"section": "A", "metric": "vs_classical_upset_ratio_L_1e6", "value": l_cl_r},
        {"section": "A", "metric": "vs_classical_upset_ratio_W_1e3", "value": w_cl_r},
        {"section": "A", "metric": "vs_classical_upset_ratio_T_1e3", "value": t_cl_r},
        {"section": "A", "metric": "vs_classical_upset_ratio_L_1e3", "value": l_cl_r},
        {"section": "A", "metric": "gap_ratio_vs_cl_median",  "value": float(gap_ratio.median())},
        {"section": "A", "metric": "gap_ratio_vs_cl_mean",    "value": float(gap_ratio.mean())},
        {"section": "A", "metric": "gap_ratio_vs_cl_P25",     "value": float(gap_ratio.quantile(0.25))},
        {"section": "A", "metric": "gap_ratio_vs_cl_P75",     "value": float(gap_ratio.quantile(0.75))},
        {"section": "A", "metric": "gap_ratio_vs_cl_P90",     "value": float(gap_ratio.quantile(0.90))},
        {"section": "A", "metric": "gap_ratio_vs_cl_max",     "value": float(gap_ratio.max())},
        {"section": "A", "metric": "rel_gap_ratio_vs_cl_median", "value": float(rel_gap_r.median())},
        {"section": "A", "metric": "rel_gap_ratio_vs_cl_mean",   "value": float(rel_gap_r.mean())},
        {"section": "A", "metric": "rel_gap_ratio_vs_cl_P25",    "value": float(rel_gap_r.quantile(0.25))},
        {"section": "A", "metric": "rel_gap_ratio_vs_cl_P75",    "value": float(rel_gap_r.quantile(0.75))},
        {"section": "A", "metric": "rel_gap_ratio_vs_cl_P90",    "value": float(rel_gap_r.quantile(0.90))},
        {"section": "A", "metric": "rel_gap_ratio_vs_cl_max",    "value": float(rel_gap_r.max())},
        {"section": "A", "metric": "vs_classical_ratio_within_1pct",  "value": int((gap_ratio.abs() <= 0.01).sum())},
        {"section": "A", "metric": "vs_classical_ratio_within_5pct",  "value": int((gap_ratio.abs() <= 0.05).sum())},
        {"section": "A", "metric": "vs_classical_ratio_within_10pct", "value": int((gap_ratio.abs() <= 0.10).sum())},
        {"section": "A", "metric": "vs_classical_ratio_ours_better",  "value": w_cl_r},
        # Section B
        {"section": "B", "metric": "vs_gnn_upset_simple_W_1e6", "value": w_gnn_s},
        {"section": "B", "metric": "vs_gnn_upset_simple_T_1e6", "value": t_gnn_s},
        {"section": "B", "metric": "vs_gnn_upset_simple_L_1e6", "value": l_gnn_s},
        {"section": "B", "metric": "vs_gnn_upset_simple_W_1e3", "value": w_gnn_s},
        {"section": "B", "metric": "vs_gnn_upset_simple_T_1e3", "value": t_gnn_s},
        {"section": "B", "metric": "vs_gnn_upset_simple_L_1e3", "value": l_gnn_s},
        {"section": "B", "metric": "gap_simple_vs_gnn_median",  "value": float(gap_simple_g.median())},
        {"section": "B", "metric": "gap_simple_vs_gnn_mean",    "value": float(gap_simple_g.mean())},
        {"section": "B", "metric": "gap_simple_vs_gnn_P25",     "value": float(gap_simple_g.quantile(0.25))},
        {"section": "B", "metric": "gap_simple_vs_gnn_P75",     "value": float(gap_simple_g.quantile(0.75))},
        {"section": "B", "metric": "gap_simple_vs_gnn_P90",     "value": float(gap_simple_g.quantile(0.90))},
        {"section": "B", "metric": "gap_simple_vs_gnn_max",     "value": float(gap_simple_g.max())},
        {"section": "B", "metric": "rel_gap_simple_vs_gnn_median", "value": float(rel_gap_sg.median())},
        {"section": "B", "metric": "rel_gap_simple_vs_gnn_mean",   "value": float(rel_gap_sg.mean())},
        {"section": "B", "metric": "rel_gap_simple_vs_gnn_P25",    "value": float(rel_gap_sg.quantile(0.25))},
        {"section": "B", "metric": "rel_gap_simple_vs_gnn_P75",    "value": float(rel_gap_sg.quantile(0.75))},
        {"section": "B", "metric": "rel_gap_simple_vs_gnn_P90",    "value": float(rel_gap_sg.quantile(0.90))},
        {"section": "B", "metric": "rel_gap_simple_vs_gnn_max",    "value": float(rel_gap_sg.max())},
        {"section": "B", "metric": "vs_gnn_within_1pct",  "value": within_gnn_simple_1pct},
        {"section": "B", "metric": "vs_gnn_within_5pct",  "value": within_gnn_simple_5pct},
        {"section": "B", "metric": "vs_gnn_within_10pct", "value": within_gnn_simple_10pct},
        {"section": "B", "metric": "vs_gnn_ours_better",  "value": w_gnn_s},
        {"section": "B", "metric": "vs_gnn_upset_ratio_W_1e6", "value": w_gnn_r},
        {"section": "B", "metric": "vs_gnn_upset_ratio_T_1e6", "value": t_gnn_r},
        {"section": "B", "metric": "vs_gnn_upset_ratio_L_1e6", "value": l_gnn_r},
        {"section": "B", "metric": "vs_gnn_upset_ratio_W_1e3", "value": w_gnn_r},
        {"section": "B", "metric": "vs_gnn_upset_ratio_T_1e3", "value": t_gnn_r},
        {"section": "B", "metric": "vs_gnn_upset_ratio_L_1e3", "value": l_gnn_r},
        {"section": "B", "metric": "gap_ratio_vs_gnn_median",  "value": float(gap_ratio_g.median())},
        {"section": "B", "metric": "gap_ratio_vs_gnn_mean",    "value": float(gap_ratio_g.mean())},
        {"section": "B", "metric": "gap_ratio_vs_gnn_P25",     "value": float(gap_ratio_g.quantile(0.25))},
        {"section": "B", "metric": "gap_ratio_vs_gnn_P75",     "value": float(gap_ratio_g.quantile(0.75))},
        {"section": "B", "metric": "gap_ratio_vs_gnn_P90",     "value": float(gap_ratio_g.quantile(0.90))},
        {"section": "B", "metric": "gap_ratio_vs_gnn_max",     "value": float(gap_ratio_g.max())},
        {"section": "B", "metric": "rel_gap_ratio_vs_gnn_median", "value": float(((gap_ratio_g) / comp["gnn_best_upset_ratio"]).dropna().median())},
        {"section": "B", "metric": "rel_gap_ratio_vs_gnn_mean",   "value": float(((gap_ratio_g) / comp["gnn_best_upset_ratio"]).dropna().mean())},
        {"section": "B", "metric": "rel_gap_ratio_vs_gnn_P25",    "value": float(((gap_ratio_g) / comp["gnn_best_upset_ratio"]).dropna().quantile(0.25))},
        {"section": "B", "metric": "rel_gap_ratio_vs_gnn_P75",    "value": float(((gap_ratio_g) / comp["gnn_best_upset_ratio"]).dropna().quantile(0.75))},
        {"section": "B", "metric": "rel_gap_ratio_vs_gnn_P90",    "value": float(((gap_ratio_g) / comp["gnn_best_upset_ratio"]).dropna().quantile(0.90))},
        {"section": "B", "metric": "rel_gap_ratio_vs_gnn_max",    "value": float(((gap_ratio_g) / comp["gnn_best_upset_ratio"]).dropna().max())},
        {"section": "B", "metric": "vs_gnn_ratio_within_1pct",  "value": int((gap_ratio_g.abs() <= 0.01).sum())},
        {"section": "B", "metric": "vs_gnn_ratio_within_5pct",  "value": int((gap_ratio_g.abs() <= 0.05).sum())},
        {"section": "B", "metric": "vs_gnn_ratio_within_10pct", "value": int((gap_ratio_g.abs() <= 0.10).sum())},
        {"section": "B", "metric": "vs_gnn_ratio_ours_better",  "value": w_gnn_r},
        # Section D
        {"section": "D", "metric": "runtime_count",  "value": len(speedup_df)},
        {"section": "D", "metric": "speedup_P25",    "value": float(speedup_df["speedup"].quantile(0.25))},
        {"section": "D", "metric": "speedup_median", "value": float(speedup_df["speedup"].median())},
        {"section": "D", "metric": "speedup_P75",    "value": float(speedup_df["speedup"].quantile(0.75))},
        {"section": "D", "metric": "speedup_mean",   "value": float(speedup_df["speedup"].mean())},
        {"section": "D", "metric": "speedup_ge10x",  "value": int((speedup_df["speedup"] >= 10).sum())},
        {"section": "D", "metric": "speedup_ge50x",  "value": int((speedup_df["speedup"] >= 50).sum())},
        {"section": "D", "metric": "speedup_ge100x", "value": int((speedup_df["speedup"] >= 100).sum())},
        {"section": "D", "metric": "Pareto_better_faster", "value": pb_fast},
        {"section": "D", "metric": "Pareto_better_slower", "value": pb_slow},
        {"section": "D", "metric": "Pareto_worse_faster",  "value": pw_fast},
        {"section": "D", "metric": "Pareto_worse_slower",  "value": pw_slow},
    ]
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Benchmark composition table (n/m ranges per family)
# ---------------------------------------------------------------------------

def _get_npz_stats(npz_path: Path) -> tuple[int, int]:
    """Return (n_nodes, n_edges) from a scipy sparse npz file."""
    mat = sp.load_npz(npz_path)
    return int(mat.shape[0]), int(mat.nnz)


def _map_dataset_to_npz(dataset: str) -> Path | None:
    """
    Attempt to locate the adjacency npz file for a given dataset name.
    Dataset names use '/' as separator and match the data directory structure.
    """
    # dataset: e.g. "Basketball_temporal/1985"
    # npz:     GNNRank-main/data/Basketball_temporal/1985adj.npz
    parts = dataset.split("/")
    if len(parts) == 1:
        # top-level: e.g. "finance", "Dryad_animal_society"
        candidate = DATA_DIR / parts[0] / "adj.npz"
        if candidate.exists():
            return candidate
        return None
    elif len(parts) == 2:
        subdir, name = parts
        # Special case: Halo2BetaData/HeadToHead — no separate adj.npz;
        # use the parent adj.npz (same node set, subset of edges).
        if subdir == "Halo2BetaData" and name == "HeadToHead":
            candidate = DATA_DIR / subdir / "adj.npz"
            if candidate.exists():
                return candidate
            return None
        candidate = DATA_DIR / subdir / f"{name}adj.npz"
        if candidate.exists():
            return candidate
        # Faculty has nested structure: FacultyHiringNetworks/Business/Business_FM_Full_
        for deeper in (DATA_DIR / subdir).rglob(f"{name}adj.npz"):
            return deeper
    elif len(parts) == 3:
        # e.g. FacultyHiringNetworks/Business/Business_FM_Full_
        subdir, sub2, name = parts
        for candidate in (DATA_DIR / subdir / sub2).glob(f"{name}adj.npz"):
            return candidate
    return None


def build_benchmark_composition(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each dataset in the 80-suite, record family, n, m.
    Returns a DataFrame with one row per dataset plus family-level summaries.
    """
    df80 = filter_80_suite(df)
    datasets = sorted(df80["dataset"].unique())

    rows = []
    n_found = 0
    for dataset in datasets:
        family = assign_family(dataset)
        npz_path = _map_dataset_to_npz(dataset)
        n, m = None, None
        if npz_path is not None:
            try:
                n, m = _get_npz_stats(npz_path)
                n_found += 1
            except Exception as exc:
                warnings.warn(f"Could not read {npz_path}: {exc}")
        rows.append(
            {
                "dataset": dataset,
                "family": family,
                "n_nodes": n,
                "n_edges": m,
                "npz_found": npz_path is not None,
            }
        )

    print(f"Benchmark composition: {len(rows)} datasets, npz found for {n_found}")
    return pd.DataFrame(rows)


def build_family_summary(composition: pd.DataFrame) -> pd.DataFrame:
    """Summarise n/m ranges per dataset family."""
    rows = []
    for family, grp in composition.groupby("family"):
        valid = grp.dropna(subset=["n_nodes"])
        rows.append(
            {
                "family": family,
                "n_datasets": len(grp),
                "n_min": int(valid["n_nodes"].min()) if len(valid) else None,
                "n_max": int(valid["n_nodes"].max()) if len(valid) else None,
                "m_min": int(valid["n_edges"].min()) if len(valid) else None,
                "m_max": int(valid["n_edges"].max()) if len(valid) else None,
            }
        )
    return pd.DataFrame(rows).sort_values("family").reset_index(drop=True)


# ---------------------------------------------------------------------------
# Dataset inventory
# ---------------------------------------------------------------------------

def build_dataset_inventory(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full inventory of all 81 datasets: name, family, in_80_suite flag.
    """
    all_datasets = sorted(df["dataset"].unique())
    rows = []
    for dataset in all_datasets:
        rows.append(
            {
                "dataset": dataset,
                "family": assign_family(dataset),
                "in_80_suite": dataset != AUTO_DATASET,
            }
        )
    inv = pd.DataFrame(rows)
    print(
        f"Dataset inventory: {len(inv)} total, "
        f"{inv['in_80_suite'].sum()} in 80-suite, "
        f"{(~inv['in_80_suite']).sum()} excluded (_AUTO)"
    )
    return inv


# ---------------------------------------------------------------------------
# Paper metrics master — all key numbers in one CSV
# ---------------------------------------------------------------------------

def build_paper_metrics_master(table4: pd.DataFrame, table5: pd.DataFrame) -> pd.DataFrame:
    """
    Combine Table 4 and Table 5 into a master metrics CSV with a 'table' column.
    """
    t4 = table4.copy()
    t4["table"] = "table4_full_suite_80d"
    t5 = table5.copy()
    t5["table"] = "table5_compute_matched"
    master = pd.concat([t4, t5], ignore_index=True)
    cols = ["table"] + [c for c in master.columns if c != "table"]
    return master[cols]


# ---------------------------------------------------------------------------
# paper_claims_master.json
# ---------------------------------------------------------------------------

def build_paper_claims_json(
    table4: pd.DataFrame,
    table5: pd.DataFrame,
    composition: pd.DataFrame,
    family_summary: pd.DataFrame,
) -> dict:
    """
    Build a structured JSON of all manuscript-facing numerical claims.
    """
    def _method_dict(row: pd.Series) -> dict:
        return {
            "coverage": row["coverage"],
            "n_datasets": int(row["n_datasets"]),
            "median_upset_simple": float(row["median_upset_simple"]),
            "mean_upset_simple": float(row["mean_upset_simple"]),
            "median_upset_ratio": float(row["median_upset_ratio"]) if pd.notna(row.get("median_upset_ratio")) else None,
            "mean_upset_ratio": float(row["mean_upset_ratio"]) if pd.notna(row.get("mean_upset_ratio")) else None,
            "median_upset_naive": float(row["median_upset_naive"]) if pd.notna(row.get("median_upset_naive")) else None,
            "mean_upset_naive": float(row["mean_upset_naive"]) if pd.notna(row.get("mean_upset_naive")) else None,
        }

    t4_by_method = {
        row["method"]: _method_dict(row)
        for _, row in table4.iterrows()
    }
    t5_by_method = {
        row["method"]: _method_dict(row)
        for _, row in table5.iterrows()
    }

    family_ranges = {}
    for _, row in family_summary.iterrows():
        family_ranges[row["family"]] = {
            "n_datasets": int(row["n_datasets"]),
            "n_range": [row["n_min"], row["n_max"]],
            "m_range": [row["m_min"], row["m_max"]],
        }

    claims = {
        "_meta": {
            "description": (
                "Canonical numerical claims for the manuscript. "
                "All values derived from GNNRank-main/paper_csv/leaderboard_per_method.csv."
            ),
            "total_datasets": 81,
            "suite_80_datasets": 80,
            "extra_dataset_excluded": AUTO_DATASET,
            "compute_matched_datasets": int(table5["n_datasets"].max()) if len(table5) > 0 else None,
        },
        "football_n_range_note": (
            "All 12 football instances (6 coarse + 6 finer) have n=20. "
            "The manuscript claim of n-range 20-107 is INCORRECT; m ranges from 107-380."
        ),
        "finance_timeout_note": (
            "In the trials10 config (primary benchmark), finance has NaN upset_simple "
            "for ALL four OURS methods, giving each coverage=77/80. "
            "The missingness_audit.csv reports a different view (across all trial configs): "
            "OURS_MFAS times out on finance in all configs (77/80 overall), "
            "while INS1/INS2/INS3 complete on finance in non-trials10 configs (80/80 overall). "
            "Table 4 uses only the trials10 config, so all OURS methods show coverage 77/80."
        ),
        "table4_full_suite": t4_by_method,
        "table5_compute_matched": t5_by_method,
        "benchmark_composition": family_ranges,
    }
    return claims


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DERIVED_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("generate_paper_tables.py")
    print("=" * 70)

    # --- Load data ---
    df = load_leaderboard()
    df_cm = load_compute_matched()
    df_miss = load_missingness_audit()
    df_contrib = load_contribution_stats()
    df_unified = load_unified_comparison()

    # --- Table 4 ---
    print("\n[Table 4] Full 80-dataset suite …")
    table4 = build_table4(df)
    out4 = OUT_DIR / "table4_full_suite.csv"
    table4.to_csv(out4, index=False)
    print(f"  → {out4}")
    print(table4[["method", "coverage", "median_upset_simple", "mean_upset_simple"]].to_string(index=False))

    # --- Table 5 ---
    print("\n[Table 5] Compute-matched suite …")
    table5 = build_table5(df_cm)
    out5 = OUT_DIR / "table5_compute_matched.csv"
    table5.to_csv(out5, index=False)
    print(f"  → {out5}")

    # --- Table 6 ---
    print("\n[Table 6] Missingness audit …")
    table6 = build_table6(df_miss, df)
    out6 = OUT_DIR / "table6_missingness.csv"
    table6.to_csv(out6, index=False)
    print(f"  → {out6}")

    # --- Table 7 ---
    print("\n[Table 7] Best-in-suite comparison …")
    table7 = build_table7(df_unified, df)
    out7 = OUT_DIR / "table7_best_in_suite.csv"
    table7.to_csv(out7, index=False)
    print(f"  → {out7}")

    # --- Table 8 ---
    print("\n[Table 8] Runtime trade-off …")
    table8 = build_table8(df_contrib, df)
    out8 = OUT_DIR / "table8_runtime_tradeoff.csv"
    table8.to_csv(out8, index=False)
    print(f"  → {out8}")

    # --- Benchmark composition ---
    print("\n[Benchmark composition] n/m ranges …")
    composition = build_benchmark_composition(df)
    family_summary = build_family_summary(composition)

    out_comp = OUT_DIR / "benchmark_composition.csv"
    composition.to_csv(out_comp, index=False)
    print(f"  → {out_comp}")

    out_fam = OUT_DIR / "benchmark_family_summary.csv"
    family_summary.to_csv(out_fam, index=False)
    print(f"  → {out_fam}")
    print(family_summary.to_string(index=False))

    # --- Paper metrics master ---
    print("\n[Paper metrics master] …")
    master = build_paper_metrics_master(table4, table5)
    out_master = OUT_DIR / "paper_metrics_master.csv"
    master.to_csv(out_master, index=False)
    print(f"  → {out_master}")

    # --- Paper claims JSON ---
    print("\n[Paper claims JSON] …")
    claims = build_paper_claims_json(table4, table5, composition, family_summary)
    out_json = OUT_DIR / "paper_claims_master.json"
    with open(out_json, "w") as fh:
        json.dump(claims, fh, indent=2, default=lambda x: None if pd.isna(x) else x)
    print(f"  → {out_json}")

    # --- Dataset inventory (outputs/derived/) ---
    print("\n[Dataset inventory] …")
    inventory = build_dataset_inventory(df)
    out_inv = DERIVED_DIR / "dataset_inventory.csv"
    inventory.to_csv(out_inv, index=False)
    print(f"  → {out_inv}")

    print("\n" + "=" * 70)
    print("All outputs generated successfully.")
    print("=" * 70)


if __name__ == "__main__":
    main()
