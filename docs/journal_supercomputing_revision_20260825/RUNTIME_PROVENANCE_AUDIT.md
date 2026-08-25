# Runtime Provenance Audit

Date: 2026-08-25
Branch: `jsuper-runtime-provenance-fix-20260825`
Worktree: `/tmp/ranking-jsuper-runtime-provenance-fix`

## 1. Suspected problem

`GNNRank-main/scripts/revision_analysis_20260825/run_reviewer_ablation.py`
(`run_config`, function-level `t0` at line 285) measures `runtime_total_sec` as
`time.time() - t0`, captured at line 460, after data loading, the ranking call, upset
metric computation, and -- for every configuration with `enable_phase_b=True` -- an
additional, diagnostic-only rerun of `ours_mfas_rmfa` (Phase A only) used solely to
compute `permutation_distance_vs_p1`. The suspicion was that `runtime_total_sec` is
therefore a harness/runtime-diagnostic quantity, not the wall time of a single canonical
`OURS-Reach` invocation, for every configuration except Phase-A-only (`A0`).

## 2. Exact code path causing contamination

`run_reviewer_ablation.py`, `run_config()`:

```python
t0 = time.time()                                    # line 285
...
scores, meta = ours_mfas_rmfa(A, **rmfa_params)      # line 360 -- the ONE real invocation
...
if params.get("enable_mincut", False):               # lines 410-416 -- separately, correctly timed
    ...
    t_mc0 = time.time()
    kept_final, ... = _apply_mincut_exchange(...)
    mincut_time = time.time() - t_mc0
...
if params["enable_phase_b"]:                          # lines 432-437 -- THE BUG
    # Run A0 to get P1 baseline scores
    scores_p1, _ = ours_mfas_rmfa(A, enable_phase_b=False, enable_phase_c=False,
                                    refine_naive=False, refine_ratio=False,
                                    time_limit_sec=params["time_limit_sec"], return_meta=True)
else:
    scores_p1 = scores

perm_dist_vs_p1 = _permutation_distance(scores, scores_p1)   # line 441
...
"runtime_total_sec": time.time() - t0,                # line 460 -- captured AFTER the second call
```

`_base_params()` sets `enable_phase_b = True` by default (line 80); only `A0` and the
`C0_A0`/`C1_A0` cycle-selection baselines explicitly set it to `False`. So every
structural-ablation configuration except `A0` (i.e. `A1`, `A2`, `A3`, `A4`, `A5`, `A6`,
and the `R*_A4`/`Z*_A4`/`C*_A4`/`K*_A5` sensitivity variants) executes a second, full
`ours_mfas_rmfa(enable_phase_b=False, ...)` call -- a complete extra Phase-A-only run on
the same graph -- inside the timed window, purely to obtain `scores_p1` for the
permutation-distance sensitivity statistic. That second call's own `meta` (and therefore
its own internal timing) is discarded (`_`); only its cost leaks into `runtime_total_sec`.

## 3. Why `runtime_total_sec` is a harness quantity, not algorithm cost

`ours_mfas_rmfa` (`GNNRank-main/src/ours_mfas.py`) records its own internal, strictly
consecutive timestamps for the one real call whose `meta` is kept:

```python
t0 = time.time()                       # line 759
...
t_after_phase1 = time.time()           # line 769  (end of Phase A)
...
t_after_phase2 = time.time()           # line 804  (end of Phase B / add-back)
...
t_after_phaseC = time.time()           # line 872  (end of Phase C / refinement)
...
"runtime_sec": float(time.time() - t0),          # line 896 -- clean single-invocation total
"time_phase1_sec": float(t_after_phase1 - t0),
"time_phase2_sec": float(t_after_phase2 - t_after_phase1),
"time_phaseC_sec": float(t_after_phaseC - t_after_phase2),
```

`time_phase1_sec + time_phase2_sec + time_phaseC_sec` telescopes exactly to
`t_after_phaseC - t0`, i.e. to that one call's own `runtime_sec` -- the true
single-invocation wall time. `run_reviewer_ablation.py` copies these three fields into
`runtime_phaseA_sec` / `runtime_phaseB_sec` / `runtime_phaseC_sec` (lines 461-463) but
never captures `meta["runtime_sec"]` itself, and instead separately records
`runtime_total_sec = time.time() - t0` from its own outer `t0`, which additionally spans
data loading, the diagnostic rerun (for non-`A0` configs), min-cut (if enabled, itself
correctly timed separately as `runtime_mincut_sec`), and upset-metric computation.
`runtime_total_sec` is therefore a harness-wallclock diagnostic quantity, correct as a
measurement of "how long this one harness call took," but not the cost of a single
`OURS-Reach` invocation.

