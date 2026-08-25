# Prior-Work Overlap Matrix

Date: 2026-08-24

**Important scope note**: this repository does not contain the actual JOS manuscript text (no
`.tex` source was found anywhere in three separate preflight searches across the three revision
branches). "Journal manuscript contains it?" below is therefore assessed against the best
available proxy: **the shipped codebase (`GNNRank-main/src/*.py`, `main`) plus the evidentiary
work product of the two sibling revision branches** (`journal-supercomputing-major-revision-20260824`
and `jsuper-revision-novelty-theory-20260824`), which represent what the manuscript *can*
currently claim with evidence. Where the manuscript's actual text may claim something not yet
backed by code/evidence, that is out of scope for this document (it is a code/evidence audit, not
a manuscript-text audit) and is flagged as such.

Sources: DF03 (Demetrescu & Finocchi 2003, primary text read in full,
`DF03_PRIMARY_THEOREM_VERIFICATION.md`); [VK25] (Vahidi & Koutis, arXiv:2412.16181 v2+v3, both
read in full).

Classifications: **IDENTICAL PRIOR WORK**, **MINOR IMPLEMENTATION CHANGE**, **ENGINEERING
EXTENSION**, **EMPIRICAL EXTENSION**, **THEORETICAL EXTENSION**, **GENUINELY NEW**, **UNCLEAR**.

