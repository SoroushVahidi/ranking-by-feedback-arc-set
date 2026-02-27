#!/usr/bin/env python3
"""
Delta explanation: Mode A (paper-style season-averaged) vs Mode B (per-dataset).

Data sources (repo artifacts only):
  - full_833614_metrics_best.csv: OURS_MFAS_INS3 + classical baselines (all datasets)
  - paper_csv/results_table.csv: DIGRACib for Dryad_animal_society, finance only

No GNN per-season data exists for basketball/football in the repo, so OURS vs GNN
Mode A vs B cannot be computed for those. We compute:
  1) OURS vs best-classical in Mode A and Mode B for basketball (30) and football (6).
  2) OURS vs DIGRACib for the 2 datasets that have GNN (Mode A = Mode B there).
  3) Top 10 datasets (seasons) where the winner OURS vs best-classical flips
     between Mode A (sport-level average) and Mode B (per-season).

Tie tolerance: 1e-6 for all metrics (as requested).
"""

from pathlib import Path
import math

import pandas as pd

HERE = Path(__file__).resolve().parent
FULL_CSV = HERE / "full_833614_metrics_best.csv"
RESULTS_TABLE_CSV = HERE / "paper_csv" / "results_table.csv"
TIE_TOL = 1e-6

OURS_METHOD = "OURS_MFAS_INS3"
CLASSICAL = [
    "SpringRank", "syncRank", "serialRank", "btl", "davidScore",
    "eigenvectorCentrality", "PageRank", "rankCentrality", "SVD_RS", "SVD_NRS",
]

# Basketball: 30 seasons (1985-2014), dataset names Basketball_temporal/YYYY
BASKETBALL_PREFIX = "Basketball_temporal/"
BASKETBALL_SEASONS = [f"{BASKETBALL_PREFIX}{y}" for y in range(1985, 2015)]
# Football: 6 seasons
FOOTBALL_DATASETS = [
    "Football_data_England_Premier_League/England_2009_2010",
    "Football_data_England_Premier_League/England_2010_2011",
    "Football_data_England_Premier_League/England_2011_2012",
    "Football_data_England_Premier_League/England_2012_2013",
    "Football_data_England_Premier_League/England_2013_2014",
    "Football_data_England_Premier_League/England_2014_2015",
]


def parse_float(x):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return None
    try:
        return float(x)
    except (ValueError, TypeError):
        return None


def compare(ours_val, other_val, tie_tol=TIE_TOL):
    """Return 'win' | 'tie' | 'loss' | None. Lower is better."""
    o = parse_float(ours_val)
    b = parse_float(other_val)
    if o is None or b is None:
        return None
    if not (math.isfinite(o) and math.isfinite(b)):
        return None
    diff = o - b
    if abs(diff) <= tie_tol:
        return "tie"
    return "win" if o < b else "loss"


