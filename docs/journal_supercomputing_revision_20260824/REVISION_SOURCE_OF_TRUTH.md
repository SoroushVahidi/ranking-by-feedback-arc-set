# Revision Source of Truth

Date: 2026-08-24
Branch: `jsuper-major-revision-integration-20260824` (integrates `b2d05c85`, `e31323a5`,
`a99029b6` onto `origin/main` @ `706b2177`)

**This is the authoritative entry point for the JOS major revision. Any future manuscript rewrite
should start here.** Where this document's summary and an underlying detailed document disagree
(e.g. due to a reconciliation correction), this document and the reconciliation notes inline in
the corrected files are authoritative; unreconciled statements elsewhere should be treated as
superseded.

## 1. Current algorithm (as shipped, `main`)

Three phases, in `GNNRank-main/src/ours_mfas.py`:
- **Phase A**: local-ratio cycle breaking (Demetrescu & Finocchi 2003, "DF03").
- **Phase B**: descending-weight edge reinsertion, currently implemented as a **fixed-topological-
  order proxy test** with up to 3 passes (INS1/2/3) — see §3.
- **Phase C**: optional ternary-search ratio-loss refinement (order-preserving).

Full pseudocode: `CURRENT_PIPELINE_PSEUDOCODE.md`. Full complexity audit:
`COMPLEXITY_AUDIT.md` + `DF03_PRIMARY_THEOREM_VERIFICATION.md` §3.

## 2. Prior-work lineage

The entire three-phase pipeline is, in its core equations and pseudocode, the same as the authors'
own prior arXiv preprint (Vahidi & Koutis, "Minimum Weighted Feedback Arc Sets for Ranking from
Pairwise Comparisons," arXiv:2412.16181, "[VK25]," read in full in both v2 [Jan 2025] and v3 [Dec
2025, current]), which itself adopts DF03's local-ratio Phase A and DF03's own suggested
descending-weight Phase-B heuristic. Full lineage: `PRIOR_ADDBACK_LINEAGE.md`. Full claim-by-claim
overlap: `PRIOR_WORK_OVERLAP_MATRIX.md` (30 rows). DF03 primary-source verification (theorem text
and proofs read in full): `DF03_PRIMARY_THEOREM_VERIFICATION.md`.

## 3. What is old (do not claim as novel)

- Local-ratio Phase A, its DFS cycle selection and residual reduction — DF03.
- Weight-prioritized edge reinsertion — DF03's own suggested heuristic, adopted verbatim in [VK25].
- The **exact** cycle-safety/reachability test for reinsertion — DF03's original Phase-2
  condition, restated identically in [VK25]'s Algorithm 1 ("if adding (u,v) back does not create a
  directed cycle").
- Topological ranking extraction, ternary-search ratio-loss refinement (Phase C) — both verbatim
  in [VK25]'s Algorithm 1/2/3.
- The general concept of exchange-based local search for feedback arc sets — prior art exists for
  tournaments (see `DISTINCTNESS_AND_NEW_WORK_VERDICT.md`); not yet implemented in this project in
  any form.

## 4. What is corrected (implementation fidelity, not novelty)

The shipped `main` Phase B is a **weakening** of DF03's/[VK25]'s own exact test into a fixed-
topological-order proxy, patched with an undocumented multi-pass mechanism (INS1/2/3) absent from
both sources. This is diagnosed in `ADDBACK_DIAGNOSIS.md` and traced precisely in
`PRIOR_ADDBACK_LINEAGE.md`. A corrected implementation, `OURS_MFAS_REACH`
(`GNNRank-main/src/ours_mfas.py::_addback_reachability`), restores the exact test. **The
restoration itself is not a novel idea** — it is a fidelity fix. See §5 for what about it *is* new.

## 5. What is genuinely new

