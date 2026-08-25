# Novelty / Literature Matrix

Date: 2026-08-24

Rows = closest prior methods/papers. Columns = defining properties of the
current pipeline. Every cell is either sourced (with citation) or marked
`UNKNOWN` where the literature search in this pass could not confirm it —
never silently assumed.

**Sources consulted this pass** (web search + direct PDF reading, 2026-08-24):

- [DF03] Demetrescu, C., Finocchi, I. "Combinatorial algorithms for feedback
  problems in directed graphs." *Information Processing Letters* 86,
  129-136, 2003. http://www.diag.uniroma1.it/~demetres/docs/mfas.pdf
- [BBFR04] Bar-Yehuda, R., Bendel, K., Freund, A., Rawitz, D. "Local ratio: a
  unified framework for approximation algorithms." *ACM Comput. Surv.* 36(4),
  2004. https://dl.acm.org/doi/10.1145/1041680.1041683
- [VK25] Vahidi, S., Koutis, I. "Minimum Weighted Feedback Arc Sets for
  Ranking from Pairwise Comparisons." arXiv:2412.16181, v2 Jan 2025 / v3 Dec
  2025. https://arxiv.org/abs/2412.16181 — **the authors' own direct prior
  work; the primary source for this codebase's Phase A/B/C.** (Read in full
  via the v2 PDF, https://arxiv.org/pdf/2412.16181v2.)
- [CCP24] Cavallaro, C., Cutello, V., Pavone, M. "Efficient heuristics to
  compute minimal and stable feedback arc sets." *Journal of Combinatorial
  Optimization* 48(4), 2024.
  https://link.springer.com/article/10.1007/s10878-024-01209-8
- [CCP25] Cavallaro, C. et al. "Minimal and stable feedback arc sets and
  graph centrality measures." *Computers & Operations Research*, Aug 2025.
  https://www.sciencedirect.com/science/article/pii/S030305482500276X
- [He22] He, Y., Gan, Q., Wipf, D., Reinert, G., Yan, J., Cucuringu, M.
  "GNNRank: Learning Global Rankings from Pairwise Comparisons via Directed
  Graph Neural Networks." ICML 2022 — cited as [20] throughout [VK25]; this
  is the canonical GNNRank comparison target already used by this repository
  (`GNNRank-main/`).
