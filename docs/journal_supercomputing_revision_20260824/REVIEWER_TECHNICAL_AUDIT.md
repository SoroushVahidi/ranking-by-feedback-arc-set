# Reviewer Technical Audit — Concern-to-Evidence Map

Date: 2026-08-24
Manuscript: "Scalable and Training-Free Ranking from Pairwise Comparisons via
Acyclic Graph Construction" (Journal of Supercomputing, major revision)

This maps each reviewer-identified concern to the evidence/work item that
addresses it in this repository, its status as of this pass, and where to look.

| # | Reviewer concern | Work item | Status this pass | Evidence location |
|---|---|---|---|---|
| 1 | Phase-B add-back may merely densify the same DAG/order rather than genuinely improving the ranking | Implement exact reachability-aware add-back (`OURS_MFAS_REACH`); compare vs legacy topo add-back on full loadable suite | **Done** (algorithm + tests); **full-suite comparison run** this pass | `GNNRank-main/src/ours_mfas.py::_addback_reachability`, `tests/test_reachability_addback.py`, `outputs/ablation/phase_ablation_summary.md`, `REVISION_RESULTS.md` |
| 2 | Duplicate `OURS_MFAS`/`OURS_MFAS_INS3` labels may double-count the same run in tables | Confirm from source + tests; document | **Done** (confirmed, documented; not silently changed — see disposition) | `ADDBACK_DIAGNOSIS.md` §2 |
| 3 | Experimental-consistency issues generally (stale classical baseline numbers) | Verify canonical table values against source CSV | **Verified against current repo state this pass** (see below) | `outputs/paper_tables/table4_full_suite.csv`, this file §"Canonical value verification" |
| 4 | Direct runtime comparison against classical baselines missing/imprecise | Build W/T/L + runtime-ratio Pareto tables per baseline | **Not started this pass** — deferred, recorded as next step | `REVISION_EXPERIMENT_PLAN.md` "Explicitly deferred" |
| 5 | NaN/missingness handling too coarse (no common-completion analysis) | Pairwise and global common-subset completion analysis | **Not started this pass** — deferred | `REVISION_EXPERIMENT_PLAN.md` |
| 6 | No formal statistical testing (Wilcoxon, bootstrap CI, multiple-comparison correction) | Add statistical-analysis script | **Not started this pass** — deferred | `REVISION_EXPERIMENT_PLAN.md` |
| 7 | Scale/density "positive-search" framing looks post-hoc | Replace with predefined stratified analysis | Existing repo audits (`outputs/audits/targeted_ours_positive_search.md`, `sparse_regime_robustness.md`) already exist; **not re-audited or extended this pass** | `outputs/audits/` (pre-existing, not modified) |
| 8 | Sensitivity analysis (insertion strategy, tolerances, budgets) | Small defensible sensitivity study, insertion-strategy axis in particular | **Insertion-strategy axis directly produced as a side effect of the phase-ablation run** (A1_topo vs B1_reach vs B2_reach); other axes (zero tolerance, refinement budget) **not started** | `outputs/ablation/phase_ablation_summary.md` |
| 9 | Need reachability add-back correctness guarantees (no cycles, minimality, determinism) | Unit tests | **Done** | `tests/test_reachability_addback.py` |
| 10 | Ablation harness previously blocked (NumPy unavailable in one audit environment) | Repair harness | **Done** — root causes in *this* environment were missing `latextable` and `torch_geometric` packages (both installed) plus a pre-existing path bug in the hardcoded dataset list (fixed); numpy/scipy were already present | `ADDBACK_DIAGNOSIS.md`, `GNNRank-main/scripts/paper/run_phase_ablation.py` |

## Canonical value verification (Section G spot-check)

Verified directly by reading `outputs/paper_tables/table4_full_suite.csv`
(the canonical, non-legacy table — legacy `GNNRank-main/paper_tables/` was
**not** used) at HEAD of `main` (commit `706b2177`) before any code changes in
this branch:

| Method | Manuscript-claimed median upset_simple | Task instructions' target | Verified in table4_full_suite.csv this pass |
|---|---|---|---|
| SpringRank | — | ~0.802724 | see `REVISION_RESULTS.md` verification block |
| DavidScore | — | ~0.824138 | see `REVISION_RESULTS.md` verification block |
| OURS/INS3 | — | ~0.878049 | see `REVISION_RESULTS.md` verification block |
| SVD-NRS | — | ~0.891564 | see `REVISION_RESULTS.md` verification block |
| BTL | — | ~0.984385 | see `REVISION_RESULTS.md` verification block |

(Exact re-derived numbers, not assumed, are recorded in `REVISION_RESULTS.md`
together with the query used, per the "verify rather than assume" instruction.)

## Scope note

This audit intentionally covers only what changed or was directly verified in
this revision pass (branch `journal-supercomputing-major-revision-20260824`,
commit recorded in `REVISION_RESULTS.md`). It supersedes nothing in
`docs/audits/` or `outputs/audits/`, which remain the record of prior audit
passes and are not modified here (per "preserve existing results and
provenance").
