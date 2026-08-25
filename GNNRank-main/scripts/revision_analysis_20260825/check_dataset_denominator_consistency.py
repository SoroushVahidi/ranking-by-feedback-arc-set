#!/usr/bin/env python3
"""Dataset denominator consistency checker for JoS revision manuscript.

Validates intended suite / loadable / missing IDs and coverage fractions
against outputs/derived/dataset_inventory.csv, e2 completion matrix, and
manuscript/response prose.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
INV = REPO / "outputs/derived/dataset_inventory.csv"
E2 = REPO / "outputs/revision_analysis_20260824/runtime_coverage_final/e2_completion_matrix.csv"
MS = REPO / "manuscript/revision_20260825/source/main_ik.tex"
RESP = REPO / "manuscript/revision_20260825/response_to_reviewers.tex"

MISSING_EXPECTED = {
    "ERO/p5K5N350eta10styleuniform",
    "Halo2BetaData/HeadToHead",
}
EXTRA_EXPECTED = {"_AUTO/Basketball_temporal__1985adj"}
HALO_LOADABLE = "Halo2BetaData"


def load_inventory():
    rows = list(csv.DictReader(INV.open()))
    suite = {r["dataset"] for r in rows if r["in_80_suite"] == "True"}
    extra = {r["dataset"] for r in rows if r["in_80_suite"] != "True"}
    return suite, extra


def e2_coverage_over_loadable(loadable_ids_proxy: set[str]):
    """Compute SUCCESS counts on e2 rows excluding ERO (proxy for 78 loadable).

    e2 labels the Halo graph as Halo2BetaData/HeadToHead and omits plain
    Halo2BetaData; excluding ERO yields the 78-row loadable proxy.
    """
    rows = [r for r in csv.DictReader(E2.open()) if r["dataset"] != "ERO/p5K5N350eta10styleuniform"]
    assert len(rows) == 78, len(rows)
    out = {}
    for m in (
        "OURS_MFAS",
        "SpringRank",
        "PageRank",
        "btl",
        "davidScore",
        "SVD_NRS",
        "serialRank",
        "rankCentrality",
        "syncRank",
        "DIGRAC",
        "ib",
    ):
        out[m] = sum(1 for r in rows if r[m] == "SUCCESS")
    return out


def check_tex(path: Path, patterns_required, patterns_forbidden):
    text = path.read_text()
    errs = []
    for pat, label in patterns_required:
        if not re.search(pat, text):
            errs.append(f"{path.name}: missing required `{label}`")
    for pat, label in patterns_forbidden:
        if re.search(pat, text):
            errs.append(f"{path.name}: forbidden stale `{label}`")
    return errs


def main() -> int:
    errors = []
    suite, extra = load_inventory()
    if len(suite) != 80:
        errors.append(f"intended suite size {len(suite)} != 80")
    if extra != EXTRA_EXPECTED:
        errors.append(f"extra inventory {extra} != {EXTRA_EXPECTED}")
    if not MISSING_EXPECTED <= suite:
        errors.append("missing IDs not both in intended suite")
    if HALO_LOADABLE not in suite:
        errors.append("Halo2BetaData not in intended suite")

    # Loadable arithmetic (authoritative inventory + known missing adj)
    loadable = len(suite) - len(MISSING_EXPECTED)
    if loadable != 78:
        errors.append(f"loadable arithmetic {loadable} != 78")

    cov = e2_coverage_over_loadable(suite - MISSING_EXPECTED)
    expected = {
        "OURS_MFAS": 77,
        "SpringRank": 78,
        "PageRank": 78,
        "btl": 78,
        "davidScore": 78,
        "SVD_NRS": 78,
        "serialRank": 78,
        "rankCentrality": 78,
        "syncRank": 77,
        "DIGRAC": 61,
        "ib": 61,
    }
    for m, n in expected.items():
        if cov.get(m) != n:
            errors.append(f"coverage {m}: got {cov.get(m)} expected {n}/78")

    # Percent strings used in manuscript
    def pct(num, den):
        return f"{100.0 * num / den:.1f}"

    if pct(77, 78) != "98.7":
        errors.append("OURS pct drift")
    if pct(61, 78) != "78.2":
        errors.append("GNN pct drift")

    req_ms = [
        (r"effective denominator of \$78\$", "78 loadable denom"),
        (r"77/78", "OURS 77/78"),
        (r"78/78", "classical 78/78"),
        (r"61/78", "GNN 61/78"),
        (r"98\.7\\%", "OURS 98.7%"),
        (r"78\.2\\%", "GNN 78.2%"),
        (r"ERO/p5K5N350eta10styleuniform", "ERO id"),
        (r"Halo2BetaData/HeadToHead", "HeadToHead id"),
        (r"_AUTO/Basketball_temporal__1985adj|_AUTO/Basketball\\_temporal\\_\\_1985adj", "_AUTO exclude"),
    ]
    forb_ms = [
        (r"77/79", "stale 77/79"),
        (r"78/79", "stale 78/79"),
        (r"61/79", "stale 61/79"),
        (r"denominator of \$79\$", "stale denom 79"),
        (r"Coverage on \$79\$", "stale coverage 79"),
        (r"readable graphs to \$79\$", "stale caption 79"),
        (r"97\.5\\%", "stale 97.5%"),
        (r"77\.2\\%", "stale 77.2%"),
    ]
    errors.extend(check_tex(MS, req_ms, forb_ms))

    req_r = [
        (r"77/78", "OURS 77/78"),
        (r"78/78", "classical 78/78"),
        (r"61/78", "GNN 61/78"),
        (r"\$78\$ loadable", "78 loadable"),
    ]
    forb_r = [
        (r"77/79", "stale 77/79"),
        (r"78/79", "stale 78/79"),
        (r"61/79", "stale 61/79"),
    ]
    errors.extend(check_tex(RESP, req_r, forb_r))

    if errors:
        print("DATASET_DENOMINATOR_CONSISTENCY = FAIL")
        for e in errors:
            print(" -", e)
        return 1
    print("DATASET_DENOMINATOR_CONSISTENCY = PASS")
    print(f"INTENDED={len(suite)} LOADABLE={loadable} MISSING={sorted(MISSING_EXPECTED)}")
    print(f"EXCLUDED_EXTRA={sorted(extra)}")
    print(
        "COVERAGE: OURS 77/78; classical 78/78; SyncRank 77/78; DIGRAC/ib 61/78"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
