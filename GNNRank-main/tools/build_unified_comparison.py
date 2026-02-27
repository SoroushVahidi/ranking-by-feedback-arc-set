#!/usr/bin/env python3
"""
Build a unified per-dataset comparison CSV and print summary statistics.

1. Runs tools/build_results_table_from_result_arrays.py if needed (or use existing
   paper_csv/results_from_result_arrays.csv).
2. Joins classical + OURS from result_arrays (full precision); falls back to
   full_833614_metrics_best.csv for any dataset/method not in result_arrays.
3. For each dataset: OURS_MFAS_INS3, best classical (min upset_simple), best GNN
   (min upset_simple over DIGRAC/ib/DIGRACib configs).
4. Writes paper_csv/unified_comparison.csv.
5. Prints W/L/T (tie 1e-6 and 1e-3), median/mean gaps, top 20 datasets where
   OURS loses most to best GNN.

Run from repo root: python tools/build_unified_comparison.py
"""

import math
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
UNIFIED_CSV = REPO_ROOT / "paper_csv" / "unified_comparison.csv"

OURS_METHOD = "OURS_MFAS_INS3"
CLASSICAL = [
    "SpringRank", "syncRank", "serialRank", "btl", "davidScore",
    "eigenvectorCentrality", "PageRank", "rankCentrality", "SVD_RS", "SVD_NRS",
]
GNN_METHODS = ["DIGRAC", "ib", "DIGRACib"]


def ensure_aggregator_run():
    if not RESULTS_CSV.exists():
        subprocess.check_call([sys.executable, str(AGGREGATOR)], cwd=str(REPO_ROOT))


def load_from_result_arrays() -> pd.DataFrame:
    df = pd.read_csv(RESULTS_CSV)
    # Use only which == "upset" for comparison (canonical metric)
    df = df[df["which"] == "upset"].copy()
    return df


def load_full_metrics() -> pd.DataFrame:
    return pd.read_csv(FULL_METRICS_CSV)


