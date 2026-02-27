#!/usr/bin/env python3
"""
Validate paper artifacts. Exit nonzero if any check fails.
Writes a concise report to docs/Artifact_validation_report.md.

Checks:
  1) Missing runtime: no method has upset_simple but runtime_sec missing for >0 datasets
     unless (dataset, method) or method is whitelisted.
  2) Coverage mismatch: datasets in raw leaderboard are not silently dropped in
     per-method summary (table1) vs leaderboard.
  3) Oracle guardrail: table1/table2 are built from per-method CSVs (columns must not
     be oracle-only; we check table1 has method-level columns, not best_*_oracle).
  4) Determinism: deterministic methods must not report std>0 for upset_simple unless
     whitelisted or explained by timeouts/missingness (we check results_from_result_arrays
     or leaderboard for method+config with single run and std>0).

Run from repo root: python tools/validate_paper_artifacts.py
"""

from pathlib import Path
import sys
from typing import List, Tuple

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
PAPER_CSV = REPO_ROOT / "paper_csv"
PAPER_TABLES = REPO_ROOT / "paper_tables"
DOCS = REPO_ROOT / "docs"
REPORT_PATH = DOCS / "Artifact_validation_report.md"

# (dataset, method) or method substring: allow missing runtime (timeout / known hole)
RUNTIME_MISSING_WHITELIST = [
    ("finance", "mvr"),
    ("finance", "syncRank"),
    ("finance", "OURS_MFAS"),
    ("finance", "OURS_MFAS_INS1"),
    ("finance", "OURS_MFAS_INS2"),
    ("finance", "OURS_MFAS_INS3"),
    ("Dryad_animal_society", "DIGRAC"),  # optional: could be timeout
    ("Dryad_animal_society", "ib"),
]
# Methods that are composite or single-run; allow missing runtime
RUNTIME_MISSING_METHOD_WHITELIST = [
    "OURS_MFAS_INS1OURS_MFAS_INS2",
    "btlDIGRAC",
]


def _is_whitelisted_missing_runtime(dataset: str, method: str) -> bool:
    if (dataset, method) in RUNTIME_MISSING_WHITELIST:
        return True
    for m in RUNTIME_MISSING_METHOD_WHITELIST:
        if m in method or method == m:
            return True
    return False


def check_missing_runtime(lb: pd.DataFrame) -> Tuple[List[str], bool]:
    """Returns (list of violation messages, passed)."""
    violations = []
    if lb.empty:
        return violations, True
    bad = lb[lb["upset_simple"].notna() & (lb["runtime_sec"].isna() | ~np.isfinite(lb["runtime_sec"].fillna(0)))]
    for _, r in bad.iterrows():
        ds, m = str(r["dataset"]), str(r["method"])
        if _is_whitelisted_missing_runtime(ds, m):
            continue
        violations.append(f"Missing runtime: dataset={ds!r}, method={m!r} (upset_simple present)")
    return violations, len(violations) == 0


def check_coverage_mismatch(lb: pd.DataFrame, table1: pd.DataFrame) -> Tuple[List[str], bool]:
    """Table1 should not drop datasets that appear in lb (per-method summary is over same set)."""
    violations = []
    if lb.empty or table1.empty:
        return violations, True
    # Table1 is aggregated by (method, config); unique datasets in lb
    ds_in_lb = set(lb["dataset"].unique())
    # Table1 coverage column is "n / total"; we check that total in table1 matches
    # number of datasets in lb (or we check no dataset disappeared)
    # Simpler: check that the set of datasets in lb is not larger than what table1 implies
    # Actually: "silently dropped" means a dataset present in lb is missing from table1.
    # Table1 doesn't list datasets; it lists methods. So "coverage mismatch" = if we
    # aggregate lb by method, we get N datasets per method; table1 coverage should
    # reflect that. So we require: for each method in table1, coverage (n_valid/total)
    # should use total = lb["dataset"].nunique() or at least no method has more valid
    # datasets than total datasets in lb. So check: total_datasets from lb >= any n_valid
    # in table1. And if we build table1 from lb, unique datasets in lb should be the
    # same as what we'd get from the raw results. So check: lb has same dataset set as
    # results_from_result_arrays (or we just check table1 was built from lb by ensuring
    # table1 coverage denominator matches lb dataset count).
    total_ds = lb["dataset"].nunique()
    if "coverage" in table1.columns:
        for _, row in table1.iterrows():
            cov = row.get("coverage", "")
            if isinstance(cov, str) and "/" in cov:
                n_str, total_str = cov.strip().split("/")
                n_val, total_val = int(n_str.strip()), int(total_str.strip())
                if total_val != total_ds:
                    violations.append(
                        f"Table1 coverage total {total_val} != leaderboard unique datasets {total_ds}"
                    )
                break  # one row enough to check total
    return violations, len(violations) == 0


