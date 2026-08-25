"""Fast tests for family-aware baseline analysis."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "revision_analysis_20260825" / "family_aware_baselines"
SCRIPT = ROOT / "GNNRank-main" / "scripts" / "revision_analysis_20260825" / "run_family_aware_baselines.py"


@pytest.mark.skipif(not OUT.exists(), reason="family_aware outputs missing")
def test_family_mapping_complete_no_dup_datasets():
    rows = list(csv.DictReader((OUT / "family_mapping.csv").open()))
    ds = [r["dataset"] for r in rows]
    assert len(ds) == len(set(ds))
    assert len(ds) >= 70
    fams = Counter(r["family"] for r in rows if r["included_excluded"] == "included")
    assert fams["Basketball_coarse"] + fams["Basketball_finer"] >= 50
    assert "Finance" in {r["family"] for r in rows}


@pytest.mark.skipif(not OUT.exists(), reason="outputs missing")
def test_equal_family_weighting_unit():
    rows = [
        r for r in csv.DictReader((OUT / "equal_family_macro.csv").open())
        if r["metric"] == "upset_simple"
    ]
    assert rows
    for r in rows:
        assert int(r["n_families"]) <= 7
        # each family one point: W+T+L == n_families
        w = int(r["family_points_favor_ours"])
        t = int(r["family_points_tie"])
        l = int(r["family_points_favor_baseline"])
        assert w + t + l == int(r["n_families"])


@pytest.mark.skipif(not OUT.exists(), reason="outputs missing")
def test_lofo_has_none_and_drops():
    rows = list(csv.DictReader((OUT / "leave_one_family_out.csv").open()))
    drops = {r["dropped_family"] for r in rows}
    assert "NONE" in drops
    assert "Basketball_coarse" in drops


@pytest.mark.skipif(not OUT.exists(), reason="outputs missing")
def test_btl_ratio_disadvantage_persists():
    claims = json.loads((OUT / "family_aware_claims.json").read_text())
    btl = claims["btl_upset_ratio_equal_family"]
    assert btl is not None
    assert float(btl["mean_of_family_medians"]) > 0  # positive => OURS worse


@pytest.mark.skipif(not OUT.exists(), reason="outputs missing")
def test_no_sign_flip_removing_basketball_for_btl():
    dep = json.loads((OUT / "family_aware_claims.json").read_text())["basketball_dependence"]
    assert dep["btl"]["sign_flip"] is False


def test_script_exists():
    assert SCRIPT.exists()
