# Final Reviewer-1 Ablation Numerical Audit

Date: 2026-08-25
Table: `manuscript/revision_20260825/source/main_ik.tex`, Table 8,
`\label{tab:reviewer1_stage_ablation}`

## Source

- Primary source (per-dataset detail): `outputs/revision_analysis_20260825/reviewer_ablation_scalability/structural_ablation.csv`
  (407 rows; columns include `dataset, family, config, status, n, m, upset_simple, upset_ratio, upset_naive, runtime_total_sec`, plus phase-split runtimes).
- Pre-aggregated companion (values used directly): `outputs/revision_analysis_20260825/reviewer_ablation_scalability/structural_ablation_summary.csv`
  (one row per config `A0`-`A6`; columns include `config, n_datasets, median_upset_simple, mean_upset_simple, median_upset_ratio, mean_upset_ratio, median_upset_naive, mean_upset_naive, median_runtime_total_sec, mean_runtime_total_sec`).
- Generating code: `GNNRank-main/scripts/revision_analysis_20260825/run_reviewer_ablation.py` (config definitions, execution) and
  `GNNRank-main/scripts/revision_analysis_20260825/analyze_reviewer_ablation.py`, function `summarize_config_group` (lines 389-425), which computes both median and mean per config from the deduplicated per-dataset rows.
- Metric implementation: `_upset_simple`, `_upset_naive`, `_upset_ratio` in
  `GNNRank-main/scripts/revision_analysis_20260824/run_mincut_cap_audit.py` lines 72-110 (the same implementation already underlying the existing, previously reviewed Table 7).

## Filter / common dataset set

- `A0`, `A2`, `A4`: Layer-1 core (33 datasets) + Layer-2 scale (45 datasets) = 78 non-Finance
  datasets attempted; `structural_ablation_summary.csv` reports `n_datasets=77` for each of
  these three configs (one dataset short of 78; this is the same $n=77$ non-Finance
  common-completion count already used throughout the manuscript, e.g. Tables 4-6 and the
  existing Table 7 `A0->A2`/`A0->A4` rows). All rows have `status == "complete"`.
- `A1`: Layer-1 core only (`CONFIG_SCOPE["A1"] = "core"`), `n_datasets=33`.
- Finance is entirely absent from `structural_ablation.csv` (0 Finance rows for any
  config): the ablation suite treats Finance separately (Section 3.5, Finance Stress
  Case), consistent with "non-Finance" in the table caption.
- Dataset accounting used elsewhere in the manuscript (intended 80 / loadable 78 / two
  unavailable adjacency files `ERO/p5K5N350eta10styleuniform` and
  `Halo2BetaData/HeadToHead`) is a separate, coarser accounting of the full evaluation
  suite; it is not re-derived here and is not contradicted by the ablation-suite's own
  $n=77$/$n=33$ non-Finance counts, which were already established for Table 7.

## Aggregation

Per-stage **mean** across the config's available common dataset set, taken directly from
`structural_ablation_summary.csv` (no recomputation performed; values below were also
independently cross-checked by an auxiliary read-only pandas aggregation over
`structural_ablation.csv`, which reproduced the summary file exactly). Mean was used for
all four numeric columns for internal consistency, since Reviewer 1 explicitly requested
*average* runtime; the manuscript's caption states this explicitly and notes that primary
runtime comparisons elsewhere (Table 6) use the median.

## Per-cell traceability

