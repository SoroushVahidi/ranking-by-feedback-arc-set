# Reproducibility Guide

This guide shows a reviewer how to verify the revised results from a fresh clone.

Three levels of reproduction are available, from quick correctness checks to full raw experiment reruns.

---

## 1. Quick Verification (Inexpensive)

These commands verify implementation correctness and artifact consistency. They complete in seconds to a few minutes and do **not** re-run any ranking experiments.

Run from the repository root:

```bash
# --- Reachability add-back correctness tests ---
# Tests: never creates cycles, inclusion-minimality, one-pass sufficiency,
#         determinism, stable tie handling, phase toggles.
# 41 tests, completes in <1s.
python -m pytest tests/test_reachability_addback.py -v

# --- Paper artifact validation ---
# Checks: all expected CSVs/JSONs exist, coverage denominators correct
# (80 for Table 4, 78 for Table 5), method labels, dataset inventory (80 suite, 1 excluded).
# Passes 33/33 checks.
python scripts/paper/validate_paper_artifacts.py

# --- Paper artifact unit tests ---
# 21 tests: file existence, inventory counts, Table 4 structure,
# Table 5 subset constraints, benchmark composition.
python -m pytest tests/test_paper_artifacts.py -v

# --- Reviewer ablation analysis tests ---
# 4 tests: Holm monotonicity, WTL direction, dedup behavior,
#           analysis on real outputs.
python -m pytest tests/test_analyze_reviewer_ablation.py -v

# --- Full canonical artifact rebuild + consistency check ---
# Rebuilds summary CSVs from committed leaderboards, validates them,
# and runs table consistency tests. ~1-2s.
cd GNNRank-main && python scripts/paper/run_all_paper_artifacts.py && cd ..
```

**All quick verification commands pass.** If any fail, check that the committed outputs under `outputs/paper_tables/`, `outputs/audits/`, and `outputs/derived/` are present and not corrupted.

---

## 2. Regenerate Manuscript Artifacts from Committed Outputs

These commands reconstruct tables, figures, and audits from the **already-committed experimental outputs**. They do **not** re-run any ranking experiments or retrain any models.

```bash
# Regenerate final summary tables from leaderboards + audits
cd GNNRank-main && python scripts/paper/run_all_paper_artifacts.py && cd ..
# This writes to:
#   outputs/paper_tables/table4_full_suite.csv
#   outputs/paper_tables/table5_compute_matched.csv
#   outputs/paper_tables/table6_missingness.csv
#   outputs/paper_tables/table7_best_in_suite.csv
#   outputs/paper_tables/table8_runtime_tradeoff.csv
#   outputs/paper_tables/paper_claims_master.json
#   outputs/paper_tables/claim_traceability.json
#   outputs/paper_tables/provenance_manifest.json
#   outputs/paper_tables/canonical_artifacts_summary.md
```

### Figure regeneration

```bash
# Figure 1 (runtime vs. edges scatter plot)
python scripts/paper/generate_paper_tables.py --figure runtime_vs_edges

# Figure 2 (structural ablation matched-support trajectories)
# Requires the structural_ablation.csv from reviewer_ablation_scalability/
python scripts/paper/generate_paper_tables.py --figure structural_ablation
```

### Data source verification

```bash
# Verify Table 4 data source integrity
python scripts/paper/targeted_ours_positive_search.py

# Validate sparse-regime thresholding
python scripts/paper/audit_sparse_regime_robustness.py
```

**Note:** The `--figure` commands read committed CSV outputs and produce PDF figures only. They do not execute any ranking code.

---

## 3. Raw Experiment Reproduction

These commands execute the full ranking pipelines. **They are expensive** — each dataset requires seconds to minutes, and the full suite with 78 datasets across 16 methods takes hours on a modern CPU/GPU.

### OURS-Reach (canonical method)

```bash
# Run OURS-Reach on a single dataset
cd GNNRank-main/src
python train.py --dataset basketball --season 2011 \
  --all_methods OURS_MFAS_REACH --SavePred

# Parameters used in the final paper (A4 config):
#   enable_phase_b=True, addback_mode="reach"
#   enable_phase_c=True, refine_rounds=2 (R2)
#   zero_tol=0, insertion_passes=1 (P1)
#   min_cut_budget=0 (off)
#   timeout=1800 seconds
#   num_trials=10
```

### Legacy ablation variants (INS1/INS2/INS3)

```bash
# Fixed-topological proxy (NOT the canonical method)
python train.py --dataset basketball --season 2011 \
  --all_methods OURS_MFAS_INS1 OURS_MFAS_INS2 OURS_MFAS_INS3 --SavePred
```

