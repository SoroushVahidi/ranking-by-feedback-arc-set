"""
test_paper_artifacts.py
=======================
Pytest test suite for canonical paper artifacts.

Run from repo root:
    pytest tests/test_paper_artifacts.py -v
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[1]
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

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def table4() -> pd.DataFrame:
    path = OUT_DIR / "table4_full_suite.csv"
    assert path.exists(), f"table4_full_suite.csv not found at {path}"
    return pd.read_csv(path)


@pytest.fixture(scope="session")
def table5() -> pd.DataFrame:
    path = OUT_DIR / "table5_compute_matched.csv"
    assert path.exists(), f"table5_compute_matched.csv not found at {path}"
    return pd.read_csv(path)


@pytest.fixture(scope="session")
def inventory() -> pd.DataFrame:
    path = DERIVED_DIR / "dataset_inventory.csv"
    assert path.exists(), f"dataset_inventory.csv not found at {path}"
    return pd.read_csv(path)


@pytest.fixture(scope="session")
def composition() -> pd.DataFrame:
    path = OUT_DIR / "benchmark_composition.csv"
    assert path.exists(), f"benchmark_composition.csv not found at {path}"
    return pd.read_csv(path)


@pytest.fixture(scope="session")
def claims() -> dict:
    path = OUT_DIR / "paper_claims_master.json"
    assert path.exists(), f"paper_claims_master.json not found at {path}"
    with open(path) as fh:
        return json.load(fh)


@pytest.fixture(scope="session")
def leaderboard() -> pd.DataFrame:
    path = CSV_DIR / "leaderboard_per_method.csv"
    assert path.exists(), f"leaderboard_per_method.csv not found at {path}"
    return pd.read_csv(path)


# ---------------------------------------------------------------------------
# Check 1: All canonical output files exist
# ---------------------------------------------------------------------------

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


@pytest.mark.parametrize("path", EXPECTED_FILES, ids=[p.name for p in EXPECTED_FILES])
def test_output_file_exists(path: Path) -> None:
    """All canonical output files must exist."""
    assert path.exists(), f"Expected output file missing: {path}"


# ---------------------------------------------------------------------------
# Check 2: Dataset count
# ---------------------------------------------------------------------------

def test_inventory_total_81(inventory: pd.DataFrame) -> None:
    """Total dataset count is 81 (80-suite + 1 _AUTO extra)."""
    assert len(inventory) == 81, f"Expected 81 datasets, got {len(inventory)}"


def test_inventory_suite_80(inventory: pd.DataFrame) -> None:
    """Exactly 80 datasets are flagged as in_80_suite=True."""
    n_in_suite = int(inventory["in_80_suite"].sum())
    assert n_in_suite == 80, f"Expected 80 in suite, got {n_in_suite}"


def test_inventory_excluded_is_AUTO(inventory: pd.DataFrame) -> None:
    """The excluded dataset is exactly _AUTO/Basketball_temporal__1985adj."""
    excluded = inventory[~inventory["in_80_suite"]]["dataset"].tolist()
    assert excluded == [AUTO_DATASET], f"Unexpected excluded datasets: {excluded}"


# ---------------------------------------------------------------------------
# Check 3: Table 4 method labels and coverage denominators
# ---------------------------------------------------------------------------

def test_table4_has_all_methods(table4: pd.DataFrame) -> None:
    """Table 4 must contain all expected methods."""
    missing = [m for m in METHODS_TABLE4 if m not in table4["method"].values]
    assert missing == [], f"Methods missing from Table 4: {missing}"


def test_table4_coverage_denominator_80(table4: pd.DataFrame) -> None:
    """All Table 4 coverage strings end with /80."""
    bad = [c for c in table4["coverage"].dropna() if not str(c).endswith("/80")]
    assert bad == [], f"Non-/80 coverage strings: {bad}"


def test_table4_n_datasets_le_80(table4: pd.DataFrame) -> None:
    """n_datasets for any method cannot exceed 80."""
    assert (table4["n_datasets"] <= 80).all(), (
        f"n_datasets > 80 found:\n{table4[table4['n_datasets'] > 80]}"
    )


# ---------------------------------------------------------------------------
# Check 4: OURS values match repo source (leaderboard_per_method.csv)
# ---------------------------------------------------------------------------

def _compute_ours_mfas_median(leaderboard: pd.DataFrame) -> float:
    """Re-derive OURS_MFAS median_upset_simple from the canonical source CSV."""
    df80 = leaderboard[leaderboard["dataset"] != AUTO_DATASET]
    df_t10 = df80[df80["config"].str.contains("trials10", na=False)]
    df_sorted = df_t10.sort_values(
        ["method", "dataset", "upset_simple"], na_position="last"
    )
    best = df_sorted.groupby(["method", "dataset"], as_index=False).first()
    ours = best[best["method"] == "OURS_MFAS"]
    return float(ours["upset_simple"].median())


def test_table4_OURS_MFAS_median_matches_source(
    table4: pd.DataFrame, leaderboard: pd.DataFrame
) -> None:
    """Table 4 OURS_MFAS median_upset_simple must match source CSV computation."""
    expected = _compute_ours_mfas_median(leaderboard)
    row = table4[table4["method"] == "OURS_MFAS"]
    assert len(row) == 1, "OURS_MFAS not found in table4"
    actual = float(row.iloc[0]["median_upset_simple"])
    assert abs(actual - expected) < 1e-9, (
        f"OURS_MFAS median mismatch: table4={actual:.9f}, source={expected:.9f}"
    )


def test_table4_OURS_MFAS_coverage_77(table4: pd.DataFrame) -> None:
    """OURS_MFAS has n_datasets=77 (finance dataset times out)."""
    row = table4[table4["method"] == "OURS_MFAS"]
    assert len(row) == 1, "OURS_MFAS not found in table4"
    n = int(row.iloc[0]["n_datasets"])
    assert n == 77, f"OURS_MFAS n_datasets={n} (expected 77)"


# ---------------------------------------------------------------------------
# Check 5: Coverage denominators consistent across tables
# ---------------------------------------------------------------------------

def test_table5_n_datasets_le_table4(
    table4: pd.DataFrame, table5: pd.DataFrame
) -> None:
    """Every method's n_datasets in Table 5 ≤ its n_datasets in Table 4."""
    t4_map = dict(zip(table4["method"], table4["n_datasets"]))
    for _, row in table5.iterrows():
        method = row["method"]
        n5 = row["n_datasets"]
        n4 = t4_map.get(method)
        if n4 is not None:
            assert n5 <= n4, (
                f"{method}: Table5 n_datasets={n5} > Table4 n_datasets={n4}"
            )


