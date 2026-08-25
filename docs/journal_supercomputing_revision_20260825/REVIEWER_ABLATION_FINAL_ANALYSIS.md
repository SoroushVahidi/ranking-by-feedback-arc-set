# Reviewer Ablation Final Analysis


> **SUPERSEDED NOTE (2026-08-25, runtime-provenance fix):** the raw `1214.76`/`1214.57` Finance timings cited below are per-run harness-timer readings, not single-invocation `OURS-Reach` algorithm cost -- each contains a diagnostic Phase-A-only rerun (used only to compute a permutation-distance sensitivity statistic) that inflates the reading by roughly one extra Phase-A execution (~612s on Finance). The corrected algorithm-only Finance timings are ~600.5s (A0), ~602.3s (A2/A4); `1800.10s` (A6, hard-wallclock timeout without a finished ranking) is unaffected. See `RUNTIME_PROVENANCE_AUDIT.md` for the full analysis.
Date: 2026-08-25  
Branch: `jsuper-reviewer-ablation-scale-20260825`  
Config hash: `712779aad638f619`  
Analysis script: `GNNRank-main/scripts/revision_analysis_20260825/analyze_reviewer_ablation.py`

This document follows `EXPERIMENT_INTERPRETATION_RULES.md` and
`ABLATION_MANUSCRIPT_TABLE_PLAN.md`. Negative and null findings are reported.

**Status note:** Aggregate tables are computed from **1009/1009** terminal raw
rows. FINANCE_A6 terminated as `TIMEOUT_HARD_WALLCLOCK` at ≈1800.10 s.
Non-finance primary pairwise statistics are unchanged vs the 1008-row snapshot.

---

## 1. Protocol

- Layer 1 (33 datasets): full structural A0–A6 + all sensitivity grids  
- Layer 2 (45 datasets): A0, A2, A4, A6 only  
- Finance stress: FINANCE_A0/A2/A4/A6 with internal `time_limit_sec=600`  
- Checkpoint/resume by `(dataset, config)` + matching config hash  
- Metrics: structural (removed weight, restored edges, min-cut), ranking
  (upset_simple / ratio / naive), runtime by stage  
- Pairwise stats: paired W/T/L, mean/median Δ (B−A), bootstrap 95% CI,
  Wilcoxon, Cliff’s δ; Holm on the five primary comparisons  
- Upset/removed-weight/runtime: **lower is better**. Restored/min-cut gain:
  **higher is better**.

## 2. Completion / failures

| Quantity | Value |
|---|---|
| Planned runs | 1009 |
| Terminal raw rows | 1009 |
| Deduped for stats | 1005 |
| Duplicate groups | 4 (`Basketball_temporal/finer2012` in Layer1∩Layer2) |
| Recorded errors | 0 |
| Missing | 0 |

Duplicate audit (`duplicate_run_audit.csv`): scientific metrics agree;
runtime jitter only; dedup rule = keep first raw row.

## 3. Structural ablation

Unpaired Layer medians (descriptive; **paired** tests are authoritative):

| Config | n | med upset_simple | med upset_ratio | med removed_w | med restored | med mincut_gain | med algorithm runtime (s) |
|---|---:|---:|---:|---:|---:|---:|---:|
| A0 | 77 | 0.206 | 0.451 | 11341 | 0 | 0 | 0.15 |
| A1 | 33 | 0.154 | 0.459 | 6382 | 385 | 0 | 0.14 |
| A2 | 77 | 0.211 | 0.446 | 5947 | 522 | 0 | 0.24 |
| A3 | 33 | 0.136 | 0.423 | 6382 | 385 | 0 | 0.25 |
| A4 | 77 | 0.211 | 0.381 | 5947 | 522 | 0 | 0.38 |
| A5 | 33 | 0.136 | 0.465 | 5250 | 445 | 47 | 2.91 |
| A6 | 77 | 0.198 | 0.429 | 5903 | 521 | 57 | 3.92 |

### Primary paired comparisons (Holm-adjusted family)

