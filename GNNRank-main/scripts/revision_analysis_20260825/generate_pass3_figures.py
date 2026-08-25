#!/usr/bin/env python3
"""Generate Pass-3 manuscript figures from completed revision CSVs only."""
from pathlib import Path
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[3]
FIG = ROOT / "manuscript/revision_20260825/figures"
FIG.mkdir(parents=True, exist_ok=True)
AB = ROOT / "outputs/revision_analysis_20260825/reviewer_ablation_scalability"


def fig_runtime_vs_edges() -> None:
    sa = pd.read_csv(AB / "structural_ablation.csv")
    a4 = sa[sa["config"] == "A4"]
    nf = a4[~a4["dataset"].astype(str).str.lower().str.contains("finance")]
    # runtime_algorithm_sec (Phase A + Phase B + Phase C, single OURS-Reach
    # invocation) is used here rather than runtime_total_sec, which for any
    # enable_phase_b=True config also contains a diagnostic Phase-A-only rerun
    # (used only to compute permutation_distance_vs_p1) and is not the cost of
    # a single OURS-Reach call. See run_reviewer_ablation.py / _add_runtime_
    # algorithm_sec in analyze_reviewer_ablation.py.
    fig, ax = plt.subplots(figsize=(5.2, 3.4))
    ax.scatter(nf["m"], nf["runtime_algorithm_sec"], s=18, alpha=0.75, c="#1f4e79")
    finance_m = 1_729_225
    ax.axvline(finance_m, color="#b22222", ls="--", lw=1)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Directed edges m (log)")
    ax.set_ylabel("OURS-Reach algorithm time (s, log)")
    # No embedded title: the manuscript's Figure 1 caption already states this.
    # No legend: with a single scatter series (identified by the y-axis label
    # and caption) and one reference line, a legend box positioned anywhere
    # near the right edge of the axes would sit immediately against -- or be
    # visually cut by -- the near-edge Finance dashed line. The Finance
    # boundary is instead labeled directly on the line itself.
    ymin, ymax = ax.get_ylim()
    ax.annotate(
        "Finance\n$m\\approx1.73\\times10^{6}$",
        xy=(finance_m, ymax), xycoords="data",
        xytext=(-6, -6), textcoords="offset points",
        ha="right", va="top", fontsize=7.5, color="#b22222",
    )
    ax.grid(True, which="both", ls=":", alpha=0.4)
    fig.tight_layout()
    fig.savefig(FIG / "fig_runtime_vs_edges.pdf", bbox_inches="tight")
    fig.savefig(FIG / "fig_runtime_vs_edges.png", dpi=150, bbox_inches="tight")
    plt.close()


def fig_structural_ablation() -> None:
    order = ["A0", "A1", "A2", "A3", "A4", "A5", "A6"]
    summ = pd.read_csv(AB / "structural_ablation_summary.csv")
    summ = summ[summ["config"].isin(order)].copy()
    summ["config"] = pd.Categorical(summ["config"], categories=order, ordered=True)
    summ = summ.sort_values("config")
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2))
    axes[0].plot(summ["config"].astype(str), summ["median_upset_simple"], "o-", color="#1f4e79")
    axes[0].set_ylabel("Median upset_simple (↓ better)")
    axes[0].set_title("Ranking metric")
    axes[1].plot(summ["config"].astype(str), summ["median_removed_final_weight"], "s-", color="#8b4513")
    axes[1].set_ylabel("Median removed weight (↓ better)")
    axes[1].set_title("Structural objective")
    for ax in axes:
        ax.set_xlabel("Config")
        ax.grid(True, ls=":", alpha=0.4)
    fig.suptitle("Structural ablation (unpaired medians; paired tests authoritative)", fontsize=10)
    fig.tight_layout()
    fig.savefig(FIG / "fig_structural_ablation.pdf", bbox_inches="tight")
    fig.savefig(FIG / "fig_structural_ablation.png", dpi=150, bbox_inches="tight")
    plt.close()


if __name__ == "__main__":
    fig_runtime_vs_edges()
    fig_structural_ablation()
    print("wrote", sorted(p.name for p in FIG.iterdir()))
