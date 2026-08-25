# Ranking ↔ MWFAS: Formal Equivalence

Date: 2026-08-24

This addresses Reviewer 1's request for a rigorous derivation of the
relationship between the ranking objective and Minimum Weighted Feedback Arc
Set (MWFAS). The authors' own prior paper ([VK25], arXiv:2412.16181) states
both problems' definitions side by side and asserts informally that "the
ranking problem can be reformulated as an instance of the MWFAS problem," but
contains **no formal proposition or proof** of this — it is asserted, not
derived (see `NOVELTY_LITERATURE_MATRIX.md` for the source-checked
confirmation that [VK25]'s §4 explicitly lists this kind of theoretical
development as *future* work). What follows is new relative to [VK25] and is
written to be manuscript-ready, with the scope of the claim stated precisely
per the task's caution against over-claiming a one-to-one correspondence.

## Setup

Let `G = (V, E)` be a directed graph with `|V| = n`, no self-loops, and a
weight function `w: E -> R_{>0}` (strictly positive; this matches
`_csr_to_edges`'s explicit filter `mask = w > 0` in the current
implementation, and is required for the MWFAS objective to have its intended
combinatorial meaning — see Remark 4 below). Antiparallel edge pairs, i.e.
both `(i,j) ∈ E` and `(j,i) ∈ E` with independent positive weights, are
explicitly permitted; nothing below assumes a simple graph or forbids them,
and this matters because two-directional comparison counts (wins and losses
both recorded as separate weighted arcs) are exactly the input format used by
this codebase's real datasets.

**Definition (Ranking).** A *ranking* is a bijection `R: V -> {1, ..., n}`
(a strict total order — no ties; see Remark 3 for the tie-allowing variant).
Edge `(i,j) ∈ E` is *violated* by `R` iff `R(i) > R(j)`. The ranking cost is
```
  cost(R) = sum_{(i,j) ∈ E : R(i) > R(j)} w(i,j).
```
(This matches the ranking-problem definition used in [VK25] and this
codebase's `upset_naive`/`upset_simple`-style conventions modulo the tie
handling discussed in Remark 3.)

**Definition (MWFAS).** A *feedback arc set (FAS)* is a subset `F ⊆ E` such
that `(V, E \ F)` is acyclic. `F` is *inclusion-minimal* iff for every
`e ∈ F`, `F \ {e}` is not a feedback arc set (equivalently: `(V, (E\F) ∪
{e})` is cyclic — reinserting any single removed edge recreates a cycle).
The MWFAS problem is
```
  OPT = min { sum_{e ∈ F} w(e) : F is a feedback arc set of G }.
```

## Proposition

```
  min_{R} cost(R) = OPT.
```
That is, the optimal ranking cost equals the optimal MWFAS weight **exactly**
— not merely bounded above or below by it. Moreover:

(a) For every feasible FAS `F`, **every** topological order `R` of the DAG
    `(V, E \ F)` satisfies `cost(R) <= sum_{e ∈ F} w(e)`.

(b) If `F` is additionally inclusion-minimal, equality holds:
    `cost(R) = sum_{e ∈ F} w(e)` for **every** topological order `R` of
    `(V, E \ F)` — not just for one specially-chosen order.

(c) The correspondence between optimal rankings and optimal FASs is
    **many-to-many, not one-to-one**: a single (inclusion-minimal, possibly
    optimal) FAS can correspond to many distinct optimal rankings whenever
    `(V, E\F)` admits more than one valid topological order (i.e. whenever
    it has two vertices with no directed path between them either way), and
    the optimum MWFAS value can in general be attained by more than one edge
    set `F`. **No claim of a bijection is made or should be made.**

## Proof

**Step 1 (any ranking induces a feasible FAS of matching cost — gives
`min_R cost(R) >= OPT`).** Fix any ranking `R`. Let
`F_R = {(i,j) ∈ E : R(i) > R(j)}`. Every edge of `E \ F_R` satisfies
`R(i) < R(j)`, i.e. is "forward" under `R`; hence `R` restricted to `V` is by
construction a valid topological order of `(V, E \ F_R)`, so that graph is
acyclic and `F_R` is a feasible FAS. Its weight is
`sum_{e ∈ F_R} w(e) = cost(R)` by the definitions above. Since `F_R` is one
particular feasible FAS, `OPT <= sum_{e ∈ F_R} w(e) = cost(R)`. As `R` was
arbitrary, `OPT <= min_R cost(R)`.

