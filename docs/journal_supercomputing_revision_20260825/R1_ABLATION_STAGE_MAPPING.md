# Reviewer-1 Ablation Stage Mapping Decision

Date: 2026-08-25 (superseded in part 2026-08-25: see below)

> **Update:** the single-table, four-row design below (A0/A1/A2/A4 in one table) was
> replaced by a two-panel design on exact matched dataset support after independent
> inspection found A1's row used a different ($n=33$) dataset scope than A0/A2/A4's
> ($n=77$) rows in the same table. The A0-A6 code-level mapping and the legacy-vs-canonical
> reasoning below are unchanged and still authoritative; only the final table layout
> changed. See `FINAL_R1_COMMON_SUPPORT_AUDIT.md` and the revised
> `FINAL_R1_ABLATION_NUMERICAL_AUDIT.md` for the current two-panel design (Panel (a):
> A0→A1→A3 legacy progression on common $n=33$; Panel (b): A0→A2→A4 canonical progression
> on common $n=77$), which additionally makes use of A3 (legacy topo add-back +
> refinement), not used in the original single-table design.

## Code-verified A0-A6 configuration definitions

Source: `GNNRank-main/scripts/revision_analysis_20260825/run_reviewer_ablation.py`,
`STRUCTURAL_VARIANTS` dict (lines 100-106):

| Config | `addback_mode` | `enable_phase_c` (refinement) | Meaning |
|---|---|---|---|
| A0 | n/a (Phase B off) | off | Phase A only |
| A1 | `topo` | off | Phase A + fixed-topological-position add-back (submitted/legacy "INS" proxy) |
| A2 | `reach` | off | Phase A + exact reachability add-back (revised canonical reinsertion) |
| A3 | `topo` | on | Phase A + legacy topo add-back + refinement (legacy full pipeline) |
| A4 | `reach` | on | Phase A + exact reachability add-back + refinement = `OURS-Reach` (revised canonical full pipeline) |
| A5 | `reach` | off | A2 + optional min-cut |
| A6 | `reach` | on | A4 + optional min-cut |

Dataset scope per config (`CONFIG_SCOPE`, lines 111-117): `A0`, `A2`, `A4`, `A6` run on
"both" (Layer-1 core, 33 datasets, + Layer-2 scale, 45 datasets = 78 non-Finance; verified
distinct across `structural_ablation.csv` A0/A2/A4 keys as $n=77$ with completed status,
one dataset short of 78 for reasons already documented for the existing Table 7 pairwise
$n=77$). `A1`, `A3`, `A5` run on "core" only (Layer-1, $n=33$).

This confirms, independent of the manuscript's prose legend, that:

- Legacy `INS`-style reinsertion in the *submitted* manuscript corresponds to `A1`
  (`addback_mode="topo"`), not to `A2`.
- The *revised* manuscript's canonical reinsertion mechanism is `A2`
  (`addback_mode="reach"`), which is **not** the same mechanism as `A1`/legacy `INS`. They
  must not be conflated or silently swapped in the ablation table.

## Reviewer 1's literal three groups vs. the revised pipeline

Reviewer 1's literal request ("Phase 1 only", "Phase 1 + INS multi-pass reinsertion",
"full pipeline with refinement") was written against the **submitted** manuscript, whose
reinsertion mechanism was the fixed-topological-position proxy (`A1`) and whose full
pipeline was `A3` (topo add-back + refinement).

The revised manuscript no longer treats the topo-proxy as canonical: exact reachability
add-back (`A2`) replaced it as the correct/canonical mechanism, and the revised full
pipeline is `A4` (`OURS-Reach`).

## Decision: final table rows

The cleanest scientifically honest design is the one recommended in the task brief: show
the canonical revised progression as the primary three rows, and retain exactly one
legacy row so the reviewer's literal wording is still directly answered without implying
that the legacy mechanism is now the paper's method.

**Final four rows (Table 8, `\label{tab:reviewer1_stage_ablation}`):**

1. **A0** -- Phase A only.
2. **A1** -- legacy fixed-topological/`INS` reinsertion (the submitted mechanism), labeled
   explicitly as "legacy topo add-back, submitted" and reported on its native $n=33$
   scope. This row exists specifically so "Phase 1 + INS multi-pass reinsertion" is
   answered using the mechanism the reviewer actually described.
3. **A2** -- Phase A + exact reachability add-back (the revised canonical reinsertion
   stage).
4. **A4** -- Phase A + exact reachability add-back + refinement = `OURS-Reach` (the
   revised canonical full pipeline).

`A3` (legacy topo add-back + refinement) is **not** added as a fifth row: it would either
force the table past a fifth mechanism variant not requested by any reviewer, or invite
confusion about which "full pipeline" is being reported. The manuscript's existing Table 7
paired-test family already contains an `A1->A2` comparison and an `A0->A4` comparison that
jointly cover the legacy-vs-canonical and Phase-A-vs-full-pipeline directions Reviewer 1
asked about; `A3` is not part of any of those primary comparisons and introducing it here
would exceed the evidence already validated in Table 7. This is consistent with the task
brief's explicit instruction to prefer the compact canonical-progression design (Phase A
only / + exact reachability reinsertion / + refinement) plus a single clearly labeled
legacy row, and to avoid table proliferation.

## Non-goal: mixing metric implementations

`A0`, `A1`, `A2`, `A4` all use the same ablation-local `upset_simple`/`upset_naive`/
`upset_ratio` implementation (`GNNRank-main/scripts/revision_analysis_20260824/
run_mincut_cap_audit.py:72-110`), which is the same implementation already underlying the
currently published Table 7. The GNNRank-canonical `calculate_upsets` re-score
(`GNNRank-main/src/metrics.py:287-321`) exists only for `A4` (feeding Tables 4-6's
cross-method `OURS-Reach` comparisons against classical/GNN baselines) and was **not**
computed for `A0`/`A1`/`A2`. Mixing the two implementations within one table would compare
non-identical metric formulas under the same column header, so the new table uses the
ablation-local implementation throughout for internal consistency, exactly matching Table
7's existing metric family. See `FINAL_R1_ABLATION_NUMERICAL_AUDIT.md` for the resulting
decision: `EXISTING_EVIDENCE_COMPLETE`.
