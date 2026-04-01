# Repository Organization and Repair Report

**Date:** 2024 (post-submission audit)  
**Repository:** `ranking-by-feedback-arc-set`  
**Paper:** *Scalable and Training-Free Ranking from Pairwise Comparisons via Acyclic Graph Construction*

---

## Executive Summary

A post-submission audit identified four categories of inconsistency between the manuscript's claimed numerical values and the repository's computed artifacts. This report documents each finding, its root cause, the corrective action taken, and the canonical files to use going forward.

---

## 1. Extra Dataset (_AUTO)

### Finding
The repository contains **81 datasets** across all experiment outputs, but the manuscript claims **80 datasets**. The extra dataset is:

```
_AUTO/Basketball_temporal__1985adj
```

### Root Cause
During an automated preprocessing step, an adjacency-matrix variant of the 1985 Basketball dataset was generated and placed in the `_AUTO/` subdirectory. This auto-generated dataset was inadvertently included in some experiment runs and summary tables. It is a derived artifact (not an independent dataset), duplicating information already present in `Basketball_temporal/1985`.

### Correction
All canonical tables in `outputs/paper_tables/` exclude `_AUTO/Basketball_temporal__1985adj`. The 80-dataset suite used in the manuscript consists exclusively of the real datasets.

### Evidence
- `outputs/derived/dataset_inventory.csv`: column `in_80_suite = False` for the _AUTO entry
- `outputs/paper_tables/table4_full_suite.csv`: denominator is /80 throughout
- `GNNRank-main/paper_tables/table1_main_leaderboard.csv` (legacy): uses /81 denominators — **do not use for manuscript**

---

## 2. Classical-Method Table Values (btl / davidScore swap)

### Finding
The early manuscript draft of Table 4 reported the following values for classical methods:

| Method | Claimed median_upset_simple | Claimed coverage |
|--------|----------------------------|-----------------|
| BTL | 0.825000 | 78/80 |
| DavidScore | 0.925000 | 78/80 |

The correct values from the repository are:

| Method | Correct median_upset_simple | Correct coverage |
|--------|----------------------------|-----------------|
| btl | **0.984385** | 78/80 |
| davidScore | **0.824138** | 78/80 |

### Root Cause
Two distinct errors were compounded:

1. **Label swap**: The values for `btl` and `davidScore` were swapped in the draft table. `davidScore`'s value (≈0.824) was reported under the BTL row, and a wrong value was reported under DavidScore.

2. **Stale draft**: The manuscript table was built from an intermediate version of the analysis pipeline that used a different aggregation logic or a subset of results, not the final `leaderboard_per_method.csv`. When the canonical data source was finalised, the manuscript table was not updated.

### Pattern
The BTL/DavidScore swap is the most egregious error, but other classical method values in the draft also appear shifted or wrong. The pattern is consistent with the manuscript table having been built from a pivoted/transposed intermediate data structure where method indices were misaligned.

### Correction
All values in `outputs/paper_tables/table4_full_suite.csv` are re-derived directly from `GNNRank-main/paper_csv/leaderboard_per_method.csv` using the procedure documented in `scripts/paper/generate_paper_tables.py`. The computation is:

1. Filter to 80-dataset suite (exclude `_AUTO`)
2. Filter to `trials10` config
3. Pick best config per (method, dataset) by minimum `upset_simple`
4. Compute median and mean across datasets per method

This is fully reproducible; see `scripts/paper/generate_paper_tables.py`.

---

## 3. Football n-range Claim

### Finding
The manuscript claimed: *"Football instances have n in the range 20–107."*

**This is incorrect.** All 12 football instances (6 coarse + 6 finer) have **n = 20**. The value 107 is an *edge count* (m), not a node count.

### Evidence

From reading adjacency `.npz` files:

| Dataset | n (nodes) | m (edges) |
|---------|-----------|-----------|
| England_2009_2010 | 20 | 215 |
| England_2010_2011 | 20 | 219 |
| England_2011_2012 | 20 | 226 |
| England_2012_2013 | 20 | 216 |
| England_2013_2014 | 20 | 222 |
| England_2014_2015 | 20 | **107** ← this is m, not n |
| finerEngland_2009_2010 | 20 | 380 |
| finerEngland_2010_2011 | 20 | 380 |
| finerEngland_2011_2012 | 20 | 380 |
| finerEngland_2012_2013 | 20 | 380 |
| finerEngland_2013_2014 | 20 | 380 |
| finerEngland_2014_2015 | 20 | 300 |

England_2014_2015 has only 107 edges (one season had fewer matches recorded), which explains the outlier value. This was confused with n in the manuscript.

