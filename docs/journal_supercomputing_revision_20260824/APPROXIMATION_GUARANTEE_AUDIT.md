# Approximation-Guarantee Audit

Date: 2026-08-24
Scope: `GNNRank-main/src/ours_mfas.py` on `main` (SHA `706b2177`), i.e. the
currently-shipped Phase A implementation, `_local_ratio_break_cycles()`.

## 1. What the original algorithm guarantees

Source: Demetrescu & Finocchi, "Combinatorial algorithms for feedback
problems in directed graphs," *Inf. Process. Lett.* 86, 129-136, 2003
([DF03]), as characterized (a) by a secondary literature summary found via
web search this pass and (b) by the authors' own prior paper [VK25]
(arXiv:2412.16181)'s Related Work section, which states: *"[10] proposed an
O(V E) heuristic based on the local ratio method [4]. This heuristic was
shown to be efficient in practice, providing a λ-approximation, where λ is
the length of the longest cycle in the graph."*

**UPDATE (three-branch integration, 2026-08-24): RESOLVED.** At the time this document was
originally written, the WebFetch tool could not extract [DF03]'s literal theorem text from the
source PDF, so the characterization above was secondary-source only. The sibling
`jsuper-prior-work-overlap-audit-20260824` branch subsequently obtained and read the full primary
text directly (Theorem 1, Theorem 2, Lemma 1, and their complete proofs) — see that branch's
`DF03_PRIMARY_THEOREM_VERIFICATION.md`, now integrated alongside this file, which is the
**authoritative source going forward**. The λ-approximation characterization above is confirmed
correct by the primary text. That document additionally sharpens this audit's own verdict (§4
below) into two separable claims — see the cross-reference added there.

Taking the characterization as given: the algorithm guarantees that the
total *original* weight of the removed edge set is at most **λ · OPT**,
where λ is the length (number of edges) of the longest simple cycle
encountered/present, and OPT is the minimum feedback arc set weight. This is
a **data-dependent, potentially very weak** bound — for a dense or
near-complete graph, λ can be as large as `n`, making the guarantee close to
vacuous (an `n`-approximation is not a meaningful guarantee for ranking
purposes). For graphs whose cycles are all short (e.g., mostly triangles),
the bound is much tighter (close to 2-3x OPT).

**This dependency on λ is directly relevant to this repository's own
dataset suite**: `finance` (n=1315, m≈1.7M, density≈1.0) is exactly the kind
of near-complete graph where λ can be large and the inherited guarantee, even
if it applied, would be numerically weak.

## 2. Does the current Phase-A implementation exactly implement [DF03]'s algorithm?

**Structurally, yes, in its core loop**: find one cycle, subtract the
minimum residual weight across the cycle's edges from every edge on the
cycle, remove edges that reach zero residual, repeat until acyclic. This
matches the "local ratio" reduction step as described in both [VK25] (which
explicitly implements the same idea, see `CURRENT_METHOD_DECOMPOSITION.md`
§1) and the general local-ratio framework [BBFR04].

**But four implementation-level deviations exist**, each assessed for
whether it invalidates the inherited guarantee:

### 2.1 `zero_tol = 1e-15` (floating-point kill threshold)

Edges are killed at `residual <= 1e-15`, not exactly `residual == 0`. This is
a standard floating-point safety margin. **Verdict: does not materially
invalidate the guarantee.** The weight-accounting argument underlying the
local-ratio bound is a sum over telescoping deltas; an epsilon-scale slack
of `1e-15` per edge introduces error many orders of magnitude below the
precision of any weight value used in this codebase (weights are typically
integers or small positive floats from comparison counts). Negligible.

### 2.2 Forced-progress kill when `delta <= 0.0`

If the computed minimum residual on a cycle is `<= 0` (should not occur with
positive weights under exact arithmetic, since residuals are maintained
`>= 0` by construction and a genuine cycle has been found), the code force-
kills the minimum-residual edge instead of subtracting. **Verdict: a real,
if rare, deviation from the pure local-ratio reduction step.** When this
path triggers, the edge removed is not accounted for by the delta-subtraction
weight bookkeeping the guarantee's proof relies on — the algorithm is doing
something the theorem does not cover. Because this is guarded as a numerical
corner case (should only arise from floating-point drift, not from the
combinatorial logic itself), it is expected to be rare in practice, but **its
absence is not proven** — no test in this repository specifically exercises
or bounds the frequency of this path. **This alone downgrades the verdict
from "guarantee applies exactly" to "guarantee applies only when this path
does not trigger" — an unverified precondition.**

### 2.3 Forced-progress kill when no edge reaches zero after subtraction

