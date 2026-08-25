# Distinctness Assessment and New-Algorithmic-Work Verdict (Sections E + I)

Date: 2026-08-24
Basis: `PRIOR_WORK_OVERLAP_MATRIX.md`, `PRIOR_ADDBACK_LINEAGE.md`, `EXPERIMENTAL_SCOPE_COMPARISON.md`,
`DF03_PRIMARY_THEOREM_VERIFICATION.md`, `SPRINGER_PREPRINT_POLICY_AUDIT.md`.

## Section E — candid publication-level assessment

**1. How much of the algorithmic core is already in arXiv:2412.16181?**
The large majority. All three phases' defining equations/pseudocode — local-ratio Phase A,
weight-ordered exact-cycle-check Phase B, ternary-search ratio-loss Phase C — are already
specified in [VK25] Algorithm 1-3 (both v2 and v3, read in full this pass), themselves adopting
DF03's Phase 1/2 structure and DF03's own suggested descending-weight heuristic. See
`PRIOR_WORK_OVERLAP_MATRIX.md` rows 1-4, 8, 9(idea), 12, 15, 16, 21 — all **IDENTICAL PRIOR
WORK**.

**2. What specifically is new in the journal submission (as evidenced by the codebase and the two
sibling revision branches)?**
- A formal ranking-MWFAS equivalence proposition and proof (absent from [VK25], which asserts the
  connection only informally, and absent from DF03, which does not address ranking at all).
- A precise approximation-guarantee audit sharpened, in this branch, into two separable claims
  (removed-FAS-weight bound vs. ranking-cost equivalence, per `DF03_PRIMARY_THEOREM_VERIFICATION.md`
  §6) — neither claim is stated in [VK25]; the underlying distinction (naive-DFS vs.
  dynamic-reachability complexity) is stated by DF03 itself, but its diagnostic application to this
  specific shipped implementation is new.
- Diagnosis of a fidelity gap between [VK25]'s own specified add-back algorithm and the shipped
  codebase's weaker topo-order proxy, plus a corrected, efficient, formally-proved implementation
  (`OURS_MFAS_REACH`) — genuinely new relative to both [VK25] and DF03 (row 9/27/28 of the overlap
  matrix).
- Ten classical ranking baselines (BTL, SpringRank, RankCentrality, SerialRank, SyncRank,
  DavidScore, EigenvectorCentrality, PageRank, SVD-RS, SVD-NRS) — [VK25] has zero. This is the
  single largest, cleanest, most easily defensible empirical delta.
- A dense/near-complete-graph stress case (`finance`) absent from [VK25], which surfaces a
  concrete, previously-undocumented failure mode (Phase A can fail to converge within a practical
  time budget, silently voiding the inherited guarantee and triggering an unbounded-error identity
  fallback).
- Reproducibility/ablation infrastructure (phase-ablation harness across the near-full suite, 41+
  new unit tests, determinism tests) not present in any form in [VK25].

**3. Is the journal manuscript currently an incremental extension of the preprint?**
**If evaluated on empirical breadth of datasets alone: yes, essentially** — the corrected count
(`EXPERIMENTAL_SCOPE_COMPARISON.md`) shows only +3 datasets out of 77 (≈4%), not the "substantial"
expansion earlier (mis-)stated on the sibling theory-audit branch. **If evaluated on baselines,
theory, and the add-back fidelity diagnosis+fix together, no** — these are qualitatively different
in kind from "more of the same experiment," and several (the formal proofs, the fidelity-gap
diagnosis, the `finance` stress case) do not exist in [VK25] in any form, weak or strong.

**4. Is it a legitimate expanded journal version?**
Conditionally yes — and there is a specific, favorable pattern supporting this: [VK25]'s own
Conclusion (both versions, read in full) explicitly lists as *future work*: "(2) developing more
efficient cycle detection techniques... on extremely large graphs" and "(3) identifying principled
tie-breaking mechanisms for vertices with no directed path between them" — the reachability-add-back
diagnosis+fix (item 2's spirit) and the approximation-guarantee audit (bearing directly on item 2's
scalability framing) are legitimate, substantive follow-through on the authors' own stated research
plan, not an opportunistic repackaging. This is the strongest single argument for legitimacy and
should be stated explicitly in the manuscript's introduction (see
`REVISED_CONTRIBUTION_POSITIONING.md` item 9).

**5. Springer/journal concerns about prior-preprint overlap?**
Administratively, no (`SPRINGER_PREPRINT_POLICY_AUDIT.md` §1). Scientifically/reviewer-risk-wise,
yes if the manuscript does not explicitly cite and differentiate from [VK25] — an omission that
would very plausibly be caught (this audit found [VK25] via ordinary literature search in minutes).

**6. Is the novelty sufficient scientifically, independent of publication-policy permissibility?**
**Conditionally yes** — sufficient *if and only if* the theoretical contributions and the
fidelity-gap diagnosis+fix are foregrounded as the primary contribution, with the dataset-count
narrative corrected to its accurate, modest scope and the baseline-expansion narrative
foregrounded instead. **Not sufficient** if the manuscript's primary framing remains "same
algorithm, bigger benchmark" without the theory and the diagnosis — that framing, given the now
corrected +3/77 dataset delta, would read as thin.