## 4. Authoritative definition: `runtime_algorithm_sec`

```
runtime_algorithm_sec = runtime_phaseA_sec + runtime_phaseB_sec + runtime_phaseC_sec + runtime_mincut_sec
```

This equals the real invocation's own `runtime_sec` (Phase A + Phase B + Phase C, proven
by telescoping above) plus, for min-cut-enabled configurations, the separately and
correctly timed `runtime_mincut_sec` post-hoc step. Verified execution order (not
assumed): for `A5`/`A6`, `ours_mfas_rmfa` runs Phase A, Phase B, and (if enabled) Phase C
in one call; min-cut then runs afterward, externally, on the returned kept-edge mask
(`run_reviewer_ablation.py` lines 410-418), with its own `t_mc0`/`mincut_time` timer. This
is a real, non-duplicated step of the `A5`/`A6` pipeline, not a diagnostic rerun, so it is
included in `runtime_algorithm_sec`; addition is commutative, so the actual
Phase-A-then-B-then-C-then-mincut order does not change the sum. `A0`/`A2`/`A4` (the
configurations used in Table 8 and Figure 1) never enable min-cut, so
`runtime_mincut_sec = 0` for all of them and `runtime_algorithm_sec` reduces to
`runtime_phaseA_sec + runtime_phaseB_sec + runtime_phaseC_sec`.

`runtime_total_sec` is preserved unmodified in every output file; `runtime_algorithm_sec`
is added as a new, non-destructive trailing column (implemented in
`GNNRank-main/scripts/revision_analysis_20260825/analyze_reviewer_ablation.py`,
function `_add_runtime_algorithm_sec`, called once on `deduped` rows inside `analyze()`).

## 5. Evidence the correction is pure reaggregation (no rerun)

- `outputs/revision_analysis_20260825/reviewer_ablation_scalability/raw_runs.csv` is
  byte-identical before and after the fix (verified by SHA256:
  `47232ac9661f04615fd0b0a24f49a22b3f5ec0c0f9f1546fb89629543f58ca5f`, unchanged). No
  ranking algorithm was re-executed.
- `analyze_reviewer_ablation.py` was re-run as pure Python post-processing over the
  unchanged `raw_runs.csv` (`python3 analyze_reviewer_ablation.py`), regenerating derived
  CSVs deterministically ("Analyzed 1009 raw -> 1005 deduped rows" on both the original
  and the corrected run).
- Every derived CSV that changed (`structural_ablation.csv`,
  `structural_ablation_summary.csv`, `cycle_selection_sensitivity.csv`,
  `legacy_pass_sensitivity.csv`, `mincut_budget_sensitivity.csv`,
  `refinement_sensitivity.csv`, `zero_tol_sensitivity.csv`) was diffed column-by-column
  against its pre-fix version: every pre-existing column (including `upset_simple`,
  `upset_naive`, `upset_ratio`, `removed_final_weight`, `n`, `m`, W/T/L-relevant fields,
  and `runtime_total_sec` itself) is byte/numerically identical; the only change is the
  new trailing `runtime_algorithm_sec` (and, in the summary file,
  `mean_runtime_algorithm_sec` / `median_runtime_algorithm_sec`) column. Verified
  programmatically (0 mismatches on old columns across all six files).
