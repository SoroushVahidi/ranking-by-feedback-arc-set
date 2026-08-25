# Min-Cut Weighted Exchange: Research Question (Design Only)

Date: 2026-08-24
**Status: design/formalization only. No implementation in this document or this branch.** This
is the rank-1 candidate from `DISTINCTNESS_AND_NEW_WORK_VERDICT.md`'s ranked list, formalized here
per this task's explicit instruction to design, not build, the mechanism.

## Setup

Let `D = (V, K)` be the current kept DAG (after Phase A and, optionally, reachability add-back has
already run to completion — i.e. `D`'s removed-edge set is inclusion-minimal per
`REACHABILITY_ADDBACK_DESIGN.md` §4). Let `e = (u, v)` be an excluded (removed) edge with weight
`w(e)`, rejected because `v` can reach `u` in `D` (the reachability test).

## Candidate mechanism

1. **Trivial case**: if `v` does not reach `u` in `D`, plain reachability add-back already handles
   it (insert `e` directly, no exchange needed). This document only concerns the case where `v`
   *does* reach `u`.
2. Since `v` reaches `u`, there is at least one directed `v -> u` path in `D`. Consider the set of
   all such paths, and find (or approximate) a **directed edge cut** `C ⊆ K`: a set of currently-
   kept edges whose removal destroys every `v -> u` path in `D`.
3. **Candidate exchange**: `D' = (D \ C) ∪ {e}`.
4. **Acceptance rule**: accept the exchange iff `w(C) < w(e)` (a strict improvement in total
   removed-edge weight — see Claim 3 below); otherwise reject `e` as before.

## Claims to prove or verify (not yet proved in this document — stated as the research questions)

**Claim 1 (acyclicity preservation).** Removing a `v -> u` edge cut `C` from `D` before adding
`e = (u, v)` yields an acyclic graph `D'`.

