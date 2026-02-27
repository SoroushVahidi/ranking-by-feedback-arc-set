# Delta explanation: OURS vs GNNRank in manuscript vs current benchmark

## 1) GNN baseline used in the repo

### What the tables/CSVs use

- **DIGRACib only.** The comparison target in the repo’s tables and CSVs is the single method **DIGRACib**, not “ib only”, not “DIGRAC only”, and not “best-of” over multiple GNN variants.
- **Sources:**
  - `paper_csv/results_table.csv`: one row per (dataset, method, which) for DIGRACib; only two datasets have GNN: **Dryad_animal_society**, **finance**.
  - `build_all_methods_metrics.py` and `build_all_methods_losses.csv.py`: they add GNN by reading `paper_csv/results_table.csv` and taking rows with `method == "DIGRACib"` and `which == "upset"`. So the merged tables (`all_methods_metrics.csv`, `all_methods_losses.csv`) use **DIGRACib only** as the GNN baseline.

### How “best GNN” is defined (and where it is not)

- **In the main table pipeline:** “Best GNN” is **not** chosen. The tables use the single DIGRACib aggregate from `results_table.csv`.
- **In `compute_wtl_by_metric.py`:**
  - **Intent:** “Best GNN” = one variant per dataset with **minimum `upset_simple_mean`** among these four methods in the same CSV:  
    `DIGRAC_dist`, `DIGRAC_proximal_baseline`, `ib_dist`, `ib_proximal_baseline`  
    (see lines 79–83 and 174–191 in `compute_wtl_by_metric.py`).
  - **Candidates:** Those four method names.
  - **Metric:** `upset_simple_mean` (min = best).
  - **Runs:** The script expects this to come from `full_833614_metrics_best.csv` (same as OURS). So “across what runs” = same runs as the benchmark that produced that CSV.
  - **Current limitation:** `full_833614_metrics_best.csv` contains **no GNN rows** (only classical + OURS). So with the current artifacts, the “best GNN” branch in `compute_wtl_by_metric.py` never gets any data; all OURS-vs-best-GNN counts would be empty/NaN. The script also expects `per_dataset_summary.csv` (deleted), which previously held `best_gnn_method`, `best_gnn_upset_simple`, etc.

**Conclusion (1):** The repo’s **actual** comparison target in tables/CSVs is **DIGRACib only**. There is no in-repo script that currently computes or writes “best-of multiple GNN variants” for the benchmark; that logic exists only in `compute_wtl_by_metric.py`, which is effectively unused for GNN because the input CSV has no GNN rows and `per_dataset_summary.csv` is missing.

---

## 2) Mode A vs Mode B and data limitation

### Evaluation modes

- **Mode A (paper-style / GNNRank-style):** For basketball (30 seasons) and football (6 seasons), **first** average GNN results over seasons (30 and 6 respectively), **then** compare methods on these season-averaged losses.
- **Mode B (current repo per-dataset):** Compare OURS vs GNN **per season/dataset** (no season averaging).

### Data limitation

- GNN (DIGRACib or any variant) appears in the repo **only** for **Dryad_animal_society** and **finance** (in `paper_csv/results_table.csv` and `paper_csv/results_table_clean.csv`). There are **no** GNN per-season metrics for basketball or football in any CSV or in `result_arrays/` (no Basketball_temporal / Football .npy files in the repo).
- So **Mode A vs Mode B for OURS vs GNN** on basketball/football **cannot be computed from current repo artifacts**. For the two datasets with GNN, there is only one “season” each, so Mode A and Mode B are identical.

### What we can compute

- **OURS vs best classical** on basketball (30 seasons) and football (6 seasons) in both modes, to show how **season-averaging vs per-season** changes WTL and gaps (as a proxy for the effect of evaluation mode).
- **OURS vs DIGRACib** for the two datasets that have GNN (Dryad_animal_society, finance), in the only possible mode (per-dataset ≈ single “season”).

The script `delta_mode_a_vs_b.py` (see below) does the above and reports:
- OURS vs best-GNN (where available) and OURS vs best-classical WTL (win/loss/tie with tie tolerance 1e-6) and median/mean gaps for `upset_simple` and `upset_ratio`.
- For OURS vs best-classical, the **top 10 datasets (seasons)** where the “winner” (OURS vs best classical) differs between Mode A and Mode B (see script for exact definition).

---

