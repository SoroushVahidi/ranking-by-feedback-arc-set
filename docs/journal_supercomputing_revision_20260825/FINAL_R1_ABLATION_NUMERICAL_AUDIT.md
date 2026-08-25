# Final Reviewer-1 Ablation Numerical Audit

Date: 2026-08-25 (revised: matched-support panels replace the earlier single mixed-support
table)
Table: `manuscript/revision_20260825/source/main_ik.tex`, Table 8,
`\label{tab:reviewer1_stage_ablation}`

## Revision note

The earlier version of this audit (and of Table 8) reported A0/A1/A2/A4 in one table where
A0/A2/A4 used the $n=77$ non-Finance common-completion set but A1 used its native $n=33$
scope -- i.e., A1's row was not on the same dataset support as the other rows, so
row-to-row means were not strictly comparable. This revision replaces that single table
with two panels, each computed on one exact common dataset-ID intersection, per
`FINAL_R1_COMMON_SUPPORT_AUDIT.md`.

## Source

- Primary per-dataset detail (unchanged upstream source): `outputs/revision_analysis_20260825/reviewer_ablation_scalability/structural_ablation.csv`.
- New re-aggregation, computed directly from the above with explicit common-support
  restriction (not reused from the old mixed-support summary CSV):
  - Per-dataset detail: `outputs/revision_analysis_20260825/reviewer_ablation_scalability/r1_common_support_stage_ablation.csv` (330 rows: 3 configs x 33 datasets for Panel A, 3 configs x 77 datasets for Panel B = 99 + 231 = 330).
  - Aggregated: `outputs/revision_analysis_20260825/reviewer_ablation_scalability/r1_common_support_stage_ablation_summary.csv` (6 rows: one per (panel, config)).
- Metric implementation (unchanged): `_upset_simple`, `_upset_naive`, `_upset_ratio` in
  `GNNRank-main/scripts/revision_analysis_20260824/run_mincut_cap_audit.py` lines 72-110.
- No ranking algorithm was re-run and no new experiment was executed. The re-aggregation
  script only reads `structural_ablation.csv`, restricts each config's per-dataset rows to
  the exact panel-level common-support dataset-ID set, and computes `statistics.mean`
  (and, for audit-only cross-checking, `statistics.median`) in Python's standard library.

## Common dataset support per panel

| Panel | Support set | Exact n | Verification |
|---|---|---:|---|
| (a) legacy INS progression | `S_legacy = A0 ∩ A1 ∩ A3` | 33 | `S_legacy == A1 == A3` as dataset-ID sets (verified by exact set equality, symmetric difference empty) |
| (b) canonical reachability progression | `S_canonical = A0 ∩ A2 ∩ A4` | 77 | `S_canonical == A0 == A2 == A4` as dataset-ID sets |

Every row within a panel uses the identical dataset-ID list (sorted lexicographically in
the detail CSV for reproducibility). No row within a panel is computed over a differently
sized or differently composed dataset set than its panel-mates. Finance is absent from
both panels (0 Finance rows in `structural_ablation.csv` for any config), consistent with
"non-Finance" throughout.

## Aggregation

Per-stage **mean** across the panel's exact common support, for `upset_simple`,
`upset_naive`, `upset_ratio`, and `runtime_total_sec`. Mean (not median) is used
throughout for internal consistency, since Reviewer 1 explicitly requested *average*
runtime; medians were also computed for audit-only cross-checking (present in
`r1_common_support_stage_ablation_summary.csv`) but are not published in the manuscript
table.

## Per-cell traceability

### Panel (a): legacy INS progression, common $n=33$

| Manuscript row | Config | Column | Raw value | Rounded (table) |
|---|---|---|---:|---:|
| A0 (Phase A only) | `A0` restricted to `S_legacy` | mean `upset_simple` | 0.25714780007121957 | 0.2571 |
| A0 (Phase A only) | `A0` restricted to `S_legacy` | mean `upset_naive` | 93621.19393939394 | 93621.2 |
| A0 (Phase A only) | `A0` restricted to `S_legacy` | mean `upset_ratio` | 0.3761791209401462 | 0.3762 |
| A0 (Phase A only) | `A0` restricted to `S_legacy` | mean `runtime_total_sec` | 0.14833916317332874 | 0.148 |
| + legacy topo/INS add-back | `A1` | mean `upset_simple` | 0.25552065804425267 | 0.2555 |
| + legacy topo/INS add-back | `A1` | mean `upset_naive` | 93588.98181818181 | 93589.0 |
| + legacy topo/INS add-back | `A1` | mean `upset_ratio` | 0.37595171551680967 | 0.3760 |
| + legacy topo/INS add-back | `A1` | mean `runtime_total_sec` | 0.2761590697548606 | 0.276 |
| + legacy refinement (full pipeline) | `A3` | mean `upset_simple` | 0.25209486303084516 | 0.2521 |
| + legacy refinement (full pipeline) | `A3` | mean `upset_naive` | 93548.8303030303 | 93548.8 |
| + legacy refinement (full pipeline) | `A3` | mean `upset_ratio` | 0.34623790930341836 | 0.3462 |
| + legacy refinement (full pipeline) | `A3` | mean `runtime_total_sec` | 0.37836376825968426 | 0.378 |

