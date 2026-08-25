# Revision Experiment Plan (frozen before inspecting outcomes)

Date: 2026-08-24
Branch: `journal-supercomputing-major-revision-20260824`

This plan was fixed *before* running `GNNRank-main/scripts/paper/run_phase_ablation.py`
in its extended form, to avoid post-hoc / cherry-picked dataset selection.

## Dataset universe

Source of truth: `outputs/derived/dataset_inventory.csv` (the canonical
80-dataset suite manifest already present in the repository), filtered to
`in_80_suite == True`.

**Selection rule (fixed in advance):** run on *all* 80 canonical datasets
except two with a documented, mechanical loader blocker (not a judgment call
about the datasets themselves):

1. `_AUTO/Basketball_temporal__1985adj` — already excluded from the canonical
   80-suite by prior repository work (duplicate/legacy artifact); confirmed
   present in the manifest with `in_80_suite=False`.
2. `ERO/p5K5N350eta10styleuniform` — the only dataset in the suite whose
   on-disk artifacts are pickled `torch_geometric.data.Data` train/test splits
   rather than a bare `scipy.sparse` adjacency `.npz`. `preprocess.load_real_data()`
   cannot load it, and reconstructing an adjacency matrix from the split would
   require re-implementing part of `generate_data.py`'s edge_index ->
   sparse-matrix logic — out of scope for this pass. Recorded as a blocker
   (see `run_phase_ablation.py`'s `EXCLUDED_DATASETS` and its printed load
   failures), not silently dropped.

This yields **79 datasets** run, covering (per `outputs/derived/dataset_inventory.csv`
family labels): Basketball_coarse (30), Basketball_finer (30), Faculty (3),
Football_coarse (6), Football_finer (6), Animal (1), Finance (1), Halo (2) —
i.e. every family in the manifest at full within-family coverage. This is the
"prefer full feasible 80-dataset suite" option from the task instructions,
made feasible by the fact that Phase A+B+C together run in well under one
second per dataset on this hardware (measured ad hoc: `Basketball_temporal/2010`,
n=347, m=4133, full A+B+C+refine < 0.3 s) — a stratified subsample was not
necessary.

Four dataset names (`Dryad_animal_society`, `finance`, `Halo2BetaData`,
`Halo2BetaData/HeadToHead`) fail `load_real_data()`'s default path
construction (it expects `<name>adj.npz`; these four are stored as
`<name>/adj.npz`, one directory level down). `run_phase_ablation.py`'s
`_robust_load_real_data()` falls back to the `<name>/adj.npz` layout for any
dataset that fails the default lookup. This is a pure path-resolution fix, not
a change to what data is loaded (verified by shape/nnz inspection during
preflight).

## Phase-mode matrix (fixed in advance)

| Mode | Phase A | Phase B | Phase C |
|------|---------|---------|---------|
| A0 | local-ratio | disabled | disabled |
| A1_topo | local-ratio | legacy topo add-back, INS3 (3 passes) | disabled |
| A2_topo | local-ratio | legacy topo add-back, INS3 | ratio refinement (2 passes, 10s budget) |
| B1_reach | local-ratio | reachability add-back (single pass) | disabled |
| B2_reach | local-ratio | reachability add-back (single pass) | ratio refinement (2 passes, 10s budget) |

`time_limit_sec=300` per run (global wall-clock budget passed to
`ours_mfas_rmfa`); this matches the order of magnitude used elsewhere in the
repo's audit scripts and is far above the measured per-dataset runtime.

## Metrics recorded per (dataset, phase_mode)

`upset_simple`, `upset_ratio`, `upset_naive` (all recomputed directly from the
returned score vector and the loaded adjacency matrix, not read from any
cached table), `runtime_sec` and its phase breakdown, `removed_phaseA`,
`kept_after_phaseA`, `kept_final`, `edges_restored`, `reinserted_per_pass`,
`break_reason`, and (reach modes only) `reach_checked`, `reach_inserted`,
`reach_rejected_reachable`, `reach_dense_matrix_used`. Additionally,
`permutation_changed_vs_A_only`: whether `argsort(-scores)` differs from the
A0 permutation for the same dataset.

## Comparisons to report (fixed in advance)

1. Edges restored: `A1_topo` vs `B1_reach`, suite-wide totals and per-dataset
   sign (does reach restore strictly more edges, on how many datasets).
2. Ranking-changed-vs-A0 rate: `A1_topo` vs `B1_reach`.
3. Paired `upset_simple` deltas (mean, median, win/tie/loss counts) for:
   `A1_topo` vs `A0`, `B1_reach` vs `A0`, `B1_reach` vs `A1_topo`, and the same
   three comparisons with Phase C enabled (`A2_topo`, `B2_reach`).
4. Runtime overhead: median/max runtime per mode.
5. Per-family breakdown of `B1_reach` vs `A1_topo` upset_simple deltas, to
   check the reviewer-relevant regimes (sparse vs. denser families) called out
   in the task instructions.

## Explicitly deferred in this pass (recorded, not hidden)

- **Section F (exchange/escape mechanism, `OURS_MFAS_REACH_EXCHANGE`)**: not
  implemented in this pass. Rationale: the task instructions gate this behind
  first establishing whether plain reachability add-back already materially
  changes rankings/quality (Section O's stopping-point question). Implementing
  a min-cut-based exchange search before that evidence exists risks building
  machinery for a problem that may not be the binding constraint. Status:
  **prototype not started**; `REVISION_RESULTS.md` will state explicitly
  whether the evidence from this pass justifies it as the next step.
- **Sections G-L (classical-baseline value verification, direct runtime
  comparisons against all ten named baselines, timeout-safe common-subset
  analysis, Wilcoxon/bootstrap/Holm statistical testing, family-aware
  robustness, scale/density stratification, sensitivity grids)**: the
  reachability-add-back question was designated the highest-priority item in
  the task instructions ("The highest-priority objective is to determine
  whether we can replace or augment..."). Sections G-L each require their own
  substantial, separately-reviewable analysis scripts and are recorded here as
  the next work items rather than attempted superficially in the same pass.
  `REVISION_RESULTS.md`'s closing section lists them as the recommended next
  experiments, per the task's own "Exact recommended next experiment"
  requirement.
