# Repository Hardening Report

## What was archived (stale manuscript-support artifacts)
Archived to `outputs/archive/legacy_manuscript_support/`:
- former `paper_tables/*` table exports
- former manuscript-support summaries from `paper_csv/` (leaderboard/missingness/unified comparison and related derived files)

Archive policy is documented in:
- `outputs/archive/legacy_manuscript_support/README.md`

## Canonical entrypoint added
- `scripts/paper/run_all_paper_artifacts.py`

This single command now runs:
1. `scripts/paper/rebuild_experiment_tables.py`
2. `scripts/paper/validate_experiment_tables.py`
3. `python -m pytest tests/test_experiment_table_consistency.py`

## Canonical-source documentation added
- `docs/paper/CANONICAL_EXPERIMENT_SOURCES.md`

Covers canonical outputs, generator scripts, upstream evidence files, dataset-count policy (81), and deprecation policy.

## Provenance metadata added
- `outputs/paper_tables/provenance_manifest.json` (central machine-readable provenance)

Includes generator path, upstream source files, generation timestamp, git commit hash, dataset-count policy, and filtering policies.

## Naming standardization applied
- Canonical method aliasing module: `scripts/paper/method_names.py`
- Canonicalization output artifact: `outputs/audits/method_name_canonicalization.json`
- Rebuild pipeline now canonicalizes method labels before aggregations.

## CI checks added
- `.github/workflows/paper_artifacts.yml`

Runs on push and workflow_dispatch:
- rebuild
- validate
- consistency pytest
- dirty-tree check to catch artifact drift after regeneration

## Commands a future agent should run first
```bash
python scripts/paper/run_all_paper_artifacts.py
```

Optional direct calls:
```bash
python scripts/paper/rebuild_experiment_tables.py
python scripts/paper/validate_experiment_tables.py
python -m pytest tests/test_experiment_table_consistency.py
```
