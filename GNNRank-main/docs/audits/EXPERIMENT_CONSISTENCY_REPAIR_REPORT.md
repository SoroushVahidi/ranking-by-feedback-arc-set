# Experiment Consistency Repair Report

## Scope
This repair regenerates manuscript-facing experiment summaries from canonical repository artifacts, with emphasis on dataset inventory, coverage denominators, missingness/timeout behavior, best-in-suite comparisons, and runtime tradeoff summaries.

## Canonical artifacts used
- `paper_csv/results_from_result_arrays.csv` (primary per-dataset/per-method metrics + runtime evidence).
- `paper_csv/leaderboard_per_method.csv` (suite manifest used by manuscript-facing table pipeline).
- `data/**/adj.npz` and `data/_AUTO/**/adj.npz` (dataset shape/nonzero evidence for n/m range summaries).
- Legacy/stale comparison artifact: `all_methods_metrics.csv` (used only for root-cause diagnosis).

## Rebuilt canonical outputs
- `outputs/audits/canonical_dataset_inventory.csv`
- `outputs/audits/canonical_dataset_inventory_summary.json`
- `outputs/paper_tables/table4_full_suite.csv`
- `outputs/paper_tables/table5_compute_matched.csv`
- `outputs/paper_tables/table6_missingness.csv`
- `outputs/paper_tables/table7_best_in_suite.csv`
- `outputs/paper_tables/table8_runtime_tradeoff.csv`
- `outputs/paper_tables/paper_claims_master.json`

## Canonical dataset inventory findings
- Corrected canonical suite size: **81 datasets**.
- Family counts (from canonical manifest):
  - Basketball_temporal: 60
  - Football_data_England_Premier_League: 12
  - FacultyHiringNetworks: 3
  - Halo2BetaData: 2
  - Dryad_animal_society: 1
  - finance: 1
  - ERO: 1
  - _AUTO: 1
- Football family n/m range (from `adj.npz`): **n=20..20, m=107..380**.
- Noted special cases:
  - One `_AUTO` dataset appears directly in the canonical suite.
  - One singleton/special dataset (`ERO/p5K5N350eta10styleuniform`) appears only through non-manuscript method rows and affects denominator if not filtered.

## Contradictions found and root causes
1. **Coverage denominator drift (80 vs 81).**
   - Root cause: manuscript-facing summaries used mixed denominator assumptions; canonical suite manifest is 81 datasets.
   - Effect: compute-matched and missingness percentages/coverage strings that used 80 are stale.

2. **Classical baseline Table-4 contradictions.**
   - Root cause: stale artifact contamination from `all_methods_metrics.csv`, which contains method-level values inconsistent with repository truth for classical methods.
   - Evidence: in `all_methods_metrics.csv`, btl and davidScore aggregate levels are effectively swapped relative to result-array truth (btl ≈ davidScore and vice versa).

3. **Possible method-label swap (BTL vs DavidScore).**
   - Outcome: **confirmed in stale artifact path** (`all_methods_metrics.csv`), **not present** in rebuilt canonical outputs.

4. **Finance timeout claim should be variant-specific.**
   - Outcome: confirmed variant/config dependence in `table6_missingness.csv` and `paper_claims_master.json`; `trials1` variants complete while `trials10` OURS variants are timeout/missing-runtime.

## Reruns
- No heavy benchmark reruns were performed.
- Only lightweight summary regeneration/validation scripts were executed.

## Reproduction commands
1. Rebuild all experiment-side canonical tables/audits:
   - `python scripts/paper/rebuild_experiment_tables.py`
2. Validate consistency invariants:
   - `python scripts/paper/validate_experiment_tables.py`
   - `python -m pytest tests/test_experiment_table_consistency.py`

## Remaining experimental risks
- The canonical suite currently includes one special singleton dataset through legacy rows; manuscript writers should explicitly document inclusion policy when reporting denominators.
- Some datasets have no directly readable `adj.npz` in primary family path and are resolved via `_AUTO` mirrors; this is now explicit in inventory notes.
- Any downstream manuscript tables should source numbers strictly from `outputs/paper_tables/*.csv` and `outputs/paper_tables/paper_claims_master.json` to avoid stale precomputed aggregates.
