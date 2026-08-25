# Reviewer Master Matrix

Date: 2026-08-24
Consolidates `REVIEWER_TECHNICAL_AUDIT.md` (reachability branch) and
`NOVELTY_THEORY_REVIEWER_MAP.md` (theory branch) into one row-per-concern matrix, updated with
this integration's reconciliation and the DF03 primary-source resolution.

| # | Reviewer | Concern | Evidence currently available | Code change needed? | Experiment needed? | Theory/doc needed? | Manuscript rewrite needed? | Resolved? | Blocking? | Authoritative artifact |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | R1 | Novelty positioning relative to prior work | Full overlap audit against [VK25] and DF03, both read in full | No | No | Done | **Yes** | Evidence-resolved; manuscript text pending | No (manuscript rewrite is a separate, tracked next step) | `NOVELTY_VERDICT.md` (reconciled), `PRIOR_WORK_OVERLAP_MATRIX.md`, `DISTINCTNESS_AND_NEW_WORK_VERDICT.md` |
| 2 | R1 | Readability / need for complete pseudocode | Full pseudocode + parameter table produced | No | No | Done | Yes (insert into manuscript) | Yes | No | `CURRENT_PIPELINE_PSEUDOCODE.md` |
| 3 | R1 | Theory / complexity claims unclear or unverified | Formal equivalence proof, sharpened approximation-guarantee verdict, complexity re-derivation, all cross-validated against DF03 primary text | No | No | Done | Yes | Yes | No | `RANKING_MWFAS_EQUIVALENCE.md`, `APPROXIMATION_GUARANTEE_AUDIT.md`, `COMPLEXITY_AUDIT.md`, `DF03_PRIMARY_THEOREM_VERIFICATION.md` |
| 4 | R2 | Novelty positioning (same underlying concern as #1) | Same as #1 | No | No | Done | Yes | Same as #1 | No | Same as #1 |
| 5 | R4 | "What exactly is scientifically new?" | Three-bullet contribution statement, cross-checked line-by-line against both prior sources | No | No | Done | Yes | Yes | No | `NOVELTY_VERDICT.md`, `REVISED_CONTRIBUTION_POSITIONING.md` |
| 6 | R4 | Approximation-guarantee ambiguity | Sharpened, primary-source-verified two-part verdict | No | No | Done | Yes | Yes | No | `DF03_PRIMARY_THEOREM_VERIFICATION.md` §6 |
| 7 | R4 | Introduction/positioning problem | Structural rewrite plan produced, now including explicit [VK25]-citation recommendation | No | No | Partially — plan exists, actual manuscript intro not written (out of scope, per this task's instruction not to begin manuscript rewriting) | Yes | Plan-resolved; manuscript-resolved pending | No | `INTRODUCTION_REWRITE_PLAN.md`, `REVISED_CONTRIBUTION_POSITIONING.md` §9-10 |
| 8 | R4 | Novelty comparison table | 30-row claim-by-claim matrix against closest prior work | No | No | Done | Yes (adapt into manuscript table) | Yes | No | `PRIOR_WORK_OVERLAP_MATRIX.md` |
| 9 | General | Does Phase-B add-back merely densify the same DAG/order? | Full 78-dataset ablation, all three metrics broken out, one regression and one compute-limited case reported honestly | Done (`OURS_MFAS_REACH` implemented) | Done (this pass) | Done | Yes | **Substantially resolved** — legacy add-back shown near-random on `upset_simple` (28/37/13), reachability shown to help on `upset_simple`/`upset_naive` (74/78) but much more mixed on `upset_ratio` (49/78) | No | `REACHABILITY_AUTHORITATIVE_SUMMARY.md` |
| 10 | General | Duplicate `OURS_MFAS`/`OURS_MFAS_INS3` labels | Confirmed from source and existing tests; documented, not silently changed | No (deliberately not changed, to avoid altering existing script behavior) | No | Done | Yes (footnote/disclosure) | Yes (documented; disposition decided) | No | `ADDBACK_DIAGNOSIS.md` §2 |
| 11 | General | Stale/wrong classical-baseline values in manuscript | Five spot-check values verified against canonical `table4_full_suite.csv`, all match task-stated targets exactly | No | No | Done | Yes (confirm manuscript numbers match) | Yes, for the 5 spot-checked values | No | `REVIEWER_TECHNICAL_AUDIT.md` "Canonical value verification" |
| 12 | General | Direct runtime comparison against classical baselines (W/T/L, Pareto) | **Not done** | No | **Yes** | No | Yes, once experiment exists | **No** | **Yes — flagged as a genuine gap, not attempted this pass** | `REVISION_EXPERIMENT_PLAN.md` "Explicitly deferred"; tracked in `REVISION_SOURCE_OF_TRUTH.md` §9 |
| 13 | General | NaN/missingness / timeout-safe common-completion analysis | **Not done**, beyond ad hoc `finance` documentation | No | **Yes** | No | Yes | **No** | Yes | `REVISION_SOURCE_OF_TRUTH.md` §9 |
| 14 | General | Formal statistical testing (Wilcoxon, bootstrap, Holm) | **Not done** | No | **Yes** | No | Yes | **No** | Yes, for any claim requiring significance | `REVISION_SOURCE_OF_TRUTH.md` §9 |
| 15 | General | Scale/density "positive-search" framing looks post-hoc | Pre-existing repo audits exist (`outputs/audits/`), not modified or re-audited this pass; the `finance` stress case is new and predefined-by-necessity (not cherry-picked) | No | Partial (pre-existing) | Partial | Yes | Partial | No (not newly blocking; pre-existing state unchanged) | `outputs/audits/sparse_regime_robustness.md` (pre-existing) |
| 16 | General | Sensitivity analysis (insertion strategy, tolerances, budgets) | Insertion-strategy axis directly covered by the full ablation; other hyperparameters argued theoretically negligible, not swept | No | Partial (deferred for non-insertion-strategy params) | Done for the primary axis | Yes | Partial | No | `CURRENT_PIPELINE_PSEUDOCODE.md` parameter table |
| 17 | General | Reachability add-back correctness guarantees (no cycles, minimality, determinism) | Proved (not just tested): one-pass sufficiency, inclusion-minimality; 41 new unit tests including a hand-constructed divergence case | Done | Done | Done | Yes (cite proofs) | Yes | No | `REACHABILITY_ADDBACK_DESIGN.md`, `tests/test_reachability_addback.py` |
| 18 | General | Ablation harness previously blocked (missing deps) | Repaired; root cause identified (missing `latextable`/`torch_geometric` in this environment, plus a pre-existing dataset-path bug) and fixed | Done | Done | Done | No | Yes | No | `ADDBACK_DIAGNOSIS.md`, `GNNRank-main/scripts/paper/run_phase_ablation.py` |
| 19 | General (new, this integration) | Preprint self-overlap / citation risk | Full policy audit + a demonstrated citation-attribution error found in [VK25] v3 itself, flagged for the authors' own citation hygiene | No | No | Done | Yes (cite [VK25] explicitly; spot-check manuscript's own citations) | Yes | No | `SPRINGER_PREPRINT_POLICY_AUDIT.md` |
| 20 | General (new, this integration) | Weighted-FAS-objective comparison (removed-edge weight, not just count) | **Not available in current data** — flagged explicitly, not fabricated | Small (`_upset` helper addition) | **Yes** (re-run harness with the new column) | No | Yes, once available | **No** | Only for any manuscript claim about FAS *weight* specifically (upset metrics are unaffected) | `REACHABILITY_AUTHORITATIVE_SUMMARY.md` §3 |

## Summary

**Fully or substantially resolved (evidence exists, cross-verified)**: rows 1-3, 5-11, 17-19 —
the large majority of the theory/novelty/positioning concerns and the core "does add-back help"
question.

**Genuinely unresolved, tracked as blockers for any claim that depends on them**: rows 12-14
(runtime W/T/L, timeout-safe coverage analysis, formal statistical testing — all explicitly
deferred, not attempted, across all three source branches) and row 20 (weighted-FAS-objective
comparison, a data gap not yet filled). Rows 15-16 are partially resolved (pre-existing or
axis-limited) and not newly blocking.
