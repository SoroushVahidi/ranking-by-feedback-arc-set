# Experimental Scope Comparison: [VK25] vs. Journal Manuscript (Codebase Evidence)

Date: 2026-08-24

**Correction to a prior overstatement.** The sibling theory-audit branch's
`NOVELTY_LITERATURE_MATRIX.md` characterized [VK25]'s dataset suite as "~50 dataset instances
across fewer families" versus the current repo's 80. **A precise line-by-line count from
[VK25]'s own Tables 1-4 (both v2 and v3, identical), performed for this document, gives 77
instances, not ~50.** This is corrected here rather than silently carried forward. The two suites
are much closer in raw size than previously stated; the real, precisely-quantifiable expansion is
narrower and different in kind than "substantially more datasets," and is detailed below.

## Dataset count — exact, verified tally

| Family | [VK25] (Tables 1-4, both versions) | Current repo (`outputs/derived/dataset_inventory.csv`, `in_80_suite=True`) | Delta |
|---|---|---|---|
| Basketball (coarse), 1985-2014 | 30 | 30 | 0 |
| Basketball (finer), 1985-2014 | 30 | 30 | 0 |
| Faculty hiring (Business/CS/History) | 3 | 3 | 0 |
| Football England (coarse) | 6 | 6 | 0 |
| Football England (finer) | 6 | 6 | 0 |
| Animal | 1 | 1 | 0 |
| Halo2Beta HeadToHead | 1 | 1 | 0 |
| Halo2Beta (plain, no HeadToHead suffix) | **0 (absent)** | 1 | **+1** |
| Finance | **0 (absent)** | 1 | **+1** |
| ERO (synthetic) | **0 (absent)** | 1 | **+1** |
| **Total** | **77** | **80** | **+3** |

**The dataset-count expansion is exactly 3 datasets (≈4%), not a large multiple.** The three
additions are: `finance` (the only dense/near-complete graph in either suite — genuinely important
qualitatively, per the sibling branch's stress-test findings, but a single dataset), plain
`Halo2BetaData` (distinct from `HeadToHead`), and a synthetic `ERO` instance (which, per the
sibling `journal-supercomputing-major-revision-20260824` branch's own ablation harness, could not
even be loaded through the standard `load_real_data` path in this pass — a genuine gap, not
confidently claimable as "evaluated").

**Recommendation**: the manuscript, and this project's own prior documents (see integration plan),
should not claim a "substantially larger" or multi-fold dataset expansion. The defensible framing
is: *"we evaluate on the same 77 real-world dataset instances as [VK25], plus one dense/
near-complete-graph stress case (`finance`) absent from that work, and identify a currently
unresolved loader gap for a synthetic ERO instance."*

## What IS substantially expanded — baseline comparison set

| | [VK25] | Current repo |
|---|---|---|
| GNN baselines | GNNRank (He et al. 2022) only | GNNRank (+ DIGRAC, per `param_parser.py`'s `all_GNNs` list) |
| Classical ranking baselines | **Zero** — no BTL, SpringRank, RankCentrality, SerialRank, SyncRank, SVD, PageRank, DavidScore, EigenvectorCentrality anywhere in either version of [VK25] | **Ten**: SpringRank, syncRank, serialRank, btl, davidScore, eigenvectorCentrality, PageRank, rankCentrality, SVD_RS, SVD_NRS (`GNNRank-main/src/comparison.py`, confirmed present in `outputs/paper_tables/table4_full_suite.csv`) |

**This is the single largest, cleanest, most defensible empirical expansion available** — going
from zero to ten classical baselines is qualitatively different from a dataset-count tweak and
should be the headline empirical claim, not the dataset count.

## Other experimental-infrastructure dimensions

| Dimension | [VK25] | Current repo |
|---|---|---|
| Trials / repeated runs for variance | None found (single run per dataset, per Table 1) | Some configs use `trials10` naming (per canonical pipeline docs on prior audit branches — not independently re-verified in this pass); determinism is separately tested (`tests/test_audit.py`) rather than relying on repeated-trial variance |
| Runtime budgets | None stated (no timeout mechanism at all) | Explicit `time_limit_sec` throughout; this is new (see `PRIOR_WORK_OVERLAP_MATRIX.md` row 5) but see row 29/`DF03_PRIMARY_THEOREM_VERIFICATION.md` for the guarantee-voiding caveat this introduces |
| Compute-matched analysis | Absent | Referenced (`table5_compute_matched.csv`) but currently **not safely claimable** — a supporting file (`leaderboard_compute_matched.csv`) is missing, causing a pre-existing test failure on both sibling branches (`test_leaderboard_compute_matched_is_subset`) |
| Timeout/coverage analysis | Absent (no timeouts exist to analyze) | Partial — the `finance` timeout is now documented (sibling branch `REVISION_RESULTS.md` §4), but no systematic per-dataset coverage table exists yet across the full suite |
| Statistical analysis (Wilcoxon, bootstrap, Holm) | Absent | **Absent** — this remains an acknowledged gap on the sibling `journal-supercomputing-major-revision-20260824` branch's own `REVISION_EXPERIMENT_PLAN.md` ("Explicitly deferred," Section J of the original task list); do not claim this as done |
| Ablations (phase-level: A-only / +add-back / +refine) | Absent (no ablation concept in [VK25] at all) | Yes — the sibling branch's extended `run_phase_ablation.py`, run across 78/80 datasets | **Genuinely new and substantial** |
| Sensitivity analysis | Absent | Partial — insertion-strategy axis (topo vs. reachability) is directly covered by the ablation above; other hyperparameters (`zero_tol`, `ternary_iters`, refinement budgets) argued theoretically negligible but not empirically swept (`CURRENT_PIPELINE_PSEUDOCODE.md` on the theory-audit branch) | New but partial |
| Density/scale breakdown | Absent (no dense case exists in [VK25] to break down) | Partial — pre-existing `outputs/audits/sparse_regime_robustness.md` plus the new `finance` stress case | New but partial |
| Reproducibility infrastructure (tests, audits, determinism checks, canonical-table validation) | Minimal — a public GitHub repo is linked, no test suite evident from the paper text | Substantial — `tests/`, `outputs/audits/`, `scripts/paper/validate_paper_artifacts.py`, and the 41+ new tests added on the sibling code branch | **Genuinely new and substantial** |

## Summary verdict for this document

The empirical expansion is real but **narrower and different in composition** than previously
stated: essentially flat on dataset *count* (+3/77 ≈ 4%), but large on baseline *breadth* (+10
classical methods from a base of zero) and on *infrastructure* (ablation tooling, reproducibility
tests, ratio/regime audits) that [VK25] does not have in any form. The manuscript's empirical
contribution claim should be phrased around baselines and infrastructure, not dataset count.
