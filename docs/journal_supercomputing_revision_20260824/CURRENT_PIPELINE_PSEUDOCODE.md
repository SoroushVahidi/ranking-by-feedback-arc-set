# Current Pipeline: Publication-Quality Pseudocode

Date: 2026-08-24
Describes the CURRENT shipped method (`main`, `ours_mfas_rmfa` in
`GNNRank-main/src/ours_mfas.py`) — i.e. topo-order add-back with INS1/2/3,
**not** the experimental reachability variant on the sibling branch.

## Algorithm: OURS-MFAS-RANK

```
Input:  Directed weighted graph G = (V, E, w), w: E -> R_{>0}
        insertion_passes P ∈ {1, 2, 3}         (INS1 / INS2 / INS3)
        global time budget T_total (seconds)
        enable_phase_b, enable_phase_c ∈ {true, false}
        zero_tol (default 1e-15)
        naive_refine_time_sec, naive_refine_passes
        refine_time_sec, refine_passes, ternary_iters
Output: score: V -> R  (larger = better rank)

t0 <- current_time()

# ---- Phase A: local-ratio cycle breaking ----
residual[e] <- w(e) for all e in E
alive[e] <- true for all e in E
build static adjacency adj[v] <- { e in E : src(e) = v }, once

while true:
    if current_time() - t0 > T_total: break                    # (*) may exit with cycles remaining
    C <- FindOneCycle(V, adj, alive)      # iterative DFS, deterministic vertex scan order 0..n-1
    if C = None: break                                          # graph is acyclic -- normal exit
    delta <- min_{e in C} residual[e]
    if delta <= 0:                                               # numerical guard (rare)
        kill argmin_{e in C} residual[e]
    else:
        residual[e] <- residual[e] - delta   for all e in C
        D <- { e in C : residual[e] <= zero_tol }
        if D != empty: alive[e] <- false for e in D
        else: kill argmin_{e in C} residual[e]                   # numerical guard (rare)

kept_A[e] <- alive[e] for all e in E
removed_A <- { e in E : not alive[e] }

# ---- Phase B: descending-weight add-back (skipped if enable_phase_b = false) ----
kept <- kept_A
order <- removed_A sorted by w(e) descending, ties broken by original edge id (stable)
for pass in 1..P:
    if current_time() - t0 > T_total: break
    topo <- TopologicalSort(V, kept)          # Kahn's algorithm; None if kept is still cyclic
    if topo = None: break                                        # (*) can happen if (*) above fired
    pos[v] <- index of v in topo, for all v in V
    changed <- 0
    for e = (u, v) in order:                  # fixed order, NOT recomputed within a pass
        if current_time() - t0 > T_total: break
        if kept[e]: continue
        if pos[u] < pos[v]:                   # forward w.r.t. THIS pass's fixed topo order
            kept[e] <- true; changed <- changed + 1
    if changed = 0: break                                         # no further progress this pass

# ---- Score extraction ----
topo <- TopologicalSort(V, kept)
if topo = None: topo <- (v_1, ..., v_n) in raw input-index order   # (*) IDENTITY FALLBACK -- see
                                                                    #     APPROXIMATION_GUARANTEE_AUDIT.md
                                                                    #     Section "Timeout and fallback
                                                                    #     reliability": this ranking has
                                                                    #     NO relation to w and NO error bound.
score[v] <- max(1, n - pos(v))   for all v in V

# ---- Optional: naive-upset adjacent-swap local search ----
if naive_refine_time_sec > 0:
    score <- AdjacentSwapRefine(E, w, score, naive_refine_passes, naive_refine_time_sec, t0, T_total)
    # greedy left-to-right adjacent-transposition sweeps; accepts a swap iff it
    # strictly reduces sum_{e=(i,j): score(i)<=score(j)} w(e); order-CHANGING

# ---- Phase C: ratio-upset ternary refinement (skipped if enable_phase_c or refine_ratio = false) ----
if enable_phase_c and refine_ratio:
    (I, J, M3) <- PairwiseRatioTargets(G)          # one row per unordered pair with >=1 direction present
    for pass in 1..refine_passes:
        if current_time() - t0 > T_total: break
        for v in V in ascending-score order:
            [lo, hi] <- bounds from v's immediate neighbors in the CURRENT order (order-preserving)
            score[v] <- TernarySearch(I, J, M3, score, v, lo, hi, ternary_iters)
        repair strict monotonicity of score along the current order (epsilon nudges)

return score
```