| Comparison | Metric (orientation) | n | W/T/L (B) | median Δ | mean Δ | Wilcoxon p | Holm p | CI excludes 0? |
|---|---|---:|---|---:|---:|---:|---:|---|
| A0 vs A2 | upset_simple (↓) | 77 | 76/0/1 | −0.0166 | −0.0125 | 4.7e−13 | 2.4e−12 | yes |
| A1 vs A2 | upset_simple (↓) | 33 | 32/0/1 | −0.0159 | −0.0065 | 7.5e−7 | 1.5e−6 | no* |
| A2 vs A5 | removed_final_weight (↓) | 33 | 26/7/0 | −47 | −98.7 | 8.3e−6 | 8.3e−6 | yes |
| A4 vs A6 | removed_final_weight (↓) | 77 | 66/11/0 | −57 | −119.7 | 1.6e−12 | 4.9e−12 | yes |
| A0 vs A4 | upset_simple (↓) | 77 | 76/0/1 | −0.0169 | −0.0129 | 4.7e−13 | 2.4e−12 | yes |

\*A1 vs A2: W/T/L and median favor A2 strongly; bootstrap CI for the mean
crosses zero (heavy-tailed mean). Per rules: **directional material improvement
with significant Wilcoxon; mean-CI not decisive**.

**Interpretation**

1. **A0→A2 (reachability):** material improvement on upset_simple (76/77).  
2. **A1→A2 (exact reach vs topo):** A2 wins 32/33; topo proxy is not sufficient.  
3. **A2→A5 (min-cut):** material structural gain (removed weight ↓; 26 wins, 0 losses).  
4. **A4→A6 (min-cut after refine):** material structural gain (66/77 wins, 0 losses).  
5. **A0→A4 (full pipeline):** material upset_simple gain matching reachability;
   refinement further improves **upset_ratio** (A2 med 0.446 → A4 med 0.381).

Runtime: manuscript-facing values now use `runtime_algorithm_sec`, not the
per-run harness timer. Reachability/refinement add sub-second median cost on
Layer-1/2 (non-finance); min-cut adds about 3-4s median.

## 4. Cycle selection

| Pair | Metric | n | W/T/L | median Δ | p | Notes |
|---|---|---:|---|---:|---:|---|
| C0_A0 vs C1_A0 | upset_simple | 33 | 22/0/11 | −0.00215 | 0.18 | not significant |
| C0_A4 vs C1_A4 | upset_simple | 33 | 25/2/6 | −0.00131 | 0.0048 | CI excludes 0 |

**Classification: MATERIALLY_SENSITIVE** on the A4 path (small but significant
upset_simple shift); A0 path directional but not significant. Cycle rule is
not inert under full refinement—report honestly; effect size remains small
(|median Δ|≈1e−3).

## 5. zero_tol sensitivity

Z12 / Z15 / Z18 on A4 (n=33):

- upset_simple vs Z15: almost all ties (31–32/33); median Δ = 0  
- removed_final_weight vs Z12: 31 ties; mean Δ ≈ −1 (noise)

**Classification: STABLE** (numerically inert on this suite).

## 6. Refinement sensitivity

| Contrast | upset_simple W/T/L | median Δ | Notes |
|---|---|---:|---|
| R2 vs R0 | 0/13/20 (R2 better) | R0 worse by ~6.6e−5 med | disabling refine hurts |
| R2 vs R1 | 0/30/3 | ~0 | nearly saturated at R1 |
| R2 vs R3 | 1/32/0 | ~0 | 2× budget adds nothing material |

**Classification: MILDLY_SENSITIVE.** Refinement **saturates** by R1/R2;
R3 does not help.

## 7. Legacy insertion passes

| Config | med restored edges | med upset_simple |
|---|---:|---:|
| P0 | 0 | 0.154 |
| P1 | 370 | 0.154 |
| P2 | 383 | 0.154 |
| P3 | 385 | 0.154 |

- P0→P1: restores many edges (topo add-back on); ranking median unchanged.  
- P1→P2: +2 median restored edges; upset_simple median Δ=0 (23/33 ties; small
  mean improvement).  
- P2→P3: +0 median restored; 32/33 upset ties.

**Answer to reviewer (INS1/2/3):** Extra passes beyond P1 restore only a handful
of edges and do **not** materially change ranking metrics. Multipass topo
insertion is weak as a quality lever; reachability (A2) / min-cut (A5/A6) are
the substantive alternatives.

Auto label vs P0 is MATERIALLY_SENSITIVE (P0 vs P1). **P1/P2/P3 among themselves:
STABLE to MILDLY_SENSITIVE.**

## 8. Min-cut K sensitivity