### Classical baselines

```bash
# Run classical baselines
python train.py --dataset football --season 2012 \
  --all_methods SpringRank syncRank serialRank btl davidScore \
  PageRank rankCentrality SVD_NRS --SavePred
```

### GNN models

```bash
# Requires GPU and PyTorch Geometric
python train.py --dataset basketball --season 2010 \
  --all_methods DIGRAC ib --SavePred
```

### Reviewer ablation (full stage progression)

```bash
# Runs A0 through A6 on all common-completion datasets
cd GNNRank-main/scripts/revision_analysis_20260825
python run_reviewer_ablation.py
```

### Family-aware analysis

```bash
# Family-aware equal-family, LOFO, basketball-collapsed
cd GNNRank-main/scripts/revision_analysis_20260825
python run_family_aware_baselines.py
```

**Warnings:**
- `run_reviewer_ablation.py` runs ~50+ configurations across ~78 datasets — expect hours.
- GNN training (DIGRAC, ib) requires GPU and is significantly more expensive than classical methods.
- Finance dataset (`--dataset finance`) is a large dense graph with ~1.7M edges. It times out for OURS-Reach (77/78 coverage).
- The dataset suite has 80 intended members; 2 adjacency files are unavailable (ERO/p5K5N350eta10styleuniform, Halo2BetaData/HeadToHead). The loadable suite is 78 graphs.
- One dataset `_AUTO/Basketball_temporal__1985adj` is excluded from the suite count as it is a duplicate auto-generated variant.

---

## Canonical OURS-Reach — Minimal Example

The canonical revised method is `OURS_MFAS_REACH`, which calls `ours_mfas_rmfa` with `addback_mode="reach"`.

### Programmatic invocation

```python
import sys
sys.path.insert(0, "GNNRank-main/src")

import scipy.sparse as sp
import numpy as np
from ours_mfas import ours_mfas_rmfa

# --- Build a tiny directed weighted graph ---
# Example: 5-node tournament graph
rows = [0, 1, 2, 3, 4, 0, 2, 1, 3, 2]
cols = [1, 2, 3, 4, 0, 2, 4, 3, 4, 1]
data = [1.0, 1.0, 1.0, 1.0, 1.0, 0.8, 0.9, 0.7, 0.85, 0.75]
n = 5
A = sp.csr_matrix((data, (rows, cols)), shape=(n, n))

# --- Run OURS-Reach ---
scores, meta = ours_mfas_rmfa(
    A,
    addback_mode="reach",       # exact reachability (canonical)
    enable_phase_b=True,        # Phase B: add-back
    enable_phase_c=True,        # Phase C: refinement
    refine_rounds=2,            # R2 (adjacent-swap + ternary)
    zero_tol=0.0,
    insertion_passes=1,         # P1
    min_cut_budget=0,           # min-cut off
    timeout=1800.0,
    seed=42,
)

print("Scores:", scores)
print("Meta keys:", sorted(meta.keys()))
# meta contains: removed_edges, addback_stats, phase_c_changes,
# runtime_phase_a/b/c, keep_graph, etc.
```

### CLI invocation

```bash
# Single dataset, OURS-Reach only
cd GNNRank-main/src
python train.py --dataset animal --all_methods OURS_MFAS_REACH --SavePred --num_trials 3

# With classical baselines for comparison
python train.py --dataset animal --all_methods OURS_MFAS_REACH SpringRank syncRank --SavePred
```

**Return type:** `scores` is a numpy array of shape `(n,)` ranking scores. Higher score = higher rank. `meta` is a dict with pipeline diagnostics.

---

## Dependencies / Environment

### Core (OURS-Reach, artifact regeneration, tests)

```
Python >= 3.8
numpy
scipy
pandas
pytest
```

These are sufficient for:
- Running `ours_mfas_rmfa`
- All quick verification tests (Section 1)
- Artifact regeneration (Section 2)
- Paper table generation scripts

### Optional / GNNRank (GNN training, DIGRAC, ib)

```
PyTorch >= 1.8
torch-scatter
PyTorch Geometric (pyg)
stellargraph
```

Install via:
```bash
cd GNNRank-main
conda env create -f environment_CPU.yml   # CPU-only
conda env create -f environment_GPU.yml   # GPU with CUDA
conda activate GNNRank
```

### LaTeX (manuscript compilation)

