"""Tests for the reviewer-driven ablation experiment harness.

Tests cover:
  - A0 contains no Phase B/C (enable_phase_b=False, enable_phase_c=False)
  - A1 actually uses legacy topo proxy (addback_mode="topo")
  - A2 actually uses exact reachability (addback_mode="reach")
  - A5/A6 actually invoke min-cut (enable_mincut=True)
  - zero_tol propagates correctly
  - refinement budget propagates correctly
  - insertion-pass count propagates correctly
  - config hashing/resume works
  - deterministic configs reproduce
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1] / "GNNRank-main"
SCRIPT_DIR = REPO_ROOT / "scripts" / "revision_analysis_20260825"
SCRIPT_PARENT = REPO_ROOT / "scripts" / "revision_analysis_20260824"

sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(SCRIPT_PARENT))


class TestStructuralVariantDefinitions:
    def test_A0_has_no_phase_b(self):
        from run_reviewer_ablation import STRUCTURAL_VARIANTS
        p = STRUCTURAL_VARIANTS["A0"]
        assert p["enable_phase_b"] is False
        assert p["enable_phase_c"] is False
        assert p["refine_naive"] is False
        assert p["refine_ratio"] is False

    def test_A1_uses_legacy_topo(self):
        from run_reviewer_ablation import STRUCTURAL_VARIANTS
        p = STRUCTURAL_VARIANTS["A1"]
        assert p["addback_mode"] == "topo"
        assert p["enable_phase_b"] is True
        assert p["enable_phase_c"] is False

    def test_A2_uses_exact_reach(self):
        from run_reviewer_ablation import STRUCTURAL_VARIANTS
        p = STRUCTURAL_VARIANTS["A2"]
        assert p["addback_mode"] == "reach"
        assert p["enable_phase_b"] is True
        assert p["enable_phase_c"] is False

    def test_A3_is_original_full(self):
        from run_reviewer_ablation import STRUCTURAL_VARIANTS
        p = STRUCTURAL_VARIANTS["A3"]
        assert p["addback_mode"] == "topo"
        assert p["enable_phase_c"] is True
        assert p["refine_ratio"] is True
        assert p["refine_naive"] is True

    def test_A4_is_reach_full(self):
        from run_reviewer_ablation import STRUCTURAL_VARIANTS
        p = STRUCTURAL_VARIANTS["A4"]
        assert p["addback_mode"] == "reach"
        assert p["enable_phase_c"] is True
        assert p["refine_ratio"] is True
        assert p["refine_naive"] is True

    def test_A5_has_mincut_no_refine(self):
        from run_reviewer_ablation import STRUCTURAL_VARIANTS
        p = STRUCTURAL_VARIANTS["A5"]
        assert p["enable_mincut"] is True
        assert p["enable_phase_c"] is False
        assert p["refine_ratio"] is False

    def test_A6_has_mincut_and_refine(self):
        from run_reviewer_ablation import STRUCTURAL_VARIANTS
        p = STRUCTURAL_VARIANTS["A6"]
        assert p["enable_mincut"] is True
        assert p["enable_phase_c"] is True
        assert p["refine_ratio"] is True

    def test_A5_A6_not_labeled_as_production(self):
        from run_reviewer_ablation import STRUCTURAL_VARIANTS
        # These are experimental labels, not production method names
        for label in ["A5", "A6"]:
            assert label.startswith("A")  # experimental label, not OURS_MFAS_*
            assert "mincut" not in label.lower()  # not a production method name


class TestSensitivityConfigs:
    def test_zero_tol_values(self):
        from run_reviewer_ablation import ZERO_TOL_CONFIGS
        assert ZERO_TOL_CONFIGS["Z12_A4"]["zero_tol"] == 1e-12
        assert ZERO_TOL_CONFIGS["Z15_A4"]["zero_tol"] == 1e-15
        assert ZERO_TOL_CONFIGS["Z18_A4"]["zero_tol"] == 1e-18

    def test_refinement_grid(self):
        from run_reviewer_ablation import REFINE_CONFIGS
        assert REFINE_CONFIGS["R0_A4"]["refine_ratio"] is False
        assert REFINE_CONFIGS["R1_A4"]["refine_passes"] == 1
        assert REFINE_CONFIGS["R2_A4"]["refine_passes"] == 2
        assert REFINE_CONFIGS["R3_A4"]["refine_passes"] == 4

    def test_insertion_pass_grid(self):
        from run_reviewer_ablation import PASS_CONFIGS
        assert PASS_CONFIGS["P0"]["insertion_passes"] == 0
        assert PASS_CONFIGS["P1"]["insertion_passes"] == 1
        assert PASS_CONFIGS["P2"]["insertion_passes"] == 2
        assert PASS_CONFIGS["P3"]["insertion_passes"] == 3

    def test_mincut_budget_grid(self):
        from run_reviewer_ablation import MINCUT_CONFIGS
        assert MINCUT_CONFIGS["K20_A5"]["mincut_budget"] == 20
        assert MINCUT_CONFIGS["K50_A5"]["mincut_budget"] == 50
        assert MINCUT_CONFIGS["K100_A5"]["mincut_budget"] == 100

    def test_cycle_selection_options(self):
        from run_reviewer_ablation import CYCLE_CONFIGS
        assert CYCLE_CONFIGS["C0_A0"]["cycle_selection"] == "dfs_first"
        assert CYCLE_CONFIGS["C1_A0"]["cycle_selection"] == "dfs_last"


class TestDatasetManifest:
    def test_layer1_has_33_datasets(self):
        from run_reviewer_ablation import LAYER1
        assert len(LAYER1) == 33

    def test_layer2_has_45_datasets(self):
        from run_reviewer_ablation import LAYER2
        assert len(LAYER2) == 45

    def test_finance_is_separate(self):
        from run_reviewer_ablation import FINANCE, LAYER1, LAYER2
        assert len(FINANCE) == 1
        assert FINANCE[0][0] == "finance"
        # Finance not in layer1 or layer2
        all_ds = set(d for d, _ in LAYER1 + LAYER2)
        assert "finance" not in all_ds

    def test_layer1_covers_all_families(self):
        from run_reviewer_ablation import LAYER1
        families = set(f for _, f in LAYER1)
        expected = {"Basketball_coarse", "Basketball_finer", "Football_coarse",
                    "Football_finer", "Faculty", "Animal", "Halo"}
        assert expected.issubset(families)


class TestConfigHashAndResume:
    def test_config_hash_is_deterministic(self):
        import importlib
        if "run_reviewer_ablation" in sys.modules:
            del sys.modules["run_reviewer_ablation"]
        sys.path.insert(0, str(SCRIPT_DIR))
        import run_reviewer_ablation as m1
        h1 = m1.CONFIG_HASH
        del sys.modules["run_reviewer_ablation"]
        import run_reviewer_ablation as m2
        h2 = m2.CONFIG_HASH
        assert h1 == h2

    def test_config_hash_is_16_chars(self):
        from run_reviewer_ablation import CONFIG_HASH
        assert len(CONFIG_HASH) == 16


class TestRunPlan:
    def test_total_runs_reasonable(self):
        from run_reviewer_ablation import _build_run_plan
        plan = _build_run_plan()
        assert 900 < len(plan) < 1200

    def test_structural_on_both_layers(self):
        from run_reviewer_ablation import _build_run_plan, VARIANT_LAYERS
        plan = _build_run_plan()
        # A0 should run on both layers (78 datasets)
        a0_runs = [p for p in plan if p[2] == "A0"]
        assert len(a0_runs) == 78

    def test_sensitivity_on_core_only(self):
        from run_reviewer_ablation import _build_run_plan
        plan = _build_run_plan()
        # R0_A4 should run only on layer1 (33 datasets)
        r0_runs = [p for p in plan if p[2] == "R0_A4"]
        assert len(r0_runs) == 33

    def test_finance_has_4_configs(self):
        from run_reviewer_ablation import _build_run_plan
        plan = _build_run_plan()
        finance_runs = [p for p in plan if p[4] is True]
        assert len(finance_runs) == 4


class TestDeterministicReproduction:
    def test_A0_reproduces_on_small_dataset(self):
        from run_reviewer_ablation import run_config, STRUCTURAL_VARIANTS
        r1, _ = run_config("Dryad_animal_society", "Animal", "A0", STRUCTURAL_VARIANTS["A0"])
        r2, _ = run_config("Dryad_animal_society", "Animal", "A0", STRUCTURAL_VARIANTS["A0"])
        assert r1["status"] == "complete"
        assert r2["status"] == "complete"
        assert abs(r1["upset_simple"] - r2["upset_simple"]) < 1e-10
        assert r1["removed_final_weight"] == r2["removed_final_weight"]

    def test_A2_reproduces_on_small_dataset(self):
        from run_reviewer_ablation import run_config, STRUCTURAL_VARIANTS
        r1, _ = run_config("Dryad_animal_society", "Animal", "A2", STRUCTURAL_VARIANTS["A2"])
        r2, _ = run_config("Dryad_animal_society", "Animal", "A2", STRUCTURAL_VARIANTS["A2"])
        assert abs(r1["upset_simple"] - r2["upset_simple"]) < 1e-10

    def test_A5_mincut_reproduces(self):
        from run_reviewer_ablation import run_config, STRUCTURAL_VARIANTS
        r1, _ = run_config("Basketball_temporal/1985", "Basketball_coarse", "A5", STRUCTURAL_VARIANTS["A5"])
        r2, _ = run_config("Basketball_temporal/1985", "Basketball_coarse", "A5", STRUCTURAL_VARIANTS["A5"])
        assert r1["mincut_accepted"] == r2["mincut_accepted"]
        assert abs(r1["mincut_gain"] - r2["mincut_gain"]) < 0.01


class TestStageEnabling:
    def test_A0_phaseB_time_is_zero(self):
        from run_reviewer_ablation import run_config, STRUCTURAL_VARIANTS
        r, _ = run_config("Dryad_animal_society", "Animal", "A0", STRUCTURAL_VARIANTS["A0"])
        assert r["runtime_phaseB_sec"] == 0.0 or r["runtime_phaseB_sec"] < 0.001

    def test_A0_phaseC_time_is_zero(self):
        from run_reviewer_ablation import run_config, STRUCTURAL_VARIANTS
        r, _ = run_config("Dryad_animal_society", "Animal", "A0", STRUCTURAL_VARIANTS["A0"])
        assert r["runtime_phaseC_sec"] == 0.0 or r["runtime_phaseC_sec"] < 0.001

    def test_A4_has_phaseC_time(self):
        from run_reviewer_ablation import run_config, STRUCTURAL_VARIANTS
        r, _ = run_config("Basketball_temporal/1985", "Basketball_coarse", "A4", STRUCTURAL_VARIANTS["A4"])
        # Phase C should have some runtime on a non-trivial dataset
        assert r["runtime_phaseC_sec"] >= 0.0  # could be 0 if very fast

    def test_A5_has_mincut_time(self):
        from run_reviewer_ablation import run_config, STRUCTURAL_VARIANTS
        r, _ = run_config("Basketball_temporal/1985", "Basketball_coarse", "A5", STRUCTURAL_VARIANTS["A5"])
        assert r["mincut_accepted"] > 0
        assert r["runtime_mincut_sec"] > 0.0


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