| Config | med attempts | med accepted | med gain | med runtime |
|---|---:|---:|---:|---:|
| K20_A5 | 20 | 9 | 33 | 2.84 |
| K50_A5 | 27 | 10 | 40 | 2.76 |
| K100_A5 | 27 | 10 | 41 | 2.96 |

K20→K50: small additional gain (8/33 wins, 25 ties).  
K50→K100: nearly flat (4/33 wins, 29 ties).

**Classification: MILDLY_SENSITIVE; saturates by K≈50.**

## 9. Family-aware results

See `family_summary.csv` and `family_aggregated_pairwise.csv`.  
Basketball dominates n; family-aggregated (one median per family) is the
supplementary check. No family-level Wilcoxon (per-family n inadequate).

## 10. Scalability

Non-finance A0/A2/A4/A6:

- n in [20, 602], A4 algorithm runtime in ~0.01-0.83s, median ~0.38s
- Stage medians (A4): Phase A ~0.16s, Phase B ~0.09s, Phase C ~0.12s  
- A6 min-cut median ~3.5s (dominates incremental cost)

No theoretical curve fitted. Empirical observation only: suite completes
comfortably for n≤602 moderate density.

## 11. Finance stress

| Config | Terminal class | algorithm runtime (s) | harness diagnostic / hard wall (s) | break_reason |
|---|---|---:|---:|---|
| FINANCE_A0 | SUCCESS* | 600.53 | 612.55 | phase_b_disabled (Phase A used full 600.01 s) |
| FINANCE_A2 | INTERNAL_TIME_LIMIT | 602.31 | 1214.76 | time_limit |
| FINANCE_A4 | INTERNAL_TIME_LIMIT | 602.28 | 1214.57 | time_limit |
| FINANCE_A6 | **TIMEOUT_HARD_WALLCLOCK** | not computable | **1800.10** | hard_wallclock_timeout |

\*A0 completed with Phase-A budget exhaustion; no Phase B by design.  
Wall times for A2/A4 exceed 600 s because the harness also re-runs Phase-A-only
for permutation distance; they are diagnostic harness readings, not completed
algorithm cost. FINANCE_A6 did not finish within the predefined 1800 s hard
wall-clock; this is a **hard scalability failure** for the full
reachability+refinement+min-cut finance stress case—not a silent omission.
We make **no universal scalability claim**. Finance remains the documented
dense/large-n stress boundary.

## 12. Statistical analysis

- Primary Holm family: A0→A2, A2→A5, A4→A6, A0→A4 all significant after Holm.  
- A1→A2: Wilcoxon significant; mean bootstrap CI includes 0.  
- Timeouts excluded from pairwise metric n (finance excluded from primary n).  
- Sample dominated by Basketball—qualify manuscript claims accordingly.

## 13. Reviewer implications

| Reviewer theme | Finding |
|---|---|
| Stage contributions | Reachability and refinement each contribute; topo proxy insufficient |
| INS1/2/3 | Extra passes beyond first add-back are ineffective for ranking |
| Min-cut | Clear structural gain; K saturates ~50 |
| Cycle selection | Small but detectable under A4—disclose |
| zero_tol | Stable |
| Scalability | Fine on suite; finance is the boundary |
| Robustness | Completion matrix transparent; finance timeouts explicit |

## 14. Manuscript-safe conclusions

1. Exact reachability add-back materially improves upset_simple vs Phase A and
   vs legacy topo add-back.  
2. Full pipeline (A4) improves upset_ratio beyond A2.  
3. Min-cut exchange improves the structural objective beyond safe restoration,
   with or without refinement.  
4. Legacy multipass insertion does not justify INS2/INS3 as quality mechanisms.  
5. zero_tol is stable; refinement and K-budgets saturate quickly.  
6. Finance is a documented stress timeout boundary—not a silent omission.
   FINANCE_A6 specifically hard-timed-out at 1800 s.

## 15. Limitations

- FINANCE_A6 is a hard wall-clock timeout (no ranking metrics produced).  
- Single deterministic run per (dataset, config)—appropriate for OURS.  
- Basketball-dominated sample.  
- finer2012 Layer1/Layer2 duplication (audited, deduped for stats).  
- Permutation-distance helper doubles Phase-A work on finance configs.  
- No per-edge attribution; no full-table weighted FAS vs all baselines.
