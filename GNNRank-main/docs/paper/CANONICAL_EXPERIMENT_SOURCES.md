# Canonical Experiment Sources (Paper-Facing)

## Canonical generated outputs (only trusted paper-facing artifacts)

### Dataset inventory
- `outputs/audits/canonical_dataset_inventory.csv`
- `outputs/audits/canonical_dataset_inventory_summary.json`

### Method naming policy
- `outputs/audits/method_name_canonicalization.json`

### Paper tables
- `outputs/paper_tables/table4_full_suite.csv`
- `outputs/paper_tables/table5_compute_matched.csv`
- `outputs/paper_tables/table6_missingness.csv`
- `outputs/paper_tables/table7_best_in_suite.csv`
- `outputs/paper_tables/table8_runtime_tradeoff.csv`

### Claims + provenance
- `outputs/paper_tables/paper_claims_master.json`
- `outputs/paper_tables/provenance_manifest.json`

## Generator scripts
- Rebuild: `scripts/paper/rebuild_experiment_tables.py`
- Validation: `scripts/paper/validate_experiment_tables.py`
- Single entrypoint: `scripts/paper/run_all_paper_artifacts.py`
- Inspection CLI: `scripts/paper/inspect_paper_artifacts.py`
- Consistency tests: `tests/test_experiment_table_consistency.py`

## Upstream source-of-truth artifacts
- Primary metrics/runtime evidence: `paper_csv/results_from_result_arrays.csv`
- Canonical suite manifest (dataset list policy source): `paper_csv/leaderboard_per_method.csv`
- Graph-size metadata evidence: `data/**/adj.npz`, `data/_AUTO/**/adj.npz`

## Dataset-count policy
- Canonical paper suite size is **81 datasets**.
- The denominator is fixed by the canonical suite manifest and must remain 81 unless the suite manifest itself is intentionally and explicitly revised.
- There is currently **no canonical 80-dataset subset** for manuscript claims.

## Deprecated/stale artifacts
- Legacy manuscript-support files were archived under:
  - `outputs/archive/legacy_manuscript_support/paper_tables/`
  - `outputs/archive/legacy_manuscript_support/paper_csv/`
- These are preserved for provenance only and must not be used for paper claims.

## Standard command
```bash
python scripts/paper/run_all_paper_artifacts.py
```