### Root Cause
Likely a copy-paste error when summarising dataset statistics: the edge count of the smallest football graph (107) was reported in the n-range instead of the m-range.

### Correction
The correct description is: *"All football instances have n = 20 (Premier League teams). Edge counts range from 107 to 380."*

This is documented in:
- `outputs/paper_tables/benchmark_composition.csv` (per-dataset n, m)
- `outputs/paper_tables/paper_claims_master.json` → `football_n_range_note`

---

## 4. Finance Timeout Finding

### Finding
The manuscript and code comments stated that only `OURS_MFAS` times out on the finance dataset (n=1315, m=1,729,225), while `OURS_MFAS_INS1/2/3` complete.

### Investigation
In the `trials10` configuration (the primary benchmark), **all four OURS methods** (`OURS_MFAS`, `OURS_MFAS_INS1`, `OURS_MFAS_INS2`, `OURS_MFAS_INS3`) have `NaN` `upset_simple` for the finance dataset, resulting in coverage = 77/80 for each in Table 4.

The `missingness_audit.csv` reports a different view — across all trial configurations:
- `OURS_MFAS`: 77/80 valid (always times out on finance)
- `OURS_MFAS_INS1/2/3`: 80/80 valid (complete on finance in some non-trials10 config)

### Root Cause
The statement "INS variants complete on finance" is true in a limited sense (they complete in non-trials10 configs), but for the `trials10` benchmark used in Table 4, finance is missing for all OURS methods.

The most likely explanation is that INS variants complete on finance when using `trials1` (single trial, less overhead), but time out under the `trials10` setting used for the primary results.

### Correction
Table 4 correctly shows coverage = 77/80 for all four OURS methods. The `paper_claims_master.json` contains an accurate note explaining both the trials10 view and the cross-config view.

---

## 5. Files Reorganized

### New directory structure created

```
outputs/
  paper_tables/           ← canonical manuscript tables (new, authoritative)
    table4_full_suite.csv
    table5_compute_matched.csv
    table6_missingness.csv
    table7_best_in_suite.csv
    table8_runtime_tradeoff.csv
    benchmark_composition.csv
    benchmark_family_summary.csv
    paper_metrics_master.csv
    paper_claims_master.json
  derived/
    dataset_inventory.csv  ← all 81 datasets with family labels
  audits/
    validation_report.json ← output of validate_paper_artifacts.py

scripts/
  paper/
    generate_paper_tables.py    ← main table generation script
    validate_paper_artifacts.py ← validation script
    __init__.py

docs/
  paper/
    PAPER_ARTIFACTS_README.md   ← this file's companion
  audits/
    REPO_ORGANIZATION_AND_REPAIR_REPORT.md  ← this file

tests/
  test_paper_artifacts.py  ← pytest test suite (21 tests, all passing)
```

### Existing files preserved

All files in `GNNRank-main/paper_tables/` and `GNNRank-main/paper_csv/` are preserved unchanged. They serve as:
- Provenance trail for how the canonical source CSV was built
- Legacy reference for earlier pipeline stages

**Do not delete** any existing files; the new canonical outputs in `outputs/paper_tables/` are additions, not replacements.

---

## 6. Validation Results

Running `python scripts/paper/validate_paper_artifacts.py`:
```
Validation summary: 33 passed, 0 failed, 0 warnings
```

Running `pytest tests/test_paper_artifacts.py -v`:
```
21 passed in 0.33s
```

---

## 7. How to Reproduce Everything from Scratch

```bash
# 1. Install dependencies
pip install pandas numpy scipy pytest

# 2. Generate all canonical tables
python scripts/paper/generate_paper_tables.py

# 3. Validate
python scripts/paper/validate_paper_artifacts.py

# 4. Run tests
pytest tests/test_paper_artifacts.py -v
```

All scripts must be run from the **repository root**.

---

## 8. Summary Table of Corrections

| # | Issue | Old (manuscript draft) | Correct (repo) | Canonical file |
|---|-------|----------------------|----------------|----------------|
| 1 | Dataset count | 81 in some tables | 80 (exclude _AUTO) | `table4_full_suite.csv` |
| 2 | btl median | 0.825000 | **0.984385** | `table4_full_suite.csv` |
| 2 | davidScore median | 0.925000 | **0.824138** | `table4_full_suite.csv` |
| 3 | Football n-range | 20–107 | **n=20 for all 12** | `benchmark_composition.csv` |
| 4 | Finance timeout | Only OURS_MFAS | All OURS in trials10 | `paper_claims_master.json` |
