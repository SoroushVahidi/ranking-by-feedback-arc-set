#!/usr/bin/env python3
"""
Compute all numeric claims for § Contribution and Practical Advantages
from paper_csv/unified_comparison.csv. Uses only rows where OURS exists (77 datasets).
Outputs: contribution_report.md and paper_csv/contribution_stats.csv
"""

import math
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
UNIFIED_CSV = REPO_ROOT / "paper_csv" / "unified_comparison.csv"
OUT_CSV = REPO_ROOT / "paper_csv" / "contribution_stats.csv"
OUT_MD = REPO_ROOT / "paper_csv" / "contribution_report.md"

TIE_1e6 = 1e-6
TIE_1e3 = 1e-3


def family_tag(dataset: str) -> str:
    if dataset.startswith("Basketball_temporal/finer"):
        return "basketball_temporal_finer"
    if dataset.startswith("Basketball_temporal/"):
        return "basketball_temporal"
    if dataset.startswith("Football_data_England_Premier_League/finer"):
        return "football_finer"
    if dataset.startswith("Football_data_England_Premier_League/"):
        return "football"
    if "FacultyHiringNetworks" in dataset:
        return "faculty"
    if dataset == "Dryad_animal_society":
        return "animal"
    if "Halo2BetaData" in dataset or "HeadToHead" in dataset:
        return "headtohead"
    if dataset == "finance":
        return "finance"
    return "other"


def compare(a: float, b: float, tie_tol: float) -> str:
    if not (math.isfinite(a) and math.isfinite(b)):
        return "skip"
    diff = a - b
    if abs(diff) <= tie_tol:
        return "tie"
    return "win" if a < b else "loss"


def wtl(ours: pd.Series, best: pd.Series, tie_tol: float) -> tuple:
    w = t = l = 0
    for o, b in zip(ours, best):
        c = compare(o, b, tie_tol)
        if c == "win": w += 1
        elif c == "tie": t += 1
        elif c == "loss": l += 1
    return w, t, l


