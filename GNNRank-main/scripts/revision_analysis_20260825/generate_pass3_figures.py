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


def _matched_medians(sa: pd.DataFrame, configs: list[str]) -> pd.DataFrame:
    """Medians on the exact common-completion dataset set shared by configs."""
    sets = []
    for c in configs:
        sub = sa[(sa["config"] == c) & (sa["status"] == "complete")]
        sets.append(set(sub["dataset"].astype(str)))
    common = set.intersection(*sets) if sets else set()
    rows = []
    for c in configs:
        sub = sa[(sa["config"] == c) & (sa["dataset"].astype(str).isin(common))].copy()
        rows.append(
            {
                "config": c,
                "n_datasets": int(sub["dataset"].nunique()),
                "median_upset_simple": float(sub["upset_simple"].median()),
                "median_removed_final_weight": float(sub["removed_final_weight"].median()),
                "median_runtime_algorithm_sec": float(sub["runtime_algorithm_sec"].median()),
            }
        )
    return pd.DataFrame(rows)


def fig_structural_ablation() -> None:
    """Two matched-support panels (analogous to Table 8); A5/A6 omitted.

    A continuous A0–A6 median trajectory mixes n=33 (legacy) and n=77
    (canonical) supports and would present dataset-composition changes as
    stage effects. Panel (a)/(b) each use one exact common-completion set.
    Optional min-cut configs A5/A6 are excluded from this trajectory figure
    because their support/purpose differs; their structural paired tests are
    in Table 7.
    """
    sa = pd.read_csv(AB / "structural_ablation.csv")
    legacy = _matched_medians(sa, ["A0", "A1", "A3"])
    canon = _matched_medians(sa, ["A0", "A2", "A4"])

    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.3), sharey=False)
    panel_specs = [
        (axes[0], legacy, "Panel (a): legacy fixed-topo/INS (common $n=33$)"),
        (axes[1], canon, "Panel (b): canonical reachability (common $n=77$)"),
    ]
    for ax, df, title in panel_specs:
        xs = list(df["config"].astype(str))
        ax.plot(xs, df["median_upset_simple"], "o-", color="#1f4e79", label="median upset_simple")
        ax.set_xlabel("Stage")
        ax.set_title(title, fontsize=9)
        ax.grid(True, ls=":", alpha=0.4)
        ax.set_ylabel("Median upset_simple (↓ better)")
        ax2 = ax.twinx()
        ax2.plot(
            xs,
            df["median_removed_final_weight"],
            "s--",
            color="#8b4513",
            alpha=0.85,
            label="median removed weight",
        )
        ax2.set_ylabel("Median removed weight (↓ better)", fontsize=8, color="#8b4513")
        ax2.tick_params(axis="y", labelsize=8, colors="#8b4513")

    fig.suptitle(
        "Matched-support stage ablation (unpaired medians; paired tests in Table 7)",
        fontsize=10,
    )
    fig.tight_layout()
    fig.savefig(FIG / "fig_structural_ablation.pdf", bbox_inches="tight")
    fig.savefig(FIG / "fig_structural_ablation.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("legacy support", int(legacy["n_datasets"].iloc[0]), legacy.to_dict("records"))
    print("canon support", int(canon["n_datasets"].iloc[0]), canon.to_dict("records"))


if __name__ == "__main__":
    fig_runtime_vs_edges()
    fig_structural_ablation()
    print("wrote", sorted(p.name for p in FIG.iterdir()))
