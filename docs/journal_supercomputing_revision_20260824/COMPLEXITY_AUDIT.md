# Complexity Audit

Date: 2026-08-24
Scope: `GNNRank-main/src/ours_mfas.py` on `main` (SHA `706b2177`).

All complexity claims below are derived by direct reading of the source, not
assumed from the manuscript or from the abstract algorithm's textbook
complexity. `n = |V|`, `m = |E|`.

## Phase A: `_local_ratio_break_cycles`

**Claimed elsewhere** ([VK25]'s Related-Work description of [10]=[DF03]):
"O(VE) heuristic." This is a claim about the *abstract* local-ratio
algorithm, not necessarily this specific implementation — verified below.

**What the code actually does, per iteration of the `while True:` loop**:
- `_find_one_cycle_edges()` is called fresh each iteration. It allocates a new
  `color` array (`np.zeros(n, ...)`) and runs an iterative DFS from every
  vertex not yet colored. Critically, **the per-vertex edge cursor `it`
  restarts at 0 on every call**, and dead (non-`alive`) edges are skipped via
  an inline `while it < len(adj_e[u]) and not alive[...]: it += 1` scan —
  they are never removed from `adj_e[u]` itself. `adj_e` is built **once**,
  before the loop starts, from *all* `m` original edges (`for ei in
  range(m): adj_e[src[ei]].append(ei)`), and is never rebuilt or compacted
  afterward.

  **Consequence**: a vertex `u` with many originally-incident edges that have
  since died still costs O(original out-degree of `u`) to visit on *every*
  call to `_find_one_cycle_edges`, not O(current alive out-degree of `u`).
  Summed over all vertices, **one call to `_find_one_cycle_edges` costs
  O(n + m)** in the worst case, regardless of how many edges are still
  alive.
- The residual-update step after finding a cycle (`residual[cyc_e] -=
  delta`, the `dead = ...` mask, killing edges) costs O(cycle length) ⊆
  O(n), dominated by the O(n+m) cycle search.

**Number of iterations, `I`**: at least one edge is killed per iteration
(either via the natural `residual <= zero_tol` condition or via one of the
two forced-progress safeguards, which each explicitly kill exactly one edge
when triggered — see `APPROXIMATION_GUARANTEE_AUDIT.md` §2.2/2.3). Since an
edge, once dead, stays dead, `I <= m`.

**Total unbudgeted worst-case complexity: O(I · (n + m)) ⊆ O(m·(n + m)) =
O(mn + m²).** This is a **materially worse bound than O(VE) = O(nm)** for
dense graphs (where `m = Θ(n²)`, giving O(n⁴) here versus O(n³) for a
properly-amortized O(VE) implementation) — because the implementation does
not maintain a pruned or amortized adjacency structure across iterations,
each cycle search re-pays the full O(n+m) cost rather than a cost
proportional to the *current* (shrinking) alive-edge count.

**Code-comment inaccuracy found in passing**: the function's own comment
states *"To keep deterministic behavior, we rebuild adj from alive each
iteration... edge-level reconstruction avoids O(m) scans."* This does not
match the code: `adj_e` is built exactly once, **before** the loop (not
rebuilt per iteration), and the "O(m) scans" the comment claims to avoid are
in fact incurred anyway via the lazy dead-edge-skipping behavior described
above. This should be corrected (either fix the comment to describe actual
behavior, or change the implementation to match the comment's intent — the
latter would also fix the complexity gap above, by maintaining a compacted
alive-only adjacency structure, e.g. via periodic rebuilds or a proper
union-find/linked-list-based removal scheme).

**Time-budgeted behavior**: since the wall-clock check happens once per
outer-loop iteration (before the O(n+m) cycle search), the *number of
iterations actually completed* under a fixed `time_limit_sec` is a runtime
property, not a closed-form function of `n`/`m` — on `finance` (n=1315,
m≈1.7M), the 60s budget used in the sibling branch's ablation pass was
exhausted after a wall-clock-dependent (not deterministic) number of
iterations (see that branch's `REVISION_RESULTS.md` §4). **A wall-clock
budget is an execution policy, not a complexity result, and must not be
described as one in the manuscript** (the task's own instruction: "Do not
call a wall-clock budget an 'average-case complexity result'" — confirmed
here as a real risk given the O(mn+m²) worst case above makes early
termination on dense graphs a near-certainty, not a corner case).

## Phase B: `_addback_desc_weight_multi`

- Edge sort (`np.argsort(-w, ...)`, once): **O(m log m)**.
- Per pass: one topological sort (`_toposort_kahn_from_edges`, a standard
  Kahn's-algorithm implementation that rebuilds `indeg`/`adj` fresh each
  call): **O(n + m)**. Then one linear scan over the (pre-sorted) full edge
  order, testing `kept[ei]` and `pos[u] < pos[v]` in O(1) per edge: **O(m)**.
  So each pass costs **O(n + m)**.
- Total over up to `insertion_passes` (≤ 3, a small constant) passes:
  **O(m log m + P·(n+m)) = O(m log m + n + m)** for constant `P ≤ 3`, i.e.
  **O(m log m)** overall. This *is* efficient and correctly bounded — no
  discrepancy found here. (Note: `insertion_passes` is a *parameter*, not a
  hidden constant in general — if it were set arbitrarily large the "small
  constant" characterization would need revisiting, but the codebase only
  ever exposes INS1/INS2/INS3, i.e. `P ∈ {1,2,3}`.)

## Phase C: `refine_scores_ratio_ternary`

- `_pair_arrays_from_A`: builds a Python dict keyed by unordered pairs from
  all `m` nonzero matrix entries, then converts to numpy arrays of length
  `P` (number of unique undirected pairs with at least one direction
  present, `P <= m`): **O(m)** time and memory.
- Main loop, per pass: iterates over all `n` nodes (`for k in range(len(order))`).
  For **each** node, `_ternary_opt_one` computes
  `mask = (I == idx) | (J == idx)`, a numpy boolean comparison over **all**
  `P` pairs — **O(P) per node**, hence **O(n·P) per pass just for mask
  construction**, independent of that node's actual degree in pair-space.
  Within the masked subset (size = the node's true pair-degree, `d_idx`,
  with `sum_idx d_idx = 2P`), `ternary_iters` (default 20) ternary-search
  steps each recompute the loss over the `d_idx`-sized subset: **O(d_idx ·
  ternary_iters) per node**, summing to **O(P · ternary_iters) per pass**
  across all nodes.
- **Total per pass: O(n·P + P·ternary_iters) ⊆ O(n·m + m·ternary_iters)**,
  and with `refine_passes` (default 2) passes: **O(refine_passes · (n·m +
  m·ternary_iters))**.

**The O(n·m) term is algorithmically avoidable** (it comes from
recomputing a full-length boolean mask over all `P` pairs for every node,
rather than precomputing a per-node adjacency-in-pair-space list once in
O(m) total and reusing it) but is present in the current implementation. For
the current dataset suite's largest non-pathological instances (n≈351,
m≈7650), `n·m ≈ 2.7M` — negligible in wall-clock terms (numpy-vectorized).
**For a dense graph like `finance` (n=1315, m≈1.7M), `n·m ≈ 2.2 billion`** —
this is a latent scalability cliff that Phase A's own timeout currently masks
(Phase C never runs on `finance` in practice because Phase A already
exhausts the budget first, per `APPROXIMATION_GUARANTEE_AUDIT.md` §3) but
would become the dominant cost if Phase A were ever sped up without also
fixing this term.

**Memory**: `_pair_arrays_from_A` and the main loop use only O(m)-sized
arrays (`I`, `J`, `M3`, and the O(n) `s` score vector) — **there is no O(n²)
memory structure anywhere in the current (pre-reachability) Phase A/B/C
pipeline.** This is stated precisely because the task's own framing (Section
L) raises "O(n^2) refinement memory" as a possible reason to reconsider the
word "Scalable" in the title — **that characterization does not match what
is actually in the current codebase's Phase C**; the only O(n²) memory
structure in this project is the dense incremental-reachability matrix
introduced on the sibling branch's `OURS_MFAS_REACH` (`_addback_reachability`,
bounded to `n <= 4000` by design, with an explicit sparse/BFS fallback above
that threshold — see that branch's `REACHABILITY_ADDBACK_DESIGN.md`), which
is a *new, opt-in, explicitly-bounded* addition, not a property of the method
already being evaluated in the current 80-dataset suite. See
`INTRODUCTION_REWRITE_PLAN.md` for how this should be reflected in the title
discussion — the correct scalability caveat is **Phase A's O(mn+m²)
worst-case time on dense graphs** (confirmed above and empirically on
`finance`), not an O(n²) memory claim.

## Summary of flagged inaccuracies

| Claim | Status | Correct statement |
|---|---|---|
| "O(VE)" for the shipped Phase A | **Not accurate for this implementation** | O(I·(n+m)) ⊆ O(mn+m²) worst case, due to non-amortized adjacency rescanning (see above); O(VE) would require fixing the adjacency-list staleness issue |
| Phase A comment "we rebuild adj from alive each iteration" | **Inaccurate** — code does not do this | `adj_e` is built once; staleness is handled by lazy per-call skipping, which is what causes the O(mn+m²) worst case |
| Wall-clock budget as complexity bound | Must not be conflated | It is an execution policy; actual completed work under a timeout is a runtime-dependent quantity, not a function of n/m alone |
| Phase B complexity | O(m log m) — **accurate**, no discrepancy found | — |
| "O(n²) refinement memory" (as a title-relevant limitation, per task framing) | **Not found in the current/legacy Phase C** — Phase C is O(m) memory | The real dense-graph scalability caveat is Phase A's O(mn+m²) *time*, not Phase C memory; a distinct O(n²) *memory* structure does exist, but only in the separate reachability-add-back workstream on another branch, bounded and opt-in |