- `outputs/revision_analysis_20260825/canonical_reachability_baseline_comparison/`
  (Table 6's source) was not touched at all.

## 6. Quantitative old-vs-corrected values

### Non-Finance, `structural_ablation.csv`

| Config | n | mean `runtime_total_sec` (old, contaminated) | mean `runtime_algorithm_sec` (corrected) | median `runtime_total_sec` (old) | median `runtime_algorithm_sec` (corrected) |
|---|---:|---:|---:|---:|---:|
| A0 (Phase A only) | 77 | 0.1737 | 0.1435 | 0.1749 | 0.1472 |
| A1 (legacy topo add-back) | 33 | 0.2762 | 0.1271 | -- | -- |
| A2 (exact reachability add-back) | 77 | 0.4266 | 0.2519 | 0.4140 | 0.2413 |
| A3 (legacy full pipeline) | 33 | 0.3784 | 0.2265 | -- | -- |
| A4 (OURS-Reach) | 77 | 0.5420 | 0.3645 | 0.5687 | 0.3806 |

`A0`'s own reduction (0.1737 to 0.1435, about 17%) is *not* the diagnostic-rerun bug (A0
never triggers it, `enable_phase_b=False`); it is the removal of generic harness overhead
(data loading + upset-metric computation) from the manuscript-facing quantity, applied
uniformly for definitional consistency (Section 4). `A1`/`A2`/`A3`/`A4`'s much larger
proportional reductions (55%, 41%, 40%, 33%) are the diagnostic-rerun bug: independently
verified by computing, per dataset, `(runtime_total_sec - sum_of_own_phase_columns) -
own_runtime_phaseA_sec`, which for `A2` averages 0.0309 and for `A4` averages 0.0302,
matching `A0`'s own baseline harness-overhead diff (0.0302) almost exactly -- i.e. once
one extra Phase-A cost is subtracted out, the remaining "diff" for every contaminated
config matches A0's clean baseline overhead to three significant figures.

### Finance (`raw_runs.csv`, single rows, `FINANCE_*` configs, 600s Phase-A budget)

| Config | status | `runtime_total_sec` (raw harness) | `runtime_phaseA_sec` | `runtime_phaseB_sec` | `runtime_phaseC_sec` | `runtime_algorithm_sec` (corrected) | `break_reason` |
|---|---|---:|---:|---:|---:|---:|---|
| FINANCE_A0 | complete | 612.5528 | 600.0097 | 0.0002 | 0.5207 | 600.5306 | `phase_b_disabled` |
| FINANCE_A2 | complete | 1214.7641 | 600.0108 | 1.7833 | 0.5114 | 602.3055 | `time_limit` |
| FINANCE_A4 | complete | 1214.5739 | 600.0108 | 1.7527 | 0.5143 | 602.2778 | `time_limit` |
| FINANCE_A6 | `TIMEOUT_HARD_WALLCLOCK` | 1800.0988 | (n/a) | (n/a) | (n/a) | not computable | `hard_wallclock_timeout` |

`FINANCE_A2`'s and `FINANCE_A4`'s raw harness gap (`1214.76 - 602.31 = 612.46s`;
`1214.57 - 602.28 = 612.30s`) matches `FINANCE_A0`'s own total runtime (612.55s) to
within 0.3s -- direct, dataset-specific confirmation that the "extra" ~612s in the raw
`FINANCE_A2`/`FINANCE_A4` harness timer is one additional Phase-A-only execution on
Finance (itself capped at the same 600s budget, plus its own ~12s of data-load/metric
overhead), not a real second stage of the pipeline.

`FINANCE_A6` was killed by the *outer* hard-wallclock guard
(`_run_config_with_hard_wallclock`, `wall_sec=1800`) before it returned any `meta`, so no
phase breakdown exists for that row and `runtime_algorithm_sec` cannot be computed for it
from existing outputs (this is not itself a scientific rerun requirement -- see Section 9).

## 7. Affected manuscript artifacts

| Artifact | Old value(s) | Corrected value(s) | Classification |
|---|---|---|---|
| Figure 1 (`fig_runtime_vs_edges.pdf`) | y-data = `runtime_total_sec`, range 0.011-1.21s | y-data = `runtime_algorithm_sec`, range 0.0087-0.83s | NEEDS_RECOMPUTATION (fixed) |
| Table 8, Panel (a) mean runtime | A0 0.148 / A1 0.276 / A3 0.378 | A0 0.122 / A1 0.127 / A3 0.227 | NEEDS_RECOMPUTATION (fixed) |
| Table 8, Panel (b) mean runtime | A0 0.174 / A2 0.427 / A4 0.542 | A0 0.144 / A2 0.252 / A4 0.364 | NEEDS_RECOMPUTATION (fixed) |
| Section 3.5 (Finance Stress Case) | "612.6s (Phase A ~600.0s); ... hit an internal time limit at ~1214.8/1214.6s" (number misattributed as algorithm cost) | distinguishes harness (~612.6s) vs. algorithm (~600.5s) for A0; algorithm ~602.3s for A2/A4; explicitly explains the 1214.8/1214.6s harness figures as containing the diagnostic rerun | NEEDS_TEXT_ONLY_CORRECTION (fixed) |
| Section 3.6 (Scalability) | "0.01-1.2s (median ~0.57s)" | "0.01-0.83s (median ~0.38s)", labeled single-invocation algorithm wall time | NEEDS_TEXT_ONLY_CORRECTION (fixed) |
| Response to reviewers, R1 Comment 2 | quoted the same "0.01-1.2s (median ~0.57s)" | corrected to "0.01-0.83s (median ~0.38s)"; added one sentence naming the harness/algorithm distinction | NEEDS_TEXT_ONLY_CORRECTION (fixed) |
| Cover letter | no specific runtime numbers cited | -- | UNAFFECTED |
| Abstract, Conclusion | qualitative only ("slower than most lightweight classical estimators", "substantially faster than archived trained GNNRank runs") | unchanged | UNAFFECTED |

