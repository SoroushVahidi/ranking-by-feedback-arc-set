# Novelty Verdict (Section E)

Date: 2026-08-24
Basis: `CURRENT_METHOD_DECOMPOSITION.md`, `NOVELTY_LITERATURE_MATRIX.md`.

Per-component verdict against the closest prior work, which — critically —
is the authors' own [VK25] (arXiv:2412.16181), not a third party:

| # | Component | Verdict | Basis |
|---|---|---|---|
| 1 | Local-ratio Phase A | **KNOWN** | Demetrescu & Finocchi 2003 [DF03]; already used identically in the authors' own [VK25] |
| 2 | Time-bounded Phase A (wall-clock budget) | **SYSTEM/PIPELINE CONTRIBUTION, with a correctness caveat** | Not present in [VK25] (which reports observed runtimes, not an enforced budget); new here, but introduces the timeout/identity-fallback issue documented in `APPROXIMATION_GUARANTEE_AUDIT.md` — should be presented as an engineering trade-off, not a strength, until the fallback is fixed |
| 3 | Deterministic traversal / tie handling | **ADAPTATION / reproducibility engineering** | Standard practice (fixed scan order, stable sort); valuable for auditability but not a research contribution in itself |
| 4 | Weight-prioritized add-back | **KNOWN** | Already specified in [VK25]'s Algorithm 1 ("Sort removed edges based on their weight in decreasing order") |
| 5 | Multi-pass add-back (INS1/2/3) | **SHOULD NOT CLAIM as a strength** | Not present in [VK25] (single pass); shown on the sibling branch to be an ad hoc compensation for the topo-order proxy's incompleteness, with passes 2/3 typically contributing zero additional reinsertions once pass 1 completes |
| 6 | Reachability-aware add-back (sibling workstream) | **KNOWN idea / NEW implementation** | The *idea* (exact "does not create a cycle" test) is **already in [VK25]'s own Algorithm 1** — implementing it correctly is a fidelity restoration, not new algorithmic novelty. What **is** new: a proof (not just a test) of one-pass sufficiency and of inclusion-minimality of the resulting residual FAS, and an efficient incremental-reachability-matrix algorithm with a stated complexity/memory analysis — none of which appear in [VK25] |
| 7 | Score extraction (topo position -> rank) | **KNOWN** | Textbook; standard DAG-to-ranking construction |
| 8 | Adjacent-swap refinement | **ADAPTATION** | Standard bubble-sort-style local search (adjacent transposition); order-changing, new relative to [VK25]'s Algorithm 2/3 (which are order-preserving) but not a novel technique in itself |
| 9 | Ratio-score (ternary search) refinement | **KNOWN** | Directly inherited from [VK25]'s Algorithm 2/3; ternary search for unimodal 1-D optimization is textbook, and unimodality is asserted empirically in [VK25], not proved (still not proved here) |
| 10 | The complete integrated pipeline (as an artifact) | **SYSTEM/PIPELINE CONTRIBUTION** | The specific combination, first-class phase-ablation toggles, determinism guarantees, and reproducibility/audit tooling are new relative to [VK25]'s codebase, and are a legitimate (if modest) contribution distinct from any single phase's algorithmic content |
| 11 | Empirical sparse-regime behavior | **NEW (empirical) / SYSTEM CONTRIBUTION** | [VK25] has no dense/near-complete-graph case and a much smaller per-family dataset count; the current repo's sparse-vs-dense regime characterization (including the `finance` stress case) is genuinely new evidence, not present in [VK25] |
| 12 | Training-free vs. GNN comparison | **KNOWN framing / NEW scope** | [VK25] already runs exactly this comparison (vs. GNNRank only); what's new is the addition of ten classical-baseline comparisons alongside it — [VK25] has **zero** classical-ranking-method baselines (BTL, SpringRank, RankCentrality, etc.), only GNNRank |

## Strongest defensible contribution bullets (no marketing language)

1. A substantially expanded and more rigorous empirical evaluation of the
   local-ratio MWFAS-based ranking approach the authors introduced in
   [VK25]: 80 canonical datasets spanning more families and a wider
   size/density range (including a near-complete-graph stress case absent
   from [VK25]), evaluated against ten classical ranking baselines in
   addition to GNN-based methods (versus [VK25]'s GNNRank-only comparison),
   with a documented, deterministic, reproducible pipeline.

2. A precise, evidence-backed diagnosis of a fidelity gap between the
   add-back algorithm as specified in the authors' own prior publication
   ([VK25]'s Algorithm 1, an exact cycle-safety test) and the algorithm as
   actually shipped in this codebase (a strictly weaker fixed-topological-
   order proxy, patched with an undocumented multi-pass mechanism) —
   together with a corrected implementation that is *proved*, not merely
   tested, to be single-pass-sufficient and to yield an inclusion-minimal
   residual feedback arc set, and that empirically restores materially
   better ranking quality across the expanded benchmark (see sibling
   branch's `REVISION_RESULTS.md`).

3. A rigorous formal treatment of the ranking-MWFAS connection that [VK25]
   only asserts informally: an exact equality of optimum objective values,
   correctly scoped as a many-to-many (not one-to-one) solution
   correspondence, paired with a precise audit of the conditions under which
   the inherited Demetrescu-Finocchi approximation guarantee actually
   applies to the shipped, time-budgeted implementation — showing it does
   not apply unconditionally, and proving the timeout fallback path carries
   no error bound in general.

**Not recommended as a contribution bullet**: multi-pass (INS1/2/3) add-back
as an algorithmic innovation (item 5) — the evidence available characterizes
it as compensating for an implementation weakening rather than adding value
in its own right, and featuring it prominently invites exactly the kind of
scrutiny that produced this finding.