def main():
    df = pd.read_csv(FULL_CSV)
    df_rt = pd.read_csv(RESULTS_TABLE_CSV)
    gnn_rows = df_rt[(df_rt["method"] == "DIGRACib") & (df_rt["which"] == "upset")]

    ours = df[df["method"] == OURS_METHOD].set_index("dataset")
    classical = df[df["method"].isin(CLASSICAL)]

    # Best classical per dataset (min upset_simple, etc.)
    best_classical = classical.groupby("dataset").agg(
        upset_simple_mean=("upset_simple_mean", "min"),
        upset_ratio_mean=("upset_ratio_mean", "min"),
    ).rename(columns={"upset_simple_mean": "best_classical_upset_simple", "upset_ratio_mean": "best_classical_upset_ratio"})

    # ------ Mode B: per-dataset (current repo style) ------
    common = ours.index.intersection(best_classical.index)
    records_b = []
    for ds in common:
        ours_row = ours.loc[ds]
        cl_row = best_classical.loc[ds]
        us = parse_float(ours_row["upset_simple_mean"])
        ur = parse_float(ours_row["upset_ratio_mean"])
        cs = parse_float(cl_row["best_classical_upset_simple"])
        cr = parse_float(cl_row["best_classical_upset_ratio"])
        if us is None or cs is None:
            continue
        res_s = compare(us, cs)
        res_r = compare(ur, cr) if (ur is not None and cr is not None) else None
        records_b.append({
            "dataset": ds,
            "ours_upset_simple": us,
            "ours_upset_ratio": ur,
            "best_classical_upset_simple": cs,
            "best_classical_upset_ratio": cr,
            "result_simple": res_s,
            "result_ratio": res_r,
            "gap_simple": us - cs,
            "gap_ratio": (ur - cr) if (ur is not None and cr is not None) else None,
        })
    df_b = pd.DataFrame(records_b)

    # ------ Mode A: season-averaged for basketball and football ------
    def season_average(datasets, ours_df, best_cl_df):
        o_list = []
        c_s_list = []
        c_r_list = []
        for ds in datasets:
            if ds not in ours_df.index or ds not in best_cl_df.index:
                continue
            o_list.append(ours_df.loc[ds])
            c_s_list.append(best_cl_df.loc[ds]["best_classical_upset_simple"])
            c_r_list.append(best_cl_df.loc[ds]["best_classical_upset_ratio"])
        if not o_list:
            return None, None, None, None
        import numpy as np
        ours_avg_s = np.nanmean([parse_float(r["upset_simple_mean"]) for r in o_list])
        ours_avg_r = np.nanmean([parse_float(r["upset_ratio_mean"]) for r in o_list])
        cl_avg_s = np.nanmean([parse_float(x) for x in c_s_list])
        cl_avg_r = np.nanmean([parse_float(x) for x in c_r_list])
        return ours_avg_s, ours_avg_r, cl_avg_s, cl_avg_r

    mode_a_results = []
    for sport_name, datasets in [("Basketball_30", BASKETBALL_SEASONS), ("Football_6", FOOTBALL_DATASETS)]:
        o_s, o_r, c_s, c_r = season_average(datasets, ours, best_classical)
        if o_s is None:
            continue
        res_s = compare(o_s, c_s)
        res_r = compare(o_r, c_r)
        mode_a_results.append({
            "sport": sport_name,
            "ours_upset_simple": o_s,
            "ours_upset_ratio": o_r,
            "best_classical_upset_simple": c_s,
            "best_classical_upset_ratio": c_r,
            "result_simple": res_s,
            "result_ratio": res_r,
            "gap_simple": o_s - c_s,
            "gap_ratio": o_r - c_r,
        })

    # ------ OURS vs DIGRACib (only 2 datasets) ------
    gnn_comparisons = []
    for _, r in gnn_rows.iterrows():
        ds = r["dataset"]
        if ds not in ours.index:
            continue
        g_s = parse_float(r["upset_simple_mean"])
        g_r = parse_float(r["upset_ratio_mean"])
        o_s = parse_float(ours.loc[ds]["upset_simple_mean"])
        o_r = parse_float(ours.loc[ds]["upset_ratio_mean"])
        res_s = compare(o_s, g_s)
        res_r = compare(o_r, g_r)
        gnn_comparisons.append({
            "dataset": ds,
            "result_simple": res_s,
            "result_ratio": res_r,
            "gap_simple": o_s - g_s if (o_s is not None and g_s is not None) else None,
            "gap_ratio": o_r - g_r if (o_r is not None and g_r is not None) else None,
        })

    # ------ Output ------
    print("=" * 60)
    print("DELTA: Mode A (season-averaged) vs Mode B (per-dataset)")
    print("Tie tolerance:", TIE_TOL)
    print("=" * 60)

    print("\n--- OURS vs best classical ---")
    print("\nMode B (per-dataset): all datasets with OURS + classical")
    if not df_b.empty:
        for metric, col in [("upset_simple", "result_simple"), ("upset_ratio", "result_ratio")]:
            w = (df_b[col] == "win").sum()
            t = (df_b[col] == "tie").sum()
            l = (df_b[col] == "loss").sum()
            n = w + t + l
            gap_col = "gap_simple" if metric == "upset_simple" else "gap_ratio"
            gaps = df_b[gap_col].dropna()
            print(f"  {metric}: wins={w} ties={t} losses={l} total={n}")
            if not gaps.empty:
                print(f"         median gap={gaps.median():.6f} mean gap={gaps.mean():.6f}")
    print("\nMode A (season-averaged): Basketball 30, Football 6")
    for row in mode_a_results:
        print(f"  {row['sport']}: upset_simple {row['result_simple']} (gap={row['gap_simple']:.6f}), upset_ratio {row['result_ratio']} (gap={row['gap_ratio']:.6f})")

    print("\n--- OURS vs best GNN (DIGRACib) ---")
    print("(GNN in results_table.csv: Dryad_animal_society, finance. finance has no OURS in full_833614_metrics_best.csv; Mode A = Mode B)")
    if gnn_comparisons:
        for g in gnn_comparisons:
            print(f"  {g['dataset']}: upset_simple {g['result_simple']}, upset_ratio {g['result_ratio']}, gap_simple={g['gap_simple']}, gap_ratio={g['gap_ratio']}")
        w_s = sum(1 for g in gnn_comparisons if g["result_simple"] == "win")
        l_s = sum(1 for g in gnn_comparisons if g["result_simple"] == "loss")
        t_s = sum(1 for g in gnn_comparisons if g["result_simple"] == "tie")
        w_r = sum(1 for g in gnn_comparisons if g["result_ratio"] == "win")
        l_r = sum(1 for g in gnn_comparisons if g["result_ratio"] == "loss")
        t_r = sum(1 for g in gnn_comparisons if g["result_ratio"] == "tie")
        gaps_s = [g["gap_simple"] for g in gnn_comparisons if g["gap_simple"] is not None]
        gaps_r = [g["gap_ratio"] for g in gnn_comparisons if g["gap_ratio"] is not None]
        print(f"  upset_simple: wins={w_s} ties={t_s} losses={l_s}; median gap={pd.Series(gaps_s).median():.6f} mean gap={pd.Series(gaps_s).mean():.6f}")
        print(f"  upset_ratio:  wins={w_r} ties={t_r} losses={l_r}; median gap={pd.Series(gaps_r).median():.6f} mean gap={pd.Series(gaps_r).mean():.6f}")
    else:
        print("  (no GNN data in results_table.csv for datasets that have OURS)")

    # ------ Top 10 datasets where Mode A vs Mode B flips the winner (OURS vs best classical) ------
    # For each sport, Mode A gives one outcome (win/tie/loss). For each season in that sport, Mode B gives an outcome.
    # "Flip" = season where Mode B outcome != Mode A outcome for that sport.
    print("\n--- Top 10 datasets (seasons) where winner flips between Mode A and Mode B (OURS vs best classical) ---")
    mode_a_by_sport = {r["sport"]: r for r in mode_a_results}
    flip_records = []
    for sport_name, datasets in [("Basketball_30", BASKETBALL_SEASONS), ("Football_6", FOOTBALL_DATASETS)]:
        res_a = mode_a_by_sport.get(sport_name)
        if res_a is None:
            continue
        res_a_s = res_a["result_simple"]
        res_a_r = res_a["result_ratio"]
        for ds in datasets:
            if ds not in df_b.set_index("dataset").index:
                continue
            row = df_b[df_b["dataset"] == ds].iloc[0]
            res_b_s = row["result_simple"]
            res_b_r = row["result_ratio"]
            flip_s = res_b_s != res_a_s
            flip_r = res_b_r != res_a_r
            if flip_s or flip_r:
                flip_records.append({
                    "dataset": ds,
                    "sport": sport_name,
                    "Mode_A_simple": res_a_s,
                    "Mode_B_simple": res_b_s,
                    "Mode_A_ratio": res_a_r,
                    "Mode_B_ratio": res_b_r,
                    "flip_simple": flip_s,
                    "flip_ratio": flip_r,
                    "gap_simple": row["gap_simple"],
                    "gap_ratio": row["gap_ratio"],
                })
    # Rank by absolute gap (so "biggest impact" flips first)
    if flip_records:
        flip_df = pd.DataFrame(flip_records)
        flip_df["abs_gap_simple"] = flip_df["gap_simple"].abs()
        top10 = flip_df.nlargest(10, "abs_gap_simple")
        for _, r in top10.iterrows():
            print(f"  {r['dataset']} ({r['sport']}): Mode_A simple={r['Mode_A_simple']} Mode_B simple={r['Mode_B_simple']} | ratio A={r['Mode_A_ratio']} B={r['Mode_B_ratio']} | gap_simple={r['gap_simple']:.6f}")
    else:
        print("  (no flips found: Mode A and Mode B agree for every season in basketball/football)")

    # Write summary CSV for reproducibility
    out_path = HERE / "delta_mode_a_vs_b_summary.csv"
    summary_rows = []
    summary_rows.append({"metric": "Mode_B_ours_vs_best_classical", "wins": (df_b["result_simple"] == "win").sum(), "ties": (df_b["result_simple"] == "tie").sum(), "losses": (df_b["result_simple"] == "loss").sum(), "median_gap_simple": df_b["gap_simple"].median(), "mean_gap_simple": df_b["gap_simple"].mean(), "median_gap_ratio": df_b["gap_ratio"].median(), "mean_gap_ratio": df_b["gap_ratio"].mean()})
    if mode_a_results:
        for row in mode_a_results:
            summary_rows.append({"metric": f"Mode_A_{row['sport']}", "result_simple": row["result_simple"], "result_ratio": row["result_ratio"], "gap_simple": row["gap_simple"], "gap_ratio": row["gap_ratio"]})
    if gnn_comparisons:
        summary_rows.append({"metric": "OURS_vs_DIGRACib", "wins_simple": sum(1 for g in gnn_comparisons if g["result_simple"] == "win"), "losses_simple": sum(1 for g in gnn_comparisons if g["result_simple"] == "loss"), "median_gap_simple": pd.Series([g["gap_simple"] for g in gnn_comparisons if g["gap_simple"] is not None]).median(), "mean_gap_simple": pd.Series([g["gap_simple"] for g in gnn_comparisons if g["gap_simple"] is not None]).mean()})
    pd.DataFrame(summary_rows).to_csv(out_path, index=False)
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