## 3) Conclusion: what drives the change

From repo artifacts only:

1. **Season-averaging vs per-season (i)**  
   The manuscript’s “GNNRank-style” reporting (Mode A) averages over 30 basketball and 6 football seasons before comparing. The current benchmark (Mode B) compares per season. That can change win/loss counts and mean/median gaps. We **cannot** quantify this for OURS vs GNN on basketball/football because GNN per-season results are not in the repo. We **can** (and the script does) quantify it for OURS vs best-classical, showing that the choice of mode changes outcomes and which seasons “flip” the winner.

2. **Choice of GNN baseline (ii)**  
   The **tables** use **DIGRACib only**. The previous manuscript may have compared to a **best-of** GNN variant per dataset (or a different single variant). If the manuscript used a stronger “best-of” GNN and the current benchmark uses only DIGRACib, that would make OURS look better in the manuscript than in the current benchmark (or the opposite if the manuscript used a weaker baseline). So **(ii)** is a plausible driver.

3. **Precision/rounding (iii)**  
   Non-GNN metrics in the repo come from parsing logs (e.g. `extract_metrics_to_csv.py` from `full_833614.out`) and are stored with limited precision (e.g. 2 decimals in printed tables). GNN values in `results_table.csv` have full float precision. A small precision/rounding mismatch could affect tie counts; the script uses a 1e-6 tie tolerance to be consistent.

4. **Timeouts/budgets/early-stopping (iv)**  
   These are fixed in code (`src/train.py`: non-GNN 1800s, GNN 7200s) and in `param_parser.py` (e.g. seeds). If the manuscript used different timeouts or stopping rules, that could change who “wins” on some datasets. This is not re-computable from CSVs alone; it would require comparing run configs to the manuscript.

**Summary:** The main factors that can explain why OURS looked much better than GNNRank in the previous manuscript but not in the current benchmark are: **(i)** evaluation mode (season-averaging vs per-season) and **(ii)** which GNN baseline is used (single DIGRACib vs best-of or another variant). **(iii)** and **(iv)** are secondary without access to the exact manuscript pipeline and run configs.

---

## Scripts and paths used

| Purpose | Script / path |
|--------|----------------|
| GNN baseline in tables | `build_all_methods_metrics.py`, `build_all_methods_losses.csv.py` → read `paper_csv/results_table.csv` (DIGRACib only) |
| “Best GNN” logic (unused with current data) | `compute_wtl_by_metric.py` (lines 79–83, 174–204); expects `full_833614_metrics_best.csv` (no GNN rows) and `per_dataset_summary.csv` (deleted) |
| OURS metrics | `full_833614_metrics_best.csv` (method `OURS_MFAS_INS3`) |
| GNN metrics (2 datasets) | `paper_csv/results_table.csv` (method `DIGRACib`, `which == "upset"`) |
| Mode A vs Mode B and WTL/gaps | `delta_mode_a_vs_b.py` (run from `GNNRank-main`: `python delta_mode_a_vs_b.py`) |
| Tie tolerance | 1e-6 (as requested; script uses this for all metrics) |

Computed numbers are produced by running `delta_mode_a_vs_b.py`; see its stdout and `delta_mode_a_vs_b_summary.csv`.

### Computed numbers (from `python delta_mode_a_vs_b.py`)

- **OURS vs best classical**
  - **Mode B (per-dataset, 77 datasets):** upset_simple: wins=3, ties=37, losses=37; median gap=0, mean gap≈0.144. upset_ratio: wins=0, ties=2, losses=75; median gap=0.09, mean gap≈0.085.
  - **Mode A (season-averaged):** Basketball_30: upset_simple **win** (gap≈−0.00067), upset_ratio loss (gap≈0.049). Football_6: upset_simple **tie**, upset_ratio loss (gap≈0.028).
- **OURS vs DIGRACib:** Only **1** dataset (Dryad_animal_society) has both OURS and GNN in the repo; finance has no OURS row in `full_833614_metrics_best.csv`. For Dryad: OURS wins on both metrics (gap_simple≈−0.53, gap_ratio≈−0.34).
- **Top 10 flips (OURS vs best classical, Mode A vs Mode B):** England_2010_2011 (Football): Mode A tie, Mode B win; England_2012_2013: Mode A tie, Mode B loss; 8 Basketball seasons (1985–1992): Mode A win, Mode B tie (per-season OURS ties classical).
