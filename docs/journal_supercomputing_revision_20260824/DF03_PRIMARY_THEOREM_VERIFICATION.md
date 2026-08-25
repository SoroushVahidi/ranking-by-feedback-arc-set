# DF03 Primary-Theorem Verification

Date: 2026-08-24
Source: Demetrescu, C., Finocchi, I. **"Combinatorial Algorithms for Feedback Problems in
Directed Graphs."** Retrieved and read in full directly from the authors' institutional PDF
(diag.uniroma1.it/~demetres/docs/mfas.pdf), all 9 pages, including both theorems' full proofs.
This resolves the item the sibling theory-audit branch (`jsuper-revision-novelty-theory-20260824`)
left as unresolved/secondary-sourced (`APPROXIMATION_GUARANTEE_AUDIT.md` §1 there). **Status:
RESOLVED — primary text obtained and read in full.**

## 1. Exact problem statements (Section 2 of the primary source)

- `FAS`: directed graph `G=(V,A)`, nonnegative arc weights `w: A -> ℜ+`. Find minimum-weight
  `A' ⊆ A` such that `(V, A\A')` is acyclic.
- `FVS`: analogous, on vertices with nonnegative vertex weights.
- A feedback set `C` is defined as **minimal** iff no proper subset of `C` is itself a feedback
  set. (This is the exact same "inclusion-minimal" definition used in
  `RANKING_MWFAS_EQUIVALENCE.md` on the sibling theory-audit branch — confirmed identical
  terminology, not a coincidence of naming.)
- An `r`-approximation is defined as `w(F') <= r · w(F*)` for the optimum `F*`.

**Weights are required to be nonnegative** (`w: A -> ℜ+`, and the paper's convention here — per
context, e.g. "any nonnegative weight functions" — includes zero; nothing in the proof requires
strict positivity). This matches, and slightly relaxes, the strictly-positive assumption both the
shipped codebase (`w > 0` filter) and the sibling theory-audit's
`RANKING_MWFAS_EQUIVALENCE.md` Remark 4 adopted; strict positivity is a safe (if slightly
stronger than necessary) implementation choice, not a mismatch with the source theorem.

## 2. Algorithm FAS (Figure 1 of the primary source) — exact pseudocode

```
F <- ∅
while (V, A\F) is not acyclic:                                  { Phase 1 }
    C <- a simple cycle in (V, A\F)
    (x,y) <- a minimum-weight arc in C, weight epsilon
    for each (v,w) in C:
        w(v,w) <- w(v,w) - epsilon
        if w(v,w) = 0: F <- F ∪ {(v,w)}
for each (v,w) in F:                                             { Phase 2 }
    if (V, (A\F) ∪ {(v,w)}) is acyclic:
        F <- F \ {(v,w)}
return F
```

**This is a verbatim match, component-for-component**, to what the sibling novelty/theory
audit's `CURRENT_METHOD_DECOMPOSITION.md` and the authors' own [VK25] Algorithm 1 both already
described as the "Phase A local-ratio reduction" and "Phase B exact-cycle-check add-back." No new
divergence found by reading the primary source directly.

## 3. Theorem 1 (running time) — precise statement and a critical nuance

> **Theorem 1.** Let `G=(V,A,w)` be a weighted directed graph with `n` vertices and `m` arcs.
> Algorithm FAS finds a **minimal** feedback arc set of `G` in **O(m·n)** worst-case running time.

**Critical nuance, confirmed directly from the proof text — this materially strengthens the
sibling branch's `COMPLEXITY_AUDIT.md` finding rather than merely repeating it**: the O(m·n)
bound is **not** achieved by a naive from-scratch cycle search each iteration. The proof states
explicitly:

> "A simple-minded implementation of the first operation (by means of a visit), would yield
> **O(m·(m+n))** overall running time. However, this bound can be reduced to **O(m·n)** by using
> a dynamic algorithm for maintaining reachability information in digraphs subject to deletion of
> arcs [i.e. Demetrescu & Italiano's own separate FOCS'00 dynamic transitive-closure data
> structure, cited as [8] in the primary source]."

