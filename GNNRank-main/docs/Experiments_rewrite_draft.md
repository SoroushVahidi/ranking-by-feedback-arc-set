# Experiments section — draft replacement text

*(Manuscript-ready; use with the new leaderboard CSVs and tables.)*

---

## Per-method results vs oracle envelopes

**Per-method results** are the primary reported outcomes. For each method (OURS variants, each classical baseline, and each GNN variant separately), we report metrics over all datasets where that method has a valid run: median and mean of upset_simple, upset_ratio, and upset_naive, plus dataset coverage (number of datasets with valid upset_simple over total datasets). No single “best” method is chosen for the headline; the main tables are per-method leaderboards sorted by median upset_simple.

**Oracle envelopes** are for context only, not as the main claim. For each dataset we define:
- **best_classical_oracle**: the minimum upset_simple among all classical baselines on that dataset, and which method achieved it.
- **best_gnn_oracle**: the minimum upset_simple among all GNN variants on that dataset, and which method (and config) achieved it.

These oracle values are reported in `leaderboard_oracle_envelopes.csv` and may be used for secondary analyses (e.g. OURS vs best classical, OURS vs best GNN), but the manuscript’s primary tables avoid “best-of” as the headline and instead show each method’s own summary statistics.

---

## Time budget policy

- **Non-GNN methods** (classical baselines and OURS): each run is subject to a **1800 s (30 min)** wall-clock timeout. Runs that exceed this are terminated and recorded as timeouts; runtime and metrics may be missing for that (dataset, method).
- **GNN methods**: a separate, longer timeout (e.g. 7200 s) may be used for training; the exact value is stated in the code and in the missingness audit.

All time limits are enforced so that compute-matched comparisons are possible at a chosen budget (e.g. 1800 s).

---

## Compute-matched subsection (1800 s)

To compare methods under a shared compute budget, we restrict to runs that finished within **1800 s**. The **compute-matched** tables and figures are built from `leaderboard_compute_matched.csv`, which contains only rows with `runtime_sec ≤ 1800`. Coverage (how many dataset–method pairs satisfy this per method) is reported in `leaderboard_compute_matched_coverage.csv`. The manuscript should state explicitly that the compute-matched summary uses this filter and report the resulting coverage so that readers can see which methods/datasets are included.

---

## Trials and determinism

- **Classical and OURS**: Many baselines and OURS are deterministic for a given dataset and seed. When multiple trials or seeds are run, we aggregate (e.g. mean over trials) and report a single representative value per (dataset, method). The number of runs (trials × seeds) is recorded in the result pipeline (e.g. in `result_arrays` and in the leaderboard source).
- **GNN**: Training is stochastic; we run multiple trials/seeds and report mean (and optionally std) of metrics. The same aggregation is used so that per (dataset, method, config) we have one row in the per-method leaderboard.

Deterministic methods thus contribute one effective “run” per dataset after aggregation; the manuscript should state that deterministic baselines are aggregated in the same way for consistency.

---

## Missingness policy

We do **not** silently drop datasets or methods. Missingness and timeouts are recorded explicitly:

- **Missingness audit** (`missingness_audit.csv`): For each method we report the number of datasets with valid metrics, the number with valid runtime, and the number of timeouts. Finance (and any other dataset treated as a known heavy case) is listed explicitly as `finance:no_data`, `finance:timeout`, or `finance:included`, so that exclusions are visible rather than implicit.
- Tables and figures that restrict to “valid” or “compute-matched” runs should reference this audit and state that Finance-like exclusions are documented there.

---

## Reproducibility

All main tables and figures can be reproduced from the repository as follows.

1. **Leaderboard CSVs** (inputs for tables and figures):
   - `paper_csv/leaderboard_per_method.csv`
   - `paper_csv/leaderboard_oracle_envelopes.csv`
   - `paper_csv/leaderboard_compute_matched.csv`
   - `paper_csv/leaderboard_compute_matched_coverage.csv`
   - `paper_csv/missingness_audit.csv`  
   These are produced by:  
   `python tools/build_leaderboard_csvs.py`  
   (from the repository root, after `paper_csv/results_from_result_arrays.csv` exists, which is built by `python tools/build_results_table_from_result_arrays.py`.)

2. **Manuscript tables** (CSV + LaTeX):
   - `paper_tables/table1_main_leaderboard.csv`, `table1_main_leaderboard.tex`
   - `paper_tables/table2_compute_matched.csv`, `table2_compute_matched.tex`, `table2_coverage.csv`
   - `paper_tables/table3_missingness_audit.csv`, `table3_missingness_audit.tex`  
   Produced by:  
   `python tools/build_paper_tables.py`

3. **Manuscript figures**:
   - `paper_figs/accuracy_vs_runtime_scatter.png` (and .pdf)
   - `paper_figs/coverage_vs_time_budget_curve.png` (and .pdf)
   - `paper_figs/ours_vs_baseline_winloss.png` (and .pdf)  
   Produced by:  
   `python tools/build_paper_figs.py`

The experiments section can cite these script and file names so that reviewers and readers can regenerate the reported tables and figures from the same CSVs.
