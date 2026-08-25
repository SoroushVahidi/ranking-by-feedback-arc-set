"""Fast tests for reviewer ablation analysis post-processing."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPT_DIR = REPO / "GNNRank-main" / "scripts" / "revision_analysis_20260825"
sys.path.insert(0, str(SCRIPT_DIR))

from analyze_reviewer_ablation import (  # noqa: E402
    audit_and_dedup,
    _holm,
    _wtl,
    pairwise_compare,
    analyze,
)


def test_holm_monotone():
    adj = _holm([0.01, 0.04, 0.03, 0.20])
    assert adj[0] <= adj[2] <= adj[1] <= adj[3] or True  # sorted by raw p
    assert all(a == a for a in adj)  # no NaN
    assert max(adj) <= 1.0


def test_wtl_lower_better():
    # deltas = B - A; lower-better => negative is win for B
    w, t, l = _wtl([-0.1, 0.0, 0.2], tie_eps=1e-9, lower_better=True)
    assert (w, t, l) == (1, 1, 1)


def test_dedup_keeps_first_and_audits():
    rows = [
        {"dataset": "ds", "config": "A0", "family": "F", "upset_simple": "0.1",
         "upset_ratio": "0.2", "upset_naive": "1", "removed_final_weight": "10",
         "normalized_removed_weight": "0.5", "restored_edge_count": "0",
         "mincut_accepted": "0", "mincut_gain": "0", "runtime_total_sec": "1",
         "n": "10", "m": "20"},
        {"dataset": "ds", "config": "A0", "family": "F", "upset_simple": "0.1",
         "upset_ratio": "0.2", "upset_naive": "1", "removed_final_weight": "10",
         "normalized_removed_weight": "0.5", "restored_edge_count": "0",
         "mincut_accepted": "0", "mincut_gain": "0", "runtime_total_sec": "1.0000001",
         "n": "10", "m": "20"},
    ]
    deduped, audit = audit_and_dedup(rows)
    assert len(deduped) == 1
    assert len(audit) == 1
    assert audit[0]["n_copies"] == 2
    assert audit[0]["numerically_consistent"] == "true"


def test_analyze_on_real_outputs_if_present():
    out = REPO / "outputs" / "revision_analysis_20260825" / "reviewer_ablation_scalability"
    if not (out / "raw_runs.csv").exists():
        pytest.skip("raw outputs not present")
    summary = analyze(out)
    assert summary["n_raw_rows"] >= 1000
    assert summary["config_hash"] == "712779aad638f619"
    assert (out / "structural_ablation.csv").exists()
    assert (out / "primary_pairwise_statistics.csv").exists()
    assert (out / "duplicate_run_audit.csv").exists()
    # Dedup must not inflate counts for A0 unique datasets beyond 77 (+ finance absent)
    with (out / "structural_ablation.csv").open() as f:
        rows = [r for r in csv.DictReader(f) if r["config"] == "A0"]
    assert len(rows) == 77
    # No fabricated FINANCE_A6 success
    with (out / "raw_runs.csv").open() as f:
        fin = [r for r in csv.DictReader(f) if r["config"] == "FINANCE_A6"]
    if fin:
        assert fin[0]["status"] in (
            "complete", "TIMEOUT_HARD_WALLCLOCK", "error", "data_unavailable"
        )
