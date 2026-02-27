#!/usr/bin/env python3
"""
Generate manuscript figures from leaderboard CSVs.

Outputs under paper_figs/:
  - accuracy_vs_runtime_scatter.png (and .pdf)
  - coverage_vs_time_budget_curve.png (and .pdf)
  - ours_vs_baseline_winloss.png (optional, .png and .pdf)

Run from repo root: python tools/build_paper_figs.py
Requires: matplotlib, pandas
"""

from pathlib import Path
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
PAPER_CSV = REPO_ROOT / "paper_csv"
PAPER_FIGS = REPO_ROOT / "paper_figs"
LEADERBOARD = PAPER_CSV / "leaderboard_per_method.csv"
ORACLE = PAPER_CSV / "leaderboard_oracle_envelopes.csv"

OURS_METHODS = {"OURS_MFAS", "OURS_MFAS_INS1", "OURS_MFAS_INS2", "OURS_MFAS_INS3"}
GNN_METHODS = {"DIGRAC", "ib", "DIGRACib"}
CLASSICAL_METHODS = {
    "SpringRank", "syncRank", "serialRank", "btl", "davidScore",
    "eigenvectorCentrality", "PageRank", "rankCentrality", "SVD_RS", "SVD_NRS", "mvr",
}
TIME_BUDGETS = [60, 120, 300, 600, 1800, 3600, 7200]


def method_family(m: str) -> str:
    if m in OURS_METHODS:
        return "OURS"
    if m in GNN_METHODS:
        return "GNN"
    if m in CLASSICAL_METHODS:
        return "classical"
    return "other"


def main():
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not found; skipping figures.")
        return

    PAPER_FIGS.mkdir(parents=True, exist_ok=True)

    # Minimal provenance print so logs record exact inputs.
    print("[build_paper_figs] Inputs:")
    print(f"  LEADERBOARD={LEADERBOARD}")
    print(f"  ORACLE={ORACLE}")

    lb = pd.read_csv(LEADERBOARD)
    lb["family"] = lb["method"].map(method_family)
    lb_valid = lb.dropna(subset=["upset_simple", "runtime_sec"]).copy()
    lb_valid = lb_valid[lb_valid["runtime_sec"] > 0]  # log scale

    # ----- 1) Accuracy vs runtime scatter -----
    fig, ax = plt.subplots(figsize=(8, 6))
    for fam in ["OURS", "classical", "GNN"]:
        sub = lb_valid[lb_valid["family"] == fam]
        if sub.empty:
            continue
        ax.scatter(
            sub["runtime_sec"],
            sub["upset_simple"],
            label=fam,
            alpha=0.5,
            s=12,
        )
    ax.set_xscale("log")
    ax.set_xlabel("Runtime (sec)")
    ax.set_ylabel("Upset simple")
    ax.legend()
    ax.set_title("Accuracy vs runtime (per dataset × method)")
    fig.tight_layout()
    for ext in ["png", "pdf"]:
        fig.savefig(PAPER_FIGS / f"accuracy_vs_runtime_scatter.{ext}", dpi=150 if ext == "png" else None)
    plt.close(fig)
    print("Wrote accuracy_vs_runtime_scatter.png, .pdf")

    # ----- 2) Coverage vs time budget curve -----
    # Per family: fraction of (dataset, method) runs with runtime_sec <= budget
    lb_rt = lb.dropna(subset=["runtime_sec"]).copy()
    n_total = len(lb_rt)
    if n_total == 0:
        n_total = 1
    curves = {}
    for fam in ["OURS", "classical", "GNN"]:
        sub = lb_rt[lb_rt["family"] == fam]
        if sub.empty:
            curves[fam] = [0.0] * len(TIME_BUDGETS)
            continue
        fracs = []
        for budget in TIME_BUDGETS:
            within = (sub["runtime_sec"] <= budget).sum()
            fracs.append(within / len(sub))
        curves[fam] = fracs

    fig, ax = plt.subplots(figsize=(7, 5))
    for fam in ["OURS", "classical", "GNN"]:
        ax.plot(TIME_BUDGETS, curves[fam], marker="o", label=fam)
    ax.set_xscale("log")
    ax.set_xticks(TIME_BUDGETS)
    ax.set_xticklabels([str(b) for b in TIME_BUDGETS])
    ax.set_xlabel("Time budget (sec)")
    ax.set_ylabel("Fraction of runs completed within budget")
    ax.legend()
    ax.set_title("Coverage vs time budget (per family)")
    fig.tight_layout()
    for ext in ["png", "pdf"]:
        fig.savefig(PAPER_FIGS / f"coverage_vs_time_budget_curve.{ext}", dpi=150 if ext == "png" else None)
    plt.close(fig)
    print("Wrote coverage_vs_time_budget_curve.png, .pdf")

    # ----- 3) Optional: OURS vs each baseline win/loss (per dataset) -----
    if ORACLE.exists():
        oracle_df = pd.read_csv(ORACLE)
        ours_rows = lb[(lb["method"] == "OURS_MFAS_INS3")].dropna(subset=["upset_simple"])
        ours_by_ds = ours_rows.set_index("dataset")["upset_simple"].rename("ours_upset_simple")
        merged = oracle_df.set_index("dataset").join(ours_by_ds, how="inner")
        merged = merged.dropna(subset=["ours_upset_simple", "best_classical_upset_simple", "best_gnn_upset_simple"])
        if len(merged) > 0:
            # Win/loss vs best classical and vs best GNN
            tie_tol = 1e-6
            vs_cl = np.where(
                merged["ours_upset_simple"] < merged["best_classical_upset_simple"] - tie_tol, 1,
                np.where(merged["ours_upset_simple"] > merged["best_classical_upset_simple"] + tie_tol, -1, 0)
            )
            vs_gnn = np.where(
                merged["ours_upset_simple"] < merged["best_gnn_upset_simple"] - tie_tol, 1,
                np.where(merged["ours_upset_simple"] > merged["best_gnn_upset_simple"] + tie_tol, -1, 0)
            )
            fig, axes = plt.subplots(1, 2, figsize=(8, 4))
            for ax, vals, title in zip(
                axes,
                [vs_cl, vs_gnn],
                ["OURS vs best classical", "OURS vs best GNN"],
            ):
                w, t, l = (vals == 1).sum(), (vals == 0).sum(), (vals == -1).sum()
                ax.bar(["Win", "Tie", "Loss"], [w, t, l], color=["#2ecc71", "#95a5a6", "#e74c3c"])
                ax.set_ylabel("Count (datasets)")
                ax.set_title(title)
            fig.suptitle("Per-dataset win/tie/loss (tie tolerance 1e-6)")
            fig.tight_layout()
            for ext in ["png", "pdf"]:
                fig.savefig(PAPER_FIGS / f"ours_vs_baseline_winloss.{ext}", dpi=150 if ext == "png" else None)
            plt.close(fig)
            print("Wrote ours_vs_baseline_winloss.png, .pdf")
        else:
            print("Skipped ours_vs_baseline_winloss (no overlapping datasets with oracle).")
    else:
        print("Skipped ours_vs_baseline_winloss (oracle CSV not found).")


if __name__ == "__main__":
    main()
