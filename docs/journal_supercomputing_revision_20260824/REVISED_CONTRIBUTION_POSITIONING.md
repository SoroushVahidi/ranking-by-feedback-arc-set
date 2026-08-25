# Revised Contribution Positioning

Date: 2026-08-24
Synthesizes: `PRIOR_WORK_OVERLAP_MATRIX.md`, `PRIOR_ADDBACK_LINEAGE.md`,
`EXPERIMENTAL_SCOPE_COMPARISON.md`, `DF03_PRIMARY_THEOREM_VERIFICATION.md`,
`DISTINCTNESS_AND_NEW_WORK_VERDICT.md`, `SPRINGER_PREPRINT_POLICY_AUDIT.md`. Conservative and
publication-safe by design — every claim below is traceable to a specific verified artifact.

## 1. What we MUST NOT claim

- That weight-prioritized edge reinsertion is a novel mechanism (it is explicit in [VK25]'s
  Algorithm 1 and originates as DF03's own suggested heuristic).
- That the exact cycle-safety/reachability test for reinsertion is a novel idea (it is DF03's
  original Phase-2 condition, restated identically in [VK25]'s Algorithm 1).
- That multi-pass (INS1/2/3) add-back is a beneficial algorithmic innovation (evidence
  characterizes it as compensation for an implementation weakening, with passes 2-3 typically
  contributing nothing).
- That the dataset suite is a "substantially expanded" or multi-fold-larger benchmark than [VK25]
  (the corrected count is +3 of 77, ≈4%).
- That the local-ratio Phase A, or its O(VE)-class complexity, is a novel result (both are DF03's,
  and DF03's own text already distinguishes the naive-DFS O(m(m+n)) case from the
  dynamic-reachability O(mn) case that this project's diagnostic finding falls into).
- That the ternary-search ratio-loss refinement (Phase C) is new (verbatim in [VK25]'s Algorithm
  2/3).
- That a constant/unconditional approximation guarantee holds for the shipped, time-budgeted
  implementation (per `DF03_PRIMARY_THEOREM_VERIFICATION.md` §6, it does not, unconditionally).
- That exchange-based local search for feedback arc sets is itself a new concept (prior art exists
  for tournaments; see `DISTINCTNESS_AND_NEW_WORK_VERDICT.md`).

## 2. What we CAN claim confidently

- A formal proposition, with proof, establishing exact equality between the optimal ranking cost
  and the optimal MWFAS weight, correctly scoped as a many-to-many (not one-to-one) solution
  correspondence — absent from [VK25] and from DF03 (the latter does not address ranking).
- A precise audit of the conditions under which DF03's inherited approximation guarantee
  transfers to the shipped implementation, sharpened into two separable claims (removed-weight
  bound vs. ranking-cost equivalence) and grounded directly in DF03's own primary theorem text and
  proof, not a secondary characterization.
- A worst-case construction proving the implementation's timeout/identity-order ranking fallback
  has unbounded error relative to OPT in general.
- Diagnosis, with controlled ablation evidence across 78/80 canonical datasets, that the currently
  shipped add-back mechanism does not reliably improve ranking quality relative to Phase-A-only
  (28 better / 37 worse / 13 tied on `upset_simple`), and that a corrected, exact-reachability
  implementation does (74/78 better, mean Δ≈-0.0086), with one honestly-reported regression
  (`Halo2BetaData`) and one honestly-reported compute-budget limitation (`finance`).
- A formally proved (not merely tested) one-pass-sufficiency and inclusion-minimality result for
  the corrected implementation's specific efficient (incremental-reachability-matrix) realization.
- A ten-baseline classical-method comparison where [VK25] has zero.
- A dense/near-complete-graph stress case (`finance`) and its associated failure-mode diagnosis,
  both absent from [VK25].

## 3. What is new relative to our own preprint ([VK25])

Everything in §2, plus: reproducibility/ablation infrastructure (41+ new tests, a full-suite
phase-ablation harness, determinism guarantees explicitly tested rather than only implicit).

## 4. What is new relative to external literature

The formal ranking-MWFAS equivalence proof and the sharpened approximation-guarantee analysis
appear new relative to the specific external sources checked this pass (DF03, the local-ratio
survey literature, [CCP24]/[CCP25]). This is a **search-scoped** claim, not an exhaustive
literature-clearance claim — a dedicated literature check by a domain expert or a more exhaustive
search pass remains advisable before final submission, per standard practice for any
theory contribution.

## 5. What is merely implementation correction

The reachability-add-back mechanism itself (the *idea*, not its specific efficient
implementation or proofs) — restoring DF03's/[VK25]'s own specified exact test in place of the
shipped topo-order proxy.

## 6. What is empirical extension

Ten classical baselines (from zero); the `finance` dense-graph case; the phase-ablation harness
and its full-suite results; the pre-existing sparse-regime audit (not produced in this revision
pass, but likewise absent from [VK25]).

## 7. What is theoretical clarification

The formal equivalence proposition; the approximation-guarantee scoping; the timeout-fallback
unbounded-error proof; the complexity re-derivation (O(mn+m²) vs. the informally-cited O(VE)),
now directly cross-validated against DF03's own text distinguishing exactly this naive-vs-optimized
gap.

## 8. Recommended three contribution bullets (publication-safe)

1. *We formally establish the exact equivalence between the optimal ranking objective and the
   optimal weighted feedback arc set value — a connection used informally in prior work
   (Vahidi & Koutis, arXiv:2412.16181) but not previously proved — and precisely characterize it
   as a many-to-many, not one-to-one, solution correspondence.*
2. *We diagnose a fidelity gap between the edge-reinsertion (add-back) procedure as originally
   specified (Demetrescu & Finocchi, 2003; adopted identically in our own prior preprint) and as
   implemented in the accompanying codebase, and provide a corrected, efficient implementation
   with proved one-pass sufficiency and inclusion-minimality, evaluated across 78 of 80 canonical
   benchmark datasets against both the legacy implementation and Phase-A-only.*
3. *We audit the conditions under which the inherited Demetrescu-Finocchi approximation guarantee
   transfers to a practically time-budgeted implementation, proving a worst-case unbounded error
   for the timeout fallback and expanding the empirical comparison to ten classical ranking
   baselines absent from prior work on this method.*

## 9. Recommended one-paragraph research-gap statement

*"Prior work (Vahidi & Koutis, arXiv:2412.16181) established that ranking from pairwise
comparisons can be effectively addressed via a local-ratio minimum-weighted-feedback-arc-set
heuristic, demonstrating strong empirical performance against learned (GNN-based) ranking methods.
That work left several questions explicitly open: it asserted, without proof, that ranking and
MWFAS share the same optimum; it inherited an approximation guarantee from Demetrescu and
Finocchi (2003) without auditing whether that guarantee survives a practical, time-budgeted
implementation; and it identified 'developing more efficient cycle detection techniques' and
'identifying principled tie-breaking mechanisms' as future work. This paper closes these gaps: we
prove the ranking-MWFAS equivalence precisely, audit the approximation guarantee's actual
applicability (finding it does not transfer unconditionally), diagnose and correct a fidelity gap
in the edge-reinsertion step relative to both the original algorithm and our own prior
specification of it, and substantially broaden the empirical comparison to classical ranking
baselines absent from prior evaluation of this method."*

## 10. Should the Introduction explicitly cite and distinguish the prior arXiv paper?

**Yes, unambiguously.** Reasons, all independently established in this audit: (a) it is the
closest prior work by a wide margin, sharing authors, algorithm, datasets, and even the specific
loss-function names and formulas; (b) it is trivially discoverable by any reviewer who searches the
topic (this audit found it via ordinary web search); (c) Springer's own policy explicitly
distinguishes administrative permissibility (favorable) from novelty sufficiency (a separate,
reviewer-judged question) — silence on the preprint would not resolve the novelty question and
would instead invite exactly the "is this new?" scrutiny this whole revision effort is trying to
pre-empt; (d) the preprint's own stated future-work items give the clearest, most legitimate
narrative available for why this journal submission exists — omitting the citation forfeits that
narrative for no benefit.
