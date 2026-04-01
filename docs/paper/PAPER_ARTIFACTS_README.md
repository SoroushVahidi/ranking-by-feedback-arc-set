# Paper Artifacts README

**Canonical reference for manuscript tables and reproducibility.**

Repository: `ranking-by-feedback-arc-set`  
Paper: *Scalable and Training-Free Ranking from Pairwise Comparisons via Acyclic Graph Construction*

---

> **Pipeline locations — which one is canonical?**
>
> There are two parallel pipeline locations in this repository, both reading from
> `GNNRank-main/paper_csv/` but writing to different output directories:
>
> | | Canonical pipeline | Root-level pipeline (this doc) |
> |---|---|---|
> | Entrypoint | `python GNNRank-main/scripts/paper/run_all_paper_artifacts.py` | `python scripts/paper/generate_paper_tables.py` |
> | Outputs | `GNNRank-main/outputs/paper_tables/` | `outputs/paper_tables/` |
> | Tests | `GNNRank-main/tests/test_experiment_table_consistency.py` | `tests/test_paper_artifacts.py` |
>
> **The canonical pipeline is `GNNRank-main/scripts/paper/run_all_paper_artifacts.py`**
> (as documented in the root `README.md`).  The root-level scripts and this README
> describe an alternative pipeline that produces equivalent outputs under the
> top-level `outputs/` directory.  Both pipelines read from the same source of
> truth (`GNNRank-main/paper_csv/leaderboard_per_method.csv`) and should produce
> identical numbers.  When in doubt, prefer the canonical pipeline.

---

## Quick reference: which files to use

| Purpose | File (root-level pipeline) | Canonical equivalent |
|---------|------|------|
| **Table 4** (full 80-dataset suite) | `outputs/paper_tables/table4_full_suite.csv` | `GNNRank-main/outputs/paper_tables/table4_full_suite.csv` |
| **Table 5** (compute-matched, 79 datasets) | `outputs/paper_tables/table5_compute_matched.csv` | `GNNRank-main/outputs/paper_tables/table5_compute_matched.csv` |
| **Table 6** (missingness audit) | `outputs/paper_tables/table6_missingness.csv` | `GNNRank-main/outputs/paper_tables/table6_missingness.csv` |
| **Table 7** (best-in-suite comparison) | `outputs/paper_tables/table7_best_in_suite.csv` | `GNNRank-main/outputs/paper_tables/table7_best_in_suite.csv` |
| **Table 8** (runtime trade-off) | `outputs/paper_tables/table8_runtime_tradeoff.csv` | `GNNRank-main/outputs/paper_tables/table8_runtime_tradeoff.csv` |
| Benchmark composition (n/m ranges) | `outputs/paper_tables/benchmark_composition.csv` | — (root-level pipeline only) |
| All key numbers in JSON | `outputs/paper_tables/paper_claims_master.json` | `GNNRank-main/outputs/paper_tables/paper_claims_master.json` |
| Master CSV (Tables 4+5 combined) | `outputs/paper_tables/paper_metrics_master.csv` | — (root-level pipeline only) |
| Dataset inventory (all 81) | `outputs/derived/dataset_inventory.csv` | — (root-level pipeline only) |
| **Canonical data source** | `GNNRank-main/paper_csv/leaderboard_per_method.csv` |

---

## Canonical data source

**`GNNRank-main/paper_csv/leaderboard_per_method.csv`** — 1468 rows, one per (dataset, method, config).

Columns:
- `dataset` — dataset name (81 unique, including 1 extra `_AUTO` entry)
- `method` — algorithm name
- `config` — config string (e.g. `trials10train_r100test_r100AllTrue`)
- `upset_simple`, `upset_naive`, `upset_ratio` — ranking quality metrics
- `kendall_tau`, `runtime_sec`, `timeout_flag` — additional metrics
- `source` — always `result_arrays`

**Do not use** `GNNRank-main/paper_tables/table1_main_leaderboard.csv` for manuscript numbers — it has `/81` denominators (includes the extra `_AUTO` dataset) and is superseded by the outputs in `outputs/paper_tables/`.

---

## How to regenerate all tables

> **Canonical pipeline:** `python GNNRank-main/scripts/paper/run_all_paper_artifacts.py` (see root `README.md`).  
> The commands below use the root-level pipeline B and produce equivalent outputs under `outputs/paper_tables/`.

```bash
# From the repository root:
python scripts/paper/generate_paper_tables.py
```

Requirements: `pandas`, `numpy`, `scipy` (for reading adjacency `.npz` files).

Install if needed:
```bash
pip install pandas numpy scipy
```

The script reads from `GNNRank-main/paper_csv/` and writes to `outputs/paper_tables/` and `outputs/derived/`.

