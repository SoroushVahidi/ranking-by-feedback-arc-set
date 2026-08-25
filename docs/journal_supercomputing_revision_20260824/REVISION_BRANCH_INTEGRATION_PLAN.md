# Revision Branch Integration Plan

Date: 2026-08-24
Branches inspected: `journal-supercomputing-major-revision-20260824` (commit `b2d05c85`),
`jsuper-revision-novelty-theory-20260824` (commit `e31323a5`), and this branch,
`jsuper-prior-work-overlap-audit-20260824`. All three are single-commit branches based directly on
`origin/main` @ `706b21771be3af61c8fd4dd22723d0d5611fa042`. **No merge has been performed; this is
a plan only, per instructions.**

## File-level overlap check

```
b2d05c85 touches:
  GNNRank-main/outputs/ablation/phase_ablation_results.csv       (data)
  GNNRank-main/outputs/ablation/phase_ablation_summary.md        (data)
  GNNRank-main/scripts/paper/run_phase_ablation.py                (code)
  GNNRank-main/src/comparison.py                                  (code)
  GNNRank-main/src/ours_mfas.py                                   (code)
  GNNRank-main/src/train.py                                       (code)
  docs/journal_supercomputing_revision_20260824/ADDBACK_DIAGNOSIS.md
  docs/journal_supercomputing_revision_20260824/MANUSCRIPT_CHANGE_MAP.md
  docs/journal_supercomputing_revision_20260824/REACHABILITY_ADDBACK_DESIGN.md
  docs/journal_supercomputing_revision_20260824/REVIEWER_TECHNICAL_AUDIT.md
  docs/journal_supercomputing_revision_20260824/REVISION_EXPERIMENT_PLAN.md
  docs/journal_supercomputing_revision_20260824/REVISION_RESULTS.md
  tests/test_reachability_addback.py

e31323a5 touches (docs only):
  docs/journal_supercomputing_revision_20260824/APPROXIMATION_GUARANTEE_AUDIT.md
  docs/journal_supercomputing_revision_20260824/COMPLEXITY_AUDIT.md
  docs/journal_supercomputing_revision_20260824/CURRENT_METHOD_DECOMPOSITION.md
  docs/journal_supercomputing_revision_20260824/CURRENT_PIPELINE_PSEUDOCODE.md
  docs/journal_supercomputing_revision_20260824/INTRODUCTION_REWRITE_PLAN.md
  docs/journal_supercomputing_revision_20260824/NOVELTY_LITERATURE_MATRIX.md
  docs/journal_supercomputing_revision_20260824/NOVELTY_THEORY_REVIEWER_MAP.md
  docs/journal_supercomputing_revision_20260824/NOVELTY_VERDICT.md
  docs/journal_supercomputing_revision_20260824/RANKING_MWFAS_EQUIVALENCE.md

this branch touches (docs only, once committed):
  docs/journal_supercomputing_revision_20260824/PRIOR_WORK_OVERLAP_MATRIX.md
  docs/journal_supercomputing_revision_20260824/PRIOR_ADDBACK_LINEAGE.md
  docs/journal_supercomputing_revision_20260824/DISTINCTNESS_AND_NEW_WORK_VERDICT.md
  docs/journal_supercomputing_revision_20260824/SPRINGER_PREPRINT_POLICY_AUDIT.md
  docs/journal_supercomputing_revision_20260824/EXPERIMENTAL_SCOPE_COMPARISON.md
  docs/journal_supercomputing_revision_20260824/DF03_PRIMARY_THEOREM_VERIFICATION.md
  docs/journal_supercomputing_revision_20260824/REVISED_CONTRIBUTION_POSITIONING.md
```

**No filename overlaps across all three branches.** All three modify disjoint files under the same
directory (or, for `b2d05c85`, additionally disjoint source/test/data files elsewhere in the
tree). **A three-way merge should be mechanically conflict-free at the git level.**

## Recommended integration base and sequence

**Recommended integration branch name**: `journal-supercomputing-major-revision-INTEGRATED-20260824`,
created from `journal-supercomputing-major-revision-20260824` (`b2d05c85`) as the base — it is the
only branch with functional code/test/data changes, so it should anchor the integration rather than
being merged *into* a docs-only branch.

```
git checkout -b journal-supercomputing-major-revision-INTEGRATED-20260824 journal-supercomputing-major-revision-20260824  # from b2d05c85
git merge --no-ff jsuper-revision-novelty-theory-20260824       # from e31323a5, docs-only, expect clean
git merge --no-ff jsuper-prior-work-overlap-audit-20260824       # this branch once committed, docs-only, expect clean
```

## What must NOT be overwritten

