# Reachability-Aware Add-Back: Design, Correctness, Complexity

Date: 2026-08-24
Implementation: `GNNRank-main/src/ours_mfas.py::_addback_reachability()`,
wired in via `ours_mfas_rmfa(..., addback_mode="reach")` and exposed as
`comparison.ours_MFAS_REACH()`.

## 1. Algorithm

Input: the Phase-A kept DAG (`kept_initial`), the full edge list `(src, dst,
w)`, a time budget.

```
kept = kept_initial
order = removed edges sorted by descending original weight, ties broken by
        original edge id (stable mergesort on -w)

for (u, v) in order:                      # single pass
    if kept[(u, v)]: continue
    if v cannot reach u in `kept`:
        kept[(u, v)] = True                # accept: cycle-safe
    else:
        reject                              # would create a cycle

return kept
```

The correctness of the acceptance test is immediate: a graph obtained from a
DAG by adding one edge `u -> v` is acyclic **iff** there was no existing path
`v -> ... -> u` (that path plus the new edge is the only way a cycle could
form, since `kept` is acyclic before the insertion). This is the exact
necessary-and-sufficient condition; unlike the legacy topo-order test (`pos[u]
< pos[v]` for one fixed order), it does not depend on which of possibly many
valid topological orders happens to have been computed.

## 2. Two implementations, chosen by graph size

Both are provided by `_addback_reachability()`; the choice is automatic via
`dense_matrix_max_n` (default 4000), which comfortably covers every dataset in
the current 80-dataset suite (largest `n = 351`, `Basketball_temporal/2014`).

### Dense mode (`n <= dense_matrix_max_n`)

Maintains an explicit `n x n` boolean matrix `reach`, where `reach[x, y]` is
`True` iff `x` can reach `y` via currently-kept edges (`x == y` excluded;
handled separately by treating `u`/`v` as trivially reaching themselves during
queries). This is initialized once from the Phase-A DAG in a single reverse
topological sweep (`O(n + m)` bitwise-row unions), then updated incrementally
on every accepted insertion:

```
insert (u, v):
    anc  = { a : reach[a, u] } ∪ {u}     # ancestors of u, inclusive
    desc = { b : reach[v, b] } ∪ {v}     # descendants of v, inclusive
    for a in anc: reach[a, :] |= desc_mask     # vectorized: reach[idx_a, :] |= desc_mask
```

This is the standard incremental-transitive-closure update for a single edge
insertion into a DAG (a folklore result; see e.g. Italiano 1986,
"Amortized efficiency of a path retrieval data structure", for the general
technique). Each update costs `O(n^2 / w)` in practice via numpy's vectorized
bitwise OR (`w` = machine word parallelism), i.e. a small constant number of
memory operations per node pair, not a Python-level loop over pairs.

**Memory**: `n^2` booleans; for the largest current dataset (`n=351`) this is
~123 KB. `dense_matrix_max_n=4000` bounds this to ~16 MB before falling back to
BFS mode, matching the "no dense transitive-closure matrix for large instances
unless justified" instruction — dense is *justified* here because it is
strictly bounded and orders of magnitude smaller than the working set already
used elsewhere in the pipeline (e.g. `n x n` adjacency matrices themselves).

### Sparse/BFS mode (`n > dense_matrix_max_n`)

No `O(n^2)` matrix is built. Each candidate edge's reachability query is a
plain BFS/DFS from `v` over currently-kept out-edges, stopping as soon as `u`
is found or the frontier is exhausted, governed by the same global
`time_limit_sec` used by the rest of Phase B/C (so a huge graph degrades to a
partial, time-bounded pass rather than hanging). This mode is exercised by the
randomized unit tests indirectly (dense mode covers all current real
datasets); it is included so the algorithm remains usable if/when the suite
grows past a few thousand nodes, per the task's sparse-graph-friendliness
requirement.

## 3. One-pass sufficiency (proved, not just asserted)

**Claim.** A single descending-weight scan, as described above, produces the
same result as running the scan to convergence over multiple passes (i.e. a
second full pass over the same removed-edge order, using the output of the
first as its starting kept-set, inserts nothing new).