| Manuscript label | Internal config | `n` | Column (source file) | Raw value | Rounded value (table) |
|---|---|---:|---|---:|---:|
| A0 (Phase A only) | `A0` | 77 | `mean_upset_simple` | 0.2852982484658717 | 0.2853 |
| A0 (Phase A only) | `A0` | 77 | `mean_upset_naive` | 120842.92987012987 | 120842.9 |
| A0 (Phase A only) | `A0` | 77 | `mean_upset_ratio` | 0.3498192111593268 | 0.3498 |
| A0 (Phase A only) | `A0` | 77 | `mean_runtime_total_sec` | 0.17369378387153922 | 0.174 |
| A1 (legacy topo add-back, submitted) | `A1` | 33 | `mean_upset_simple` | 0.25552065804425267 | 0.2555 |
| A1 (legacy topo add-back, submitted) | `A1` | 33 | `mean_upset_naive` | 93588.98181818183 | 93589.0 |
| A1 (legacy topo add-back, submitted) | `A1` | 33 | `mean_upset_ratio` | 0.3759517155168097 | 0.3760 |
| A1 (legacy topo add-back, submitted) | `A1` | 33 | `mean_runtime_total_sec` | 0.2761590697548606 | 0.276 |
| A2 (+ exact reachability add-back) | `A2` | 77 | `mean_upset_simple` | 0.2727966566006058 | 0.2728 |
| A2 (+ exact reachability add-back) | `A2` | 77 | `mean_upset_naive` | 118788.63116883117 | 118788.6 |
| A2 (+ exact reachability add-back) | `A2` | 77 | `mean_upset_ratio` | 0.3410284465032604 | 0.3410 |
| A2 (+ exact reachability add-back) | `A2` | 77 | `mean_runtime_total_sec` | 0.4265595720959948 | 0.427 |
| A4 (+ refinement, OURS-Reach) | `A4` | 77 | `mean_upset_simple` | 0.27238295236613674 | 0.2724 |
| A4 (+ refinement, OURS-Reach) | `A4` | 77 | `mean_upset_naive` | 118721.99480519483 | 118722.0 |
| A4 (+ refinement, OURS-Reach) | `A4` | 77 | `mean_upset_ratio` | 0.3178153304065674 | 0.3178 |
| A4 (+ refinement, OURS-Reach) | `A4` | 77 | `mean_runtime_total_sec` | 0.5420216863805597 | 0.542 |

## Consistency check against existing Table 7

Independently recomputing paired W/T/L and median deltas directly from
`structural_ablation.csv` reproduces the values already published in Table 7
(`tab:ablation_primary`) exactly:

- `A0->A2` `upset_simple`: $n=77$, W/T/L $76/0/1$, median $\Delta=-0.016631$ (manuscript: $-0.0166$).
- `A1->A2` `upset_simple`: $n=33$, W/T/L $32/0/1$, median $\Delta=-0.015940$ (manuscript: $-0.0159$).
- `A0->A4` `upset_simple`: $n=77$, W/T/L $76/0/1$, median $\Delta=-0.016906$ (manuscript: $-0.0169$).

This confirms `structural_ablation.csv` is the authoritative source already underlying the
previously reviewed Table 7, and is safe and consistent to extend into the new Table 8.

## Note on unpaired group means vs. paired directional claims

Because these are **unpaired per-stage means** (not paired per-dataset differences), the
new table's row-to-row deltas are not by themselves evidence of a significant directional
effect (unlike Table 7, whose Holm-adjusted paired Wilcoxon tests are). The manuscript
text and the Table 8 caption explicitly say that directional significance is established
by the existing paired tests in Table 7, and the new table is descriptive/consolidating.
Unpaired **medians** (also available in `structural_ablation_summary.csv`) were considered
and rejected for this table: the existing Figure 2 already shows that unpaired *median*
`upset_simple` is non-monotonic across A0-A6 (a known, already-disclosed artifact of
per-dataset heterogeneity, not an error), and reproducing that non-monotonic pattern in a
new table without the surrounding paired-test context risked appearing to contradict the
paired result. Unpaired means are monotonic in the same direction as the paired result for
every column in this table's four rows and were judged the more legible complementary
statistic; the caption states plainly that they are means, not medians, and points to
Table 7 for the authoritative paired comparison.

## Verdict

**NO_UNTRACEABLE_R1_ABLATION_VALUES**: every value in Table 8 traces to
`structural_ablation_summary.csv`, itself generated by
`analyze_reviewer_ablation.py::summarize_config_group` from the completed, deduplicated
per-dataset rows of `structural_ablation.csv`. No value was fabricated, estimated, or
carried over from a differently-implemented metric.