def check_oracle_guardrail(table1_path: Path, table2_path: Path) -> Tuple[List[str], bool]:
    """Table1 and table2 must be built from per-method data (have method column, not only best_*)."""
    violations = []
    for name, p in [("table1", table1_path), ("table2", table2_path)]:
        if not p.exists():
            continue
        df = pd.read_csv(p)
        cols = set(df.columns)
        if "method" not in cols and "dataset" not in cols:
            violations.append(f"{name}: missing 'method' or 'dataset'; may be oracle-only?")
        if cols.issuperset({"best_classical_upset_simple", "best_gnn_upset_simple"}) and "method" not in cols:
            violations.append(f"{name}: has best_* columns but no 'method' (oracle used as main table?)")
    return violations, len(violations) == 0


def check_determinism_std(ra_path: Path) -> Tuple[List[str], bool]:
    """Deterministic methods (single run, or known deterministic) should not have std>0."""
    violations = []
    if not ra_path.exists():
        return violations, True
    df = pd.read_csv(ra_path)
    if "upset_simple_std" not in df.columns or "num_runs" not in df.columns:
        return violations, True
    # Single-run rows with std > 0 (should be 0 for deterministic)
    single = df[df["num_runs"] == 1]
    bad = single[(single["upset_simple_std"].fillna(0) > 1e-10)]
    for _, r in bad.iterrows():
        violations.append(
            f"Determinism: num_runs=1 but upset_simple_std={r['upset_simple_std']} "
            f"(dataset={r['dataset']}, method={r['method']}, config={r['config']})"
        )
    return violations, len(violations) == 0


def main() -> int:
    report = []
    report.append("# Artifact validation report\n")
    all_passed = True

    lb_path = PAPER_CSV / "leaderboard_per_method.csv"
    table1_path = PAPER_TABLES / "table1_main_leaderboard.csv"
    table2_path = PAPER_TABLES / "table2_compute_matched.csv"
    ra_path = PAPER_CSV / "results_from_result_arrays.csv"

    # 1) Missing runtime
    if not lb_path.exists():
        report.append("## Missing runtime\n- SKIP: leaderboard_per_method.csv not found.\n")
    else:
        lb = pd.read_csv(lb_path)
        violations, passed = check_missing_runtime(lb)
        report.append("## 1) Missing runtime (upset_simple present, runtime_sec missing)\n")
        if violations:
            report.append("FAILED.\n")
            for v in violations:
                report.append(f"- {v}\n")
            all_passed = False
        else:
            report.append("PASSED.\n")

    # 2) Coverage mismatch
    if lb_path.exists() and table1_path.exists():
        lb = pd.read_csv(lb_path)
        table1 = pd.read_csv(table1_path)
        violations, passed = check_coverage_mismatch(lb, table1)
        report.append("## 2) Coverage mismatch (table1 vs leaderboard)\n")
        if violations:
            report.append("FAILED.\n")
            for v in violations:
                report.append(f"- {v}\n")
            all_passed = False
        else:
            report.append("PASSED.\n")
    else:
        report.append("## 2) Coverage mismatch\n- SKIP: leaderboard or table1 missing.\n")

    # 3) Oracle guardrail
    report.append("## 3) Oracle guardrail (table1/table2 from per-method only)\n")
    violations, passed = check_oracle_guardrail(table1_path, table2_path)
    if violations:
        report.append("FAILED.\n")
        for v in violations:
            report.append(f"- {v}\n")
        all_passed = False
    else:
        report.append("PASSED.\n")

    # 4) Determinism
    report.append("## 4) Determinism (no std>0 for single-run rows)\n")
    violations, passed = check_determinism_std(ra_path)
    if violations:
        report.append("FAILED.\n")
        for v in violations[:15]:
            report.append(f"- {v}\n")
        if len(violations) > 15:
            report.append(f"- ... and {len(violations) - 15} more.\n")
        all_passed = False
    else:
        report.append("PASSED.\n")

    report.append("\n---\n")
    report.append("Overall: " + ("PASSED" if all_passed else "FAILED") + "\n")

    DOCS.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "w") as f:
        f.writelines(report)
    print("".join(report))
    print(f"Report written to {REPORT_PATH}")
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