**Proof.** The algorithm only ever sets `kept[e] := True`; it never clears a
bit. Reachability is therefore monotone non-decreasing in the number of passes
already applied: if `v` can reach `u` after some prefix of insertions, it can
still reach `u` after any further insertions (the witnessing path uses only
edges that remain in `kept`, and `kept` only grows). Consider a removed edge
`(u, v)` rejected at the point in the scan where it was considered, because `v`
reached `u` in the kept set *at that moment*, call it `K_reject`. Any kept set
`K' \supseteq K_reject` reachable from further insertions still has `v`
reaching `u` (monotonicity), so `(u, v)` remains unsafe to insert for the rest
of the same pass, and for the start of any subsequent pass (whose starting
kept-set is exactly the first pass's final `K \supseteq K_reject`). Hence no
second pass over the same order can accept an edge the first pass rejected.
Conversely, every edge the first pass *accepted* is already in `kept`, so a
second pass trivially skips it (`if kept[e]: continue`). Therefore a second
pass is a no-op, and by induction so is every subsequent pass. **QED.**

This is exactly why `_addback_reachability()` is single-pass by construction —
there is no `INS1_REACH`/`INS2_REACH`/`INS3_REACH` family; `insertion_passes`
is accepted by `ours_mfas_rmfa()` but ignored for `addback_mode="reach"`.

This claim is checked empirically, not just argued, by
`tests/test_reachability_addback.py::TestReachabilityProperties::
test_one_pass_sufficiency`, which re-runs `_addback_reachability` on its own
output across 10 randomized graphs and asserts zero further insertions.

## 4. Inclusion-minimality (proved and tested)

**Claim.** After the reachability add-back pass, for every remaining removed
edge `(u, v)`, inserting `(u, v)` into the final kept set would create a
cycle.

**Proof.** Every removed edge was considered exactly once during the single
pass (the pass iterates over *all* removed edges from Phase A). At the moment
`(u, v)` was considered, it was either accepted (contradiction — it would not
be "remaining removed") or rejected because `v` reached `u` in the kept set
*at that time*, `K_t \subseteq K_{final}`. By the monotonicity argument in
Section 3, `v` still reaches `u` in `K_{final} \supseteq K_t`. Hence inserting
`(u, v)` into `K_{final}` recreates that same reachability-implied cycle.
**QED.**

Note the explicit scope limitation requested in the task: this establishes
**inclusion-minimality** of the final removed set (no remaining removed edge
can be added back without creating a cycle) — it does **not** establish
**minimum-weight** optimality of the kept/removed partition (i.e. it is not
claimed to solve minimum feedback arc set exactly; Phase A's local-ratio
peeling and the descending-weight greedy order of Phase B are both heuristics
with no exactness guarantee on total removed weight). This distinction is
checked by
`tests/test_reachability_addback.py::TestReachabilityProperties::
test_final_removed_set_is_inclusion_minimal`, which brute-force verifies, for
every remaining removed edge in several randomized graphs, that reinserting it
alone creates a cycle.

## 5. What this does *not* claim

- It does not claim to find the minimum-weight feedback arc set (NP-hard in
  general; Phase A + greedy add-back remains a heuristic).
- It does not, by itself, resolve ties between multiple structurally
  different but equally cycle-safe insertion orders — like the legacy
  variant, it commits to a single deterministic order (stable descending
  weight, ties broken by original edge id) and does not search over
  alternative orders. Section F's exchange-move prototype is the natural next
  step for edges rejected here that are high-weight; see
  `REVISION_EXPERIMENT_PLAN.md` for its status in this revision pass.

## 6. Complexity summary

| Mode   | Precondition | Per-insertion cost | Total Phase-B cost |
|--------|--------------|---------------------|---------------------|
| Dense  | n <= 4000    | O(n^2 / w) (vectorized) | O(R * n^2 / w), R = #removed edges |
| Sparse | n > 4000     | O(n + m) worst case (BFS) | O(R * (n + m)), time-bounded |

For the current suite (`n <= 351`), measured wall-clock overhead of
reachability add-back vs. legacy topo add-back is reported in
`REVISION_RESULTS.md` (`outputs/ablation/phase_ablation_summary.md`,
`B1_reach` vs `A1_topo` median runtimes) and was on the order of tens to
hundreds of milliseconds per dataset in ad hoc benchmarking
(`Basketball_temporal/2010`, n=347, m=4133: topo A+B ≈ 0.165 s, reach A+B ≈
0.245 s).