## 8. Unaffected artifacts

- **Table 6** (`tab:runtime_wtl`, "Runtime and Coverage") and its supporting Section 3.4
  prose: sourced from
  `outputs/revision_analysis_20260825/canonical_reachability_baseline_comparison/a4_gnnrank_metrics.csv`,
  generated by `run_a4_gnnrank_metrics.py`. That script contains exactly one call to
  `ours_mfas_rmfa` per dataset (no diagnostic permutation-distance rerun of any kind), so
  its `runtime_total_sec` is already a clean single-invocation quantity. Independently
  verified: `a4_gnnrank_metrics.csv`'s median non-Finance `runtime_total_sec` is
  `0.348641`, which reproduces every `median_ours` and every `median_paired_ratio` value
  in `e1_runtime_wtl.csv` used by Table 6 (SpringRank `5.6699935... -> 5.7x`, DavidScore
  `107.609... -> 108x`, SVD_NRS `59.565... -> 60x`, BTL `7.9307... -> 7.9x`, PageRank
  `169.527... -> 170x`, SyncRank `0.8006... -> 0.80x`, SerialRank `32.326... -> 32x`,
  RankCentrality `17.031... -> 17x`, DIGRAC `0.02247... -> 0.022x`, ib
  `0.02738... -> 0.027x`) to the precision printed in the manuscript. **Table 6 was not
  modified.** As an independent sanity check, its clean median (0.3486s) is close in
  order of magnitude to the ablation pipeline's now-corrected `median_runtime_algorithm_sec`
  for A4 (0.3806s) -- both well below the old, contaminated `median_runtime_total_sec`
  (0.5687s), consistent with the diagnosis.
- Response-to-reviewers passages R2 Comment 3, R3 Comment 3, R3 Comment 4, R4 Comment 4
  cite only Table 6-sourced ratios (5.7x, 170x, 37-45x, etc.) or make qualitative
  statements; none quote a Table-8/ablation-pipeline runtime number, so none needed
  correction.
- Dataset denominators (80 intended / 78 loadable / 77-78/78-78/61-78 coverage),
  quality metrics (`upset_simple`, `upset_naive`, `upset_ratio`), W/T/L counts, and
  Holm/Wilcoxon p-values throughout the manuscript: unchanged (Section 5 above).

## 9. Interpretation of surviving large harness times

`1214.8`/`1214.6`/`1800.1` remain in the manuscript (Section 3.5) but are now explicitly
and correctly labeled as raw per-run harness-timer readings, not algorithm cost:

- `1214.8`/`1214.6` are explained as containing a diagnostic Phase-A-only rerun and are
  explicitly excluded from the stated algorithm wall time (~602.3s).
- `1800.1` remains accurate as a description of a genuine non-completion event: the
  `FINANCE_A6` process was killed by an outer hard-wallclock guard before producing a
  ranking. This claim ("hard wall-clock timeout... without a finished ranking") does not
  assert a completed algorithm cost and is not contradicted by the diagnostic-rerun
  finding -- if anything, the diagnostic rerun is a plausible *contributor* to why that
  configuration did not finish within 1800s, which is consistent with, not undermined by,
  the corrected picture. No claim about `FINANCE_A6`'s number was changed.

## 10. Explicit statement

Diagnostic harness overhead (the extra Phase-A-only rerun executed solely to compute
`permutation_distance_vs_p1`, and generic data-loading/metric-computation overhead) is
**not** reported anywhere in the corrected manuscript as `OURS-Reach` algorithm cost.
Every manuscript-facing runtime number in Figure 1, Table 8, and Sections 3.5-3.6 is now
either `runtime_algorithm_sec` (Phase A + Phase B + Phase C, plus min-cut where
applicable) or is explicitly labeled as a harness/diagnostic quantity when quoted for
transparency.