*Proof sketch (to be formalized/verified, not yet a completed proof)*: `D` is acyclic. Adding `e`
to `D \ C` can only create a cycle through `e` if there remains a `v -> u` path in `D \ C` (the
same reachability argument used throughout this project — see
`RANKING_MWFAS_EQUIVALENCE.md`'s Step 2(a) construction). By definition, `C` is chosen to be a cut
that destroys *every* `v -> u` path in `D`; if `C` is a correct/complete cut, no such path
survives in `D \ C`, so `D' = (D \ C) ∪ {e}` is acyclic. **This claim is only as strong as the
correctness of the cut computation** — an approximate or incomplete cut would not guarantee this,
so any implementation must use an exact min-cut (or exact reachability re-verification after
removing `C`, as a cheap correctness check) rather than a heuristic cut approximation, at least
until the heuristic's completeness is separately established.

**Claim 2 (removed-weight delta).** `Δ = w(C) - w(e)` is the exact change in total removed-edge
weight from performing the exchange (removing `C` from the kept set adds `w(C)` to the removed-set
weight; adding `e` to the kept set removes `w(e)` from it).

*This is immediate from the definitions* (removed-set weight is additive over independent edge
membership changes), not a deep result — recorded as a claim only to make the acceptance rule's
arithmetic explicit and auditable.

**Claim 3 (strict local improvement).** If `w(C) < w(e)`, accepting the exchange strictly
decreases the total removed-edge weight (equivalently, strictly increases total kept-edge weight).

*Follows directly from Claim 2*: `Δ < 0` iff `w(C) < w(e)`, which is exactly the acceptance rule.

**Claim 4 (termination).** A sequence of exchanges, each accepted only when strictly improving
(Claim 3), terminates in finitely many steps on a finite graph.

*Proof sketch*: total removed-edge weight is a nonnegative real number, strictly decreasing at
each accepted step, and bounded below by 0 (or, more precisely, by the true optimum `OPT`, which
is itself finite and nonnegative). A strictly decreasing sequence bounded below converges, but
**this does not by itself bound the number of *discrete* steps** unless weights are bounded away
from 0 by some `epsilon` (e.g., integer or rational weights with bounded denominator, which is the
practical case for pairwise-comparison counts) — **this gap should be closed explicitly before
claiming termination as a theorem**: state the claim as "terminates in finitely many steps given
weights drawn from a discrete/rational set with bounded precision" rather than for arbitrary real
weights, where a pathological infinite-descent sequence is conceivable (though not encountered in
practice with count-based weights).

**Claim 5 (this does NOT imply global optimality — must be stated explicitly).** A locally-accepted
exchange strictly improves the *current* solution's removed-edge weight; **it does not imply the
final result is a global optimum for MWFAS**. This is standard for any local-search/exchange
method (the same caveat applies to the tournament-restricted "fc-exchange" local search found in
the literature search for `DISTINCTNESS_AND_NEW_WORK_VERDICT.md`). The manuscript must not
overclaim optimality from this mechanism alone.

**Claim 6 (ranking loss may differ from the FAS-set objective — must be evaluated empirically, not
assumed).** Per `RANKING_MWFAS_EQUIVALENCE.md` Remark 2 and the empirical `Halo2BetaData`
counter-example in `REACHABILITY_AUTHORITATIVE_SUMMARY.md` §5, a strict improvement in total
removed-edge *weight* does not, by itself, guarantee an improvement in `upset_simple`,
`upset_ratio`, or `upset_naive` — the induced ranking depends on *which* edges are kept, not only
on the total weight, and the equivalence between ranking cost and FAS weight specifically requires
inclusion-minimality (already true of `D` by construction here) *and* is with respect to *some*
topological order of the result, not necessarily the one the pipeline happens to extract. **Any
manuscript claim that this mechanism improves ranking quality must be backed by the same kind of
paired empirical W/T/L evidence used elsewhere in this project (`REACHABILITY_AUTHORITATIVE_SUMMARY.md`),
not inferred from the weight-improvement guarantee alone.**

## Unresolved design questions (explicitly not decided in this document)

- **Full-graph min-cut vs. affected-region min-cut**: computing an exact min-cut on the full graph
  per candidate edge is likely too expensive at scale; restricting to the subgraph "between" `u`
  and `v` (e.g. the union of `v -> u` paths, or the relevant SCC) is the natural optimization but
  its correctness (does a min-cut on the restricted region equal the min-cut on the full graph for
  this specific `v -> u` separation problem?) needs a formal argument, not an assumption.
- **Cost of one min-cut per rejected edge**: even a fast max-flow/min-cut algorithm run once per
  candidate rejected edge, across potentially many rejected edges per dataset, could dominate
  runtime; needs a complexity budget analysis before implementation (see `COMPLEXITY_AUDIT.md` for
  the project's existing budget-discipline conventions).
- **Top-K candidate restriction**: per the original ablation-workstream task's own framing, only
  attempting this for the highest-weight rejected edges (bounded by an explicit wall-clock budget)
  is the natural scoping — the exact `K` or budget policy is undetermined.
- **Incremental reachability interaction**: `D`'s reachability structure (the incremental matrix
  from `REACHABILITY_ADDBACK_DESIGN.md`) would need to be updated after each accepted exchange
  (both the removal of `C` and the addition of `e`) — removal is *not* handled by the existing
  incremental-reachability design, which only supports insertion; a removal-aware update (or a
  full rebuild after each accepted exchange) needs to be designed.
- **Should cut edges re-enter the candidate pool?** After removing `C` and adding `e`, the edges in
  `C` become "removed" again — should they be re-considered for their own reachability/exchange
  check later in the same pass? Doing so could cascade; not doing so could leave a
  reachability-safe-after-the-fact edge unconsidered. Undecided.
- **Cycling possibility**: if a previously-inserted edge can later be removed by a subsequent
  exchange's cut, and a subsequent-subsequent exchange could reinsert a related edge, is a cycle of
  exchanges (not to be confused with a *graph* cycle) possible, where the same edge set
  configuration recurs? Claim 4's strict-improvement property should rule this out (each accepted
  step strictly decreases a bounded-below quantity, so exact repetition is impossible), but this
  should be stated as a corollary of Claim 4, not assumed independently.
- **Deterministic tie handling**: if multiple minimum cuts exist for a given `(u,v)`, or multiple
  rejected edges tie in weight, a deterministic tie-break rule (consistent with the project's
  existing stable-sort-by-original-edge-id convention) needs to be specified.
- **Interaction with Phase C ranking refinement**: does running Phase C after an exchange-modified
  kept set behave identically to running it after plain reachability add-back (i.e. is Phase C
  agnostic to *how* the kept set was produced)? Expected yes (Phase C only depends on the final
  kept/removed partition, per its own code), but should be confirmed, not assumed.
- **Time-budget semantics**: how the existing global `time_limit_sec` budget should be shared
  between reachability add-back and the exchange pass (sequential sub-budgets? a single shared
  clock checked throughout?) is undetermined.

## Explicit non-goal for this document

This document does not implement, benchmark, or claim novelty for the mechanism above — see
`MINCUT_EXCHANGE_PRIOR_ART_CHECKLIST.md` for the literature-search questions that must be answered
before any novelty claim, and `DISTINCTNESS_AND_NEW_WORK_VERDICT.md` for why this is treated as
risk-reduction, not a scientific necessity, for the current revision.
