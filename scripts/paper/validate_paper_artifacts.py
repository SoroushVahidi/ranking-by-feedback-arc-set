"""
validate_paper_artifacts.py
============================
Validation script for all canonical paper artifacts.

Checks:
  1. All expected output files exist.
  2. Coverage denominators are correct (80 for Table 4, ≤80 for Table 5).
  3. Method labels match expected names.
  4. OURS_MFAS values are internally consistent with leaderboard source.
  5. Table 5 subset is strictly ≤ Table 4 in dataset count.
  6. Dataset count in 80-suite (excluding _AUTO) is exactly 80.
  7. Family-level assertions (all football n=20, etc.).

Run from repo root:
    python scripts/paper/validate_paper_artifacts.py

Exit codes:
    0 — all checks passed
    1 — one or more checks failed
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import numpy as np

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "outputs" / "paper_tables"
DERIVED_DIR = REPO_ROOT / "outputs" / "derived"
CSV_DIR = REPO_ROOT / "GNNRank-main" / "paper_csv"

AUTO_DATASET = "_AUTO/Basketball_temporal__1985adj"

METHODS_TABLE4 = [
    "OURS_MFAS", "OURS_MFAS_INS1", "OURS_MFAS_INS2", "OURS_MFAS_INS3",
    "SpringRank", "syncRank", "serialRank", "btl", "davidScore",
    "eigenvectorCentrality", "PageRank", "rankCentrality", "SVD_RS", "SVD_NRS",
    "DIGRAC", "ib",
]

EXPECTED_FILES = [
    OUT_DIR / "table4_full_suite.csv",
    OUT_DIR / "table5_compute_matched.csv",
    OUT_DIR / "table6_missingness.csv",
    OUT_DIR / "table7_best_in_suite.csv",
    OUT_DIR / "table8_runtime_tradeoff.csv",
    OUT_DIR / "benchmark_composition.csv",
    OUT_DIR / "paper_metrics_master.csv",
    OUT_DIR / "paper_claims_master.json",
    DERIVED_DIR / "dataset_inventory.csv",
]

# ---------------------------------------------------------------------------
# Validation infrastructure
# ---------------------------------------------------------------------------

_PASS = "PASS"
_FAIL = "FAIL"
_WARN = "WARN"


class ValidationReport:
    def __init__(self) -> None:
        self.checks: list[dict[str, Any]] = []

    def record(self, name: str, status: str, message: str) -> None:
        icon = {"PASS": "✓", "FAIL": "✗", "WARN": "⚠"}.get(status, "?")
        print(f"  [{icon}] {name}: {message}")
        self.checks.append({"name": name, "status": status, "message": message})

    def check(self, name: str, condition: bool, pass_msg: str, fail_msg: str) -> None:
        if condition:
            self.record(name, _PASS, pass_msg)
        else:
            self.record(name, _FAIL, fail_msg)

    def warn(self, name: str, condition: bool, pass_msg: str, warn_msg: str) -> None:
        if condition:
            self.record(name, _PASS, pass_msg)
        else:
            self.record(name, _WARN, warn_msg)

    @property
    def n_pass(self) -> int:
        return sum(1 for c in self.checks if c["status"] == _PASS)

    @property
    def n_fail(self) -> int:
        return sum(1 for c in self.checks if c["status"] == _FAIL)

    @property
    def n_warn(self) -> int:
        return sum(1 for c in self.checks if c["status"] == _WARN)

    def summary(self) -> str:
        return (
            f"\n{'='*60}\n"
            f"Validation summary: {self.n_pass} passed, "
            f"{self.n_fail} failed, {self.n_warn} warnings\n"
            f"{'='*60}"
        )

    def all_passed(self) -> bool:
        return self.n_fail == 0


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

def check_files_exist(report: ValidationReport) -> None:
    print("\n--- Check 1: Output files exist ---")
    for path in EXPECTED_FILES:
        report.check(
            f"exists:{path.name}",
            path.exists(),
            f"found at {path}",
            f"MISSING: {path}",
        )


def check_table4(report: ValidationReport) -> pd.DataFrame | None:
    print("\n--- Check 2: Table 4 structure and coverage ---")
    path = OUT_DIR / "table4_full_suite.csv"
    if not path.exists():
        report.record("table4_load", _FAIL, "File missing, cannot check")
        return None

    t4 = pd.read_csv(path)

    # Coverage denominator must be 80
    coverages = t4["coverage"].dropna().unique()
    all_80 = all(str(c).endswith("/80") for c in coverages)
    report.check(
        "table4_coverage_denominator",
        all_80,
        f"All {len(coverages)} coverage values use /80 denominator",
        f"Non-/80 coverage strings found: {coverages.tolist()}",
    )

    # Expected methods present
    methods_in = set(t4["method"].tolist())
    missing = [m for m in METHODS_TABLE4 if m not in methods_in]
    report.check(
        "table4_expected_methods",
        len(missing) == 0,
        f"All {len(METHODS_TABLE4)} expected methods present",
        f"Missing methods: {missing}",
    )

    # OURS_MFAS coverage = 77/80 (finance times out)
    ours_row = t4[t4["method"] == "OURS_MFAS"]
    if len(ours_row) == 1:
        n_ds = int(ours_row.iloc[0]["n_datasets"])
        report.check(
            "table4_OURS_MFAS_coverage",
            n_ds == 77,
            f"OURS_MFAS n_datasets={n_ds} (expected 77, finance times out)",
            f"OURS_MFAS n_datasets={n_ds} (expected 77)",
        )
    else:
        report.record("table4_OURS_MFAS_coverage", _FAIL, "OURS_MFAS not found in table4")

    # INS variants should have n_datasets = 77 in trials10 config (finance NaN)
    for method in ["OURS_MFAS_INS1", "OURS_MFAS_INS2", "OURS_MFAS_INS3"]:
        row = t4[t4["method"] == method]
        if len(row) == 1:
            n_ds = int(row.iloc[0]["n_datasets"])
            report.check(
                f"table4_{method}_coverage",
                n_ds == 77,
                f"{method} n_datasets={n_ds} (77 in trials10: finance NaN, Halo+ERO absent)",
                f"{method} n_datasets={n_ds} (expected 77 for trials10 config)",
            )

    # OURS_MFAS median_upset_simple should match leaderboard source
    _validate_ours_against_source(report, t4)

    return t4


def _validate_ours_against_source(
    report: ValidationReport, t4: pd.DataFrame
) -> None:
    """Re-derive OURS_MFAS stats from source CSV and compare."""
    source_path = CSV_DIR / "leaderboard_per_method.csv"
    if not source_path.exists():
        report.record("table4_OURS_source_check", _WARN, "Source CSV not found, skipping")
        return

    df = pd.read_csv(source_path)
    df80 = df[df["dataset"] != AUTO_DATASET]
    df_t10 = df80[df80["config"].str.contains("trials10", na=False)]
    df_sorted = df_t10.sort_values(["method", "dataset", "upset_simple"], na_position="last")
    best = df_sorted.groupby(["method", "dataset"], as_index=False).first()

    for method in ["OURS_MFAS", "OURS_MFAS_INS1"]:
        grp = best[best["method"] == method]
        expected_median = grp["upset_simple"].median()
        row = t4[t4["method"] == method]
        if len(row) == 0:
            continue
        actual_median = row.iloc[0]["median_upset_simple"]
        match = abs(float(actual_median) - float(expected_median)) < 1e-9
        report.check(
            f"table4_{method}_median_matches_source",
            match,
            f"{method} median_upset_simple={actual_median:.6f} matches source",
            f"{method} median mismatch: table={actual_median:.6f}, source={expected_median:.6f}",
        )


def check_table5(report: ValidationReport) -> pd.DataFrame | None:
    print("\n--- Check 3: Table 5 structure and coverage ---")
    path = OUT_DIR / "table5_compute_matched.csv"
    if not path.exists():
        report.record("table5_load", _FAIL, "File missing, cannot check")
        return None

    t5 = pd.read_csv(path)

    # n_datasets should be ≤ 80
    max_n = int(t5["n_datasets"].max()) if len(t5) > 0 else 0
    report.check(
        "table5_max_n_datasets_le_80",
        max_n <= 80,
        f"Max n_datasets in table5 = {max_n} (≤80)",
        f"Max n_datasets in table5 = {max_n} (should be ≤80)",
    )

    # Coverage denominator should be consistent
    coverages = t5["coverage"].dropna().unique()
    report.warn(
        "table5_coverage_consistent",
        len(set(c.split("/")[1] for c in coverages if "/" in str(c))) <= 1,
        f"Coverage denominators consistent: {set(c.split('/')[1] for c in coverages if '/' in str(c))}",
        f"Multiple coverage denominators: {coverages.tolist()}",
    )

    # No ERO dataset (it times out) — check by looking at which methods have smaller n
    ours_row = t5[t5["method"] == "OURS_MFAS"]
    if len(ours_row) > 0:
        n_ds = int(ours_row.iloc[0]["n_datasets"])
        report.warn(
            "table5_OURS_coverage_lt_table4",
            n_ds <= 77,
            f"Table5 OURS_MFAS n_datasets={n_ds} (≤77, ERO excluded)",
            f"Table5 OURS_MFAS n_datasets={n_ds} (unexpected)",
        )

    return t5


def check_dataset_inventory(report: ValidationReport) -> None:
    print("\n--- Check 4: Dataset inventory ---")
    path = DERIVED_DIR / "dataset_inventory.csv"
    if not path.exists():
        report.record("inventory_load", _FAIL, "File missing")
        return

    inv = pd.read_csv(path)
    total = len(inv)
    in_suite = int(inv["in_80_suite"].sum())
    excluded = int((~inv["in_80_suite"]).sum())

    report.check(
        "inventory_total_81",
        total == 81,
        f"Total datasets = {total}",
        f"Expected 81 datasets, got {total}",
    )
    report.check(
        "inventory_suite_80",
        in_suite == 80,
        f"In-80-suite count = {in_suite}",
        f"Expected 80 in suite, got {in_suite}",
    )
    report.check(
        "inventory_excluded_1",
        excluded == 1,
        f"Excluded datasets = {excluded} (_AUTO)",
        f"Expected 1 excluded, got {excluded}",
    )

    # Check the excluded dataset is the correct one
    excluded_datasets = inv[~inv["in_80_suite"]]["dataset"].tolist()
    report.check(
        "inventory_excluded_is_AUTO",
        excluded_datasets == [AUTO_DATASET],
        f"Excluded = {excluded_datasets}",
        f"Excluded dataset unexpected: {excluded_datasets}",
    )


def check_benchmark_composition(report: ValidationReport) -> None:
    print("\n--- Check 5: Benchmark composition (football n=20) ---")
    path = OUT_DIR / "benchmark_composition.csv"
    if not path.exists():
        report.record("composition_load", _FAIL, "File missing")
        return

    comp = pd.read_csv(path)

    football = comp[comp["family"].str.startswith("Football")]
    if len(football) > 0 and "n_nodes" in football.columns:
        all_n20 = (football["n_nodes"] == 20).all()
        report.check(
            "football_all_n20",
            bool(all_n20),
            f"All {len(football)} football datasets have n=20",
            f"Some football datasets do not have n=20: {football[football['n_nodes'] != 20][['dataset','n_nodes']].to_dict('records')}",
        )
    else:
        report.warn(
            "football_n_check",
            False,
            "N/A",
            "Football datasets not found or n_nodes missing in composition",
        )

    # Basketball coarse datasets should have n ≥ 200
    bball = comp[comp["family"] == "Basketball_coarse"]
    if len(bball) > 0 and "n_nodes" in bball.columns:
        valid = bball.dropna(subset=["n_nodes"])
        min_n = int(valid["n_nodes"].min()) if len(valid) > 0 else None
        report.warn(
            "basketball_coarse_n_ge_200",
            min_n is not None and min_n >= 200,
            f"Basketball coarse min n={min_n} (≥200)",
            f"Basketball coarse min n={min_n} (expected ≥200)",
        )


def check_json_claims(report: ValidationReport) -> None:
    print("\n--- Check 6: paper_claims_master.json ---")
    path = OUT_DIR / "paper_claims_master.json"
    if not path.exists():
        report.record("json_load", _FAIL, "File missing")
        return

    with open(path) as fh:
        claims = json.load(fh)

    report.check(
        "json_has_meta",
        "_meta" in claims,
        "_meta block present",
        "_meta block missing",
    )
    report.check(
        "json_total_datasets_81",
        claims.get("_meta", {}).get("total_datasets") == 81,
        "total_datasets=81",
        f"total_datasets={claims.get('_meta', {}).get('total_datasets')} (expected 81)",
    )
    report.check(
        "json_suite_80_datasets",
        claims.get("_meta", {}).get("suite_80_datasets") == 80,
        "suite_80_datasets=80",
        f"suite_80_datasets={claims.get('_meta', {}).get('suite_80_datasets')} (expected 80)",
    )
    report.check(
        "json_has_table4",
        "table4_full_suite" in claims,
        "table4_full_suite block present",
        "table4_full_suite block missing",
    )
    report.check(
        "json_has_OURS_MFAS",
        "OURS_MFAS" in claims.get("table4_full_suite", {}),
        "OURS_MFAS present in table4 claims",
        "OURS_MFAS missing from table4 claims",
    )
    report.check(
        "json_football_note",
        "football_n_range_note" in claims,
        "Football n-range correction note present",
        "Football n-range correction note missing",
    )
    report.check(
        "json_finance_note",
        "finance_timeout_note" in claims,
        "Finance timeout note present",
        "Finance timeout note missing",
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    print("=" * 60)
    print("validate_paper_artifacts.py")
    print("=" * 60)

    report = ValidationReport()

    check_files_exist(report)
    check_table4(report)
    check_table5(report)
    check_dataset_inventory(report)
    check_benchmark_composition(report)
    check_json_claims(report)

    print(report.summary())

    # Write report to file
    report_path = REPO_ROOT / "outputs" / "audits" / "validation_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as fh:
        json.dump(
            {
                "n_pass": report.n_pass,
                "n_fail": report.n_fail,
                "n_warn": report.n_warn,
                "checks": report.checks,
            },
            fh,
            indent=2,
        )
    print(f"\nValidation report written to: {report_path}")

    return 0 if report.all_passed() else 1


if __name__ == "__main__":
    sys.exit(main())