def build_unified():
    ensure_aggregator_run()
    ra = load_from_result_arrays()
    full = load_full_metrics()

    datasets_ra = set(ra["dataset"].unique())
    datasets_full = set(full["dataset"].unique())
    all_datasets = sorted(datasets_ra | datasets_full)
    records = []
    for ds in all_datasets:
        # OURS
        ours_row_ra = ra[(ra["dataset"] == ds) & (ra["method"] == OURS_METHOD)]
        ours_row_full = full[(full["dataset"] == ds) & (full["method"] == OURS_METHOD)]
        if len(ours_row_ra):
            ours_s = float(ours_row_ra["upset_simple_mean"].iloc[0])
            ours_r = float(ours_row_ra["upset_ratio_mean"].iloc[0])
            ours_n = float(ours_row_ra["upset_naive_mean"].iloc[0])
            ours_rt = float(ours_row_ra["runtime_sec_mean"].iloc[0]) if pd.notna(ours_row_ra["runtime_sec_mean"].iloc[0]) else np.nan
        elif len(ours_row_full):
            ours_s = float(ours_row_full["upset_simple_mean"].iloc[0])
            ours_r = float(ours_row_full["upset_ratio_mean"].iloc[0])
            ours_n = float(ours_row_full["upset_naive_mean"].iloc[0])
            ours_rt = float(ours_row_full["runtime_sec_mean"].iloc[0]) if "runtime_sec_mean" in ours_row_full.columns and pd.notna(ours_row_full["runtime_sec_mean"].iloc[0]) else np.nan
        else:
            ours_s = ours_r = ours_n = ours_rt = np.nan

        # Best classical: min upset_simple over classical methods (from ra first, then full)
        best_cl_s = best_cl_r = best_cl_n = best_cl_rt = np.nan
        for m in CLASSICAL:
            r_ra = ra[(ra["dataset"] == ds) & (ra["method"] == m)]
            r_full = full[(full["dataset"] == ds) & (full["method"] == m)]
            val = np.nan
            if len(r_ra):
                val = float(r_ra["upset_simple_mean"].iloc[0])
            elif len(r_full):
                val = float(r_full["upset_simple_mean"].iloc[0])
            if not math.isnan(val) and (math.isnan(best_cl_s) or val < best_cl_s):
                best_cl_s = val
                if len(r_ra):
                    best_cl_r = float(r_ra["upset_ratio_mean"].iloc[0])
                    best_cl_n = float(r_ra["upset_naive_mean"].iloc[0])
                    best_cl_rt = float(r_ra["runtime_sec_mean"].iloc[0]) if pd.notna(r_ra["runtime_sec_mean"].iloc[0]) else np.nan
                else:
                    best_cl_r = float(r_full["upset_ratio_mean"].iloc[0])
                    best_cl_n = float(r_full["upset_naive_mean"].iloc[0])
                    best_cl_rt = float(r_full["runtime_sec_mean"].iloc[0]) if "runtime_sec_mean" in r_full.columns and pd.notna(r_full["runtime_sec_mean"].iloc[0]) else np.nan

        # Best GNN: min upset_simple over DIGRAC/ib/DIGRACib (only from ra; full has no per-config GNN)
        gnn_rows = ra[(ra["dataset"] == ds) & (ra["method"].isin(GNN_METHODS))]
        if len(gnn_rows):
            idx = gnn_rows["upset_simple_mean"].idxmin()
            best_gnn_row = gnn_rows.loc[idx]
            best_gnn_s = float(best_gnn_row["upset_simple_mean"])
            best_gnn_r = float(best_gnn_row["upset_ratio_mean"])
            best_gnn_n = float(best_gnn_row["upset_naive_mean"])
            best_gnn_rt = float(best_gnn_row["runtime_sec_mean"]) if pd.notna(best_gnn_row["runtime_sec_mean"]) else np.nan
        else:
            best_gnn_s = best_gnn_r = best_gnn_n = best_gnn_rt = np.nan

        records.append({
            "dataset": ds,
            "ours_upset_simple": ours_s,
            "ours_upset_ratio": ours_r,
            "ours_upset_naive": ours_n,
            "ours_runtime_sec": ours_rt,
            "best_classical_upset_simple": best_cl_s,
            "best_classical_upset_ratio": best_cl_r,
            "best_classical_upset_naive": best_cl_n,
            "best_classical_runtime_sec": best_cl_rt,
            "best_gnn_upset_simple": best_gnn_s,
            "best_gnn_upset_ratio": best_gnn_r,
            "best_gnn_upset_naive": best_gnn_n,
            "best_gnn_runtime_sec": best_gnn_rt,
        })

    uf = pd.DataFrame(records)
    UNIFIED_CSV.parent.mkdir(parents=True, exist_ok=True)
    uf.to_csv(UNIFIED_CSV, index=False)
    print(f"Wrote {len(uf)} rows to {UNIFIED_CSV}")
    return uf


def compare(a: float, b: float, tie_tol: float) -> str:
    if not (math.isfinite(a) and math.isfinite(b)):
        return "skip"
    diff = a - b
    if abs(diff) <= tie_tol:
        return "tie"
    return "win" if a < b else "loss"


