# Add-Back Mechanism: Chronological Lineage

Date: 2026-08-24
Established from: direct primary-source read of DF03 (2003, full text), direct full read of
[VK25] v2 (Jan 2025) and v3 (Dec 2025, current), and direct source inspection of the shipped
codebase on `main` (SHA `706b2177`).

## Step 0 — DF03 (2003), the origin

Exact pseudocode (Figure 1, §3.1), Phase 2:
```
for each (v,w) in F:
    if (V, (A\F) ∪ {(v,w)}) is acyclic:
        F <- F \ {(v,w)}
```
- **Test**: exact — reinsert iff the result is acyclic (equivalent to: does the other endpoint
  already reach this one? — the exact reachability condition).
- **Order**: **unspecified** in the algorithm itself — any order over `F` preserves both the
  λ-approximation (which depends only on Phase 1, per `DF03_PRIMARY_THEOREM_VERIFICATION.md` §4)
  and minimality (Theorem 1, which holds for *any* order of Phase-2 processing, since a "maximal
  subset added back" is order-independent for this particular greedy-acyclicity-preserving
  procedure — confirmed by direct reading, no order dependence anywhere in the proof of Theorem
  1's minimality claim).
- **Passes**: exactly one (a single `for each` loop over `F`, no repetition).
- **Explicit remark (Concluding Remarks, §3.1 mid-page and end of proof of Thm 2)**: DF03
  themselves suggest, as an optional *heuristic* (not required for the guarantee), *"ordering arcs
  by decreasing weight in Phase 2 might be helpful to improve the quality of the solution."*
  **This is the direct origin of the descending-weight ordering used by every later stage of this
  lineage.**

## Step 1 — [VK25] v2 (Jan 2025) / v3 (Dec 2025), the authors' own prior paper

Algorithm 1, "Step 2" (both versions, verbatim-equivalent pseudocode, confirmed by direct read of
both PDFs):
```
Sort removed edges in decreasing order of their weights
foreach edge (u,v) in the sorted list do
    if adding (u,v) back does not create a directed cycle then
        Reinsert (u,v) into the graph
```
- **Test**: still exact ("does not create a directed cycle" — literally DF03's Phase-2 condition,
  unchanged).
- **Order**: now explicitly descending weight — **directly adopting DF03's own suggested
  heuristic** (§Step 0 above), not an independent invention.
- **Passes**: exactly one (single `foreach` loop, no INS1/2/3 concept, in both v2 and v3).
- Implementation note (from [VK25]'s own prose, §2.2/2 in both versions): *"DFS is also used to
  evaluate whether removed edges can be reinserted without reintroducing cycles"* — i.e. [VK25]'s
  own implementation, as described by the authors, tests cycle-safety via a **fresh DFS check per
  candidate edge**, not via a fixed topological-order proxy. This is a plain, direct (if
  potentially not the most efficient) implementation of the exact test.

## Step 2 — historical/early implementation in this repository (not independently recoverable in this pass)

This audit did not locate an intermediate git history state showing a direct, unmodified port of
[VK25]'s Algorithm 1 into this repository's `GNNRank-main/src/ours_mfas.py` (the file's earliest
inspected state, `main` @ `706b2177`, already contains the topo-order-proxy version — see Step 3).
**This is recorded as an evidence gap, not filled in with speculation**: whether an intermediate
exact-cycle-check commit ever existed in this repository's history and was later replaced, or
whether the topo-order-proxy was introduced directly when the ranking algorithm was first ported
from the separate `Ranking_with_MWFAS` codebase (linked in [VK25] §5) into this
`ranking-by-feedback-arc-set` / `GNNRank-main` repository, was not determined in this pass. A
`git log -p` / `git blame` history dig on `GNNRank-main/src/ours_mfas.py` across the full commit
history (not just the recent commits visible from the two sibling revision branches) would resolve
this and is recommended as a fast follow-up (see final report, next action).

## Step 3 — current fixed-topo-order implementation (`main`, `GNNRank-main/src/ours_mfas.py`)

```python
topo = _toposort_kahn_from_edges(n, src, dst, kept)   # ONE topo order per pass
...
if pos[u] < pos[v]:      # forward w.r.t. THIS fixed order -- a PROXY for "no cycle created"
    kept[ei] = True
```
- **Test**: weakened from exact to a sufficient-but-not-necessary proxy (forward-in-one-order).
- **Order**: descending weight, preserved from [VK25]/DF03's suggestion.
- **Passes**: up to 3 (`INS1`/`INS2`/`INS3`), recomputing the topo order at the start of each —
  **a mechanism absent from both DF03 and [VK25]**.

## Step 4 — INS1/2/3 multi-pass patch

Directly co-located with Step 3 in the same function (`_addback_desc_weight_multi`,
`insertion_passes` parameter). Not a separately-dated historical step in the evidence available to
this audit, but logically and functionally a **compensation mechanism** for Step 3's test
weakening: since a single fixed topo order rejects some cycle-safe edges, recomputing the order
after accepting a first batch and re-scanning can occasionally recover a few more (a topo order
compatible with the enlarged kept set may happen to make a previously-rejected edge forward). The
sibling `journal-supercomputing-major-revision-20260824` branch's `ADDBACK_DIAGNOSIS.md` confirms
empirically that passes 2 and 3 typically contribute zero further reinsertions once pass 1
completes (`break_reason == "no_change"`), consistent with this being a patch of limited
effectiveness rather than an independently valuable mechanism.

## Step 5 — reachability restoration (sibling branch `journal-supercomputing-major-revision-20260824`, `OURS_MFAS_REACH`)

```python
if not reach[v, u]:   # exact reachability test, incremental transitive closure
    kept[ei] = True
```
- **Test**: exact again — restores DF03's/[VK25]'s original condition, implemented via an
  efficient incremental dense-matrix (or BFS-fallback) reachability structure rather than a fresh
  DFS per candidate (an efficiency improvement over both DF03's naive-DFS caveat and [VK25]'s own
  stated per-edge-DFS implementation).
- **Order**: descending weight, preserved (same lineage).
- **Passes**: exactly one, and that branch's `REACHABILITY_ADDBACK_DESIGN.md` **proves** (not
  merely observes) this is sufficient — a formal strengthening of what DF03 leaves as an
  order-independent but unproven-single-pass-sufficient procedure (DF03's own Phase 2 is also
  effectively single-pass in its pseudocode, but the paper does not remark on or prove
  single-pass sufficiency as a named property the way the sibling branch does).

## Summary: is Step 5 restoring Step 1 (and ultimately Step 0), or inventing something new?

**Restoring, primarily — with two genuine additions.** The *test* (exact reachability/cycle-safety)
and the *order* (descending weight) in Step 5 are identical in kind to Step 0/Step 1. What Step 5
adds beyond restoration: (a) an efficient incremental data structure for the reachability test
(neither DF03's naive-DFS caveat nor [VK25]'s stated per-edge-DFS implementation describe this),
and (b) formal proofs of one-pass sufficiency and inclusion-minimality (DF03 states minimality as
a theorem for its own *unordered* Phase 2, but neither DF03 nor [VK25] proves single-pass
sufficiency for the *descending-weight-ordered* variant specifically, nor do either connect
minimality to the ranking-cost equivalence the way `RANKING_MWFAS_EQUIVALENCE.md` Remark 2 does).
See `DISTINCTNESS_AND_NEW_WORK_VERDICT.md` for how this bears on the overall novelty verdict.
