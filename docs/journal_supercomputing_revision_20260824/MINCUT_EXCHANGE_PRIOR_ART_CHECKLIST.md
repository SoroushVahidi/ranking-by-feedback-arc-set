# Min-Cut Exchange: Prior-Art Search Checklist

Date: 2026-08-24
**Status: checklist of open literature-search questions. No novelty claim is made in this
document.** One relevant prior-art fact is already established (see item 1) from the search
performed for `DISTINCTNESS_AND_NEW_WORK_VERDICT.md`; the remainder are open questions to resolve
before `MINCUT_WEIGHTED_EXCHANGE_RESEARCH_QUESTION.md`'s mechanism could be described as novel in
any manuscript.

## Already answered (from prior search this revision effort)

1. **General exchange-based local search for weighted FAS**: exists, but specifically for
   **tournaments** (complete graphs) — a paper titled approximately *"Fast Local Search Algorithm
   for Weighted Feedback Arc Set in Tournaments"* studies an "fc-exchange" neighborhood. **Exact
   venue/authors/year not independently verified in this pass** — re-verify via a direct
   bibliographic lookup (not just a search-result summary) before citing in the manuscript.

## Open questions (not yet searched, or searched only incidentally)

2. **Weighted FAS local exchange on arbitrary (non-tournament) digraphs**: does an exchange-based
   local-search mechanism for weighted FAS exist for general digraphs (not restricted to complete
   graphs)? The tournament-restricted result (item 1) does not answer this.
3. **Cut-based FAS repair specifically**: is there prior work that repairs/improves a feedback arc
   set by computing a min-cut to enable reinsertion of a specific excluded arc, as opposed to
   general edge-swap neighborhoods? This is a more specific mechanism than "exchange" broadly and
   was not directly searched.
4. **Min-cut replacement of excluded arcs** (the specific "trade one excluded arc for a cut of
   kept arcs" framing): not directly searched; closest related concept found so far is Demetrescu
   & Italiano's dynamic transitive-closure / reachability maintenance work (cited by DF03 itself,
   see `DF03_PRIMARY_THEOREM_VERIFICATION.md` §3) but that is a *data structure* for maintaining
   reachability under edge insertion/deletion, not an *optimization mechanism* for improving a FAS.
5. **Path-destroying cut exchange** (as a named technique in the graph-algorithms literature under
   any name): not searched.
6. **DAG augmentation with compensating deletion** (adding an edge to a DAG while removing a
   minimal set of edges to preserve acyclicity, as a general graph-editing operation independent of
   the FAS/ranking context): plausibly related to graph-editing / graph-repair literature broadly;
   not searched in this pass.
7. **Kemeny/ranking exchange using cuts**: whether any ranking-aggregation method (Kemeny
   optimization or otherwise) uses a min-cut-based local exchange step: not searched. Note
   `RANKING_MWFAS_EQUIVALENCE.md`'s citation context (Ailon, Charikar, Newman "Aggregating
   inconsistent information: Ranking and clustering," referenced as [1] in [VK25]'s bibliography)
   is a plausible starting point given its ranking-and-clustering framing, but its actual
   algorithmic content relative to this specific mechanism was not checked.
8. **Tournament-only exchange versus general-digraph exchange**: beyond confirming item 1's
   tournament restriction, whether any paper explicitly generalizes fc-exchange-style local search
   to general weighted digraphs (which is exactly what this project's candidate mechanism would
   need to be compared against) was not searched.
9. **Incremental DAG repair literature more broadly** (outside the FAS/ranking context — e.g.
   database/constraint-repair literature on restoring acyclicity after a forbidden insertion): not
   searched; this is a plausible source of prior art from an entirely different application
   domain (e.g. dependency-graph repair in build systems, or foreign-key/constraint-graph repair
   in databases) that uses structurally similar "remove a separating cut, then insert" operations
   under a different name.

## Recommended next step for this checklist

Each open question above (2-9) should become one targeted literature search before any
implementation or novelty claim is made for the mechanism in
`MINCUT_WEIGHTED_EXCHANGE_RESEARCH_QUESTION.md`. This checklist is intentionally left as
questions, not answers, per this task's explicit instruction not to make a novelty claim yet.