### Panel (b): canonical reachability progression, common $n=77$

| Manuscript row | Config | Column | Raw value | Rounded (table) |
|---|---|---|---:|---:|
| A0 (Phase A only) | `A0` restricted to `S_canonical` | mean `upset_simple` | 0.28529824846587176 | 0.2853 |
| A0 (Phase A only) | `A0` restricted to `S_canonical` | mean `upset_naive` | 120842.92987012987 | 120842.9 |
| A0 (Phase A only) | `A0` restricted to `S_canonical` | mean `upset_ratio` | 0.3498192111593268 | 0.3498 |
| A0 (Phase A only) | `A0` restricted to `S_canonical` | mean `runtime_total_sec` | 0.17369378387153922 | 0.174 |
| + exact reachability add-back | `A2` | mean `upset_simple` | 0.27279665660060576 | 0.2728 |
| + exact reachability add-back | `A2` | mean `upset_naive` | 118788.63116883117 | 118788.6 |
| + exact reachability add-back | `A2` | mean `upset_ratio` | 0.3410284465032605 | 0.3410 |
| + exact reachability add-back | `A2` | mean `runtime_total_sec` | 0.4265595720959948 | 0.427 |
| + refinement (OURS-Reach) | `A4` | mean `upset_simple` | 0.27238295236613674 | 0.2724 |
| + refinement (OURS-Reach) | `A4` | mean `upset_naive` | 118721.9948051948 | 118722.0 |
| + refinement (OURS-Reach) | `A4` | mean `upset_ratio` | 0.31781533040656745 | 0.3178 |
| + refinement (OURS-Reach) | `A4` | mean `runtime_total_sec` | 0.5420216863805597 | 0.542 |

Panel (b) is numerically identical to the previous (single-table) pass's A0/A2/A4 values,
because `S_canonical` equals A0/A2/A4's full native 77-dataset scope -- restricting to the
common set changed nothing for these three configs. Only Panel (a)'s A0 row changed:
previously A0 was reported on its full 77-dataset scope (mean `upset_simple` 0.2853); it
is now correctly restricted to the 33-dataset legacy scope shared with A1/A3 (mean
`upset_simple` 0.2571), which is the scientifically valid comparison for that panel.

## Consistency check against existing Table 7

Table 7's paired tests are unaffected by this change (they already used matched pairs:
`A0->A2`/`A0->A4` at $n=77$, `A1->A2` at $n=33$ via paired intersection, which was already
support-matched at the pair level). This table-8 revision brings the *group-level means*
into the same discipline Table 7's paired tests already followed.

## Note on unpaired means vs. paired directional claims (unchanged from prior audit)

These remain unpaired per-panel means, not paired per-dataset differences. Directional
significance is established by Table 7's paired Holm-adjusted Wilcoxon tests, not by
Table 8's descriptive per-stage means. Within each panel, the three rows are monotonic in
the expected direction for every column (Panel (a): `upset_simple`
0.2571→0.2555→0.2521; `upset_naive` 93621.2→93589.0→93548.8; `upset_ratio`
0.3762→0.3760→0.3462; mean runtime 0.148→0.276→0.378 s. Panel (b): `upset_simple`
0.2853→0.2728→0.2724; `upset_naive` 120842.9→118788.6→118722.0; `upset_ratio`
0.3498→0.3410→0.3178; mean runtime 0.174→0.427→0.542 s), which is expected now that each
panel's rows share identical dataset composition.

## Validation

- All rows in each panel use identical dataset IDs (verified by exact Python set
  equality: `S_legacy == A1 == A3`, `S_canonical == A0 == A2 == A4`).
- No duplicate `(config, dataset)` pairs in any config's rows.
- No missing datasets, no missing metric values, no NaNs in any of `upset_simple`,
  `upset_naive`, `upset_ratio`, `runtime_total_sec` for any row used.
- Runtime definition consistent throughout (`runtime_total_sec`, the same field used by
  the previous pass and by `structural_ablation_summary.csv`).
- Metric definitions consistent throughout (single implementation, `run_mincut_cap_audit.py`
  lines 72-110, for all five configs -- no mixing with the separately-scored GNNRank
  canonical `calculate_upsets` values that feed Tables 4-6).

`LEGACY_PANEL_COMMON_SUPPORT = PASS`
`CANONICAL_PANEL_COMMON_SUPPORT = PASS`
`NO_UNTRACEABLE_R1_ABLATION_VALUES = PASS`