def test_claims_json_meta(claims: dict) -> None:
    """JSON claims must have correct meta-level counts."""
    meta = claims.get("_meta", {})
    assert meta.get("total_datasets") == 81, (
        f"total_datasets={meta.get('total_datasets')} (expected 81)"
    )
    assert meta.get("suite_80_datasets") == 80, (
        f"suite_80_datasets={meta.get('suite_80_datasets')} (expected 80)"
    )
    assert meta.get("extra_dataset_excluded") == AUTO_DATASET, (
        f"extra_dataset_excluded={meta.get('extra_dataset_excluded')}"
    )


# ---------------------------------------------------------------------------
# Check 6: Family-level correctness
# ---------------------------------------------------------------------------

def test_benchmark_composition_football_n20(composition: pd.DataFrame) -> None:
    """All football datasets must have n_nodes = 20."""
    football = composition[composition["family"].str.startswith("Football", na=False)]
    if len(football) == 0:
        pytest.skip("No football rows in composition (npz may not be readable)")
    n_nodes_col = "n_nodes"
    if n_nodes_col not in football.columns:
        pytest.skip("n_nodes column missing")
    valid = football.dropna(subset=[n_nodes_col])
    bad = valid[valid[n_nodes_col] != 20]
    assert len(bad) == 0, (
        f"Football datasets with n != 20:\n{bad[['dataset', 'n_nodes']].to_string()}"
    )


def test_benchmark_composition_has_80_rows(composition: pd.DataFrame) -> None:
    """Composition table must have exactly 80 rows (80-dataset suite)."""
    assert len(composition) == 80, (
        f"benchmark_composition.csv has {len(composition)} rows (expected 80)"
    )
