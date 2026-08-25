# Final Reviewer-1 Common-Support Audit

Date: 2026-08-25
Checkpoint before this pass: git tag `checkpoint-before-common-support-fix` at
`31d91fade0c85ae31d9e91a2a4ba35c0f8631a74`.

## Trigger

Independent inspection of the previous `final_submission_package.zip` found that Table 8
mixed dataset support across rows: A0/A2/A4 were reported on their common $n=77$
non-Finance scope, while the legacy A1 row was reported on its native $n=33$ scope. Row
means were therefore not directly comparable within the table. This audit re-derives the
table on exact common dataset support per comparison panel.

## Configuration coverage, verified from code and outputs

Source: `GNNRank-main/scripts/revision_analysis_20260825/run_reviewer_ablation.py`
(`STRUCTURAL_VARIANTS`, `CONFIG_SCOPE`) and
`outputs/revision_analysis_20260825/reviewer_ablation_scalability/structural_ablation.csv`.

| Config | Meaning | Completed dataset count | Metrics present | Runtime present | Metric implementation | Source |
|---|---|---:|---|---|---|---|
| A0 | Phase A only | 77 | `upset_simple`, `upset_naive`, `upset_ratio` all present, no NaN | `runtime_total_sec` present, no NaN | `_upset_simple`/`_upset_naive`/`_upset_ratio` in `GNNRank-main/scripts/revision_analysis_20260824/run_mincut_cap_audit.py:72-110` | `structural_ablation.csv` |
| A1 | legacy fixed-topological/INS add-back (submitted) | 33 | present, no NaN | present, no NaN | same | `structural_ablation.csv` |
| A2 | exact reachability add-back (revised canonical) | 77 | present, no NaN | present, no NaN | same | `structural_ablation.csv` |
| A3 | legacy topo add-back + refinement (legacy/original full pipeline) | 33 | present, no NaN | present, no NaN | same | `structural_ablation.csv` |
| A4 | reachability + refinement = `OURS-Reach` | 77 | present, no NaN | present, no NaN | same | `structural_ablation.csv` |

All rows for all five configs have `status == "complete"`. No duplicate `(config, dataset)`
pairs were found for any of A0/A1/A2/A3/A4. This was checked programmatically (script
retained at `/tmp/ranking-jsuper-final-r1-ablation-fix` session scratch; results
reproduced below) directly against `structural_ablation.csv`, not assumed from the
previous pass's aggregation.

## Exact dataset-set verification (not assumed)

Computed as exact Python set intersections over the `dataset` column, restricted to
`config in {A0,A1,A2,A3,A4}`:

- `|A0| = 77`, `|A1| = 33`, `|A2| = 77`, `|A3| = 33`, `|A4| = 77`.
- `A1 == A3` as dataset-ID sets (verified: symmetric difference is empty). Both the
  legacy-reinsertion-only stage (A1) and the legacy full-pipeline-with-refinement stage
  (A3) were run on the identical 33-dataset Layer-1 core scope.
- `A0 == A2 == A4` as dataset-ID sets (all three share the identical 77-dataset
  non-Finance scope).
- `A1 ⊆ A0` (the 33-dataset legacy scope is a strict subset of the 77-dataset
  canonical scope).

Requested set constructions:

| Set | Definition | Exact n |
|---|---|---:|
| `S_legacy` | `A0 ∩ A1 ∩ A3` | **33** |
| `S_all4` | `A0 ∩ A1 ∩ A2 ∩ A4` | **33** |
| `S_canonical` | `A0 ∩ A2 ∩ A4` | **77** |

Because `A1 == A3` exactly, `S_legacy == A1 == A3` (the legacy scope is not merely
intersected down to something smaller -- A0's 77-set fully contains it, so restricting A0
to the legacy scope loses no legacy-side information). `S_all4` also equals 33 for the
same reason (adding A2/A4, which both already contain A1 as a subset, does not shrink the
intersection further).

**A3 completeness verdict:** A3 supplies all three requested upset metrics and runtime,
complete (no NaN, no missing datasets), on the exact same 33-dataset scope as A1. This
means the **preferred design (two panels, each on one exact common support)** from the
task brief applies directly -- the fallback four-row design was not needed.

## Design decision

- **Panel (a) -- legacy INS progression**, common support `S_legacy` (**n = 33**, exactly
  the intersection of A0, A1, A3, which equals A1's and A3's own native scope): A0
  restricted to `S_legacy` → A1 → A3.
- **Panel (b) -- canonical reachability progression**, common support `S_canonical`
  (**n = 77**): A0 restricted to `S_canonical` → A2 → A4.

Because `S_canonical` already equals A0's, A2's, and A4's full native scope, Panel (b)'s
A0/A2/A4 means are numerically identical to the single-panel Table 8 values from the
previous pass. Only Panel (a)'s A0 row changes (previously reported on the full 77-dataset
scope; now correctly restricted to the exact 33-dataset scope shared with A1/A3).

See `FINAL_R1_ABLATION_NUMERICAL_AUDIT.md` for the full per-cell traceability and
`R1_ABLATION_STAGE_MAPPING.md` (prior pass) for the original A0-A6 code-level mapping,
which this audit does not revise.

## Status

`LEGACY_PANEL_COMMON_SUPPORT = PASS`
`CANONICAL_PANEL_COMMON_SUPPORT = PASS`
