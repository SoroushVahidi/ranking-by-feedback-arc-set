#!/usr/bin/env python3
"""
Generate manuscript-ready tables (CSV + LaTeX) from leaderboard CSVs.
No "best-of" as headline; per-method summary only.

Outputs under paper_tables/:
  - table1_main_leaderboard.csv / .tex
  - table2_compute_matched.csv / .tex
  - table3_missingness_audit.csv / .tex

Run from repo root: python tools/build_paper_tables.py
"""

from pathlib import Path
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
PAPER_CSV = REPO_ROOT / "paper_csv"
PAPER_TABLES = REPO_ROOT / "paper_tables"

LEADERBOARD = PAPER_CSV / "leaderboard_per_method.csv"
COMPUTE_MATCHED = PAPER_CSV / "leaderboard_compute_matched.csv"
COVERAGE = PAPER_CSV / "leaderboard_compute_matched_coverage.csv"
MISSINGNESS = PAPER_CSV / "missingness_audit.csv"

# Method family for display order
OURS_METHODS = {"OURS_MFAS", "OURS_MFAS_INS1", "OURS_MFAS_INS2", "OURS_MFAS_INS3"}
GNN_METHODS = {"DIGRAC", "ib", "DIGRACib"}
CLASSICAL_METHODS = {
    "SpringRank", "syncRank", "serialRank", "btl", "davidScore",
    "eigenvectorCentrality", "PageRank", "rankCentrality", "SVD_RS", "SVD_NRS", "mvr",
}


def method_family(m: str) -> str:
    if m in OURS_METHODS:
        return "OURS"
    if m in GNN_METHODS:
        return "GNN"
    if m in CLASSICAL_METHODS:
        return "classical"
    return "other"


def short_config(config: str, max_len: int = 20) -> str:
    if not config or pd.isna(config):
        return ""
    s = str(config).strip()
    if len(s) <= max_len:
        return s
    return s[: max_len - 3] + "..."


def build_summary_table(df: pd.DataFrame, total_datasets: int, table_label: str) -> pd.DataFrame:
    """One row per (method, config): median/mean upset_*, coverage."""
    df = df.dropna(subset=["upset_simple"]).copy()
    if df.empty:
        return pd.DataFrame()

    # Use method + config as key so each GNN config is separate
    df["_key"] = df["method"].astype(str) + "|" + df["config"].fillna("").astype(str)
    g = df.groupby("_key", as_index=False).agg(
        method=("method", "first"),
        config=("config", "first"),
        median_upset_simple=("upset_simple", "median"),
        mean_upset_simple=("upset_simple", "mean"),
        median_upset_ratio=("upset_ratio", "median"),
        mean_upset_ratio=("upset_ratio", "mean"),
        median_upset_naive=("upset_naive", "median"),
        mean_upset_naive=("upset_naive", "mean"),
        n_valid_upset_simple=("upset_simple", "count"),
    )
    g["coverage"] = g["n_valid_upset_simple"].astype(str) + " / " + str(total_datasets)
    g["method_family"] = g["method"].map(method_family)
    # Sort by median upset_simple ascending
    g = g.sort_values("median_upset_simple", ascending=True).reset_index(drop=True)
    return g


def df_to_latex_tabular(df: pd.DataFrame, caption: str, label: str, float_fmt: str = ".4f") -> str:
    """Produce a LaTeX tabular (no table env, so it can be used in longtable or table)."""
    cols = [c for c in df.columns if not c.startswith("_")]
    header = " & ".join([c.replace("_", " ").title() for c in cols]) + " \\\\"
    rows = []
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            if pd.isna(v):
                cells.append("---")
            elif isinstance(v, (int, np.integer)):
                cells.append(str(v))
            elif isinstance(v, float):
                cells.append(f"{v:{float_fmt}}")
            else:
                cells.append(str(v).replace("&", "\\&").replace("_", "\\_"))
        rows.append(" & ".join(cells) + " \\\\")
    body = "\n".join(rows)
    return (
        f"% {label}\n"
        f"\\begin{{tabular}}{{{'l' * len(cols)}}}\n"
        f"\\toprule\n{header}\n\\midrule\n{body}\n\\bottomrule\n\\end{{tabular}}\n"
        f"% caption: {caption}\n% label: {label}\n"
    )


