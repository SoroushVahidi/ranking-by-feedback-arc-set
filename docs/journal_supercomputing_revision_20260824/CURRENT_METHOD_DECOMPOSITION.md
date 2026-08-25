# Current Method Decomposition (Novelty/Theory Workstream)

Date: 2026-08-24
Branch/worktree: `jsuper-revision-novelty-theory-20260824` @ `/tmp/ranking-jsuper-novelty-theory`
Base: `origin/main` @ `706b21771be3af61c8fd4dd22723d0d5611fa042`
Source verified: `GNNRank-main/src/ours_mfas.py`, `GNNRank-main/src/comparison.py` (as of
`main`, i.e. WITHOUT the reachability-add-back variant being developed on the
sibling branch `journal-supercomputing-major-revision-20260824` — that
variant is explicitly out of scope for this document per the task
instructions ("the CURRENT method, not the experimental reachability variant
being developed elsewhere")).

## 0. Critical context discovered during this audit

The exact algorithm implemented here (local-ratio cycle breaking + weight-
sorted cycle-safe add-back + ternary-search ratio-loss refinement, with
loss functions literally named "naive upset", "simple upset", "ratio upset")
is not merely *similar to* prior work — it is the direct continuation of the
authors' own prior publication:

> Soroush Vahidi, Ioannis Koutis. **"Minimum Weighted Feedback Arc Sets for
> Ranking from Pairwise Comparisons."** arXiv:2412.16181 (v2, Jan 7 2025;
> v3, Dec 4 2025). NJIT. Code: github.com/SoroushVahidi/Ranking_with_MWFAS.

This was found via literature search while investigating "closest prior
work" for Section C/D of this audit (see `NOVELTY_LITERATURE_MATRIX.md`).
Its Algorithm 1 (cycle-breaking via DFS + local-ratio residual reduction,
descending-weight add-back with an **exact** "does not create a cycle"
test), Algorithm 2/3 (ternary-search ratio-loss score refinement), and its
three loss definitions (naive/simple/ratio upset, Eqs. 1-3 of that paper)
match this repository's `_local_ratio_break_cycles`, `_addback_desc_weight_multi`
(component-wise, modulo the fidelity gap noted in §2 below),
`refine_scores_ratio_ternary`, and `upset_naive`/`upset_simple`/`upset_ratio`
respectively, essentially one-to-one. **This is the single most important
fact for the novelty positioning of the JOS manuscript**: whatever is claimed
as new must be new *relative to this prior arXiv paper*, not merely relative
to the general literature. See `NOVELTY_LITERATURE_MATRIX.md` and
`NOVELTY_THEORY_REVIEWER_MAP.md`.

## 1. Phase A: local-ratio cycle breaking

Implementation: `_local_ratio_break_cycles()`, `_find_one_cycle_edges()`.

- **Cycle detection**: iterative (explicit-stack, non-recursive) DFS with a
  three-color (white/gray/black) scheme over all `n` vertices, restricted to
  currently-`alive` edges via a per-vertex adjacency list built once from all
  edges (dead edges skipped in-place during traversal, not removed from the
  adjacency list). Vertices are scanned for DFS roots in increasing index
  order (`for s in range(n)`), so which cycle is found first (when several
  exist) is **deterministic** given the input edge order — but it is an
  *arbitrary* simple cycle in the sense that no attempt is made to find the
  shortest, longest, or minimum-weight cycle; it is whichever cycle the fixed
  DFS traversal order encounters first.
- **Residual reduction (the "local-ratio" step)**: maintains a residual
  weight `residual[e]` per edge, initialized to the original weight. On each
  iteration: find one cycle (edge-id list), compute
  `delta = min(residual[e] for e in cycle)`, subtract `delta` from every
  edge's residual on that cycle, then permanently kill (`alive[e] = False`)
  every edge whose residual reaches `<= zero_tol` (default `1e-15`).
- **Numerical/forced-progress safeguards** (two distinct ones, both absent
  from a textbook description of the local-ratio method):
  1. If the computed `delta <= 0.0` (should not happen with positive weights
     and a genuine cycle, but guarded against floating-point drift), the
     minimum-residual edge on the cycle is force-killed instead of
     subtracting.
  2. If, after subtracting `delta`, *no* edge actually drops to `<= zero_tol`
     (possible only through floating-point round-off, since `delta` is
     defined as the exact minimum), the minimum-residual edge is force-killed
     anyway, to guarantee the loop makes progress every iteration.
- **Termination**: the `while True` loop checks `time.time() - t0 >
  time_limit_sec` at the *start* of every iteration (i.e. before searching
  for the next cycle) and breaks if the global wall-clock budget is
  exhausted — **not** when the graph becomes acyclic per se, though in
  practice the loop also exits via `cyc_e is None` (no cycle found) once
  acyclicity is reached. **If the time budget is exhausted first, Phase A
  returns a graph that may still be cyclic.** This is confirmed directly in
  this pass's ablation run: `finance` (n=1315, m=1.7M) exhausts its entire
  60s budget inside this loop without necessarily reaching acyclicity (see
  the sibling ablation workstream's `REVISION_RESULTS.md` §4 for the
  empirical confirmation on that dataset, and §"Timeout and fallback
  reliability" in `APPROXIMATION_GUARANTEE_AUDIT.md` for the theoretical
  consequence).
- **Classification: adapted implementation detail** of a known algorithm
  (Demetrescu & Finocchi 2003's local-ratio MFAS/MFVS heuristic — see
  `NOVELTY_LITERATURE_MATRIX.md`), with three implementation-specific
  deviations (`zero_tol`, forced-progress kills, wall-clock early exit) that
  are engineering necessities but are **not** part of the guarantee proof for
  the original algorithm and must be audited separately
  (`APPROXIMATION_GUARANTEE_AUDIT.md`).

## 2. Phase B: descending-weight add-back

Implementation: `_addback_desc_weight_multi()`.

- Computes **one** topological order (`_toposort_kahn_from_edges`, Kahn's
  algorithm) of the current kept-edge DAG at the start of each of up to
  `insertion_passes` (1/2/3 for INS1/INS2/INS3) passes.
- Scans Phase-A-removed edges in **stable descending original weight** order
  (`np.argsort(-w, kind="mergesort")`).
- Accepts edge `(u, v)` iff `pos[u] < pos[v]` in the **single fixed order**
  computed at the start of the pass — i.e. "forward w.r.t. one arbitrary
  topological order," a *sufficient* but not *necessary* condition for
  cycle-safety.
- Repeats for additional passes, recomputing the topological order from the
  larger kept set each time.

**Fidelity gap versus the prior arXiv paper's Algorithm 1.** That paper's
pseudocode for this exact step reads: *"foreach edge (u,v) removed in Phase 1
do: if re-adding (u,v) does not create a cycle then re-add (u,v) to the
graph"* — a single pass testing the **exact** necessary-and-sufficient
cycle-safety condition (does `v` reach `u`?), with no mention of a fixed
topological-order proxy and no INS1/INS2/INS3 multi-pass concept. The
currently-shipped code instead tests a strictly more conservative,
order-dependent proxy condition, and compensates for that proxy's
incompleteness by adding multiple passes. **This means the current
implementation is not a faithful reproduction of the algorithm as the
authors themselves already described it in their own prior publication** —
it is a (likely later, undocumented) implementation change that trades
exactness for the cheaper "reuse a fixed topo order" check, then patches
around the resulting gap with repeated passes. This is a correctness/fidelity
finding, not merely a stylistic one, and is independent of whatever the
sibling reachability-add-back workstream produces — see
`NOVELTY_THEORY_REVIEWER_MAP.md` for how this should be communicated to
reviewers alongside that workstream's results.
- **Classification: adapted implementation detail that deviates from the
  authors' own previously-published pseudocode.** Not itself claimable as
  novel (the arXiv paper's exact-cycle-check version already existed); the
  multi-pass INS1/2/3 mechanism is better read as an ad hoc compensation for
  an implementation weakening than as an independent contribution.

## 3. Score extraction from the kept DAG

Implementation: `_scores_from_kept_edges()`. Topological order -> integer
position -> `score = n - pos` (earlier in topo order = larger score = better
rank), floored at 1. **Classification: standard/engineering element** (any
topological sort trivially induces a total order; this is the textbook way
to turn a DAG into a ranking).

## 4. Optional naive-upset local search (adjacent-swap refinement)

Implementation: `_refine_order_naive_swaps()`. Greedy left-to-right sweep of
*adjacent* pairs in the current order, accepting a swap iff it strictly
reduces the weighted naive-upset loss (Eq. 1 of the prior arXiv paper,
`upset_naive` here), for up to `max_passes` sweeps, bounded by both a local
and the global time budget. This is a bubble-sort-like local search — a
standard, well-known technique (adjacent transposition / bubble-sort local
search is textbook material in the linear-arrangement / minimum linear
arrangement literature). **Classification: adaptation of a standard local
search, not a new algorithmic idea by itself.**

## 5. Phase C: ratio-upset ternary-search refinement

Implementation: `refine_scores_ratio_ternary()`, `_ternary_opt_one()`. For
each node (processed in ascending-score order, one coordinate at a time,
holding all other scores fixed), a ternary search over the score's feasible
interval (bounded by its immediate neighbors in the current order, so the
*order* can never change — only the numeric gaps between adjacent scores) is
used to locally minimize the ratio-upset loss (Eq. 3 of the prior arXiv
paper). Multiple passes with a final "monotone repair" step re-enforce strict
ordering against floating-point drift. This is essentially identical to the
prior paper's Algorithm 2/3 ("Trinary Search Optimization for Minimizing
Ratio Upset Loss" / "Minimize Ratio Upset Loss"), which already documents
this as coordinate-wise, order-preserving, ternary-search-based local
optimization, justified empirically by an observed (not proven) unimodality
of the ratio-loss function along one coordinate. **Classification: directly
inherited from the authors' own prior work; not new relative to it.**
Ternary search itself for unimodal 1-D optimization is textbook.

## 6. Overall pipeline

Phase A -> Phase B -> score extraction -> optional naive-swap refinement ->
optional Phase C. Deterministic (see `tests/test_audit.py`'s repeatability
tests) and explicitly time-budgeted at every phase. **Classification:
system/pipeline contribution** — the *engineering* integration (determinism,
per-phase time budgets, edge-id-based bookkeeping for O(1) toggling of
Phase B/C, the specific choice and combination of loss functions) is a
legitimate, if modest, contribution distinct from any single phase's
algorithmic novelty, and is largely *new relative to the arXiv preprint*
(that version did not have first-class phase-ablation toggles, a documented
80-dataset canonical suite, or the reproducibility/audit tooling now present
in this repository — see `REVISION_EXPERIMENT_PLAN.md` on the sibling branch
for the scale of the current dataset suite versus Table 1-4 here, which cover
a much smaller set).

## 7. Summary classification table

| Component | Classification |
|---|---|
| Phase A cycle detection (DFS) | Adapted implementation detail (standard DFS) |
| Phase A local-ratio residual reduction | Directly inherited (Demetrescu-Finocchi 2003, via authors' own prior paper) |
| Phase A numerical/forced-progress safeguards | Engineering/reproducibility element; not part of the inherited guarantee (see `APPROXIMATION_GUARANTEE_AUDIT.md`) |
| Phase A wall-clock early exit | Engineering element; invalidates the inherited guarantee when triggered (see `APPROXIMATION_GUARANTEE_AUDIT.md`) |
| Phase B topo-order add-back test | Adapted implementation detail that is a *weakening* of the authors' own prior exact-cycle-check pseudocode |
| Phase B INS1/2/3 multi-pass | Ad hoc compensation for the above weakening; not independently novel |
| Score extraction | Standard/engineering element |
| Naive-swap refinement | Adaptation of standard adjacent-transposition local search |
| Phase C ternary-search ratio refinement | Directly inherited from authors' own prior paper |
| Overall deterministic, time-budgeted, ablation-instrumented pipeline | System/pipeline contribution (new relative to the arXiv preprint) |

No component surveyed here is unclear-novelty-requiring-further-verification
in isolation; the literature audit (`NOVELTY_LITERATURE_MATRIX.md`) resolves
each one against a specific prior source.