- `GNNRank-main/outputs/ablation/phase_ablation_results.csv` / `phase_ablation_summary.md`: these
  are `b2d05c85`'s generated experimental artifacts (78-dataset full-suite ablation run). Neither
  other branch touches them, so a mechanical merge will not overwrite them — flagged explicitly
  anyway per the task's "must not be overwritten" instruction, since regenerating them
  post-merge (e.g. by re-running the harness on the integrated branch to "refresh" results) is
  unnecessary and should not be done casually — the existing run is a valid, already-analyzed
  artifact (`REVISION_RESULTS.md` was written against these exact numbers).
- `tests/test_reachability_addback.py`: `b2d05c85`'s 41 new tests; no other branch touches this
  file.
- No file in `outputs/paper_tables/`, `outputs/audits/`, or `docs/audits/` (the pre-existing,
  earlier-audit-pass artifacts) is touched by any of the three branches — confirmed by the file
  lists above — so none of this integration work risks the "preserve existing results and
  provenance" instruction from the original task.

## Manual reconciliation required despite the absence of git conflicts

**This is the important part of this plan — a clean git merge does not mean the content is
consistent.** Three specific content-level items need manual reconciliation after merging, because
they live in *different* files (so git will not flag them) but say inconsistent things:

1. **Dataset-count narrative.** `jsuper-revision-novelty-theory-20260824`'s
   `NOVELTY_LITERATURE_MATRIX.md` and `NOVELTY_VERDICT.md` (bullet 1) describe [VK25]'s dataset
   suite as "~50 dataset instances" and characterize the current 80-dataset suite as a
   "substantially expanded" benchmark on that basis. **This branch's**
   `EXPERIMENTAL_SCOPE_COMPARISON.md` establishes, via a precise line-by-line recount of [VK25]'s
   own Tables 1-4, that the correct figure is **77 instances**, i.e. a **+3/77 (~4%) delta**, not a
   multi-fold expansion. **Action**: when integrating, edit `NOVELTY_LITERATURE_MATRIX.md` and
   `NOVELTY_VERDICT.md` (bullet 1) on the theory branch's content to cite the corrected figure and
   shift the empirical-contribution emphasis to the baseline-count expansion (0 -> 10 classical
   methods, which remains fully accurate and is the stronger claim) rather than dataset count. This
   branch's own `PRIOR_WORK_OVERLAP_MATRIX.md` row 19-20 and `EXPERIMENTAL_SCOPE_COMPARISON.md`
   already reflect the corrected framing and can be used as the source of truth.
2. **Approximation-guarantee wording.** `jsuper-revision-novelty-theory-20260824`'s
   `APPROXIMATION_GUARANTEE_AUDIT.md` verdict "(B): applies only to an unbudgeted, idealized
   variant" is **correct but less precise** than this branch's
   `DF03_PRIMARY_THEOREM_VERIFICATION.md` §6, which — having read DF03's actual proof directly —
   splits this into two separable claims (the λ-bound on removed weight, which depends only on
   Phase-1 convergence, vs. the ranking-cost-equals-FAS-weight equivalence, which additionally
   depends on Phase-2 minimality). **Action**: when integrating, treat
   `DF03_PRIMARY_THEOREM_VERIFICATION.md` §6 as the authoritative, sharpened statement and have the
   manuscript-facing recommended language in `APPROXIMATION_GUARANTEE_AUDIT.md` §4 (on the theory
   branch) updated to match it, or simply have the manuscript cite the sharpened version directly.
3. **"OURS_MFAS_REACH is novel" framing.** `jsuper-revision-novelty-theory-20260824`'s
   `NOVELTY_VERDICT.md` (item 6) already correctly frames the reachability-add-back workstream as
   "KNOWN idea / NEW implementation" — **this is consistent with**, and independently corroborated
   by, this branch's `PRIOR_ADDBACK_LINEAGE.md`, which traces the idea all the way back to DF03's
   primary text (not just [VK25]). No correction needed here, but the manuscript should cite
   `PRIOR_ADDBACK_LINEAGE.md`'s fuller chain (DF03 -> [VK25] -> proxy deviation -> INS patch ->
   restoration) rather than stopping at "[VK25] already had this," since the DF03-level grounding
   is stronger evidence still.

## Recommended commit sequence for the integration itself (when performed, not in this pass)

1. Merge as above (three `--no-ff` merges, base on `b2d05c85`).
2. Apply the three reconciliation edits above as a single, clearly-labeled commit ("Reconcile
   cross-branch findings: correct dataset-count claim, adopt sharpened approximation-guarantee
   language, cross-link add-back lineage") rather than silently editing history.
3. Re-run the fast test suites from all three branches together once, to confirm no regressions
   introduced by the doc edits (doc-only changes should not affect any test, but this is a cheap
   sanity check).
4. Do not regenerate `phase_ablation_results.csv`/`_summary.md` as part of this integration commit
   — those remain `b2d05c85`'s artifact of record unless a deliberate, separately-justified re-run
   is requested later.