- **Theory** (absent from both [VK25] and DF03 in the specific form given):
  - Formal ranking↔MWFAS exact-equivalence proposition and proof, correctly scoped as many-to-many
    (`RANKING_MWFAS_EQUIVALENCE.md`).
  - A sharpened, two-part approximation-guarantee verdict distinguishing the removed-FAS-weight
    λ-bound (depends only on Phase-1 convergence) from the ranking-cost-equals-FAS-weight
    equivalence (additionally depends on Phase-2 minimality) — `DF03_PRIMARY_THEOREM_VERIFICATION.md`
    §6, refining `APPROXIMATION_GUARANTEE_AUDIT.md`.
  - A worst-case construction proving the implementation's timeout/identity-order fallback has
    unbounded error relative to OPT (`APPROXIMATION_GUARANTEE_AUDIT.md` §3).
  - One-pass sufficiency and inclusion-minimality **proofs** (not just tests) for the specific
    efficient incremental-reachability implementation of the corrected Phase B
    (`REACHABILITY_ADDBACK_DESIGN.md` §3-4).
  - A complexity re-derivation (O(mn+m²), not the informally-cited O(VE)) for the shipped Phase A,
    independently cross-validated against DF03's own primary text, which itself distinguishes the
    naive-DFS case (what is shipped) from the dynamic-reachability-structure case (what would be
    needed for O(mn)) — `COMPLEXITY_AUDIT.md` + `DF03_PRIMARY_THEOREM_VERIFICATION.md` §3.
- **Empirical**:
  - Ten classical ranking baselines (BTL, SpringRank, RankCentrality, SerialRank, SyncRank,
    DavidScore, EigenvectorCentrality, PageRank, SVD-RS, SVD-NRS) vs. **zero** in [VK25] — the
    single largest, cleanest empirical delta (`EXPERIMENTAL_SCOPE_COMPARISON.md`).
  - A dense/near-complete-graph stress case (`finance`, n=1315) absent from [VK25], surfacing a
    concrete guarantee-voiding failure mode.
  - Full-suite (78/80 dataset) phase-ablation comparison of Phase-A-only vs. legacy topo add-back
    vs. corrected reachability add-back — see §6/`REACHABILITY_AUTHORITATIVE_SUMMARY.md`.
  - Reproducibility/ablation infrastructure (41+ new unit tests, a repaired and extended
    full-suite ablation harness, determinism guarantees explicitly tested) — none of this exists in
    any form in [VK25].
- **What is efficient-implementation-new, building on known DF03 results**: the specific
  incremental-reachability-matrix realization of the (conceptually old) exact cycle-safety test,
  and its proved minimality (extending DF03's own Theorem 1, proved for its own unordered variant,
  to this specific descending-weight-ordered, efficiently-implemented variant).

## 6. Current experimental evidence (authoritative numbers)

See `REACHABILITY_AUTHORITATIVE_SUMMARY.md` (this integration) for the full table. Headline
figures (`upset_simple`, n=78 datasets with usable results):
- **A1 (legacy topo add-back) vs. A0 (Phase-A-only)**: 28 better / 37 worse / 13 tied — legacy
  add-back does **not** reliably improve ranking quality.
- **B1 (reachability add-back) vs. A0**: 74 better / 2 worse / 2 tied.
- **B1 vs. A1** (direct): 73 better / 2 worse / 3 tied.
- One genuine regression (`Halo2BetaData`, Δ≈+0.249) and one unresolved compute-budget limitation
  (`finance`, neither add-back mechanism completed within the time budget used).
- **More restored edges does not automatically mean a better ranking** — `Halo2BetaData` is a
  direct counter-example (reachability restores more edges than legacy topo add-back there, yet
  its `upset_simple` is substantially worse) — do not state the edges-restored count as a proxy
  for ranking quality in the manuscript.

## 7. Current reviewer-response state

See `REVIEWER_MASTER_MATRIX.md` (this integration) for the row-by-row status. Summary: Reviewer 1
Issues 1/3/4, Reviewer 2 Issue 1, and Reviewer 4's novelty/approximation-guarantee/positioning
concerns are answerable from current evidence (documents exist and are cross-verified). Remaining
blockers are listed in §8.

## 8. Remaining novelty risk