| # | Contribution | In [VK25]? | In journal (codebase+evidence)? | Identical? | Classification | Evidence | Safe novelty claim? | Recommended wording |
|---|---|---|---|---|---|---|---|---|
| 1 | Ranking ↔ MWFAS framing (informal) | Yes (Def. 1 + informal §1.1 discussion, both versions) | Yes | Yes | **IDENTICAL PRIOR WORK** | [VK25] §1.1; codebase's entire design rationale | No — do not claim as new | "We adopt the ranking-MWFAS framing of [VK25]" |
| 2 | Local-ratio Phase A | Yes (Algorithm 1 Step 2, both versions; ultimately from DF03) | Yes | Yes | **IDENTICAL PRIOR WORK** | `_local_ratio_break_cycles` | No | Cite DF03 and [VK25] |
| 3 | DFS cycle selection | Yes ("cycle detection via DFS", both versions) | Yes | Yes | **IDENTICAL PRIOR WORK** | `_find_one_cycle_edges` | No | — |
| 4 | Residual reduction | Yes (Algorithm 1 Step 2 `while` loop) | Yes | Yes | **IDENTICAL PRIOR WORK** | Same function | No | — |
| 5 | Time budgeting (wall-clock) | **No** (neither DF03 nor [VK25] specify a time budget; [VK25] only *reports* observed 0.02-0.35s runtimes) | Yes (`time_limit_sec`, checked throughout) | N/A | **ENGINEERING EXTENSION, with a correctness caveat** | `ours_mfas_rmfa`'s `t0`/`time_limit_sec` checks; `APPROXIMATION_GUARANTEE_AUDIT.md` (sibling branch) | Yes, as an engineering addition — but must be paired with the disclosure that it can void DF03's guarantee (row 29) | "We add an explicit wall-clock budget... which, as we show in §[X], can void the inherited approximation guarantee on dense inputs" |
| 6 | Numerical safeguards (`zero_tol`, forced-progress kills) | No (not mentioned in DF03 or [VK25] — both papers' pseudocode assumes exact arithmetic) | Yes | N/A | **ENGINEERING EXTENSION** | `ours_mfas.py` `zero_tol` handling; `APPROXIMATION_GUARANTEE_AUDIT.md` §2.1-2.2 | Yes, minor | Mention as an implementation detail, not a contribution |
| 7 | Deterministic traversal / tie handling | Implicit in [VK25] (no randomization stated) but not tested/asserted | Yes, explicitly tested (`tests/test_audit.py`) | Partial | **ENGINEERING EXTENSION** | `test_ours_no_randomness_in_source_code`, `test_ours_uses_stable_sort` | Yes, as reproducibility infrastructure | — |
| 8 | Weight-prioritized edge reinsertion | Yes (explicit in Algorithm 1, both versions — itself adopting DF03's own suggested heuristic) | Yes | Yes | **IDENTICAL PRIOR WORK** | See `PRIOR_ADDBACK_LINEAGE.md` Steps 0-1 | No | — |
| 9 | Exact cycle-safety / reachability test for reinsertion | Yes (Algorithm 1: "if adding (u,v) back does not create a directed cycle"; ultimately DF03 Phase 2) | Only on sibling branch `OURS_MFAS_REACH`, **not** on `main` | Yes, where present | **IDENTICAL PRIOR WORK (the idea)**; the *implementation* (incremental reachability matrix, proofs) is new | `PRIOR_ADDBACK_LINEAGE.md` Step 5 | The exact test itself: No. The efficient implementation + proofs: Yes | "We restore the exact cycle-safety test of [VK25]/[DF03], implemented via an efficient incremental reachability structure, with new correctness proofs (one-pass sufficiency, inclusion-minimality)" |
| 10 | Fixed-topological-order proxy (current `main` behavior) | **No** — absent from both DF03 and [VK25]; a deviation, not an extension | Yes (`main`) | No | **MINOR IMPLEMENTATION CHANGE that is a fidelity regression, not an advance** | `_addback_desc_weight_multi`; `PRIOR_ADDBACK_LINEAGE.md` Step 3 | No — must not be presented as an improvement | Disclose as a diagnosed implementation gap, now being corrected |
| 11 | Multiple INS passes | **No** (single pass in both DF03 and [VK25]) | Yes (`main`) | No | **MINOR IMPLEMENTATION CHANGE**, compensatory, empirically near-inert on passes 2-3 | `ADDBACK_DIAGNOSIS.md` (sibling branch) | No — should not be claimed as a strength | Do not feature as a contribution |
| 12 | Topological ranking extraction | Yes (Algorithm 1 Step 3) | Yes | Yes | **IDENTICAL PRIOR WORK** | `_scores_from_kept_edges` | No | — |
| 13 | Real-valued score construction | Partial — [VK25] Step 3 uses topo-position ranks with a tie-break score formula; not a general real-valued construction | Yes (integer topo position -> real via Phase C) | Partial | **MINOR IMPLEMENTATION CHANGE / ADAPTATION** | `_scores_from_kept_edges` + Phase C | No, standard | — |
| 14 | Adjacent-swap refinement | **No** (absent from both DF03 and [VK25]) | Yes (`_refine_order_naive_swaps`) | No | **ADAPTATION of a standard technique (bubble-sort local search), new relative to [VK25] but not novel in itself** | `CURRENT_METHOD_DECOMPOSITION.md` (sibling branch) §4 | Weak — standard technique | Present as engineering, not algorithmic novelty |
| 15 | Ratio-upset refinement (concept) | Yes (§3.1/3, both versions — motivated by observing ratio loss can be worse than naive/simple loss) | Yes | Yes | **IDENTICAL PRIOR WORK** | [VK25] §3(.1) | No | — |
| 16 | Ternary-search refinement (Algorithm 2/3) | Yes (Algorithm 2 + 3, both versions, near-verbatim match to shipped code) | Yes | Yes | **IDENTICAL PRIOR WORK** | `refine_scores_ratio_ternary`, `_ternary_opt_one` | No | — |
| 17 | Deterministic implementation (as a tested/asserted property) | No (asserted only implicitly by absence of randomization) | Yes, explicitly | Partial | **ENGINEERING EXTENSION** | Same as row 7 | Yes, modestly | — |
| 18 | Sparse input representation (CSR / edge-id adjacency) | Unclear — [VK25] describes "an adjacency list" and "a weights dictionary" generically, no sparse-matrix-specific detail given | Yes (`scipy.sparse`, edge-id-indexed arrays throughout) | Unclear | **UNCLEAR** (likely engineering extension, not confirmable as identical or different from the prose description alone) | [VK25] §2.2 prose vs. `_csr_to_edges` | Weak claim only | Do not over-claim; describe as implementation detail |
| 19 | Benchmark datasets | Yes, but far fewer instances (see `EXPERIMENTAL_SCOPE_COMPARISON.md`) and **no `finance` dataset at all** | Yes, 80-dataset canonical suite | No | **EMPIRICAL EXTENSION** | `outputs/derived/dataset_inventory.csv` vs. [VK25] Tables 2-4 | Yes | Quantify precisely (see scope comparison doc) |
| 20 | Classical baselines (BTL, SpringRank, RankCentrality, SerialRank, SyncRank, SVD, etc.) | **No — zero classical baselines in [VK25]**, only GNNRank | Yes, ten baselines in `outputs/paper_tables/table4_full_suite.csv` | No | **EMPIRICAL EXTENSION (large)** | Canonical table4; [VK25] Table 1 (GNNRank columns only) | Yes, strongly | This is one of the clearest, safest novelty claims available |
| 21 | GNNRank comparison | Yes (the only comparison in [VK25]) | Yes | Yes (same target method) | **IDENTICAL PRIOR WORK (as a comparison target)**; broadened by row 20 | — | No, for the comparison itself | — |
| 22 | Runtime analysis | Yes, informal (observed 0.02-0.35s, GNNRank CLI timing anecdotes) | Yes, systematic per-dataset/per-phase runtime columns | No | **EMPIRICAL / ENGINEERING EXTENSION** | `outputs/paper_tables` runtime columns; sibling branch's ablation runtime tables | Yes | — |
| 23 | Compute-matched analysis | **No** (not present in [VK25] in any form) | Referenced in codebase (`table5_compute_matched.csv`) though one supporting file was found missing in this pass (`leaderboard_compute_matched.csv` — see both sibling branches' test failures) | No | **EMPIRICAL EXTENSION, but currently incompletely evidenced** — flag, do not claim until the missing file is resolved | `tests/test_audit.py::test_leaderboard_compute_matched_is_subset` (failing on both sibling branches, pre-existing) | Not yet — pending a data-provenance fix | Do not claim in the manuscript until this test passes |
| 24 | Timeout/coverage treatment | **No** (not addressed in [VK25]) | Partial — `finance` timeout is documented (sibling branch), but no systematic timeout/coverage analysis across the full suite exists yet | No | **EMPIRICAL EXTENSION, partial** | `REVISION_RESULTS.md` §4 (sibling branch) | Yes, for what exists; do not overstate completeness | — |
| 25 | Density/regime analysis | **No** (no dense/near-complete-graph case exists anywhere in [VK25]'s dataset list) | Yes, partially — pre-existing `outputs/audits/sparse_regime_robustness.md` plus this revision's `finance` stress case | No | **EMPIRICAL EXTENSION** | `outputs/audits/` (pre-existing); sibling branch results | Yes | — |
| 26 | Formal ranking-MWFAS proof | **No** (asserted informally only, both versions, no Proposition/Theorem environment anywhere in either PDF) | Yes, on the theory-audit sibling branch (`RANKING_MWFAS_EQUIVALENCE.md`) | No | **THEORETICAL EXTENSION** | Direct read of both [VK25] versions (no theorem found); sibling branch document | Yes, clearly novel relative to [VK25] | Strong, safe claim |
| 27 | One-pass reachability-add-back sufficiency (proof) | **No** (DF03's Phase 2 is order-independent by construction and its minimality proof doesn't address single-pass sufficiency for a *weight-ordered* variant as a named property; [VK25] states no such property) | Yes, proved and tested on `journal-supercomputing-major-revision-20260824` | No | **THEORETICAL EXTENSION** | `REACHABILITY_ADDBACK_DESIGN.md` §3 (sibling branch); confirmed absent from DF03/[VK25] by direct read | Yes | — |
| 28 | Inclusion-minimality of residual FAS (proof, for the reachability variant) | **Partially known at the definitional level** — DF03 Theorem 1 proves minimality for its own (unordered) Phase 2; [VK25] does not restate or reprove this for its ordered variant | Yes, proved and tested for the specific descending-weight-ordered incremental-reachability implementation | Partial | **THEORETICAL EXTENSION (of a known result, adapted to a new implementation)** | `REACHABILITY_ADDBACK_DESIGN.md` §4; DF03 Theorem 1 (this document, §3) | Yes, but must cite DF03's Theorem 1 as the origin of the *concept*, not claim minimality itself is new | "We prove minimality holds for our specific efficient implementation, extending DF03's Theorem 1" |
| 29 | Time-budget approximation-guarantee limitation (that the guarantee can be voided by a wall-clock cutoff) | **No** (not discussed in either DF03 or [VK25], since neither imposes a time budget) | Yes, on the theory-audit sibling branch, now sharpened by this branch's primary-source read into two separable claims (removed-weight bound vs. ranking-cost equivalence) | No | **THEORETICAL EXTENSION** | `APPROXIMATION_GUARANTEE_AUDIT.md` (sibling); `DF03_PRIMARY_THEOREM_VERIFICATION.md` §6 (this branch) | Yes, clearly novel and directly reviewer-relevant | Strong, safe claim |
| 30 | Corrected practical complexity analysis (O(mn+m²) vs. claimed O(VE)) | DF03 itself already flags this exact naive-vs-optimized distinction in its own proof (Theorem 1's proof text) — so the *distinction* is known; **applying it diagnostically to this specific shipped implementation is new** | Yes, on the theory-audit sibling branch, now confirmed against DF03's own text by this branch | No (the diagnosis, not the underlying distinction) | **THEORETICAL/ENGINEERING EXTENSION (diagnostic application of a known distinction)** | `COMPLEXITY_AUDIT.md` (sibling); `DF03_PRIMARY_THEOREM_VERIFICATION.md` §3 (this branch) | Yes, for the diagnostic finding; do not claim the underlying complexity-gap *concept* (naive DFS vs. dynamic reachability) as new, since DF03 states it themselves | "We show the shipped implementation falls into the slower of the two cases DF03 themselves distinguish" |

## Reading the matrix

- Rows 1-4, 8, 9(idea only), 12, 15, 16, 21: **directly inherited**, safely citable but not
  claimable as new.
- Rows 10, 11: **should not be presented as contributions at all** — they are deviations/patches,
  and their presence is better disclosed as a diagnosed problem than featured.
- Rows 5-7, 13, 14, 17, 18: **modest engineering extensions**, legitimate but minor; useful as
  supporting infrastructure, not headline claims.
- Rows 19, 20, 22, 24, 25: **the safest, largest, most defensible novelty claims available** —
  concrete, quantifiable, verifiable empirical expansion, especially row 20 (ten classical
  baselines vs. zero in [VK25]).
- Row 23: **currently not safe to claim** — pending data-provenance fix (a pre-existing failing
  test on both sibling branches).
- Rows 26-30: **the theoretical contributions genuinely absent from [VK25]**, now additionally
  confirmed absent from DF03 itself for rows 26, 27, 29 (row 28 and row 30 build on results DF03
  *does* state, applied/proved in a new context — cite DF03 there, do not claim from scratch).