**Step 2 (a) (any feasible FAS induces a ranking with cost at most its
weight).** Fix any feasible FAS `F` and any topological order `R` of the DAG
`(V, E \ F)` (one exists because the graph is acyclic; if several exist, pick
any). By definition of topological order, every edge `(i,j) ∈ E \ F`
satisfies `R(i) < R(j)`, i.e. is not violated by `R`. Hence every edge
violated by `R` lies in `F`:
`{(i,j) ∈ E : R(i) > R(j)} ⊆ F`, so
`cost(R) = sum_{(i,j): R(i)>R(j)} w(i,j) <= sum_{e ∈ F} w(e)`
(sum over a subset of a nonnegative-weighted set is at most the sum over the
whole set — this is where `w > 0`, or at least `w >= 0`, is used). This
proves (a).

**Step 2 (b) (inclusion-minimality forces equality for every topological
order).** Suppose `F` is inclusion-minimal and let `R` be any topological
order of `(V, E\F)`. By Step 2(a), the violated-edge set under `R` is a
*subset* of `F`; we show it is not a *proper* subset. Take any `(i,j) ∈ F`.
Inclusion-minimality means `(V, (E\F) ∪ \{(i,j)\})` is cyclic, i.e. adding
`(i,j)` back creates a cycle. Since `(V, E\F)` alone is acyclic, that cycle
must use the new edge `(i,j)` together with an existing directed path from
`j` to `i` entirely within `E\F` (this is precisely the reachability
characterization of cycle-safety used elsewhere in this project — see the
sibling branch's `REACHABILITY_ADDBACK_DESIGN.md`). Every edge on a `j -> i`
path in `E\F` is forward under the topological order `R` (by definition of
topological order), so positions strictly increase along the path, giving
`R(j) < R(i)`, i.e. `R(i) > R(j)` — exactly the violation condition for edge
`(i,j)`. Hence every `(i,j) ∈ F` is violated by `R`, i.e. `F ⊆` (violated set
under `R`). Combined with the reverse inclusion from Step 2(a),
(violated set under `R`) `= F` exactly, so `cost(R) = sum_{e ∈ F} w(e)`. This
holds for **every** topological order `R` of `(V, E\F)` (the argument never
depended on which one was chosen), proving (b).

**Step 3 (combining).** Apply Step 2(a)/(b) to an *optimal* FAS `F*`
(`sum_{e ∈ F*} w(e) = OPT`; note an optimal FAS is automatically
inclusion-minimal under strictly positive weights, since removing a
redundant edge from any feasible FAS strictly decreases its weight, so a
minimum-weight FAS cannot contain one). Let `R*` be any topological order of
`(V, E\F*)`. By Step 2(b), `cost(R*) = OPT`. Hence
`min_R cost(R) <= cost(R*) = OPT`. Combined with Step 1's
`OPT <= min_R cost(R)`, we get `min_R cost(R) = OPT`. **QED.**

## Remarks (scope of the claim, stated precisely per the task's caution)

**Remark 1 (many-to-many, not one-to-one).** Step 2(b) shows *every*
topological order of an optimal FAS's surviving DAG achieves the optimum —
so as soon as `(V, E\F*)` has two vertices with no path between them in
either direction (common whenever the comparison graph is not already a
total order after cycle removal — e.g. two players/items that never played
each other and share no indirect chain of common opponents at the relevant
positions), there are **multiple, generally many**, distinct optimal
rankings, all with identical cost, corresponding to the *same* optimal FAS.
Symmetrically, if the MWFAS optimum is attained by more than one edge set
(ties in the combinatorial optimization, which generically occur with
integer or coarsely-quantized weights, exactly the setting of pairwise
comparison counts), different optimal FASs can induce different sets of
optimal rankings. **The manuscript must not claim a bijection.** The correct
statement is exactly the Proposition above: equality of *optimal objective
values*, with an explicit (generally non-unique) witnessing map in each
direction (Steps 1 and 2), not a one-to-one correspondence of solutions.

**Remark 2 (this is why extraction from a non-minimal FAS can be
suboptimal).** Step 2(a) (the weaker, non-minimality-dependent direction)
only gives `cost(R) <= sum_{e ∈ F} w(e)`, a one-sided inequality. If `F` is
**not** inclusion-minimal (e.g., because it was produced by a heuristic that
leaves some removable edges out unnecessarily — exactly the failure mode
diagnosed for the legacy topo-order add-back mechanism in
`CURRENT_METHOD_DECOMPOSITION.md` §2 and quantified on the sibling branch),
the induced ranking's cost can be **strictly less** than `sum_{e ∈ F} w(e)`,
meaning a heuristic that reports "we removed a FAS of weight `X`" is not
directly reporting the ranking cost the pipeline will actually incur — the
two only coincide once inclusion-minimality is established (part (b)). This
gives a precise theoretical reason (not just an empirical one) why the
reachability-add-back workstream's inclusion-minimality property (proved
there, not merely tested) is the theoretically correct target, and why the
legacy topo-order add-back's kept set — which is **not** proven or
guaranteed inclusion-minimal, and can leave reachability-safe edges
unrestored (see `CURRENT_METHOD_DECOMPOSITION.md` §2) — has no theoretical
guarantee that its induced ranking cost even approaches `sum_{e ∈ F} w(e)`
for the `F` it actually removed.

