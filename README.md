# Ranking by Feedback Arc Set

This repository compares **ranking by minimum feedback arc set (MFAS)** with classical ranking methods and GNN-based rankers (e.g. [GNNRank](https://github.com/SherylHYX/GNNRank), DIGRAC, ib) on directed pairwise-comparison data. All code and experiments live under **`GNNRank-main/`**, which extends the [GNNRank](https://github.com/SherylHYX/GNNRank) codebase with our method (OURS) and a full evaluation pipeline.

## What’s in this repo

- **OURS (MFAS)**: ranking via minimum feedback arc set (several variants: OURS_MFAS_INS1, INS2, INS3).
- **Classical baselines**: SpringRank, syncRank, serialRank, BTL, David’s score, PageRank, rankCentrality, SVD_RS, SVD_NRS, etc.
- **GNN rankers**: DIGRAC, ib (from the GNNRank line of work).
- **Datasets**: ERO synthetic, Basketball temporal, Football (England Premier League), animal society, faculty hiring, Head-to-Head, and others (see below).
- **Pipeline**: scripts to aggregate results from `result_arrays/`, build leaderboards, paper tables/figures, and validate artifacts.

## Quick start

### 1. Environment

From `GNNRank-main/`:

```bash
cd GNNRank-main
conda env create -f environment_GPU.yml   # or environment_CPU.yml
conda activate GNNRank
```

See **`GNNRank-main/README.md`** for detailed requirements (Python 3.6/3.7, PyTorch, PyG, etc.).

### 2. Run training and evaluation

All methods (OURS, classical, GNN) are run via the same entry point:

```bash
cd GNNRank-main/src
python train.py --dataset <name> --all_methods <methods> [options]
```

**Examples**

- Single dataset, OURS only, save predictions:
  ```bash
  python train.py --dataset football --season 2012 --all_methods OURS_MFAS_INS1 OURS_MFAS_INS2 OURS_MFAS_INS3 --SavePred --num_trials 5
  ```
- Basketball 2010, OURS + classical baselines (shorter list):
  ```bash
  python train.py --dataset basketball --season 2010 --all_methods baselines_shorter -SP
  ```
- ERO synthetic (350 nodes, default style):
  ```bash
  python train.py --dataset ERO --N 350 --all_methods OURS_MFAS_INS3 DIGRAC SpringRank --num_trials 10
  ```
- CPU only:
  ```bash
  python train.py --dataset animal --all_methods OURS_MFAS_INS3 --no-cuda --num_trials 3
  ```

**Dataset names** (as used with `--dataset`):

| Short name   | Expands to / notes |
|-------------|---------------------|
| `ERO`       | ERO synthetic (use `--N`, `--eta`, `--ERO_style` to tune) |
| `basketball`| Basketball temporal (use `--season`, e.g. 2009–2016) |
| `football`  | England Premier League (use `--season`, e.g. 2009–2012) |
| `animal`    | Dryad animal society |
| `finance`   | Finance (needs data; see GNNRank-main README) |
| `headtohead`| Halo2 Head-to-Head |
| `faculty_cs`, `faculty_business`, `faculty_history` | Faculty hiring networks |

**Method presets** (for `--all_methods`):

- `baselines_shorter` — classical + OURS (no mvr)
- `baselines_full`  — classical + OURS (with mvr)
- `all_methods_shorter` — classical + OURS + DIGRAC + ib
- `all_GNNs` — DIGRAC, ib

You can also pass explicit lists, e.g. `--all_methods OURS_MFAS_INS3 SpringRank DIGRAC`.

### 3. Build leaderboards and paper artifacts

From the **repository root** (parent of `GNNRank-main/`):

1. **Result table from saved runs** (reads `GNNRank-main/result_arrays/` and writes `paper_csv/results_from_result_arrays.csv`):
   ```bash
   python GNNRank-main/tools/build_results_table_from_result_arrays.py
   ```

2. **Leaderboard CSVs** (per-method, compute-matched, missingness audit):
   ```bash
   python GNNRank-main/tools/build_leaderboard_csvs.py
   ```
   Outputs go to `GNNRank-main/paper_csv/` (see `GNNRank-main/paper_csv/README_leaderboard_outputs.md`).

3. **Canonical manuscript-facing paper artifacts** (tables + audits + provenance):
   ```bash
   python GNNRank-main/scripts/paper/run_all_paper_artifacts.py
   ```
   Canonical outputs are written under `GNNRank-main/outputs/paper_tables/` and `GNNRank-main/outputs/audits/`.
   Legacy exports under `GNNRank-main/paper_tables/` are historical/non-canonical and should not be used for current manuscript numbers.

4. **Validate artifacts** (dataset counts, coverage, missing runtime):
   ```bash
   python GNNRank-main/tools/validate_paper_artifacts.py
   ```

## Repository layout

```
.
├── README.md                 # this file
├── GITHUB_SYNC.md            # how to sync to GitHub without large files
├── GNNRank-main/
│   ├── README.md             # original GNNRank + detailed run options
│   ├── src/                  # training and evaluation
│   │   ├── train.py          # main entry point
│   │   ├── param_parser.py   # CLI arguments
│   │   └── ...
│   ├── data/                 # datasets (some large; not all on GitHub)
│   ├── result_arrays/        # saved metrics per (dataset, method, config) — not on GitHub
│   ├── tools/                # pipeline scripts
│   │   ├── build_results_table_from_result_arrays.py
│   │   ├── build_leaderboard_csvs.py
│   │   ├── build_paper_tables.py
│   │   ├── build_paper_figs.py
│   │   ├── validate_paper_artifacts.py
│   │   └── ...
│   ├── paper_csv/            # leaderboards, unified comparison, missingness
│   ├── paper_tables/         # legacy historical table exports (non-canonical)
│   ├── paper_figs/           # figures
│   ├── docs/                 # status, audits, evidence
│   ├── execution/            # example shell scripts for batches
│   └── environment_GPU.yml   # conda env (GPU)
```

Large paths (e.g. `result_arrays/`, `data/finance/`, big logs) are listed in `.gitignore` and are not pushed to GitHub; see **`GITHUB_SYNC.md`**.

## Citation

- **GNNRank (underlying framework and GNN baselines):**
  ```bibtex
  @inproceedings{he2022gnnrank,
    title={GNNRank: Learning Global Rankings from Pairwise Comparisons via Directed Graph Neural Networks},
    author={He, Yixuan and Gan, Quan and Wipf, David and Reinert, Gesine D and Yan, Junchi and Cucuringu, Mihai},
    booktitle={ICML},
    pages={8581--8612},
    year={2022},
    organization={PMLR}
  }
  ```
- **This repository / ranking by feedback arc set:** please cite the paper that accompanies this codebase (when available) and the [GNNRank repo](https://github.com/SherylHYX/GNNRank).

## License

MIT (see **LICENSE**).