**7. Would stronger new algorithmic work be advisable?**
Yes, as a risk-reduction measure rather than a strict scientific necessity — see the verdict below.

## Section I — verdict

**Verdict: B — probably sufficient after the corrected experiments/theory described above, but a
modest new algorithmic extension would materially reduce reviewer risk.**

Rationale for B over A: the core algorithmic fix (`OURS_MFAS_REACH`) is, per
`PRIOR_ADDBACK_LINEAGE.md`, substantially a *restoration* of an algorithm the authors already
specified in [VK25]/inherited from DF03, not an invention. A reviewer who independently locates
[VK25] (as this audit did, via ordinary search) could reasonably ask "what is algorithmically new
here, beyond correcting your own prior implementation and adding classical baselines?" The formal
theory answers this in large part, but a genuinely new algorithmic idea would answer it more
completely and durably.

Rationale for B over C: the theoretical package (formal equivalence proof, sharpened
approximation-guarantee audit, minimality/one-pass proofs, complexity diagnosis grounded directly
in DF03's own primary text) is substantial, correctly scoped, and — critically — was independently
verified in this pass against both the authors' own prior paper and the ultimate primary source,
not merely asserted. This is not "too incremental"; it is a legitimate, if modest, package that a
Journal of Supercomputing audience (which routinely publishes complexity/correctness analyses of
existing heuristics) would recognize as a real contribution.

Rationale against D (reposition as purely empirical/systematic study): the theoretical
contributions are strong enough, and sufficiently novel relative to both [VK25] and DF03, that
discarding the "algorithmic contribution" framing entirely would under-sell real work; a
hybrid framing (algorithmic correction + formal theory + expanded baseline comparison) is more
accurate than either "new algorithm" or "pure empirical study" alone.

## Three candidate algorithmic additions (ranked)

Per the task's explicit instruction, the weighted exchange/perturb-and-repair concept is included
but was **first checked against prior art**: a search this pass found *"Fast Local Search Algorithm
for Weighted Feedback Arc Set in Tournaments"* (exact venue not independently verified this pass),
which studies an **"fc-exchange" neighborhood local search for weighted FAS — but specifically
restricted to tournaments (complete graphs)**, not general weighted digraphs. **The general
concept of exchange-based local search for FAS is therefore not novel**; a min-cut-triggered
exchange integrated with an incremental reachability structure, applied to general (non-tournament)
weighted digraphs, is a narrower, unverified-as-existing instantiation — cite the tournament-restricted
prior work explicitly and scope the novelty claim accordingly (structural integration and
generalization beyond tournaments, not the exchange concept itself).

| Rank | Addition | Novelty potential | Reviewer relevance | Implementation difficulty | Experimental cost | Theoretical cleanliness |
|---|---|---|---|---|---|---|
| 1 | **Weighted exchange / min-cut-triggered edge swap** (Section F of the original ablation-workstream task, not yet implemented on the sibling branch) | Moderate — general exchange-based FAS local search exists for tournaments; a min-cut-triggered version integrated with incremental reachability, for general digraphs, is narrower and plausibly new | **Highest** — directly targets the exact "does add-back merely densify vs. genuinely improve" reviewer concern this whole revision is centered on, and is directly motivated by a concrete, already-observed failure case (`Halo2BetaData`'s regression under plain reachability add-back, sibling branch's `REVISION_RESULTS.md` §3) | Moderate — requires a directed min-cut/mincut-like computation on the affected subgraph per candidate high-weight rejected edge | Moderate — bounded to highest-weight rejected edges per a wall-clock budget, per the original task's own design constraints | Clean — a monotone local-improvement argument (strictly decreases total removed weight when accepted) is straightforward to state and prove |
| 2 | **Exact-solver ground-truthing on tractable sub-instances** (SCC-decompose the Phase-A residual structure; run an existing exact FAS solver, e.g. Baharev et al.'s method already cited in [VK25]'s own bibliography, on small enough components; report the heuristic's actual gap to true OPT where measurable) | Moderate — methodologically standard practice, not yet done anywhere in this project's lineage | High — directly, empirically grounds the approximation-guarantee discussion with real gap-to-OPT numbers rather than only a worst-case λ bound | Low-moderate — can reuse an existing open-source exact solver rather than implementing one | Moderate — only feasible on small/tractable components, which must be identified first | Clean — no new proof required, purely empirical validation of already-proved bounds |
| 3 | **Principled tie-breaking for incomparable vertex pairs via a secondary centrality signal** | Low-moderate — [VK25]'s own Conclusion names this as future work item 3, and Cavallaro et al. 2025 (`[CCP25]`, per the sibling theory-audit branch's `NOVELTY_LITERATURE_MATRIX.md`) already explores centrality-based orderings for FAS, so this must be scoped and cited carefully, not claimed from scratch | Moderate — a clean, low-risk "delivers on our own stated future work" narrative | Low | Low | Clean — a straightforward secondary sort key; easy to test |

**Recommendation**: if pursuing new algorithmic work at all, **prioritize #1**, since it is the
only one of the three that would give reviewers a genuinely new, non-restorative algorithmic idea
directly answering the central reviewer concern — but treat it as risk-*reduction*, not a
scientific necessity, per the B verdict above. #2 is the cheapest, lowest-risk way to strengthen
the existing theoretical package without new algorithm design. #3 is optional polish.