def main():
    PAPER_TABLES.mkdir(parents=True, exist_ok=True)

    lb = pd.read_csv(LEADERBOARD)
    total_datasets = lb["dataset"].nunique()

    # Minimal provenance print so logs record exact inputs.
    print("[build_paper_tables] Inputs:")
    print(f"  LEADERBOARD={LEADERBOARD}")
    print(f"  COMPUTE_MATCHED={COMPUTE_MATCHED}")
    print(f"  COVERAGE={COVERAGE}")
    print(f"  MISSINGNESS={MISSINGNESS}")

    # ----- Table 1: Main per-method leaderboard -----
    t1 = build_summary_table(lb, total_datasets, "table1")
    cols_t1 = [
        "method", "config", "method_family",
        "median_upset_simple", "mean_upset_simple",
        "median_upset_ratio", "mean_upset_ratio",
        "median_upset_naive", "mean_upset_naive",
        "coverage",
    ]
    t1_out = t1[[c for c in cols_t1 if c in t1.columns]]
    t1_out.to_csv(PAPER_TABLES / "table1_main_leaderboard.csv", index=False)
    with open(PAPER_TABLES / "table1_main_leaderboard.tex", "w") as f:
        f.write(df_to_latex_tabular(
            t1_out,
            caption="Per-method leaderboard summary (median and mean upset metrics, coverage). Sorted by median upset\\_simple ascending.",
            label="tab:main-leaderboard",
        ))
    print(f"Wrote table1_main_leaderboard.csv and .tex ({len(t1_out)} rows)")

    # ----- Table 2: Compute-matched @1800s -----
    cm = pd.read_csv(COMPUTE_MATCHED)
    cov = pd.read_csv(COVERAGE)
    total_cm = cm["dataset"].nunique() if len(cm) else total_datasets
    t2 = build_summary_table(cm, total_cm, "table2")
    cols_t2 = [c for c in cols_t1 if c in t2.columns]
    t2_out = t2[cols_t2]
    t2_out.to_csv(PAPER_TABLES / "table2_compute_matched.csv", index=False)
    # Merge coverage (n_within_time_budget) into table2 note or separate row
    with open(PAPER_TABLES / "table2_compute_matched.tex", "w") as f:
        f.write(df_to_latex_tabular(
            t2_out,
            caption="Compute-matched summary (runtime $\\leq 1800$s). Per-method median/mean and coverage.",
            label="tab:compute-matched",
        ))
    cov.to_csv(PAPER_TABLES / "table2_coverage.csv", index=False)
    print(f"Wrote table2_compute_matched.csv, .tex, and table2_coverage.csv ({len(t2_out)} rows)")

    # ----- Table 3: Missingness / timeout audit -----
    audit = pd.read_csv(MISSINGNESS)
    audit["method_family"] = audit["method"].map(method_family)
    t3_per_method = audit[["method", "method_family", "n_datasets_with_valid_metrics", "n_datasets_with_valid_runtime", "n_timeouts", "finance_like_exclusions"]].copy()
    t3_per_method = t3_per_method.rename(columns={
        "n_datasets_with_valid_metrics": "valid_metrics",
        "n_datasets_with_valid_runtime": "valid_runtime",
        "n_timeouts": "timeouts",
    })
    t3_per_method = t3_per_method.sort_values(["method_family", "method"])
    t3_per_method.to_csv(PAPER_TABLES / "table3_missingness_audit.csv", index=False)
    # Compact by method family (sum valid_metrics, valid_runtime, timeouts)
    t3_family = (
        audit.groupby("method_family", as_index=False)
        .agg(
            valid_metrics=("n_datasets_with_valid_metrics", "sum"),
            valid_runtime=("n_datasets_with_valid_runtime", "sum"),
            timeouts=("n_timeouts", "sum"),
        )
    )
    t3_family = t3_family.sort_values("method_family")
    t3_family.to_csv(PAPER_TABLES / "table3_missingness_audit_by_family.csv", index=False)
    t3 = t3_per_method  # LaTeX uses per-method; family CSV is extra
    with open(PAPER_TABLES / "table3_missingness_audit.tex", "w") as f:
        f.write(df_to_latex_tabular(
            t3_per_method,
            caption="Missingness and timeout audit per method (valid\\_metrics, valid\\_runtime, timeouts; Finance exclusions).",
            label="tab:missingness-audit",
            float_fmt=".0f",
        ))
    with open(PAPER_TABLES / "table3_missingness_audit_by_family.tex", "w") as f:
        f.write(df_to_latex_tabular(
            t3_family,
            caption="Missingness and timeout audit by method family (valid\\_metrics, valid\\_runtime, timeouts).",
            label="tab:missingness-audit-family",
            float_fmt=".0f",
        ))
    print(f"Wrote table3_missingness_audit.csv, .tex, table3_missingness_audit_by_family.csv, .tex ({len(t3_per_method)} rows per-method, {len(t3_family)} by family)")

    return PAPER_TABLES


if __name__ == "__main__":
    main()