## 11. Sources

| Quantity | Script/source | Source CSV | SHA256 / notes |
|---|---|---|---|
| Contamination diagnosis | `GNNRank-main/scripts/revision_analysis_20260825/run_reviewer_ablation.py` (`run_config`, lines 285-468) | -- | script SHA256 `9477cc8aeefcf1e65c35b269323a407616a3d1549943906d7188de8a31c7b258`; code inspection |
| Single-invocation phase timing proof | `GNNRank-main/src/ours_mfas.py` (`ours_mfas_rmfa`, lines 736-905) | -- | source SHA256 `35483d37fc7de5dd62b1a00b7f25abf92dde7827ed9176c7cfd59b53feab37a0`; code inspection |
| `runtime_algorithm_sec` derivation | `GNNRank-main/scripts/revision_analysis_20260825/analyze_reviewer_ablation.py` (`_add_runtime_algorithm_sec`) | `outputs/revision_analysis_20260825/reviewer_ablation_scalability/raw_runs.csv` | script SHA256 `93b54fbe82729fb4f217795a73b9721fc06ebbc3b9b8d85bae7496833e878710`; raw CSV SHA256 `47232ac9661f04615fd0b0a24f49a22b3f5ec0c0f9f1546fb89629543f58ca5f`, unchanged; pure reaggregation |
| Table 8 values | matched-support aggregation over the corrected structural output | `structural_ablation.csv`, `r1_common_support_stage_ablation.csv`, `r1_common_support_stage_ablation_summary.csv` | structural SHA256 `fe30256b31ae7d8a43dbd268d6125ed0611c96e0a2555ce578822163afdf4e32`; detail SHA256 `dd37f207f3859c05434b863047703a595c520d22c5d81004485bc7d5511ac8f4`; summary SHA256 `8ada08874741373ae53244dec55420292e7903d0083d582f86f6aac78fc07228`; matched-support panels, see `FINAL_R1_ABLATION_NUMERICAL_AUDIT.md` |
| Figure 1 | `GNNRank-main/scripts/revision_analysis_20260825/generate_pass3_figures.py` (`fig_runtime_vs_edges`) | `structural_ablation.csv`, 77 non-Finance A4 rows, columns `dataset`, `m`, `runtime_algorithm_sec` | script SHA256 `058d556ca10411a5af1d9869e52bc72bb014c6787d8e6e9e7cb83ea0bf6eff95`; source-point count `77`; source-point SHA256 `0955704865c99ede3530b3f76e429a43478842686b1c1c7bd4b80144f99c0a12` |
| Finance timing | direct row inspection | `outputs/revision_analysis_20260825/reviewer_ablation_scalability/raw_runs.csv`, `FINANCE_A0`/`FINANCE_A2`/`FINANCE_A4`/`FINANCE_A6` rows | single completed rows for A0/A2/A4; A6 hard timeout row has no phase metadata; no rerun |
| Table 6 (verified clean) | `GNNRank-main/scripts/revision_analysis_20260825/run_a4_gnnrank_metrics.py` | `a4_gnnrank_metrics.csv`, `e1_runtime_wtl.csv` | `a4_gnnrank_metrics.csv` SHA256 `96d0d4958807feea0b6a8c23ae06f0b8529de7b195add5bb7874bc01d0219f5b`; `e1_runtime_wtl.csv` SHA256 `d19528093a98336f1dc0aef8a3b7eb53f4126524e3742d9fc14df2ae31e2bb06`; independent pipeline, not modified |

## 12. Verdict

**RUNTIME_PROVENANCE = PASS**

The suspected contamination was confirmed real, exactly localized in code, precisely
quantified from already-completed raw outputs with no scientific rerun, and corrected
non-destructively (new `runtime_algorithm_sec` field; `runtime_total_sec` preserved
unmodified everywhere). All manuscript-facing artifacts identified as affected (Figure 1,
Table 8, Sections 3.5-3.6, the corresponding response-letter passage) have been corrected
and rebuilt. Table 6 was independently verified to already use a clean, single-invocation
runtime measurement and required no change. This verdict covers only the runtime
provenance issue; it is not a statement about overall manuscript submission readiness.