**This is a direct, primary-sourced confirmation of exactly the complexity gap the sibling
`journal-supercomputing-major-revision-20260824` branch's `COMPLEXITY_AUDIT.md` (on that branch)
independently derived from reading the shipped codebase**: that codebase's Phase A rebuilds a
fresh DFS/color array each iteration and rescans stale adjacency-list entries rather than
maintaining an incremental reachability structure — i.e., it is precisely the **"simple-minded
implementation... O(m·(m+n))"** case DF03 themselves identify and explicitly warn is the
*slower* alternative, not the O(m·n) case, which DF03 states requires the dedicated
dynamic-reachability data structure of Demetrescu & Italiano (FOCS 2000) — a structure that is
**not present anywhere in this project's codebase** (neither on `main` nor on either sibling
branch). **Verdict: the O(VE)/O(mn) complexity characterization cited in [VK25] and repeated
informally elsewhere is only valid for a version of Phase A that neither the shipped codebase nor
[VK25]'s own implementation (a plain Python/DFS implementation, per [VK25]'s own text: "cycle
detection via depth-first (or breadth-first) search") actually is.** Both [VK25] and the current
JOS codebase implement the "simple-minded," slower variant.

## 4. Theorem 2 (approximation ratio) — precise statement, full proof read

> **Theorem 2.** Let `G=(V,A,w)` be a weighted directed graph. Algorithm FAS approximates a
> minimum feedback arc set of `G` within a ratio bounded by the length **λ** of a **longest
> simple cycle of `G`** (length counted in number of arcs, independent of the weight function).

Proof structure (read in full, Lemma 1 + induction on while-loop iterations):
- **The approximation ratio is established using Phase 1 alone.** The proof explicitly states:
  *"The second phase of algorithm FAS is only required for making the previously found feedback
  arc set minimal. Since the weight of the feedback arc set can only decrease during this phase,
  it is sufficient to prove that the approximation ratio is already guaranteed after Phase 1."*
  **This is an important, precise nuance not previously stated this precisely on either sibling
  branch**: the λ-approximation bound on the *removed-weight* of the FAS depends only on Phase 1
  running to convergence (i.e. until the graph is acyclic) — it does **not** depend at all on how
  Phase 2/add-back is implemented (topo-order proxy vs. exact reachability vs. skipped
  entirely), because Phase 2 can only ever *decrease* `w(F)`, which trivially preserves an
  upper-bound guarantee. **What Phase 2's fidelity *does* determine is minimality** (Theorem 1),
  which is what makes the *ranking cost* (not the raw FAS weight) provably equal to `w(F)` — see
  the sibling theory-audit branch's `RANKING_MWFAS_EQUIVALENCE.md` Remark 2, which this finding
  now sharpens: **the λ-approximation bound protects the removed-edge weight regardless of
  add-back fidelity; it is specifically the ranking-cost-equals-FAS-weight equivalence (Remark 2
  there) that breaks down under the topo-order proxy's non-minimality, not the λ-approximation
  bound itself.** These are two distinct guarantees and the fidelity gap diagnosed on the sibling
  branch affects only the second one.
