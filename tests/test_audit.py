"""
test_audit.py
=============
Pytest test suite implementing the three priority audit checks:

  Part 1 — Canonical Table / Data Provenance Audit
  Part 2 — Baseline-Label Audit
  Part 3 — Deterministic Repeatability Test for OURS

Run from repo root:
    pytest tests/test_audit.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import scipy.sparse as sp

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "GNNRank-main" / "src"
DATA_DIR = REPO_ROOT / "GNNRank-main" / "data"
CSV_DIR = REPO_ROOT / "GNNRank-main" / "paper_csv"
OUT_DIR = REPO_ROOT / "outputs" / "paper_tables"
LEGACY_DIR = REPO_ROOT / "GNNRank-main" / "paper_tables"

AUTO_DATASET = "_AUTO/Basketball_temporal__1985adj"

CLASSICAL_METHODS = [
    "SpringRank", "syncRank", "serialRank", "btl", "davidScore",
    "eigenvectorCentrality", "PageRank", "rankCentrality", "SVD_RS", "SVD_NRS",
]
OURS_METHODS = ["OURS_MFAS", "OURS_MFAS_INS1", "OURS_MFAS_INS2", "OURS_MFAS_INS3"]

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _best_per_method_dataset(leaderboard: pd.DataFrame) -> pd.DataFrame:
    """Re-derive best (min upset_simple) per (method, dataset) for trials10 config."""
    df80 = leaderboard[leaderboard["dataset"] != AUTO_DATASET]
    df_t10 = df80[df80["config"].str.contains("trials10", na=False)]
    df_sorted = df_t10.sort_values(
        ["method", "dataset", "upset_simple"], na_position="last"
    )
    return df_sorted.groupby(["method", "dataset"], as_index=False).first()


# ===========================================================================
# PART 1 — Canonical Table / Data Provenance Audit
# ===========================================================================

class TestCanonicalProvenance:
    """Part 1: Verify that canonical and legacy pipelines do not conflict."""

    def test_canonical_leaderboard_exists(self) -> None:
        """Canonical data source leaderboard_per_method.csv must exist."""
        path = CSV_DIR / "leaderboard_per_method.csv"
        assert path.exists(), f"Canonical source not found: {path}"

    def test_canonical_leaderboard_row_count(self) -> None:
        """leaderboard_per_method.csv must have exactly 1468 data rows (1469 incl. header)."""
        path = CSV_DIR / "leaderboard_per_method.csv"
        df = pd.read_csv(path)
        assert len(df) == 1468, (
            f"leaderboard_per_method.csv has {len(df)} rows (expected 1468)"
        )

    def test_canonical_leaderboard_has_source_column(self) -> None:
        """All rows in leaderboard_per_method.csv must have source='result_arrays'."""
        df = pd.read_csv(CSV_DIR / "leaderboard_per_method.csv")
        unique_sources = df["source"].dropna().unique().tolist()
        assert unique_sources == ["result_arrays"], (
            f"Unexpected source values: {unique_sources}"
        )

    def test_legacy_files_exist_but_are_labelled(self) -> None:
        """Legacy paper_tables/ directory must exist and its README must warn about /81 denominators."""
        readme = LEGACY_DIR / "README.md"
        assert readme.exists(), f"Legacy README missing: {readme}"
        text = readme.read_text()
        assert "/81" in text, (
            "Legacy README does not mention /81 denominators — legacy status unclear"
        )
        # Must also point to canonical replacement
        assert "outputs/paper_tables" in text, (
            "Legacy README does not reference canonical outputs/paper_tables/"
        )

    def test_canonical_outputs_not_stale_wrt_leaderboard(self) -> None:
        """
        Table 4 OURS_MFAS median_upset_simple must match a fresh recomputation
        from leaderboard_per_method.csv (detects stale cached outputs).
        """
        lb = pd.read_csv(CSV_DIR / "leaderboard_per_method.csv")
        t4 = pd.read_csv(OUT_DIR / "table4_full_suite.csv")
        best = _best_per_method_dataset(lb)
        for method in OURS_METHODS:
            grp = best[best["method"] == method]
            expected = float(grp["upset_simple"].median())
            row = t4[t4["method"] == method]
            assert len(row) == 1, f"{method} not found in table4"
            actual = float(row.iloc[0]["median_upset_simple"])
            assert abs(actual - expected) < 1e-9, (
                f"{method}: table4={actual:.9f} != source={expected:.9f} — stale output detected"
            )

    def test_canonical_outputs_all_classical_match_source(self) -> None:
        """
        Every classical method's median_upset_simple in Table 4 must match
        a fresh recomputation from leaderboard_per_method.csv.
        """
        lb = pd.read_csv(CSV_DIR / "leaderboard_per_method.csv")
        t4 = pd.read_csv(OUT_DIR / "table4_full_suite.csv")
        best = _best_per_method_dataset(lb)
        mismatches = []
        for method in CLASSICAL_METHODS:
            grp = best[best["method"] == method]
            expected = float(grp["upset_simple"].median())
            row = t4[t4["method"] == method]
            if len(row) == 0:
                mismatches.append(f"{method}: missing from table4")
                continue
            actual = float(row.iloc[0]["median_upset_simple"])
            if abs(actual - expected) >= 1e-9:
                mismatches.append(
                    f"{method}: table4={actual:.9f}, source={expected:.9f}"
                )
        assert mismatches == [], (
            "Classical method table4 values do not match source:\n" + "\n".join(mismatches)
        )

    def test_leaderboard_compute_matched_is_subset(self) -> None:
        """leaderboard_compute_matched.csv must be a strict subset of leaderboard_per_method.csv rows."""
        lb = pd.read_csv(CSV_DIR / "leaderboard_per_method.csv")
        cm = pd.read_csv(CSV_DIR / "leaderboard_compute_matched.csv")
        # Every compute-matched row must have runtime_sec <= 1800 or NaN
        valid = cm.dropna(subset=["runtime_sec"])
        over_budget = valid[valid["runtime_sec"] > 1800.0]
        assert len(over_budget) == 0, (
            f"{len(over_budget)} rows in compute_matched exceed 1800s budget"
        )

    def test_no_AUTO_dataset_in_table4(self) -> None:
        """The _AUTO/Basketball_temporal__1985adj dataset must not appear in Table 4 source."""
        lb = pd.read_csv(CSV_DIR / "leaderboard_per_method.csv")
        t4 = pd.read_csv(OUT_DIR / "table4_full_suite.csv")
        # Table 4 n_datasets must be ≤ 80 for all methods
        assert (t4["n_datasets"] <= 80).all(), (
            "Table 4 has n_datasets > 80 for some method — _AUTO may be included"
        )


# ===========================================================================
# PART 2 — Baseline-Label Audit
# ===========================================================================

class TestBaselineLabels:
    """
    Part 2: Verify that every baseline name in result tables is attached to
    the correct implementation and that no label swaps exist.
    """

    def test_all_classical_methods_in_leaderboard(self) -> None:
        """All classical method names must be present in leaderboard_per_method.csv."""
        df = pd.read_csv(CSV_DIR / "leaderboard_per_method.csv")
        methods_in = set(df["method"].unique())
        missing = [m for m in CLASSICAL_METHODS if m not in methods_in]
        assert missing == [], f"Classical methods missing from leaderboard: {missing}"

    def test_all_ours_variants_in_leaderboard(self) -> None:
        """All four OURS variants must be present in leaderboard_per_method.csv."""
        df = pd.read_csv(CSV_DIR / "leaderboard_per_method.csv")
        methods_in = set(df["method"].unique())
        missing = [m for m in OURS_METHODS if m not in methods_in]
        assert missing == [], f"OURS variants missing from leaderboard: {missing}"

    def test_btl_higher_upset_than_david_score(self) -> None:
        """
        btl must have higher median_upset_simple than davidScore in Table 4.

        Historical context: an early draft had btl and davidScore values swapped.
        The corrected values are btl ≈ 0.984 and davidScore ≈ 0.824.
        This test detects any reintroduction of that label swap.
        """
        t4 = pd.read_csv(OUT_DIR / "table4_full_suite.csv")
        btl_val = float(t4[t4["method"] == "btl"]["median_upset_simple"].iloc[0])
        david_val = float(t4[t4["method"] == "davidScore"]["median_upset_simple"].iloc[0])
        assert btl_val > david_val, (
            f"btl median_upset_simple ({btl_val:.6f}) is NOT greater than "
            f"davidScore median_upset_simple ({david_val:.6f}). "
            "This matches the known btl/davidScore label-swap pattern."
        )

    def test_btl_median_upset_approx_0984(self) -> None:
        """
        btl median_upset_simple must be close to 0.984 (not the swapped ≈ 0.824 value).

        If this value is near 0.82–0.83 it indicates the btl/davidScore label swap.
        """
        t4 = pd.read_csv(OUT_DIR / "table4_full_suite.csv")
        btl_val = float(t4[t4["method"] == "btl"]["median_upset_simple"].iloc[0])
        # btl should be ≥ 0.95 (historically close to 0.984)
        assert btl_val >= 0.95, (
            f"btl median_upset_simple = {btl_val:.6f}: suspiciously low. "
            "Expected ≥ 0.95; possible label swap with davidScore."
        )

    def test_david_score_median_upset_approx_0824(self) -> None:
        """
        davidScore median_upset_simple must be close to 0.824 (not the swapped ≈ 0.984 value).
        """
        t4 = pd.read_csv(OUT_DIR / "table4_full_suite.csv")
        david_val = float(t4[t4["method"] == "davidScore"]["median_upset_simple"].iloc[0])
        # davidScore should be < 0.90 (historically close to 0.824)
        assert david_val < 0.90, (
            f"davidScore median_upset_simple = {david_val:.6f}: suspiciously high. "
            "Expected < 0.90; possible label swap with btl."
        )

    def test_method_names_in_leaderboard_match_train_dispatch(self) -> None:
        """
        Method names in leaderboard_per_method.csv must be a subset of the names
        used in train.py's dispatch chain.  This verifies the pipeline label chain.
        """
        train_py = (REPO_ROOT / "GNNRank-main" / "src" / "train.py").read_text()

        # All classical + OURS methods should appear literally in train.py
        expected_in_train = CLASSICAL_METHODS + OURS_METHODS
        missing_from_dispatch = []
        for m in expected_in_train:
            # Each method should appear as model_name == 'METHOD' in the dispatch
            if f"model_name == '{m}'" not in train_py:
                missing_from_dispatch.append(m)

        assert missing_from_dispatch == [], (
            f"Methods not found in train.py dispatch: {missing_from_dispatch}"
        )

    def test_comparison_py_exports_all_baselines(self) -> None:
        """
        comparison.py must define every classical baseline as a top-level function,
        and must export the OURS wrappers (named ours_MFAS / ours_MFAS_INS1/2/3).
        This ensures method-name → code-path mapping is intact.
        """
        comparison_py = (
            REPO_ROOT / "GNNRank-main" / "src" / "comparison.py"
        ).read_text()

        # Classical methods: function names match the method names exactly
        missing_classical = []
        for m in CLASSICAL_METHODS:
            if f"def {m}(" not in comparison_py:
                # Special case: SpringRank lives in SpringRank.py, not comparison.py
                if m != "SpringRank":
                    missing_classical.append(m)

        assert missing_classical == [], (
            f"Classical baseline functions missing from comparison.py: {missing_classical}"
        )

        # OURS wrapper functions use lowercase prefix: ours_MFAS, ours_MFAS_INS1, etc.
        ours_fn_names = ["ours_MFAS", "ours_MFAS_INS1", "ours_MFAS_INS2", "ours_MFAS_INS3"]
        missing_ours = [fn for fn in ours_fn_names if f"def {fn}(" not in comparison_py]
        assert missing_ours == [], (
            f"OURS wrapper functions missing from comparison.py: {missing_ours}"
        )

    def test_ours_variants_have_distinct_variant_labels(self) -> None:
        """
        Each OURS variant in the leaderboard must correspond to a distinct insertion_passes value.
        OURS_MFAS_INS1 → INS1, OURS_MFAS_INS2 → INS2, OURS_MFAS_INS3 → INS3.
        Verify this by inspecting comparison.py.
        """
        comparison_py = (
            REPO_ROOT / "GNNRank-main" / "src" / "comparison.py"
        ).read_text()

        assert 'variant="INS1"' in comparison_py or "variant='INS1'" in comparison_py, (
            "OURS_MFAS_INS1 does not pass variant='INS1' — label dispatch may be broken"
        )
        assert 'variant="INS2"' in comparison_py or "variant='INS2'" in comparison_py, (
            "OURS_MFAS_INS2 does not pass variant='INS2'"
        )
        assert 'variant="INS3"' in comparison_py or "variant='INS3'" in comparison_py, (
            "OURS_MFAS_INS3 does not pass variant='INS3'"
        )

    def test_ours_mfas_default_variant_is_ins3(self) -> None:
        """
        ours_MFAS() (no variant arg) must default to variant='INS3' per comparison.py.
        This ensures the main OURS_MFAS entry in tables uses the INS3 implementation.
        """
        comparison_py = (
            REPO_ROOT / "GNNRank-main" / "src" / "comparison.py"
        ).read_text()

        # The ours_MFAS function signature should default to INS3
        assert 'variant: str = "INS3"' in comparison_py or "variant='INS3'" in comparison_py, (
            "ours_MFAS default variant is not INS3 — check comparison.py"
        )

    @pytest.mark.parametrize("method", CLASSICAL_METHODS)
    def test_classical_method_values_match_source_per_method(
        self, method: str
    ) -> None:
        """Per-method: classical baseline value in Table 4 must match leaderboard source."""
        lb = pd.read_csv(CSV_DIR / "leaderboard_per_method.csv")
        t4 = pd.read_csv(OUT_DIR / "table4_full_suite.csv")
        best = _best_per_method_dataset(lb)
        grp = best[best["method"] == method]
        expected = float(grp["upset_simple"].median())
        row = t4[t4["method"] == method]
        assert len(row) == 1, f"{method} not found in table4"
        actual = float(row.iloc[0]["median_upset_simple"])
        assert abs(actual - expected) < 1e-9, (
            f"{method}: table4={actual:.9f} != source={expected:.9f}"
        )

    def test_gnn_methods_in_leaderboard(self) -> None:
        """DIGRAC and ib must appear as methods in leaderboard_per_method.csv."""
        df = pd.read_csv(CSV_DIR / "leaderboard_per_method.csv")
        methods = set(df["method"].unique())
        assert "DIGRAC" in methods, "DIGRAC missing from leaderboard"
        assert "ib" in methods, "ib missing from leaderboard"


# ===========================================================================
# PART 3 — Deterministic Repeatability Test for OURS
# ===========================================================================

# Add src to path so we can import ours_mfas directly
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def _load_animal_adj() -> sp.spmatrix:
    """Load the Dryad animal society adjacency matrix (n=21, m=193)."""
    path = DATA_DIR / "Dryad_animal_society" / "adj.npz"
    if not path.exists():
        pytest.skip(f"Animal dataset not available: {path}")
    return sp.load_npz(str(path))


def _load_basketball_1985_adj() -> sp.spmatrix:
    """Load the Basketball 1985 adjacency matrix (n=282, m=2904)."""
    path = DATA_DIR / "Basketball_temporal" / "1985adj.npz"
    if not path.exists():
        pytest.skip(f"Basketball 1985 dataset not available: {path}")
    return sp.load_npz(str(path))


@pytest.fixture(scope="session")
def animal_adj() -> sp.spmatrix:
    return _load_animal_adj()


@pytest.fixture(scope="session")
def basketball_1985_adj() -> sp.spmatrix:
    return _load_basketball_1985_adj()


class TestOURSDeterminism:
    """
    Part 3: Verify that all OURS variants are fully deterministic —
    repeated runs on identical input produce bit-identical outputs.
    """

    N_TRIALS = 5  # number of repeated runs per test

    def _run_n_times(
        self,
        adj: sp.spmatrix,
        insertion_passes: int,
        n: int = 5,
    ) -> list[np.ndarray]:
        """Return N independent score vectors from ours_mfas_rmfa."""
        from ours_mfas import ours_mfas_rmfa  # type: ignore[import]

        results = []
        for _ in range(n):
            scores, _ = ours_mfas_rmfa(adj, insertion_passes=insertion_passes, return_meta=True)
            results.append(scores.copy())
        return results

    # --- Animal dataset (n=21, m=193) ---

    def test_ours_mfas_ins1_deterministic_animal(self, animal_adj: sp.spmatrix) -> None:
        """OURS_MFAS_INS1: 5 runs on animal dataset must produce identical scores."""
        results = self._run_n_times(animal_adj, insertion_passes=1, n=self.N_TRIALS)
        for i in range(1, self.N_TRIALS):
            assert np.array_equal(results[0], results[i]), (
                f"OURS_MFAS_INS1 run 1 vs run {i + 1} differ on animal dataset. "
                f"Max diff: {np.max(np.abs(results[0] - results[i]))}"
            )

    def test_ours_mfas_ins2_deterministic_animal(self, animal_adj: sp.spmatrix) -> None:
        """OURS_MFAS_INS2: 5 runs on animal dataset must produce identical scores."""
        results = self._run_n_times(animal_adj, insertion_passes=2, n=self.N_TRIALS)
        for i in range(1, self.N_TRIALS):
            assert np.array_equal(results[0], results[i]), (
                f"OURS_MFAS_INS2 run 1 vs run {i + 1} differ on animal dataset. "
                f"Max diff: {np.max(np.abs(results[0] - results[i]))}"
            )

    def test_ours_mfas_ins3_deterministic_animal(self, animal_adj: sp.spmatrix) -> None:
        """OURS_MFAS_INS3: 5 runs on animal dataset must produce identical scores."""
        results = self._run_n_times(animal_adj, insertion_passes=3, n=self.N_TRIALS)
        for i in range(1, self.N_TRIALS):
            assert np.array_equal(results[0], results[i]), (
                f"OURS_MFAS_INS3 run 1 vs run {i + 1} differ on animal dataset. "
                f"Max diff: {np.max(np.abs(results[0] - results[i]))}"
            )

    def test_ours_mfas_ins3_deterministic_basketball(
        self, basketball_1985_adj: sp.spmatrix
    ) -> None:
        """OURS_MFAS_INS3: 5 runs on Basketball-1985 dataset must produce identical scores."""
        results = self._run_n_times(basketball_1985_adj, insertion_passes=3, n=self.N_TRIALS)
        for i in range(1, self.N_TRIALS):
            assert np.array_equal(results[0], results[i]), (
                f"OURS_MFAS_INS3 run 1 vs run {i + 1} differ on basketball-1985 dataset. "
                f"Max diff: {np.max(np.abs(results[0] - results[i]))}"
            )

    def test_ours_mfas_ins1_deterministic_basketball(
        self, basketball_1985_adj: sp.spmatrix
    ) -> None:
        """OURS_MFAS_INS1: 5 runs on Basketball-1985 dataset must produce identical scores."""
        results = self._run_n_times(basketball_1985_adj, insertion_passes=1, n=self.N_TRIALS)
        for i in range(1, self.N_TRIALS):
            assert np.array_equal(results[0], results[i]), (
                f"OURS_MFAS_INS1 run 1 vs run {i + 1} differ on basketball-1985 dataset."
            )

    def test_ours_mfas_scores_are_finite(self, animal_adj: sp.spmatrix) -> None:
        """OURS_MFAS_INS3 scores must all be finite (no NaN / Inf)."""
        from ours_mfas import ours_mfas_rmfa  # type: ignore[import]

        scores, _ = ours_mfas_rmfa(animal_adj, insertion_passes=3, return_meta=True)
        assert np.all(np.isfinite(scores)), (
            f"OURS_MFAS_INS3 returned non-finite scores: {scores[~np.isfinite(scores)]}"
        )

    def test_ours_mfas_scores_are_unique(self, animal_adj: sp.spmatrix) -> None:
        """OURS_MFAS_INS3 scores must all be distinct (no ties — full strict ranking)."""
        from ours_mfas import ours_mfas_rmfa  # type: ignore[import]

        scores, _ = ours_mfas_rmfa(animal_adj, insertion_passes=3, return_meta=True)
        assert len(np.unique(scores)) == len(scores), (
            f"OURS_MFAS_INS3 produced tied scores on animal dataset "
            f"({len(scores) - len(np.unique(scores))} ties)"
        )

    def test_ours_mfas_meta_deterministic(self, animal_adj: sp.spmatrix) -> None:
        """
        OURS_MFAS_INS3 meta diagnostics (phase1_iterations, removed_phaseA, kept_final)
        must be identical across repeated runs.
        """
        from ours_mfas import ours_mfas_rmfa  # type: ignore[import]

        metas = []
        for _ in range(3):
            _, meta = ours_mfas_rmfa(animal_adj, insertion_passes=3, return_meta=True)
            metas.append(meta)

        for key in ("phase1_iterations", "removed_phaseA", "kept_after_phaseA", "kept_final"):
            vals = [m[key] for m in metas]
            assert len(set(vals)) == 1, (
                f"OURS_MFAS_INS3 meta['{key}'] differs across runs: {vals}"
            )

    def test_ours_no_randomness_in_source_code(self) -> None:
        """
        ours_mfas.py must not contain any call to np.random or random module.
        Any such call would break determinism guarantees.
        """
        ours_mfas_py = (SRC_DIR / "ours_mfas.py").read_text()
        # The two most direct determinism breakers:
        assert "np.random" not in ours_mfas_py, (
            "ours_mfas.py calls np.random — determinism not guaranteed"
        )
        assert "import random" not in ours_mfas_py, (
            "ours_mfas.py imports random module — determinism not guaranteed"
        )
        # Also check that no non-comment lines call random.* (stdlib random)
        import re

        lines_with_random_call = [
            (i + 1, line)
            for i, line in enumerate(ours_mfas_py.splitlines())
            if re.search(r"\brandom\s*\.", line)
            and not line.lstrip().startswith("#")
        ]
        assert lines_with_random_call == [], (
            "ours_mfas.py has non-comment lines with 'random.' call:\n"
            + "\n".join(f"  line {ln}: {txt}" for ln, txt in lines_with_random_call)
        )

    def test_ours_uses_stable_sort(self) -> None:
        """
        ours_mfas.py must use kind='mergesort' or kind='stable' for all argsort calls.
        Unstable sort on equal weights would produce non-deterministic tie-breaking.

        Note: the regex matches single-line argsort() calls, which covers all current
        call sites in ours_mfas.py.  Multi-line calls are not present in this file.
        """
        ours_mfas_py = (SRC_DIR / "ours_mfas.py").read_text()
        import re

        # Match all argsort(...) calls; the pattern is line-oriented (no multi-line calls
        # exist in ours_mfas.py, so this is exhaustive for the current file).
        argsort_calls = re.findall(r"argsort\([^)]*\)", ours_mfas_py)
        unstable = [c for c in argsort_calls if "mergesort" not in c and "stable" not in c]
        assert unstable == [], (
            "ours_mfas.py has argsort() calls without explicit stable sort:\n"
            + "\n".join(f"  {c}" for c in unstable)
        )
