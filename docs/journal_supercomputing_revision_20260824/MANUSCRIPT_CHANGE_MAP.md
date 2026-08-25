# Manuscript Change Map

Date: 2026-08-24

This maps the code/evidence changes in this revision pass to the manuscript
sections/tables/figures they should ultimately affect. It is a planning
document for the manuscript rewrite, not a claim that the manuscript text has
already been edited (it has not — this repository holds code and evidence,
not the manuscript source).

## Algorithm section (Phase B / add-back description)

- **Current text (inferred from code, to verify against actual manuscript
  source):** likely describes add-back as accepting edges "consistent with the
  induced order," possibly without stating this is a single fixed topological
  order re-derived at the start of each pass.
- **Required change:** state explicitly that the deployed method
  (`OURS_MFAS`/`OURS_MFAS_INS1..3`) uses a *sufficient but not necessary*
  cycle-safety test (forward w.r.t. one fixed topological order), and either
  (a) introduce `OURS_MFAS_REACH` as the exact-reachability alternative
  evaluated in this revision, with its one-pass-sufficiency and
  inclusion-minimality properties stated and proved (see
  `REACHABILITY_ADDBACK_DESIGN.md`), or (b) if the full-suite results in
  `REVISION_RESULTS.md` do not show material improvement, reposition the
  contribution around Phase A + deterministic/time-bounded execution instead
  (per the task's Section O framing) and describe add-back as a minor,
  order-preserving refinement rather than a major mechanism.

## Table 4 (full-suite results) / Table 5 (compute-matched)

- No manuscript-number changes required from this pass alone (canonical
  values were verified, not altered — see `REVIEWER_TECHNICAL_AUDIT.md`).
- **If** `OURS_MFAS_REACH` is adopted as a reported variant, Table 4 should
  gain a row for it, sourced the same way as existing OURS rows (via
  `GNNRank-main/paper_csv/leaderboard_per_method.csv` ->
  `scripts/paper/generate_paper_tables.py`), not by hand-editing the CSV.
  This requires wiring `OURS_MFAS_REACH` into whatever full-corpus run
  produces `leaderboard_per_method.csv` (out of scope for this pass; see
  "Remaining reviewer-critical experiments" in `REVISION_RESULTS.md`).

## New ablation table (add-back mechanism comparison)

- **New table/figure recommended:** A0 vs A1_topo vs B1_reach (and their +C
  variants), upset_simple/upset_ratio/upset_naive, edges-restored,
  permutation-changed-rate, sourced directly from
  `outputs/ablation/phase_ablation_results.csv` /
  `phase_ablation_summary.md` (this revision's output). This directly
  answers the reviewer's central algorithmic-weakness concern with primary
  evidence rather than assertion.

## Methods description of `OURS_MFAS`/`OURS_MFAS_INS3` duplication

- **Required change:** if the manuscript's results tables list both
  `OURS_MFAS` and `OURS_MFAS_INS3` as if independently evaluated, either
  remove the redundant row or add a footnote clarifying `OURS_MFAS` is an
  alias for the INS3 configuration (see `ADDBACK_DIAGNOSIS.md` §2). Do not
  present them as two configurations in any W/T/L or "number of OURS variants
  evaluated" count.

## Runtime claims (Section H)

- **Required change (deferred to next pass, see `REVISION_RESULTS.md`):**
  soften any blanket "OURS is faster" claim to explicitly compare against
  lightweight classical baselines with W/T/L + runtime ratios, not just
  training-based GNN baselines. Not executed in this pass.

## Statistical rigor (Section J)

- **Required addition (deferred):** paired significance testing (Wilcoxon +
  Holm correction) and bootstrap CIs for the principal OURS-vs-baseline and
  topo-vs-reach comparisons, plus a family-aware robustness note given
  temporal correlation among basketball-year instances. Not executed in this
  pass; `REVISION_EXPERIMENT_PLAN.md` records it as next work.

## Scale/density framing (Section K)

- **Required change:** the manuscript's sparse-regime strength claim should
  be cross-checked against the family-level breakdown in
  `outputs/ablation/phase_ablation_summary.md` (this revision) once available,
  to confirm the reachability variant does not simply amplify or erase that
  existing finding without comment.