- Induction is on the number of Phase-1 while-loop iterations (finite, strictly decreasing since
  `>= 1` arc is removed per iteration — matching exactly the `I <= m` bound independently derived
  in the sibling branch's `COMPLEXITY_AUDIT.md`).
- Base case: already-acyclic input, empty FAS is trivially optimal.
- Inductive step: for the cycle `C` (length `k <= λ`) found at a given iteration with minimum
  arc weight `epsilon`, a weight-splitting argument (`w = w1 + w2`, `w1` supported only on `C`)
  plus Lemma 1 (`w1(F1*) + w2(F2*) <= w(F*)`, valid for **any** linear weight decomposition, not
  specific to this algorithm) gives `w(F) <= λ·w(F*)` by direct algebraic telescoping. The
  full chain is reproduced faithfully; no gap or unstated assumption was found in the proof
  itself.

## 5. Assumptions explicitly required by the theorem

1. **Nonnegative arc weights** (`w: A -> ℜ+`) — required for `Lemma 1`'s inequalities
   (`w1(F*) >= w1(F1*)` etc.) to hold in the stated direction; matches
   `RANKING_MWFAS_EQUIVALENCE.md` Remark 4 on the sibling branch.
2. **Phase 1 runs to convergence** (the `while` loop in the pseudocode terminates only when the
   graph is acyclic — there is **no time budget, wall-clock cutoff, or iteration cap** anywhere
   in DF03's algorithm or its proof). **This is the single most important precondition for this
   revision's purposes**: DF03's guarantee is unconditionally about the *fully-converged*
   algorithm. Any implementation (the shipped JOS codebase, and — per its own text describing a
   plain DFS-based implementation with no mentioned time budget — very likely [VK25]'s own
   implementation too) that imposes a wall-clock early exit is, by DF03's own theorem statement,
   outside the scope of what Theorem 2 proves, exactly as the sibling
   `journal-supercomputing-major-revision-20260824` branch's `APPROXIMATION_GUARANTEE_AUDIT.md`
   independently concluded (verdict "(B): applies only to an unbudgeted, idealized variant") —
   **now confirmed against the actual primary theorem text rather than a secondary
   characterization.**
3. **Directed graphs, arc weights** — DF03 also gives an FVS (vertex) variant (§3.2) by a direct
   analogy (same algorithm, vertices/vertex-weights in place of arcs/arc-weights); not used by
   this project (which only ever needs FAS), noted for completeness only.
4. **Weighted digraphs generally** (no restriction to tournaments, no restriction on density) —
   the guarantee applies to arbitrary weighted digraphs, consistent with how it is used
   throughout this project's codebase and [VK25].

## 6. Relationship to the shipped implementation — final verdict

Combining this primary-source read with the sibling branches' independent findings:

| DF03 requirement | Shipped codebase (`main`) | Consequence |
|---|---|---|
| Nonnegative weights | `w > 0` (strictly positive, a safe strengthening) | No issue |
| Phase 1 to convergence, no time budget | Wall-clock `time_limit_sec` cutoff inside the Phase-1 loop, confirmed to trigger on `finance` (sibling branch's `REVISION_RESULTS.md` §4) | **Guarantee void on any dataset where this triggers** — confirmed exactly per DF03's own theorem preconditions, not merely inferred |
| O(m·n) requires a dynamic reachability structure (Demetrescu-Italiano FOCS'00) for the cycle search | Fresh DFS + stale-adjacency-list rescanning each iteration (no such structure) | **Actual complexity is DF03's own explicitly-named "simple-minded," O(m·(m+n)) case**, not O(mn) — this pass's own primary-source read directly confirms the complexity-audit finding rather than merely corroborating it secondarily |
| Phase 2 (any order, any correctness) only affects **minimality**, not the λ-bound itself | Phase 2 implemented as a fixed-topo-order proxy (weaker than DF03's exact test) | The λ-bound on **removed FAS weight** is unaffected by this specific deviation (per §4 above) **as long as Phase 1 converges**; what breaks is minimality, hence the ranking-cost-equals-FAS-weight equivalence (see `RANKING_MWFAS_EQUIVALENCE.md` Remark 2 on the theory-audit branch) — a more precise, narrower statement of harm than "the guarantee doesn't apply" |

**Overall verdict, refining the sibling branch's (B): "applies only to an unbudgeted, idealized
variant"** — now sharpened into two separable claims, both confirmed against the primary
source:

- **(B-i) Removed-FAS-weight λ-approximation**: holds if and only if Phase 1 runs to
  convergence, independent of Phase 2's fidelity. Void on `finance` and any other dataset where
  the wall-clock budget is exhausted before acyclicity.
- **(B-ii) Ranking-cost equals removed-FAS-weight** (needed to make (B-i) meaningful for the
  *ranking* objective specifically, not just the abstract FAS objective): holds only if the final
  removed set is inclusion-minimal, which requires Phase 2 to implement the exact
  reachability/cycle-safety test — which the shipped topo-order-proxy Phase 2 does not guarantee,
  independent of whether Phase 1 converged.

Recommended manuscript language (refines the sibling branch's recommendation):
*"Phase A is based on the local-ratio feedback-arc-set algorithm of Demetrescu and Finocchi
[DF03], whose Theorem 2 guarantees the removed edge weight is within a factor λ (the length of
the longest simple cycle in the input graph) of optimum, provided the algorithm is run to
convergence. Two implementation-level conditions must both hold for this guarantee to transfer
to our reported ranking-cost metrics: (i) our wall-clock-budgeted Phase A must reach acyclicity
before its time budget is exhausted (see Table [X] for the [N] of [M] datasets where this holds),
and (ii) our edge-reinsertion step must produce an inclusion-minimal residual feedback arc set
(Demetrescu and Finocchi's own Theorem 1), which requires the exact reachability-based
cycle-safety test of their Phase 2 rather than a topological-order proxy."*