- Standard/background (not re-verified by fresh search this pass, cited from
  general knowledge and cross-checked against [VK25]'s own reference list):
  Bradley-Terry-Luce model (BTL); Negahban, Oh, Shah, "Rank Centrality,"
  *Oper. Res.* 65(1), 2017 ([VK25] ref [26]); Fogel, d'Aspremont, Vojnovic,
  "SerialRank," NeurIPS 2014 ([VK25] ref [16]); Cucuringu, "Sync-Rank," 2015
  ([VK25] ref [9]); De Bacco, Larremore, Moore, "A physical model for
  efficient ranking in networks" (SpringRank), *Science Advances* 2018
  (**not independently re-verified this pass — flagged UNKNOWN-VERIFIED
  below where used**).

## Matrix

Legend: ✓ = property present per source; ✗ = property absent/not addressed;
UNKNOWN = not confirmed by any source consulted this pass.

| Property | [DF03] | [VK25] (authors' own prior arXiv) | [CCP24]/[CCP25] | Current repo (`main`, pre-reachability) |
|---|---|---|---|---|
| Pairwise-ranking objective | ✗ (general MFAS/MFVS, not ranking-specific) | ✓ (explicit ranking definition, Def. "The Ranking Problem") | ✗ (general MFAS) | ✓ |
| Weighted directed graphs | ✓ | ✓ | UNKNOWN (search snippets suggest unweighted/weighted variants both discussed; not confirmed which is primary) | ✓ |
| FAS/MWFAS backbone | ✓ (defines the algorithm class) | ✓ (explicit MWFAS definition + reduction from ranking) | ✓ | ✓ |
| Local-ratio cycle breaking | ✓ (this is [DF03]'s contribution) | ✓ (explicitly "we chose to implement the heuristic algorithm from [10]"=[DF03]) | ✗ (different heuristic family — linear-arrangement/centrality-based, per [CCP24]/[CCP25] abstracts) | ✓ (via [VK25] via [DF03]) |
| Exact / approximation guarantee | ✓ — **λ-approximation, λ = length of longest simple cycle** (per [DF03]'s Theorem 2; **confirmed by direct primary-source read** — see `DF03_PRIMARY_THEOREM_VERIFICATION.md`, integrated from the sibling overlap-audit branch, superseding this row's original secondary-source caveat) | ✗ (no formal theorem stated anywhere in [VK25]; purely empirical paper) | UNKNOWN | Inherited *in principle* from [DF03] only if Phase A runs to convergence unbudgeted — see `APPROXIMATION_GUARANTEE_AUDIT.md` and `DF03_PRIMARY_THEOREM_VERIFICATION.md` §6 for the sharpened two-part verdict |
| Deterministic | UNKNOWN (not addressed in secondary sources found) | ✓ (implicit; no randomization in Algorithm 1-3) | UNKNOWN | ✓ (explicitly tested, `tests/test_audit.py`) |
| Training-free | ✓ (classical combinatorial algorithm) | ✓ (explicit selling point, contrasted with He et al. 2022's learned method) | ✓ | ✓ |
| Explicit wall-clock budget | ✗ (not part of the original algorithm) | ✗ (no time budget in [VK25]'s Algorithm 1-3; only reports observed runtimes, 0.02-0.35s) | UNKNOWN | ✓ (added later; not present in [VK25]) |
| Edge add-back / reinsertion after cycle removal | ✗ ([DF03] itself, as characterized in secondary sources, is a one-shot removal heuristic — reinsertion is not part of the base local-ratio algorithm) | ✓ (Algorithm 1, Phase-B step) | ✗ (different mechanism: [CCP24]/[CCP25] aim for "minimal and stable" FAS directly via linear-arrangement heuristics, not a remove-then-reinsert pipeline) | ✓ |
| Descending-weight reinsertion order | ✗ | ✓ ("Sort removed edges based on their weight in decreasing order") | UNKNOWN | ✓ |
| Reachability-aware (exact) reinsertion test | ✗ | ✓ ("if re-adding (u,v) does not create a cycle") — **this is the exact test, already in the authors' own 2025 preprint** | UNKNOWN | ✗ — **current repo weakens this to a fixed-topo-order proxy test (see `CURRENT_METHOD_DECOMPOSITION.md` §2)** |
| Multi-pass reinsertion (INS1/2/3) | ✗ | ✗ (single pass in [VK25]'s Algorithm 1) | UNKNOWN | ✓ — **appears to compensate for the proxy-test weakening, not present in [VK25]** |
| Inclusion-minimal FAS guarantee (stated/proved) | UNKNOWN | ✗ (not stated as a formal property in [VK25]) | ✓ ([CCP24]/[CCP25]'s explicit definition of "minimal" FAS: no arc can be reintroduced without breaking acyclicity — this is exactly what [VK25]'s exact-cycle-check add-back, if faithfully implemented, would also guarantee by construction, though [VK25] does not state or prove this) | ✗ (not stated; and not even guaranteed by construction given the proxy-test weakening — the topo-order test can leave inclusion-*non*-minimal removed sets, since it can reject edges that would not actually create a cycle) |
| Score extraction to real values | UNKNOWN | ✓ (topo position -> integer rank; then ternary-refined real scores) | UNKNOWN | ✓ |
| Order-changing local search (post add-back) | ✗ | ✗ (Algorithm 3 is explicitly order-preserving) | UNKNOWN | Adjacent-swap naive refinement (`_refine_order_naive_swaps`) **does** change order — new relative to [VK25]'s Algorithm 2/3, though it is a standard bubble-sort-style local search, not a novel algorithmic idea |
| Score-magnitude (order-preserving) refinement | ✗ | ✓ (Algorithm 2/3, ternary search on ratio loss) | ✗ | ✓ — directly inherited from [VK25] |
| Evaluated against modern classical ranking baselines (BTL/RankCentrality/SerialRank/SyncRank/SpringRank/SVD) | N/A (not a ranking paper) | Partial — [VK25]'s Table 1 compares only against GNNRank ([He22]); no BTL/RankCentrality/SerialRank/SyncRank/SpringRank numbers appear in the excerpted content | N/A | ✓ — current repo's canonical 80-dataset suite includes all of these (`outputs/paper_tables/table4_full_suite.csv`) — **this is a genuine, verifiable expansion over [VK25]** |
| Evaluated against GNN ranking (GNNRank/DIGRAC) | N/A | ✓ (only comparison in [VK25]) | N/A | ✓ |
| Sparse-graph emphasis | UNKNOWN | Not explicitly framed as a regime study; datasets used are the same families (basketball/football/faculty/animal/head-to-head) but far fewer instances (Table 1-4 of [VK25]: ~6 football + 3 faculty + ~30 basketball-coarse + a handful of basketball-finer + 1 head-to-head + 1 animal ≈ same families, smaller per-family counts, and **no finance dataset** at all in [VK25]) | UNKNOWN | ✓ — current repo has an explicit sparse-vs-dense regime audit (`outputs/audits/sparse_regime_robustness.md`, pre-existing) — **new relative to [VK25]** |
| Dense-graph behavior | ✗ (not addressed) | ✗ (no dense/near-complete graph in [VK25]'s dataset list) | UNKNOWN | Partial — `finance` (n=1315, near-complete) is in the current 80-suite but is known to time out (see sibling branch's `REVISION_RESULTS.md` §4) — **this is a genuinely new stress case relative to [VK25], but not yet a genuinely characterized one** |

## RECONCILIATION NOTE (added during three-branch integration, 2026-08-24)

The dataset-count claim in item 1 immediately below was **corrected** by a precise line-by-line
recount performed on the sibling `jsuper-prior-work-overlap-audit-20260824` branch (see that
branch's `EXPERIMENTAL_SCOPE_COMPARISON.md`, now integrated into this branch alongside this file).
**[VK25]'s Tables 1-4 list exactly 77 dataset instances, not "~50."** The corrected comparison is
77 ([VK25]) vs. 80 (current repo) — a **+3 (~4%)** delta, not a "substantial" expansion. The
original (superseded) text of item 1 is preserved below for provenance, followed by the correction.
**`EXPERIMENTAL_SCOPE_COMPARISON.md` and `REVISION_SOURCE_OF_TRUTH.md` are the authoritative
sources for this figure going forward — do not cite "~50" from this file.**

## Reading the matrix: what changed between [VK25] (Jan 2025 preprint) and the current repo

1. **[SUPERSEDED — see reconciliation note above] Dataset suite**: [VK25] Table 1-4 lists on the
   order of ~50 dataset instances across the same families (England football x6, faculty hiring
   x3, Basketball_1985-2014 x~28 coarse, a partial Basketball_finer subset,
   1 HeadToHead, 1 Animal) and explicitly has **no `finance` dataset**. The
   current repo's canonical suite is 80 datasets and includes `finance`
   (n=1315). This is a real, verifiable expansion (see
   `outputs/derived/dataset_inventory.csv`), not a re-novelty of the method.
   **Correction: a precise recount gives 77 instances in [VK25], not ~50 — the true delta is
   +3/77 (~4%), i.e. essentially flat. Do not describe this as a "real, verifiable expansion" in
   dataset count; the real, verifiable expansion is the baseline set (item 2 below) and
   infrastructure, not dataset count. See `EXPERIMENTAL_SCOPE_COMPARISON.md` for the full,
   corrected accounting.**
2. **Baseline set**: [VK25] compares only against GNNRank. The current repo's
   canonical tables compare against ten baselines (SpringRank, BTL,
   DavidScore, SVD-RS, SVD-NRS, PageRank, RankCentrality, SerialRank,
   SyncRank, EigenvectorCentrality) plus GNN methods. Also a real,
   verifiable expansion.
3. **Add-back mechanism fidelity**: [VK25]'s own Algorithm 1 already
   specifies the *exact* cycle-safety test for add-back. The current repo's
   shipped code implements a strictly weaker proxy (fixed topological
   order) plus an ad hoc multi-pass patch (INS1/2/3) that is not present in
   [VK25] at all. This is **not** an improvement over [VK25] — if anything it
   is a regression in fidelity to the authors' own previously-published
   algorithm, now being investigated for repair on the sibling branch
   (`journal-supercomputing-major-revision-20260824`, `OURS_MFAS_REACH`).
4. **No formal theory added**: [VK25] contains no theorem, proposition, or
   formal MWFAS-ranking equivalence proof — it is a purely empirical/algorithm-
   engineering paper (its own §4 "Conclusion and Future Research" explicitly
   lists "investigating improved cycle detection techniques" and "alternative
   tie-breaking mechanisms" as *future* work, not completed contributions).
   Any approximation-guarantee language, formal equivalence proof, or
   complexity analysis appearing in the JOS manuscript is therefore new
   *relative to [VK25]* by construction — but its correctness must be
   independently verified against the actual code, which is exactly what
   `APPROXIMATION_GUARANTEE_AUDIT.md`, `RANKING_MWFAS_EQUIVALENCE.md`, and
   `COMPLEXITY_AUDIT.md` do below.

## Explicit UNKNOWNs (not resolved this pass, flagged rather than guessed)

- Exact statement/page number of [DF03]'s theorem was not extracted (the
  source PDF returned only structural/compressed content to the fetch tool
  in this pass); the "λ-approximation, λ = longest simple cycle"
  characterization is taken from a secondary source (the WebSearch summary)
  and from [VK25]'s own Related-Work description of [10]=[DF03] ("This
  heuristic was shown to be efficient in practice, providing a
  λ-approximation, where λ is the length of the longest cycle in the
  graph"), not from a direct read of [DF03]'s own theorem statement.
  **Recommendation: obtain the actual theorem text before finalizing
  manuscript wording** — see `APPROXIMATION_GUARANTEE_AUDIT.md` verdict.
- SpringRank's exact citation (De Bacco, Larremore, Moore, *Science
  Advances* 2018) was not independently re-verified by a fresh search this
  pass; it is standard/well-known but should be spot-checked against the
  manuscript's own bibliography before submission.
- [CCP24]/[CCP25]'s exact algorithmic mechanism (linear-arrangement /
  centrality-based ordering, per abstract) was only read from search-result
  summaries, not the full text; whether it uses weighted graphs primarily or
  only as an extension is UNKNOWN from this pass's evidence.