`(*)` marks the two places where the timeout/fallback interaction discussed
in `APPROXIMATION_GUARANTEE_AUDIT.md` §3 originates: if the wall-clock budget
is exhausted inside Phase A before acyclicity is reached, both the
Phase-B topological sort and the final score-extraction topological sort can
fail (`None`), and the latter silently substitutes the raw input-vertex-index
order as the ranking.

**Determinism.** Every step above is deterministic given a fixed input edge
list and a fixed wall-clock budget's worth of completed work: vertex scan
order in DFS is `0..n-1`; ties in the descending-weight sort are broken by
stable sort on original edge id; Kahn's algorithm's queue is a FIFO
(`collections.deque`) populated in a fixed edge-iteration order. The
non-determinism risk is entirely confined to *how much work fits in
`T_total`* when the wall-clock check fires mid-loop (confirmed as the source
of `finance`'s run-to-run varying `removed_phaseA` counts — see the sibling
branch's `REVISION_RESULTS.md` §4); the *algorithm's logic* itself makes no
random choices anywhere.

## Parameter table

| Parameter | Default | Role | Documented in manuscript? | Sensitivity study needed? |
|---|---|---|---|---|
| `time_limit_sec` (`T_total`) | 900.0 (library default; ablation scripts use smaller values, e.g. 60-300s) | Global wall-clock budget shared by Phase A/B/C | UNKNOWN — depends on manuscript text not available in this repo; recommend explicit documentation given §3's finding that it can silently degrade output quality | **Yes** — this is the single most consequential parameter given the identity-fallback risk (§Approximation audit) |
| `zero_tol` | 1e-15 | Floating-point kill threshold in Phase A's residual reduction | Likely not documented (implementation detail) | No — shown negligible in `APPROXIMATION_GUARANTEE_AUDIT.md` §2.1; not worth a grid study |
| `insertion_passes` (INS1/2/3) | 3 (`OURS_MFAS`/`OURS_MFAS_INS3` default) | Number of Phase-B add-back passes | Yes (this is the INS1/2/3 naming itself) | **Yes, but the sibling branch's ablation already shows most of the story**: pass 2/3 typically contribute zero additional reinsertions (`break_reason == "no_change"`) once pass 1 completes — see `ADDBACK_DIAGNOSIS.md` on that branch |
| `refine_naive` / `naive_refine_time_sec` / `naive_refine_passes` | `True` / 2.0s / 2 | Adjacent-swap local search budget after add-back, before Phase C | UNKNOWN | Low priority — small, bounded local search; unlikely to be the dominant sensitivity factor |
| `refine_ratio` / `refine_time_sec` / `refine_passes` | `True` / 20.0s / 2 | Phase-C ternary refinement budget/passes | UNKNOWN | Low-to-medium — `refine_passes` beyond 1-2 likely has diminishing returns given the order-preserving, per-coordinate nature of the search, but this was not tested in this pass |
| `ternary_iters` | 20 | Ternary-search iterations per coordinate per Phase-C pass | UNKNOWN | Low priority — ternary search converges geometrically; 20 iterations already shrinks the bracket by `(2/3)^20 ≈ 3e-4` of its original width |
| Tie tolerance (add-back topo comparison) | none (strict `pos[u] < pos[v]`, integer positions, no epsilon) | N/A — Phase B uses integer topological positions, not floating scores, so no tie-tolerance parameter exists at this step | N/A | N/A |

**The important sensitivity factor, per the task's own framing, is
insertion/add-back *strategy*** (topo vs. reachability, and — on the sibling
branch — reachability+exchange), not this pipeline's numeric hyperparameters,
which are each shown above to be either already empirically inert (INS
passes 2/3) or theoretically negligible (`zero_tol`, `ternary_iters`) at
their current defaults. See the sibling branch's ablation results for the
add-back-strategy comparison; a numeric-hyperparameter grid beyond what is
tabulated above is not recommended as a priority for this revision.