Per `DISTINCTNESS_AND_NEW_WORK_VERDICT.md`: **Verdict B** — probably sufficient once the
theoretical contributions and fidelity-gap diagnosis are foregrounded and the (now-corrected)
dataset-count narrative is used, but a modest new algorithmic addition would reduce risk. Top
candidate (design-only, not implemented): min-cut-triggered weighted exchange — see
`MINCUT_WEIGHTED_EXCHANGE_RESEARCH_QUESTION.md` and
`MINCUT_EXCHANGE_PRIOR_ART_CHECKLIST.md`.

## 9. Remaining experiments (not yet performed)

- Direct runtime W/T/L/Pareto comparison against all ten classical baselines (Section H of the
  original task list; deferred on the reachability branch).
- Timeout-safe common-completion analysis (Section I of the original task list; deferred).
- Formal statistical testing — Wilcoxon, bootstrap CI, Holm correction (Section J; deferred).
- Fixing the `Halo2BetaData/HeadToHead` and `ERO` dataset-loader gaps so the full 80/80 suite is
  usable (currently 78/80 usable — see `REVISION_RESULTS.md` §1).
- Re-running `finance` with a substantially larger time budget or a vectorized/amortized Phase A
  (per `COMPLEXITY_AUDIT.md`'s recommended fix) before drawing any conclusion about dense-graph
  behavior.
- The compute-matched analysis file gap (`leaderboard_compute_matched.csv` missing, causing a
  pre-existing, unrelated test failure — do not claim compute-matched results until this is fixed).
- If pursued: prototyping the min-cut exchange mechanism (design-only at present).

## 10. Authoritative artifact index

| Category | Authoritative file(s) |
|---|---|
| Current algorithm / pseudocode | `CURRENT_PIPELINE_PSEUDOCODE.md` |
| Prior-work lineage (add-back) | `PRIOR_ADDBACK_LINEAGE.md` |
| Full claim-by-claim overlap | `PRIOR_WORK_OVERLAP_MATRIX.md` |
| DF03 primary-source verification | `DF03_PRIMARY_THEOREM_VERIFICATION.md` |
| Dataset/baseline scope comparison | `EXPERIMENTAL_SCOPE_COMPARISON.md` (supersedes dataset-count claims elsewhere) |
| Ranking↔MWFAS theory | `RANKING_MWFAS_EQUIVALENCE.md` |
| Approximation-guarantee audit | `APPROXIMATION_GUARANTEE_AUDIT.md` + `DF03_PRIMARY_THEOREM_VERIFICATION.md` §6 (sharpened verdict) |
| Complexity audit | `COMPLEXITY_AUDIT.md` + `DF03_PRIMARY_THEOREM_VERIFICATION.md` §3 |
| Reachability add-back design/correctness | `REACHABILITY_ADDBACK_DESIGN.md` |
| Reachability empirical results | `REVISION_RESULTS.md` (raw) + `REACHABILITY_AUTHORITATIVE_SUMMARY.md` (this integration, curated) |
| Novelty verdict | `NOVELTY_VERDICT.md` (as reconciled) + `DISTINCTNESS_AND_NEW_WORK_VERDICT.md` |
| Springer/policy | `SPRINGER_PREPRINT_POLICY_AUDIT.md` |
| Reviewer mapping | `NOVELTY_THEORY_REVIEWER_MAP.md` + `REVIEWER_TECHNICAL_AUDIT.md` + `REVIEWER_MASTER_MATRIX.md` (this integration, consolidated) |
| Manuscript change plan | `MANUSCRIPT_CHANGE_MAP.md` + `INTRODUCTION_REWRITE_PLAN.md` + `REVISED_CONTRIBUTION_POSITIONING.md` |
| Branch integration | `REVISION_BRANCH_INTEGRATION_PLAN.md` (plan) + this integration branch (execution) |
| Candidate new algorithm (design-only) | `MINCUT_WEIGHTED_EXCHANGE_RESEARCH_QUESTION.md` + `MINCUT_EXCHANGE_PRIOR_ART_CHECKLIST.md` |
