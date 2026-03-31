# How To Look Up a Paper Number

Start here:

```bash
python scripts/paper/run_all_paper_artifacts.py
```

Then use the inspection CLI:

```bash
python scripts/paper/inspect_paper_artifacts.py summary
python scripts/paper/inspect_paper_artifacts.py list-tables
```

## Example 1: Find the source of a Table 4 row

```bash
python scripts/paper/inspect_paper_artifacts.py trace-row \
  --table table4_full_suite \
  --method davidScore \
  --config trials10train_r100test_r100AllTrue
```

This prints the canonical row and points to upstream source `paper_csv/results_from_result_arrays.csv`.

## Example 2: Verify dataset count

```bash
python scripts/paper/inspect_paper_artifacts.py summary
```

Cross-check with:
- `outputs/audits/canonical_dataset_inventory_summary.json` (`canonical_dataset_count`)
- policy is fixed at 81 unless explicitly changed.

## Example 3: Inspect best-in-suite inputs

```bash
python scripts/paper/inspect_paper_artifacts.py explain-best \
  --dataset Basketball_temporal/1985
```

This prints the corresponding `table7_best_in_suite.csv` row.

## Example 4: Inspect runtime/speedup input row

```bash
python scripts/paper/inspect_paper_artifacts.py explain-runtime \
  --dataset Basketball_temporal/1985
```

This prints the corresponding `table8_runtime_tradeoff.csv` row.

## Example 5: Explain coverage denominator for a table row

```bash
python scripts/paper/inspect_paper_artifacts.py explain-coverage \
  --table table5_compute_matched \
  --method SpringRank \
  --config trials10train_r100test_r100AllTrue
```

## Example 6: Inspect provenance for a generated output

```bash
python scripts/paper/inspect_paper_artifacts.py provenance \
  --output-file outputs/paper_tables/table4_full_suite.csv
```

## Notes
- Use only files under `outputs/paper_tables/` and `outputs/audits/` for paper-facing numbers.
- Legacy files under `outputs/archive/legacy_manuscript_support/` are provenance-only.