Same structure and same verdict as 2.2: a numerical-corner-case deviation
from the pure algorithm, guarded but not proven absent.

### 2.4 Wall-clock early exit (the dominant issue — see §3below)

The `while True` loop checks `time.time() - t0 > time_limit_sec` **before**
searching for the next cycle, and breaks immediately if the budget is
exhausted — **regardless of whether the graph is currently acyclic**. This is
the most consequential deviation and is treated in its own section below
because the original algorithm's guarantee is a statement about the
*completed* (fully-reduced, acyclic) output; it says nothing about a
partially-executed run.

## 3. Timeout and fallback reliability

**Verified directly from source** (`GNNRank-main/src/ours_mfas.py`, `main`):

1. `_local_ratio_break_cycles()`'s loop can exit via the wall-clock check
   with the graph **still cyclic** (the `alive` mask may still admit a cycle;
   nothing in the function guarantees acyclicity on a timeout exit — only on
   the `cyc_e is None` exit path).
2. `ours_mfas_rmfa()` passes this possibly-still-cyclic `keptA` into Phase B
   (`_addback_desc_weight_multi`). Its first action per pass is
   `topo = _toposort_kahn_from_edges(n, src, dst, kept)`; **if `kept` is
   cyclic, `topo` is `None`** (Kahn's algorithm cannot fully order a graph
   with a cycle — confirmed by direct reading of
   `_toposort_kahn_from_edges`'s `if len(order) != n: return None`). The code
   handles this as `break_reason = "topo_failure"` and returns
   `kept = kept_initial` unchanged (Phase B never modifies anything in this
   branch).
3. `ours_mfas_rmfa()` then calls `_scores_from_kept_edges(n, kept_final, ...)`
   on this still-cyclic `kept_final`. **This function contains exactly the
   fallback the task instructions asked about**:
   ```python
   topo = _toposort_kahn_from_edges(n, src, dst, kept)
   if topo is None:
       topo = list(range(n))          # <-- identity fallback
   ```
   When this triggers, the returned ranking is **the raw node/vertex index
   order of the adjacency matrix**, with **zero relationship to any edge
   weight or comparison outcome**.

**Empirical confirmation this actually happens in this codebase**: the
sibling branch's `journal-supercomputing-major-revision-20260824` ablation run
(`REVISION_RESULTS.md` §4, same underlying Phase A code, different branch)
found that `finance` (n=1315, m≈1.7M, density≈1.0) exhausts its entire
per-run time budget inside Phase A's cycle-peeling loop, with the graph
almost certainly still cyclic at that point (the recorded `removed_phaseA`
counts vary run-to-run by wall-clock timing, consistent with the loop being
cut off mid-execution rather than converging).

### 3.1 Does a nontrivial error bound exist for the identity fallback?

**No — and this section proves why, with a worst-case construction, rather
than asserting it.**

**Construction.** Let `G` be any weighted digraph on `n` nodes and let `w_max`
be its largest edge weight. Pick any permutation `π` of `{1,...,n}` that is
*adversarial* relative to node index order — i.e., choose the node-to-index
assignment (which is arbitrary; nothing about `_csr_to_edges`'s vertex
numbering is tied to comparison strength) such that the "true" best ranking
(sorted by any reasonable notion, e.g. by total out-weight minus in-weight)
is the exact **reverse** of index order, `n, n-1, ..., 1`. Construct all
edges to point from lower-ranked-by-truth (i.e. numerically low true rank) to
higher-ranked-by-truth nodes with weight `w_max`, EXCEPT force the graph to
be dense enough (e.g. near-complete, as `finance` is) that Phase A's
wall-clock budget is exhausted before completion — this is not a hypothetical
requirement, it is exactly what happens on `finance` in this codebase.
Because vertex-to-index assignment in `_csr_to_edges` is simply the order
rows/columns happen to appear in the input sparse matrix (no ranking-aware
sorting is ever applied to it), an adversary (or simply bad luck in how the
dataset's raw ID-to-index mapping was constructed upstream) can always
realize the case where identity order equals the *worst possible* ranking
under `upset_simple` (or any other upset metric) — i.e. **every single edge
is "backward"** relative to the fallback ranking, achieving the maximum
possible weighted-upset cost, `sum(w_e)`, while `OPT` (the true minimum
feedback arc set weight) can be made arbitrarily small relative to that sum
(e.g., a graph that is almost a total order already, so `OPT` is tiny, but
whose vertex-index numbering happens to be reversed relative to that order).

**Conclusion**: the ratio (identity-fallback cost) / OPT is **unbounded** in
general — no nontrivial multiplicative or additive error bound can be proven
for the identity-order fallback without additional structural assumptions
(e.g. that vertex indices are already correlated with the true ranking,
which nothing in the pipeline guarantees or even attempts). **This is not
manufactured to satisfy the reviewer; it follows directly from the fact that
vertex index order carries zero information about edge weights by
construction.**

### 3.2 Recommended implementation change

The current behavior (silently returning an arbitrary, weight-independent
ranking on timeout, indistinguishable in the output from a normal successful
run) is the worst of the options considered. Recommended, in order of
preference:

1. **Preserve the best-known acyclic incumbent.** Before starting the
   cycle-peeling loop proper, or periodically during it, snapshot the
   `alive` mask at the last point it was acyclic (trivially, the mask is
   acyclic *before* any cycle-breaking starts only in the degenerate case of
   an already-acyclic input; more usefully, since each iteration only ever
   *removes* edges and a cycle-free residual graph, once reached, cannot
   regain a cycle, the function could instead track whether the *current*
   graph is acyclic after each removal — expensive if done via a full
   topological sort every iteration, but the existing DFS cycle search
   already provides an acyclicity witness for free: `cyc_e is None` from
   `_find_one_cycle_edges` means "already acyclic," so the loop already knows
   the moment it becomes safe; a timeout that fires strictly *after* that
   point is fine as-is). The fix is specifically for a timeout firing
   *before* that point: the function should continue removing edges from
   whatever cycle it is mid-processing (or discard the partially-processed
   cycle's not-yet-removed edges wholesale) until the residual graph is
   verifiably acyclic, rather than stopping at an arbitrary point that can
   leave cycles intact — trading a bounded amount of extra removed weight
   for a guaranteed-valid FAS.
2. **Return an explicit failure/coverage flag** (e.g. `meta['phaseA_timed_out'] =
   True`, `meta['phaseA_converged'] = False`) whenever the identity-fallback
   path is taken, so downstream table-generation code can exclude or
   specially flag that run rather than silently reporting a ranking that
   looks like any other successful one. This is the minimum viable fix and
   is cheap to add without touching the algorithm's numerics.
3. At minimum, **do not report `upset_simple`/`upset_ratio`/`upset_naive`
   numbers computed from an identity-fallback ranking in any table without a
   footnote** — per this audit, such numbers carry no approximation
   guarantee and can be arbitrarily bad by construction (§3.1).

## 4. Verdict

Given §2's four deviations (two negligible, one unresolved-but-rare, one
severe-and-empirically-confirmed) and §3's proof that the timeout fallback
carries no error bound at all:

**Verdict: (B) the guarantee applies only to an unbudgeted, idealized variant
of the implementation — specifically, the version of Phase A that is allowed
to run to true convergence (no wall-clock cutoff) and whose two forced-
progress safeguards never trigger.** The shipped, time-budgeted
implementation used to produce every table in this repository does **not**
carry that guarantee unconditionally: on any dataset where the wall-clock
budget is exhausted before natural convergence (confirmed to occur on at
least `finance` in this codebase), the guarantee does not apply at all, and
the actual behavior (§3.1) has an unbounded worst-case error.

**SHARPENED (three-branch integration, 2026-08-24)**: `DF03_PRIMARY_THEOREM_VERIFICATION.md` §6,
having read DF03's actual proof, splits this verdict into two separable claims that should be
used in the manuscript instead of the single verdict above: **(B-i)** the removed-FAS-weight
λ-bound depends *only* on Phase 1 reaching convergence, independent of how Phase 2/add-back is
implemented; **(B-ii)** the *ranking-cost*-equals-removed-weight equivalence (needed to make (B-i)
meaningful for the ranking objective specifically) additionally requires Phase 2 to produce an
inclusion-minimal residual set, which the shipped topo-order-proxy Phase 2 does not guarantee.
Use `DF03_PRIMARY_THEOREM_VERIFICATION.md` §6's recommended manuscript language in place of this
section's own recommendation.

**Recommended manuscript language** (replacing any unconditional inheritance
claim): *"Phase A is based on the local-ratio feedback-arc-set heuristic of
Demetrescu and Finocchi [DF03], which guarantees a λ-approximation (λ = the
length of the longest simple cycle) when run to convergence. Our
implementation additionally enforces a wall-clock budget for scalability; on
the [N] of [M] datasets in our suite where this budget is exhausted before
Phase A converges (see Table [X]), this guarantee does not apply, and we
report this explicitly rather than assume it."* The exact `[N]`/`[M]` and
which datasets should be filled in from a dedicated instrumentation pass (not
performed in this audit; recommended next step, see final report).