def print_summary(uf: pd.DataFrame):
    print("\n" + "=" * 70)
    print("SUMMARY STATISTICS (unified comparison)")
    print("=" * 70)

    for tie_tol, name in [(1e-6, "1e-6"), (1e-3, "1e-3")]:
        print(f"\n--- Tie tolerance: {name} ---")

        # OURS vs best GNN (only datasets where both exist)
        uf_gnn = uf.dropna(subset=["ours_upset_simple", "best_gnn_upset_simple"])
        w_s = sum(1 for _, r in uf_gnn.iterrows() if compare(r["ours_upset_simple"], r["best_gnn_upset_simple"], tie_tol) == "win")
        t_s = sum(1 for _, r in uf_gnn.iterrows() if compare(r["ours_upset_simple"], r["best_gnn_upset_simple"], tie_tol) == "tie")
        l_s = sum(1 for _, r in uf_gnn.iterrows() if compare(r["ours_upset_simple"], r["best_gnn_upset_simple"], tie_tol) == "loss")
        print(f"OURS vs best GNN (upset_simple): W={w_s} T={t_s} L={l_s}  (n={len(uf_gnn)})")
        w_r = sum(1 for _, r in uf_gnn.iterrows() if compare(r["ours_upset_ratio"], r["best_gnn_upset_ratio"], tie_tol) == "win")
        t_r = sum(1 for _, r in uf_gnn.iterrows() if compare(r["ours_upset_ratio"], r["best_gnn_upset_ratio"], tie_tol) == "tie")
        l_r = sum(1 for _, r in uf_gnn.iterrows() if compare(r["ours_upset_ratio"], r["best_gnn_upset_ratio"], tie_tol) == "loss")
        print(f"OURS vs best GNN (upset_ratio):  W={w_r} T={t_r} L={l_r}  (n={len(uf_gnn)})")
        gap_s = (uf_gnn["ours_upset_simple"] - uf_gnn["best_gnn_upset_simple"]).dropna()
        gap_r = (uf_gnn["ours_upset_ratio"] - uf_gnn["best_gnn_upset_ratio"]).dropna()
        if len(gap_s):
            print(f"  Gap upset_simple: median={gap_s.median():.6f} mean={gap_s.mean():.6f}")
        if len(gap_r):
            print(f"  Gap upset_ratio:  median={gap_r.median():.6f} mean={gap_r.mean():.6f}")

        # OURS vs best classical
        uf_cl = uf.dropna(subset=["ours_upset_simple", "best_classical_upset_simple"])
        w_cs = sum(1 for _, r in uf_cl.iterrows() if compare(r["ours_upset_simple"], r["best_classical_upset_simple"], tie_tol) == "win")
        t_cs = sum(1 for _, r in uf_cl.iterrows() if compare(r["ours_upset_simple"], r["best_classical_upset_simple"], tie_tol) == "tie")
        l_cs = sum(1 for _, r in uf_cl.iterrows() if compare(r["ours_upset_simple"], r["best_classical_upset_simple"], tie_tol) == "loss")
        print(f"OURS vs best classical (upset_simple): W={w_cs} T={t_cs} L={l_cs}  (n={len(uf_cl)})")
        w_cr = sum(1 for _, r in uf_cl.iterrows() if compare(r["ours_upset_ratio"], r["best_classical_upset_ratio"], tie_tol) == "win")
        t_cr = sum(1 for _, r in uf_cl.iterrows() if compare(r["ours_upset_ratio"], r["best_classical_upset_ratio"], tie_tol) == "tie")
        l_cr = sum(1 for _, r in uf_cl.iterrows() if compare(r["ours_upset_ratio"], r["best_classical_upset_ratio"], tie_tol) == "loss")
        print(f"OURS vs best classical (upset_ratio):  W={w_cr} T={t_cr} L={l_cr}  (n={len(uf_cl)})")
        gap_cs = (uf_cl["ours_upset_simple"] - uf_cl["best_classical_upset_simple"]).dropna()
        gap_cr = (uf_cl["ours_upset_ratio"] - uf_cl["best_classical_upset_ratio"]).dropna()
        if len(gap_cs):
            print(f"  Gap upset_simple: median={gap_cs.median():.6f} mean={gap_cs.mean():.6f}")
        if len(gap_cr):
            print(f"  Gap upset_ratio:  median={gap_cr.median():.6f} mean={gap_cr.mean():.6f}")

    # Top 20 datasets where OURS loses most to best GNN (by gap = ours - best_gnn, positive = OURS worse)
    uf_gnn = uf.dropna(subset=["ours_upset_simple", "best_gnn_upset_simple"])
    uf_gnn = uf_gnn.copy()
    uf_gnn["gap_simple"] = uf_gnn["ours_upset_simple"] - uf_gnn["best_gnn_upset_simple"]
    top20_lose = uf_gnn.nlargest(20, "gap_simple")[["dataset", "ours_upset_simple", "best_gnn_upset_simple", "gap_simple"]]
    print("\n--- Top 20 datasets where OURS loses most to best GNN (by upset_simple gap) ---")
    for _, r in top20_lose.iterrows():
        print(f"  {r['dataset']}: ours={r['ours_upset_simple']:.6f} best_gnn={r['best_gnn_upset_simple']:.6f} gap={r['gap_simple']:.6f}")


def main():
    uf = build_unified()
    print_summary(uf)
    return UNIFIED_CSV


if __name__ == "__main__":
    main()
