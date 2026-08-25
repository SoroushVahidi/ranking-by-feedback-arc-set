# Final Reviewer-1 Explicit Ablation Requirement Audit

Date: 2026-08-25
Branch: `jsuper-final-r1-ablation-fix-20260825`
Worktree: `/tmp/ranking-jsuper-final-r1-ablation-fix`

Runtime provenance update (2026-08-25): this audit predated the
`runtime_algorithm_sec` correction. Reviewer 1's average-runtime requirement remains
complete, but the manuscript-facing runtime column is now mean `runtime_algorithm_sec`;
`runtime_total_sec` is retained only as a harness diagnostic.

## Exact preserved Reviewer 1 wording (Comment 2, `response_to_reviewers.tex`)

> "Provide ablations of Phase 1 only, Phase 1 with reinsertion, and the full pipeline;
> report upset metrics and runtime; study scale/density and sensitivity to zero
> tolerance, reinsertion passes, and refinement iterations."

The task brief additionally preserves the fuller original phrasing:

> "Supplement ablation experiments covering three groups: Phase 1 only, Phase 1 + INS
> multi-pass reinsertion, and the full pipeline with refinement. Report three upset
> losses and average runtime for each group..."

This is **not** weakened to a single upset metric: the requirement is read as three
groups x three upset losses (`upset_simple`, `upset_naive`, `upset_ratio`) x average
runtime.

## Requirement breakdown

| Requested item | Requirement |
|---|---|
| Stage 1 | Phase 1 (Phase A) only |
| Stage 2 | Phase 1 + reinsertion (submitted: INS/fixed-topological multi-pass; revised: exact reachability) |
| Stage 3 | Full pipeline with refinement |
| Metric 1 | `upset_simple` |
| Metric 2 | `upset_naive` |
| Metric 3 | `upset_ratio` |
| Runtime | Average (mean) runtime per group |
| Secondary (already answered elsewhere) | Scale/density (`\S`3.6 Scalability), zero-tolerance sensitivity, reinsertion-pass sensitivity, refinement-iteration sensitivity (`\S`3.8 Parameter Sensitivity) |

## Mapping to stored configuration / source output

| Requested stage | Stored config | Source output | Available |
|---|---|---|---|
| Phase 1 only | `A0` | `outputs/revision_analysis_20260825/reviewer_ablation_scalability/structural_ablation.csv` + `structural_ablation_summary.csv` | Yes ($n=77$ non-Finance) |
| Phase 1 + submitted INS/topo-proxy reinsertion | `A1` | same files | Yes ($n=33$, Layer-1 core scope only) |
| Phase 1 + revised exact-reachability reinsertion (canonical) | `A2` | same files | Yes ($n=77$ non-Finance) |
| Full pipeline with refinement (canonical, `OURS-Reach`) | `A4` | same files | Yes ($n=77$ non-Finance) |
| Full pipeline with refinement (legacy/submitted mechanism) | `A3` | same files | Yes ($n=33$), not used in the manuscript table (see `R1_ABLATION_STAGE_MAPPING.md`) |

All rows used in the manuscript table are present with completed status
(`status == "complete"` for all 407 rows in `structural_ablation.csv`) and with
`upset_simple`, `upset_naive`, `upset_ratio`, `runtime_total_sec`, and
`runtime_algorithm_sec` populated per dataset. The final manuscript table uses
matched-support panels (`A0/A1/A3`, n=33; `A0/A2/A4`, n=77) and publishes mean
`runtime_algorithm_sec`.

## Availability verdict

**EXISTING_EVIDENCE_COMPLETE.** No stored quantity required by Reviewer 1's request was
found to be genuinely absent. No new scientific experiment was run and no re-scoring was
needed beyond reading the already-generated summary CSV (itself produced by code already
in the repository before this correction pass).

See `R1_ABLATION_STAGE_MAPPING.md` for the stage-to-config mapping decision and
`FINAL_R1_ABLATION_NUMERICAL_AUDIT.md` for the per-cell numerical traceability of every
value placed in the new manuscript table (Table~8, `\label{tab:reviewer1_stage_ablation}`).
