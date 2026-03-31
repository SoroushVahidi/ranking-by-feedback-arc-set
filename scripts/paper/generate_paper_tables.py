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
    Uses unified_comparison.csv if available.
    """
    if not df_unified.empty:
        # Filter to 80-dataset suite
        result = df_unified[df_unified["dataset"] != AUTO_DATASET].copy()
        result["family"] = result["dataset"].apply(assign_family)
        return result

    # Fallback: basic per-dataset best
    df80 = filter_80_suite(df)
    df_t10 = filter_trials10(df80)
    best = pick_best_per_dataset(df_t10)

    ours_methods = [m for m in METHODS_TABLE4 if m.startswith("OURS_")]
    classical_methods = [
        m for m in METHODS_TABLE4 if not m.startswith("OURS_") and m not in GNN_METHODS
    ]
    gnn_methods = [m for m in METHODS_TABLE4 if m in GNN_METHODS]

    rows = []
    for dataset in sorted(best["dataset"].unique()):
        sub = best[best["dataset"] == dataset]
        ours_best_val = sub[sub["method"].isin(ours_methods)]["upset_simple"].min()
        classical_best_val = sub[sub["method"].isin(classical_methods)]["upset_simple"].min()
        gnn_best_val = sub[sub["method"].isin(gnn_methods)]["upset_simple"].min()
        rows.append(
            {
                "dataset": dataset,
                "family": assign_family(dataset),
                "ours_best_upset_simple": ours_best_val,
                "classical_best_upset_simple": classical_best_val,
                "gnn_best_upset_simple": gnn_best_val,
                "ours_beats_classical": int(ours_best_val < classical_best_val),
                "ours_beats_gnn": int(ours_best_val < gnn_best_val),
            }
        )
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Table 8: Runtime trade-off
# ---------------------------------------------------------------------------

def build_table8(df_contrib: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
    """
    Table 8 — Speedup and Pareto statistics.
    Uses contribution_stats.csv if available, otherwise computes runtime summaries.
    """
    if not df_contrib.empty:
        return df_contrib

    # Fallback: runtime comparison between OURS_MFAS and classical methods
    df80 = filter_80_suite(df)
    df_t10 = filter_trials10(df80)
    best = pick_best_per_dataset(df_t10)

    ours = best[best["method"] == "OURS_MFAS"][["dataset", "runtime_sec"]].rename(
        columns={"runtime_sec": "ours_runtime"}
    )
    classical_methods = [
        m for m in METHODS_TABLE4 if not m.startswith("OURS_") and m not in GNN_METHODS
    ]
    classical = (
        best[best["method"].isin(classical_methods)]
        .groupby("dataset")["runtime_sec"]
        .min()
        .reset_index()
        .rename(columns={"runtime_sec": "classical_best_runtime"})
    )
    merged = ours.merge(classical, on="dataset", how="inner")
    merged["speedup"] = merged["classical_best_runtime"] / merged["ours_runtime"]

    summary = pd.DataFrame(
        [
            {
                "metric": "median_speedup_vs_classical_best",
                "value": merged["speedup"].median(),
            },
            {
                "metric": "mean_speedup_vs_classical_best",
                "value": merged["speedup"].mean(),
            },
            {
                "metric": "n_datasets_compared",
                "value": len(merged),
            },
        ]
    )
    return summary


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