The manuscript compiles with standard LaTeX distributions (TeX Live, MiKTeX). Required packages:
- `lmodern`, `graphicx`, `tcolorbox`, `algorithm2e`, `booktabs`
- `amsmath`, `mathtools`, `amssymb`, `amsthm`
- `tabularx`, `float`, `natbib`
- `geometry`, `hyperref`
- `apalike` bibliography style (standard)

The Springer-ready ZIP at `manuscript/Journal_of_Supercomputing_revised_manuscript_LaTeX.zip` contains all necessary source files.

---

## Artifact Provenance Map

| Artifact | Final source data | Generation/validation script | Output |
|----------|-------------------|------------------------------|--------|
| Table 4 (`upset_simple`) | `GNNRank-main/paper_csv/leaderboard_per_method.csv` | `GNNRank-main/scripts/paper/rebuild_experiment_tables.py` | `outputs/paper_tables/table4_full_suite.csv` |
| Table 5 (`upset_ratio`, compute-matched) | Same leaderboard | Same script | `outputs/paper_tables/table5_compute_matched.csv` |
| Table 6 (runtime W/T/L) | `outputs/revision_analysis_20260825/canonical_reachability_baseline_comparison/e1_runtime_wtl.csv` | `outputs/revision_analysis_20260825/canonical_reachability_baseline_comparison/` (pre-computed) | `outputs/paper_tables/table6_missingness.csv` |
| Table 7 (ablation primary tests) | `outputs/revision_analysis_20260825/reviewer_ablation_scalability/primary_pairwise_statistics.csv` | Pre-computed from ablation outputs | `outputs/paper_tables/table7_best_in_suite.csv` |
| Table 8 (stage ablation) | `outputs/revision_analysis_20260825/reviewer_ablation_scalability/structural_ablation.csv` | `outputs/revision_analysis_20260825/reviewer_ablation_scalability/` (pre-computed) | `outputs/paper_tables/table8_runtime_tradeoff.csv` |
| Figure 1 (runtime vs. edges) | `outputs/paper_tables/table8_runtime_tradeoff.csv` | `scripts/paper/generate_paper_tables.py --figure runtime_vs_edges` | `manuscript/revision_20260825/figures/fig_runtime_vs_edges.pdf` |
| Figure 2 (structural ablation) | `outputs/revision_analysis_20260825/reviewer_ablation_scalability/structural_ablation.csv` | `scripts/paper/generate_paper_tables.py --figure structural_ablation` | `manuscript/revision_20260825/figures/fig_structural_ablation.pdf` |
| Runtime provenance | `GNNRank-main/paper_csv/` | `docs/journal_supercomputing_revision_20260825/RUNTIME_PROVENANCE_AUDIT.md` | Audit document |
| Dataset denominator | `GNNRank-main/outputs/audits/canonical_dataset_inventory.csv` | `scripts/paper/validate_paper_artifacts.py` (Check 4) | Validation report |
| Corrected RankCentrality | `outputs/revision_analysis_20260825/rankcentrality_correction_20260825/rankcentrality_fixed_metrics.csv` | `GNNRank-main/scripts/revision_analysis_20260825/rerun_rankcentrality_fixed.py` | Fixed metrics CSV |

---

## Dataset Availability

| Property | Value |
|----------|-------|
| Intended suite size | 80 |
| Loadable (adjacency files present) | 78 |
| Unavailable | `ERO/p5K5N350eta10styleuniform` (missing `adj.npz`), `Halo2BetaData/HeadToHead` (missing `adj.npz`) |
| Excluded from suite | `_AUTO/Basketball_temporal__1985adj` (duplicate auto-generated variant) |
| Finance | Present but large-dense (m ≈ 1.73M edges). Times out for OURS-Reach: coverage 77/78. |
| Dataset location | `GNNRank-main/data/` (partial — not all datasets are committed to GitHub) |
| Family structure | ERO (synthetic), Basketball_temporal, Football_data_England_Premier_League, Dryad_animal_society, FacultyHiringNetworks, Halo2BetaData, finance |

**Note:** The two missing adjacency files are not derivable from other committed data. The loadable suite denominator is 78. OURS-Reach achieves 77/78 (Finance times out at the configured wall-clock budget).

---

## What to Ignore

These historical files are retained for research provenance but are **not** authoritative for the final paper:

- `GNNRank-main/paper_tables/` — legacy historical table exports (not final)
- `outputs/revision_analysis_20260824/` — pre-final revision analysis (use `20260825/`)
- `docs/journal_supercomputing_revision_20260824/` — pre-final revision audits

The canonical outputs are in `outputs/paper_tables/` and `outputs/revision_analysis_20260825/`.