**Remark 3 (ties).** The Proposition is stated for *strict* total-order
rankings (bijections to `{1,...,n}`). This is not a restrictive choice: Step
2's construction already produces a strict order (any topological order of a
DAG is a strict linear extension), so allowing ties (weak orders / total
preorders) cannot improve on the optimum already achieved by a strict order
— the optimum is attained within the strict-order class. However, this
codebase's own `upset_naive`/`upset_simple` loss functions use the
convention `mask = (s_i <= s_j)` to define "violated," which counts an exact
tie (`s_i == s_j`) as a violation. This is a stricter operational convention
than the Proposition's `R(i) > R(j)` (which does not penalize non-strict
equality because `R` is required to be a bijection, so `R(i) = R(j)` cannot
occur for `i != j`). **Practical consequence**: the equivalence in the
Proposition is exact for the abstract ranking-cost objective as defined
above; it is exact for this codebase's operational metrics *only when the
returned score vector is tie-free* (confirmed as a tested property for
`OURS_MFAS_INS3` by `tests/test_audit.py::test_ours_mfas_scores_are_unique`,
but not proven as a general property of the pipeline, and specifically not
guaranteed for any variant whose score-extraction step could in principle
produce ties — worth a one-line caveat in the manuscript rather than silent
elision).

**Remark 4 (why weights must be positive/nonnegative).** Step 2(a)'s
inequality `sum over violated subset <= sum over F` requires `w >= 0`
term-by-term; with negative weights permitted, "minimum weight edge set whose
removal breaks all cycles" stops being the right formalization of "minimum
total disagreement," since one could always further reduce the objective by
removing additional negative-weight edges regardless of whether they help
break any cycle, decoupling the FAS-minimization objective from the
cycle-breaking motivation entirely. This matches the codebase's own explicit
`w > 0` filter and should be stated as an explicit standing assumption in the
manuscript (currently implicit, per `CURRENT_METHOD_DECOMPOSITION.md`).

**Remark 5 (what this does *not* prove).** This Proposition is an *exact
value* equivalence for the two *optimization problems*, both NP-hard in
general (feedback arc set is NP-hard; Karp 1972, cited as [23] in [VK25]).
It says nothing about how *close* any particular polynomial-time heuristic's
output ranking is to the true optimum — that is the separate question
addressed by `APPROXIMATION_GUARANTEE_AUDIT.md`. The two documents are
complementary: this one licenses treating "solve MWFAS well" and "rank well"
as the same target (in the exact-optimum sense); the other establishes that
the specific heuristic actually shipped does not carry an unconditional
approximation guarantee for that target.