---

## How to validate the outputs

```bash
python scripts/paper/validate_paper_artifacts.py
```

Or run the full pytest suite:
```bash
pytest tests/test_paper_artifacts.py -v
```

Expected: all checks pass.

---

## Table 4 computation logic

1. Load `leaderboard_per_method.csv`.
2. Exclude `_AUTO/Basketball_temporal__1985adj` → 80-dataset suite.
3. Filter rows where `config` contains `"trials10"`.
4. For each `(method, dataset)` pair, select the row with the **minimum `upset_simple`** (handles GNN methods with multiple K configs).
5. For each method, compute `median` and `mean` of `upset_simple`, `upset_ratio`, `upset_naive` across datasets.
6. Report `n_datasets` (rows with non-NaN `upset_simple`) and `coverage = n_datasets/80`.

For Table 5, use `leaderboard_compute_matched.csv` instead (pre-filtered to remove timed-out runs; ERO is absent → 79 datasets after excluding `_AUTO`).

---

## Dataset suite

The **80-dataset suite** (manuscript benchmark) consists of:

| Family | Count | n range | m range |
|--------|-------|---------|---------|
| Basketball coarse | 30 | 282–351 | 2904–4196 |
| Basketball finer | 30 | 282–351 | 4814–7650 |
| Football coarse | 6 | 20 | 107–226 |
| Football finer | 6 | 20 | 300–380 |
| Faculty | 3 | 113–206 | 1204–1787 |
| Animal | 1 | 21 | 193 |
| Halo | 2 | 602 | 5010 |
| Finance | 1 | 1315 | 1,729,225 |
| ERO | 1 | 350 | (synthetic) |

**Extra dataset (excluded from 80-suite):** `_AUTO/Basketball_temporal__1985adj`  
This is an auto-generated adjacency variant of the 1985 Basketball dataset and is NOT part of the manuscript benchmark.

---

## Known corrections from original manuscript draft

### 1. Football n-range
- ❌ **Old claim**: football datasets have n in range 20–107  
- ✅ **Correct**: all 12 football instances have n=20; the value 107 was an edge count (m), not n

### 2. Finance timeout
- In the `trials10` configuration, **all four OURS methods** have NaN metrics for `finance` (coverage 77/80 in Table 4).  
- In other trial configs, OURS_MFAS_INS1/2/3 complete on finance; only OURS_MFAS always times out.
- The `missingness_audit.csv` reports the cross-config view (INS variants show 80/80 there).

### 3. Classical method table values (btl / davidScore)
- An early manuscript draft had btl and davidScore values swapped and numerically wrong.
- The `outputs/paper_tables/table4_full_suite.csv` has the **correct** repo-derived values.
- Correct Table 4 values (trials10, 80-dataset suite):
  - btl: median_upset_simple = **0.984385**, coverage = 78/80
  - davidScore: median_upset_simple = **0.824138**, coverage = 78/80
- (The draft claimed btl=0.825000 and davidScore=0.925000, which were incorrect.)

### 4. _AUTO dataset
- The repository contains 81 datasets; the manuscript reports 80.
- The extra dataset is `_AUTO/Basketball_temporal__1985adj`.
- All canonical tables in `outputs/paper_tables/` exclude this dataset.

---

## Pipeline dependency map

```
GNNRank-main/result_arrays/          ← raw per-trial numpy arrays (ground truth)
         │
         ▼
GNNRank-main/paper_csv/leaderboard_per_method.csv    ← canonical source (per dataset/method)
GNNRank-main/paper_csv/leaderboard_compute_matched.csv
         │
         ▼
scripts/paper/generate_paper_tables.py
         │
         ▼
outputs/paper_tables/table4_full_suite.csv           ← Table 4 (manuscript)
outputs/paper_tables/table5_compute_matched.csv      ← Table 5
outputs/paper_tables/table6_missingness.csv          ← Table 6
outputs/paper_tables/table7_best_in_suite.csv        ← Table 7
outputs/paper_tables/table8_runtime_tradeoff.csv     ← Table 8
outputs/paper_tables/benchmark_composition.csv       ← n/m per dataset
outputs/paper_tables/paper_claims_master.json        ← all numbers as JSON
outputs/paper_tables/paper_metrics_master.csv        ← Tables 4+5 merged
outputs/derived/dataset_inventory.csv               ← all 81 datasets labelled
         │
         ▼
scripts/paper/validate_paper_artifacts.py  ← validation
tests/test_paper_artifacts.py              ← pytest suite
```

---

## Legacy files

The files in `GNNRank-main/paper_tables/` are **legacy** (generated from the original pipeline, use /81 denominators). Do not cite them in the manuscript. See `GNNRank-main/paper_tables/README.md` for their original purpose.