def main():
    df = pd.read_csv(UNIFIED_CSV)
    # Only rows where OURS metrics exist
    df = df.dropna(subset=["ours_upset_simple"]).copy()
    n = len(df)
    assert n == 77, f"Expected 77 datasets with OURS, got {n}"

    # Gaps vs classical
    df["gap_simple_vs_cl"] = df["ours_upset_simple"] - df["best_classical_upset_simple"]
    df["gap_ratio_vs_cl"] = df["ours_upset_ratio"] - df["best_classical_upset_ratio"]
    df["rel_gap_simple_vs_cl"] = df["gap_simple_vs_cl"] / df["best_classical_upset_simple"].replace(0, np.nan)
    df["rel_gap_ratio_vs_cl"] = df["gap_ratio_vs_cl"] / df["best_classical_upset_ratio"].replace(0, np.nan)

    # Gaps vs GNN
    df["gap_simple_vs_gnn"] = df["ours_upset_simple"] - df["best_gnn_upset_simple"]
    df["gap_ratio_vs_gnn"] = df["ours_upset_ratio"] - df["best_gnn_upset_ratio"]
    df["rel_gap_simple_vs_gnn"] = df["gap_simple_vs_gnn"] / df["best_gnn_upset_simple"].replace(0, np.nan)
    df["rel_gap_ratio_vs_gnn"] = df["gap_ratio_vs_gnn"] / df["best_gnn_upset_ratio"].replace(0, np.nan)

    records = []
    def add(key, value, section=""):
        records.append({"section": section, "metric": key, "value": value})

    # --- A) OURS vs best classical ---
    df_cl = df.dropna(subset=["ours_upset_simple", "best_classical_upset_simple"])
    n_cl = len(df_cl)

    w_s_1e6, t_s_1e6, l_s_1e6 = wtl(df_cl["ours_upset_simple"], df_cl["best_classical_upset_simple"], TIE_1e6)
    w_s_1e3, t_s_1e3, l_s_1e3 = wtl(df_cl["ours_upset_simple"], df_cl["best_classical_upset_simple"], TIE_1e3)
    add("vs_classical_upset_simple_W_1e6", w_s_1e6, "A")
    add("vs_classical_upset_simple_T_1e6", t_s_1e6, "A")
    add("vs_classical_upset_simple_L_1e6", l_s_1e6, "A")
    add("vs_classical_upset_simple_W_1e3", w_s_1e3, "A")
    add("vs_classical_upset_simple_T_1e3", t_s_1e3, "A")
    add("vs_classical_upset_simple_L_1e3", l_s_1e3, "A")

    gs_cl = df_cl["gap_simple_vs_cl"].dropna()
    rgs_cl = df_cl["rel_gap_simple_vs_cl"].dropna()
    for name, s in [("gap_simple_vs_cl", gs_cl), ("rel_gap_simple_vs_cl", rgs_cl)]:
        if len(s):
            add(f"{name}_median", float(s.median()), "A")
            add(f"{name}_mean", float(s.mean()), "A")
            add(f"{name}_P25", float(s.quantile(0.25)), "A")
            add(f"{name}_P75", float(s.quantile(0.75)), "A")
            add(f"{name}_P90", float(s.quantile(0.90)), "A")
            add(f"{name}_max", float(s.max()), "A")

    # near-best vs classical (upset_simple)
    rgs = df_cl["rel_gap_simple_vs_cl"].dropna()
    add("vs_classical_within_1pct", int((rgs <= 0.01).sum()), "A")
    add("vs_classical_within_5pct", int((rgs <= 0.05).sum()), "A")
    add("vs_classical_within_10pct", int((rgs <= 0.10).sum()), "A")
    add("vs_classical_ours_better", int((rgs < -1e-6).sum()), "A")

    # A) upset_ratio vs classical
    w_r_1e6, t_r_1e6, l_r_1e6 = wtl(df_cl["ours_upset_ratio"], df_cl["best_classical_upset_ratio"], TIE_1e6)
    w_r_1e3, t_r_1e3, l_r_1e3 = wtl(df_cl["ours_upset_ratio"], df_cl["best_classical_upset_ratio"], TIE_1e3)
    add("vs_classical_upset_ratio_W_1e6", w_r_1e6, "A")
    add("vs_classical_upset_ratio_T_1e6", t_r_1e6, "A")
    add("vs_classical_upset_ratio_L_1e6", l_r_1e6, "A")
    add("vs_classical_upset_ratio_W_1e3", w_r_1e3, "A")
    add("vs_classical_upset_ratio_T_1e3", t_r_1e3, "A")
    add("vs_classical_upset_ratio_L_1e3", l_r_1e3, "A")

    gr_cl = df_cl["gap_ratio_vs_cl"].dropna()
    rgr_cl = df_cl["rel_gap_ratio_vs_cl"].dropna()
    for name, s in [("gap_ratio_vs_cl", gr_cl), ("rel_gap_ratio_vs_cl", rgr_cl)]:
        if len(s):
            add(f"{name}_median", float(s.median()), "A")
            add(f"{name}_mean", float(s.mean()), "A")
            add(f"{name}_P25", float(s.quantile(0.25)), "A")
            add(f"{name}_P75", float(s.quantile(0.75)), "A")
            add(f"{name}_P90", float(s.quantile(0.90)), "A")
            add(f"{name}_max", float(s.max()), "A")
    rgr = df_cl["rel_gap_ratio_vs_cl"].dropna()
    add("vs_classical_ratio_within_1pct", int((rgr <= 0.01).sum()), "A")
    add("vs_classical_ratio_within_5pct", int((rgr <= 0.05).sum()), "A")
    add("vs_classical_ratio_within_10pct", int((rgr <= 0.10).sum()), "A")
    add("vs_classical_ratio_ours_better", int((rgr < -1e-6).sum()), "A")

    # --- B) OURS vs best GNN ---
    df_gnn = df.dropna(subset=["ours_upset_simple", "best_gnn_upset_simple"])
    n_gnn = len(df_gnn)

    w_s_1e6, t_s_1e6, l_s_1e6 = wtl(df_gnn["ours_upset_simple"], df_gnn["best_gnn_upset_simple"], TIE_1e6)
    w_s_1e3, t_s_1e3, l_s_1e3 = wtl(df_gnn["ours_upset_simple"], df_gnn["best_gnn_upset_simple"], TIE_1e3)
    add("vs_gnn_upset_simple_W_1e6", w_s_1e6, "B")
    add("vs_gnn_upset_simple_T_1e6", t_s_1e6, "B")
    add("vs_gnn_upset_simple_L_1e6", l_s_1e6, "B")
    add("vs_gnn_upset_simple_W_1e3", w_s_1e3, "B")
    add("vs_gnn_upset_simple_T_1e3", t_s_1e3, "B")
    add("vs_gnn_upset_simple_L_1e3", l_s_1e3, "B")

    gs_gnn = df_gnn["gap_simple_vs_gnn"].dropna()
    rgs_gnn = df_gnn["rel_gap_simple_vs_gnn"].dropna()
    for name, s in [("gap_simple_vs_gnn", gs_gnn), ("rel_gap_simple_vs_gnn", rgs_gnn)]:
        if len(s):
            add(f"{name}_median", float(s.median()), "B")
            add(f"{name}_mean", float(s.mean()), "B")
            add(f"{name}_P25", float(s.quantile(0.25)), "B")
            add(f"{name}_P75", float(s.quantile(0.75)), "B")
            add(f"{name}_P90", float(s.quantile(0.90)), "B")
            add(f"{name}_max", float(s.max()), "B")
    rgs_g = df_gnn["rel_gap_simple_vs_gnn"].dropna()
    add("vs_gnn_within_1pct", int((rgs_g <= 0.01).sum()), "B")
    add("vs_gnn_within_5pct", int((rgs_g <= 0.05).sum()), "B")
    add("vs_gnn_within_10pct", int((rgs_g <= 0.10).sum()), "B")
    add("vs_gnn_ours_better", int((rgs_g < -1e-6).sum()), "B")

    w_r_1e6, t_r_1e6, l_r_1e6 = wtl(df_gnn["ours_upset_ratio"], df_gnn["best_gnn_upset_ratio"], TIE_1e6)
    w_r_1e3, t_r_1e3, l_r_1e3 = wtl(df_gnn["ours_upset_ratio"], df_gnn["best_gnn_upset_ratio"], TIE_1e3)
    add("vs_gnn_upset_ratio_W_1e6", w_r_1e6, "B")
    add("vs_gnn_upset_ratio_T_1e6", t_r_1e6, "B")
    add("vs_gnn_upset_ratio_L_1e6", l_r_1e6, "B")
    add("vs_gnn_upset_ratio_W_1e3", w_r_1e3, "B")
    add("vs_gnn_upset_ratio_T_1e3", t_r_1e3, "B")
    add("vs_gnn_upset_ratio_L_1e3", l_r_1e3, "B")

    gr_gnn = df_gnn["gap_ratio_vs_gnn"].dropna()
    rgr_gnn = df_gnn["rel_gap_ratio_vs_gnn"].dropna()
    for name, s in [("gap_ratio_vs_gnn", gr_gnn), ("rel_gap_ratio_vs_gnn", rgr_gnn)]:
        if len(s):
            add(f"{name}_median", float(s.median()), "B")
            add(f"{name}_mean", float(s.mean()), "B")
            add(f"{name}_P25", float(s.quantile(0.25)), "B")
            add(f"{name}_P75", float(s.quantile(0.75)), "B")
            add(f"{name}_P90", float(s.quantile(0.90)), "B")
            add(f"{name}_max", float(s.max()), "B")
    rgr_g = df_gnn["rel_gap_ratio_vs_gnn"].dropna()
    add("vs_gnn_ratio_within_1pct", int((rgr_g <= 0.01).sum()), "B")
    add("vs_gnn_ratio_within_5pct", int((rgr_g <= 0.05).sum()), "B")
    add("vs_gnn_ratio_within_10pct", int((rgr_g <= 0.10).sum()), "B")
    add("vs_gnn_ratio_ours_better", int((rgr_g < -1e-6).sum()), "B")

    # --- C) Tail diagnosis ---
    df_gnn_copy = df_gnn.copy()
    df_gnn_copy["family"] = df_gnn_copy["dataset"].apply(family_tag)
    top20_gnn = df_gnn_copy.nlargest(20, "rel_gap_simple_vs_gnn")[["dataset", "family", "rel_gap_simple_vs_gnn", "ours_upset_simple", "best_gnn_upset_simple"]]
    top10_cl = df_cl.copy()
    top10_cl["family"] = top10_cl["dataset"].apply(family_tag)
    top10_cl = top10_cl.nlargest(10, "rel_gap_simple_vs_cl")[["dataset", "family", "rel_gap_simple_vs_cl", "ours_upset_simple", "best_classical_upset_simple"]]

    # --- D) Runtime ---
    df_rt = df.dropna(subset=["ours_runtime_sec", "best_gnn_runtime_sec"])
    df_rt = df_rt[df_rt["ours_runtime_sec"] > 0]
    df_rt = df_rt.copy()
    df_rt["speedup"] = df_rt["best_gnn_runtime_sec"] / df_rt["ours_runtime_sec"]
    n_rt = len(df_rt)
    add("runtime_count", n_rt, "D")
    if n_rt:
        sp = df_rt["speedup"]
        add("speedup_P25", float(sp.quantile(0.25)), "D")
        add("speedup_median", float(sp.median()), "D")
        add("speedup_P75", float(sp.quantile(0.75)), "D")
        add("speedup_mean", float(sp.mean()), "D")
        add("speedup_ge10x", int((sp >= 10).sum()), "D")
        add("speedup_ge50x", int((sp >= 50).sum()), "D")
        add("speedup_ge100x", int((sp >= 100).sum()), "D")

    # Pareto (upset_simple): better = ours < best_gnn (by 1e-6), faster = ours_runtime < best_gnn_runtime
    df_p = df_gnn.dropna(subset=["ours_runtime_sec", "best_gnn_runtime_sec"]).copy()
    df_p = df_p[df_p["ours_runtime_sec"] > 0]
    better = (df_p["ours_upset_simple"] - df_p["best_gnn_upset_simple"]) < -TIE_1e6
    worse = (df_p["ours_upset_simple"] - df_p["best_gnn_upset_simple"]) > TIE_1e6
    faster = df_p["ours_runtime_sec"] < df_p["best_gnn_runtime_sec"]
    slower = df_p["ours_runtime_sec"] > df_p["best_gnn_runtime_sec"]
    add("Pareto_better_faster", int((better & faster).sum()), "D")
    add("Pareto_better_slower", int((better & slower).sum()), "D")
    add("Pareto_worse_faster", int((worse & faster).sum()), "D")
    add("Pareto_worse_slower", int((worse & slower).sum()), "D")

    # Save CSV
    stats_df = pd.DataFrame(records)
    stats_df.to_csv(OUT_CSV, index=False)
    print(f"Wrote {OUT_CSV}")

    # Build lookup for report
    stats = {r["metric"]: r["value"] for r in records}

    # Markdown report
    md = []
    md.append("# Contribution and Practical Advantages — Numeric Claims")
    md.append("")
    md.append("Source: `paper_csv/unified_comparison.csv` (77 datasets with OURS).")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## A) OURS vs best classical")
    md.append("")
    md.append("### Upset simple")
    md.append(f"- **W/T/L** (tie 1e-6): {stats['vs_classical_upset_simple_W_1e6']} / {stats['vs_classical_upset_simple_T_1e6']} / {stats['vs_classical_upset_simple_L_1e6']}  (n={n_cl})")
    md.append(f"- **W/T/L** (tie 1e-3): {stats['vs_classical_upset_simple_W_1e3']} / {stats['vs_classical_upset_simple_T_1e3']} / {stats['vs_classical_upset_simple_L_1e3']}")
    md.append(f"- **gap_simple**: median = {stats['gap_simple_vs_cl_median']:.6f}, mean = {stats['gap_simple_vs_cl_mean']:.6f}, P25 = {stats['gap_simple_vs_cl_P25']:.6f}, P75 = {stats['gap_simple_vs_cl_P75']:.6f}, P90 = {stats['gap_simple_vs_cl_P90']:.6f}, max = {stats['gap_simple_vs_cl_max']:.6f}")
    md.append(f"- **rel_gap_simple**: median = {stats['rel_gap_simple_vs_cl_median']:.6f}, mean = {stats['rel_gap_simple_vs_cl_mean']:.6f}, P25 = {stats['rel_gap_simple_vs_cl_P25']:.6f}, P75 = {stats['rel_gap_simple_vs_cl_P75']:.6f}, P90 = {stats['rel_gap_simple_vs_cl_P90']:.6f}, max = {stats['rel_gap_simple_vs_cl_max']:.6f}")
    md.append(f"- **Near-best**: within 1% = {stats['vs_classical_within_1pct']}, within 5% = {stats['vs_classical_within_5pct']}, within 10% = {stats['vs_classical_within_10pct']}; **OURS better** (rel_gap < −1e-6) = {stats['vs_classical_ours_better']}")
    md.append("")
    md.append("### Upset ratio")
    md.append(f"- **W/T/L** (1e-6): {stats['vs_classical_upset_ratio_W_1e6']} / {stats['vs_classical_upset_ratio_T_1e6']} / {stats['vs_classical_upset_ratio_L_1e6']}")
    md.append(f"- **W/T/L** (1e-3): {stats['vs_classical_upset_ratio_W_1e3']} / {stats['vs_classical_upset_ratio_T_1e3']} / {stats['vs_classical_upset_ratio_L_1e3']}")
    md.append(f"- **gap_ratio**: median = {stats['gap_ratio_vs_cl_median']:.6f}, mean = {stats['gap_ratio_vs_cl_mean']:.6f}, P25 = {stats['gap_ratio_vs_cl_P25']:.6f}, P75 = {stats['gap_ratio_vs_cl_P75']:.6f}, P90 = {stats['gap_ratio_vs_cl_P90']:.6f}, max = {stats['gap_ratio_vs_cl_max']:.6f}")
    md.append(f"- **rel_gap_ratio**: median = {stats['rel_gap_ratio_vs_cl_median']:.6f}, mean = {stats['rel_gap_ratio_vs_cl_mean']:.6f}, P25 = {stats['rel_gap_ratio_vs_cl_P25']:.6f}, P75 = {stats['rel_gap_ratio_vs_cl_P75']:.6f}, P90 = {stats['rel_gap_ratio_vs_cl_P90']:.6f}, max = {stats['rel_gap_ratio_vs_cl_max']:.6f}")
    md.append(f"- **Near-best**: within 1% = {stats['vs_classical_ratio_within_1pct']}, within 5% = {stats['vs_classical_ratio_within_5pct']}, within 10% = {stats['vs_classical_ratio_within_10pct']}; **OURS better** = {stats['vs_classical_ratio_ours_better']}")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## B) OURS vs best GNN")
    md.append("")
    md.append("### Upset simple")
    md.append(f"- **W/T/L** (1e-6): {stats['vs_gnn_upset_simple_W_1e6']} / {stats['vs_gnn_upset_simple_T_1e6']} / {stats['vs_gnn_upset_simple_L_1e6']}  (n={n_gnn})")
    md.append(f"- **W/T/L** (1e-3): {stats['vs_gnn_upset_simple_W_1e3']} / {stats['vs_gnn_upset_simple_T_1e3']} / {stats['vs_gnn_upset_simple_L_1e3']}")
    md.append(f"- **gap_simple**: median = {stats['gap_simple_vs_gnn_median']:.6f}, mean = {stats['gap_simple_vs_gnn_mean']:.6f}, P25 = {stats['gap_simple_vs_gnn_P25']:.6f}, P75 = {stats['gap_simple_vs_gnn_P75']:.6f}, P90 = {stats['gap_simple_vs_gnn_P90']:.6f}, max = {stats['gap_simple_vs_gnn_max']:.6f}")
    md.append(f"- **rel_gap_simple**: median = {stats['rel_gap_simple_vs_gnn_median']:.6f}, mean = {stats['rel_gap_simple_vs_gnn_mean']:.6f}, P25 = {stats['rel_gap_simple_vs_gnn_P25']:.6f}, P75 = {stats['rel_gap_simple_vs_gnn_P75']:.6f}, P90 = {stats['rel_gap_simple_vs_gnn_P90']:.6f}, max = {stats['rel_gap_simple_vs_gnn_max']:.6f}")
    md.append(f"- **Near-best**: within 1% = {stats['vs_gnn_within_1pct']}, within 5% = {stats['vs_gnn_within_5pct']}, within 10% = {stats['vs_gnn_within_10pct']}; **OURS better** = {stats['vs_gnn_ours_better']}")
    md.append("")
    md.append("### Upset ratio")
    md.append(f"- **W/T/L** (1e-6): {stats['vs_gnn_upset_ratio_W_1e6']} / {stats['vs_gnn_upset_ratio_T_1e6']} / {stats['vs_gnn_upset_ratio_L_1e6']}")
    md.append(f"- **W/T/L** (1e-3): {stats['vs_gnn_upset_ratio_W_1e3']} / {stats['vs_gnn_upset_ratio_T_1e3']} / {stats['vs_gnn_upset_ratio_L_1e3']}")
    md.append(f"- **gap_ratio**: median = {stats['gap_ratio_vs_gnn_median']:.6f}, mean = {stats['gap_ratio_vs_gnn_mean']:.6f}, P25 = {stats['gap_ratio_vs_gnn_P25']:.6f}, P75 = {stats['gap_ratio_vs_gnn_P75']:.6f}, P90 = {stats['gap_ratio_vs_gnn_P90']:.6f}, max = {stats['gap_ratio_vs_gnn_max']:.6f}")
    md.append(f"- **rel_gap_ratio**: median = {stats['rel_gap_ratio_vs_gnn_median']:.6f}, mean = {stats['rel_gap_ratio_vs_gnn_mean']:.6f}, P25 = {stats['rel_gap_ratio_vs_gnn_P25']:.6f}, P75 = {stats['rel_gap_ratio_vs_gnn_P75']:.6f}, P90 = {stats['rel_gap_ratio_vs_gnn_P90']:.6f}, max = {stats['rel_gap_ratio_vs_gnn_max']:.6f}")
    md.append(f"- **Near-best**: within 1% = {stats['vs_gnn_ratio_within_1pct']}, within 5% = {stats['vs_gnn_ratio_within_5pct']}, within 10% = {stats['vs_gnn_ratio_within_10pct']}; **OURS better** = {stats['vs_gnn_ratio_ours_better']}")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## C) Tail diagnosis")
    md.append("")
    md.append("### Top 20 datasets — largest rel_gap_simple vs best GNN (OURS worse)")
    md.append("")
    md.append("| # | dataset | family | rel_gap_simple | ours | best_gnn |")
    md.append("|---|--------|--------|----------------|------|----------|")
    for i, (_, r) in enumerate(top20_gnn.iterrows(), 1):
        md.append(f"| {i} | {r['dataset']} | {r['family']} | {r['rel_gap_simple_vs_gnn']:.6f} | {r['ours_upset_simple']:.4f} | {r['best_gnn_upset_simple']:.4f} |")
    md.append("")
    md.append("### Top 10 datasets — largest rel_gap_simple vs best classical")
    md.append("")
    md.append("| # | dataset | family | rel_gap_simple | ours | best_classical |")
    md.append("|---|--------|--------|----------------|------|----------------|")
    for i, (_, r) in enumerate(top10_cl.iterrows(), 1):
        md.append(f"| {i} | {r['dataset']} | {r['family']} | {r['rel_gap_simple_vs_cl']:.6f} | {r['ours_upset_simple']:.4f} | {r['best_classical_upset_simple']:.4f} |")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## D) Runtime and Pareto")
    md.append("")
    md.append(f"- **Speedup** (best_gnn_runtime / ours_runtime): n = {stats['runtime_count']}")
    if n_rt:
        md.append(f"  - P25 = {stats['speedup_P25']:.2f}, median = {stats['speedup_median']:.2f}, P75 = {stats['speedup_P75']:.2f}, mean = {stats['speedup_mean']:.2f}")
        md.append(f"  - Counts: ≥10× = {stats['speedup_ge10x']}, ≥50× = {stats['speedup_ge50x']}, ≥100× = {stats['speedup_ge100x']}")
    md.append("")
    md.append("**Pareto (upset_simple vs best GNN, tie 1e-6):**")
    md.append(f"- Better & faster: {stats['Pareto_better_faster']}")
    md.append(f"- Better but slower: {stats['Pareto_better_slower']}")
    md.append(f"- Worse but faster: {stats['Pareto_worse_faster']}")
    md.append(f"- Worse & slower: {stats['Pareto_worse_slower']}")

    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
