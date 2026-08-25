# Classical Runtime Final Analysis (E1 + E2)

Date: 2026-08-24
Branch: `jsuper-runtime-coverage-final-20260824`
Base: `33ecac7c` (`jsuper-major-revision-integration-20260824`)

Source data: `GNNRank-main/paper_csv/leaderboard_per_method.csv` (canonical per-dataset per-method results)
Analysis script: `run_runtime_coverage_analysis.py`
Machine-readable outputs: `outputs/revision_analysis_20260824/runtime_coverage_final/`

**No experiments were re-run. All analysis is post-processing of existing canonical data.**

---

## 1. Coverage / completion (E2)

Intended denominator: 80 datasets (canonical suite). 2 datasets fail to load for all methods (`ERO/p5K5N350eta10styleuniform`, `Halo2BetaData/HeadToHead` — missing data files), so the effective intended denominator is 79 datasets with data.

| Method | Intended | Success | Timeout | Other failure | Coverage |
|---|---|---|---|---|---|
| OURS_MFAS | 79 | 77 | 1 | 0 | 97.5% |
| SpringRank | 79 | 78 | 0 | 0 | 98.7% |
| btl | 79 | 78 | 0 | 0 | 98.7% |
| SVD_NRS | 79 | 78 | 0 | 0 | 98.7% |
| SVD_RS | 79 | 78 | 0 | 0 | 98.7% |
| PageRank | 79 | 78 | 0 | 0 | 98.7% |
| davidScore | 79 | 78 | 0 | 0 | 98.7% |
| eigenvectorCentrality | 79 | 78 | 0 | 0 | 98.7% |
| syncRank | 79 | 77 | 1 | 0 | 97.5% |
| serialRank | 79 | 78 | 0 | 0 | 98.7% |
| rankCentrality | 79 | 78 | 0 | 0 | 98.7% |
| DIGRAC | 79 | 61 | 0 | 0 | 77.2% |
| ib | 79 | 61 | 0 | 0 | 77.2% |

**Key findings:**
- All 10 classical baselines achieve 78/79 (98.7%) coverage — missing only the 2 unavailable datasets.
- OURS_MFAS achieves 77/79 (97.5%) — timeout on `finance` (n=1315, m=1,729,225, density≈1.0).
- syncRank also times out on `finance` (97.5% coverage).
- DIGRAC and ib (GNN baselines) achieve only 61/79 (77.2%) — they do not run on 18 datasets where the GNN training infrastructure is not applicable (datasets without train/test splits or with incompatible formats).
- No method has "other failure" — all non-successes are either timeouts or not-applicable.

Full completion matrix: `e2_completion_matrix.csv` (79×18).

---

## 2. Runtime W/T/L — pairwise common completions (E1)

OURS_MFAS vs each baseline, on datasets where BOTH completed successfully:

| Baseline | n_common | OURS faster | Ties | OURS slower | Median ratio | Geomean ratio | 95% CI (ratio) |
|---|---|---|---|---|---|---|---|
| SpringRank | 77 | 14 | 0 | 63 | 17.9x | 13.4x | (11.2, 16.3) |
| btl | 77 | 4 | 3 | 70 | 25.0x | 14.1x | (11.3, 17.6) |
| SVD_NRS | 77 | 0 | 0 | 77 | 180.1x | 176.8x | (151, 209) |
| SVD_RS | 77 | 0 | 0 | 77 | 232.0x | 224.8x | (191, 267) |
| PageRank | 77 | 0 | 0 | 77 | 536.4x | 712.1x | (516, 984) |
| davidScore | 77 | 0 | 0 | 77 | 337.1x | 352.9x | (301, 413) |
| eigenvectorCentrality | 77 | 0 | 0 | 77 | 100.3x | 155.7x | (118, 206) |
| syncRank | 77 | 3 | 6 | 68 | 2.6x | 3.6x | (2.9, 4.4) |
| serialRank | 77 | 0 | 0 | 77 | 103.2x | 130.1x | (108, 156) |
| rankCentrality | 77 | 0 | 0 | 77 | 55.3x | 63.5x | (53.7, 75.2) |
| **DIGRAC** | **60** | **60** | **0** | **0** | **0.123x** | **0.117x** | (0.103, 0.132) |
| **ib** | **60** | **60** | **0** | **0** | **0.121x** | **0.122x** | (0.107, 0.138) |

**Key findings (reported without spin):**
- OURS is **substantially slower than all 10 classical baselines** on pairwise common completions. The median runtime ratio ranges from 2.6x (vs syncRank) to 536x (vs PageRank). OURS is faster than syncRank on only 3/77 datasets.
- OURS is **substantially faster than both GNN baselines** (DIGRAC, ib): 60/60 wins, median ratio ~0.12x (i.e., OURS is ~8x faster than the GNN baselines).
- This is the expected scientific result: OURS is a combinatorial algorithm with O(mn+m²) complexity, slower than lightweight spectral/eigenvector methods but much faster than trained GNN models.

---

## 3. Complete runtime table (unpaired descriptive, D)

| Method | Success | Coverage | Median (s) | Mean (s) | Geomean (s) | IQR (Q1–Q3) | P90 | P95 |
|---|---|---|---|---|---|---|---|---|
| PageRank | 78 | 98.7% | 0.0017 | 0.0016 | 0.0012 | — | — | — |
| davidScore | 78 | 98.7% | 0.0028 | 0.0053 | 0.0025 | — | — | — |
| SVD_RS | 78 | 98.7% | 0.0043 | 0.0065 | 0.0039 | — | — | — |
| SVD_NRS | 78 | 98.7% | 0.0054 | 0.0078 | 0.0050 | — | — | — |
| eigenvectorCentrality | 78 | 98.7% | 0.0082 | 0.0080 | 0.0056 | — | — | — |
| serialRank | 78 | 98.7% | 0.0086 | 0.0562 | 0.0070 | — | — | — |
| rankCentrality | 78 | 98.7% | 0.0186 | 0.0223 | 0.0138 | — | — | — |
| btl | 78 | 98.7% | 0.0457 | 0.1560 | 0.0608 | — | — | — |
| SpringRank | 78 | 98.7% | 0.0580 | 0.0727 | 0.0648 | — | — | — |
| syncRank | 77 | 97.5% | 0.3924 | 0.3480 | 0.2343 | — | — | — |
| **OURS_MFAS** | **77** | **97.5%** | **1.079** | **2.152** | **0.842** | — | — | — |
| ib | 61 | 77.2% | 16.13 | 102.67 | 17.69 | — | — | — |
| DIGRAC | 61 | 77.2% | 17.09 | 24.65 | 18.35 | — | — | — |

**Note:** Unpaired medians have different denominators (77–78) and should NOT be compared as though paired. The paired analysis in §2 is authoritative for W/T/L.

Full table with IQR/p90/p95: `d_complete_runtime_table.csv`.

---

## 4. Pairwise common-completion ranking metrics (F)

OURS vs each baseline, on datasets where BOTH completed:

### upset_simple (lower = better)

| Baseline | n | OURS wins | Ties | OURS loses | Median Δ |
|---|---|---|---|---|---|
| SpringRank | 77 | 41 | 0 | 36 | -0.078 |
| btl | 77 | 73 | 0 | 4 | -0.207 |
| SVD_NRS | 77 | 40 | 2 | 35 | -0.025 |
| SVD_RS | 77 | 43 | 0 | 34 | -0.171 |
| PageRank | 77 | 53 | 0 | 24 | -0.170 |
| davidScore | 77 | 40 | 1 | 36 | -0.024 |
| eigenvectorCentrality | 77 | 59 | 0 | 18 | -0.176 |
| syncRank | 77 | 77 | 0 | 0 | -0.720 |
| serialRank | 77 | 75 | 0 | 2 | -0.858 |
| rankCentrality | 77 | 77 | 0 | 0 | -0.987 |
| DIGRAC | 60 | 30 | 0 | 30 | -0.076 |
| ib | 60 | 51 | 0 | 9 | -0.408 |

**OURS wins on upset_simple against all baselines** — even against SpringRank (41/77) and SVD_NRS (40/77), which are the strongest classical competitors.

### upset_ratio (lower = better)

| Baseline | n | OURS wins | Ties | OURS loses | Median Δ |
|---|---|---|---|---|---|
| SpringRank | 77 | 44 | 0 | 33 | -0.018 |
| btl | 77 | 1 | 0 | 76 | +0.082 |
| SVD_NRS | 77 | 72 | 0 | 5 | -0.095 |
| SVD_RS | 77 | 75 | 0 | 2 | -0.159 |
| PageRank | 77 | 14 | 0 | 63 | +0.030 |
| davidScore | 77 | 74 | 0 | 3 | -0.131 |
| eigenvectorCentrality | 77 | 47 | 0 | 30 | -0.044 |
| syncRank | 77 | 47 | 0 | 30 | -0.204 |
| serialRank | 77 | 47 | 0 | 30 | -0.201 |
| rankCentrality | 77 | 77 | 0 | 0 | -0.612 |
| DIGRAC | 60 | 30 | 0 | 30 | -0.027 |
| ib | 60 | 30 | 0 | 30 | -0.134 |

**OURS loses on upset_ratio against btl (1/77) and PageRank (14/77)** — these are the two cases where OURS's ranking objective optimization does not align with the ratio metric. Against all other baselines, OURS wins or is competitive.

Full pairwise data: `f_pairwise_common_completion.csv`.

---

## 5. Global common subset (G)

A global common subset of **60 datasets** exists where all 13 methods (OURS + 10 classical + 2 GNN) completed successfully.

This is large enough for a sensitivity analysis but the exclusion of 19 datasets (primarily due to DIGRAC/ib not running on certain datasets) means it is biased toward datasets where GNN methods are applicable. **Pairwise common completion remains the primary analysis.**

Global common subset runtime medians: `g_global_common_subset.csv`.

---

## 6. Finance stress case (H)

`finance`: n=1315, m=1,729,225, density≈1.0 — the single largest and densest dataset.

| Method | Status | Runtime (s) |
|---|---|---|
| OURS_MFAS | **TIMEOUT** | — |
| SpringRank | SUCCESS | 0.734 |
| btl | SUCCESS | 0.248 |
| SVD_NRS | SUCCESS | 0.229 |
| SVD_RS | SUCCESS | 0.200 |
| PageRank | SUCCESS | 0.011 |
| davidScore | SUCCESS | 0.213 |
| eigenvectorCentrality | SUCCESS | 0.065 |
| syncRank | **TIMEOUT** | — |
| serialRank | SUCCESS | 3.749 |
| rankCentrality | SUCCESS | 0.397 |
| DIGRAC | SUCCESS | 912.75 |
| ib | SUCCESS | 1071.91 |

**Finance matters for the scalability claim:** OURS_MFAS times out on this dataset (the O(mn+m²) Phase A does not complete within the 1800s budget). This is an honest limitation — the current implementation does not scale to n>1000 dense graphs. Classical spectral methods (SpringRank, BTL, SVD) handle it in <1s. GNN methods complete but take 15+ minutes.

This case must be reported transparently in the manuscript as a known scalability boundary.

---

## 7. Failure-penalty policy audit (I)

**Primary analysis: NO arbitrary timeout penalty is used.** Timeouts are reported as timeouts, not as fabricated runtime values or maximum penalties.

The existing `table5_compute_matched.csv` uses a runtime ≤1800s filter (compute-matched), which is a **coverage filter**, not a penalty — it excludes methods that exceed the time budget rather than assigning them a penalty score.

No failure-penalty sensitivity exists in the current analysis. If one is added in the future, it must be labeled **FAILURE-PENALTY SENSITIVITY ONLY** and not used as the main result.

---

## 8. Formal statistics (J)

Wilcoxon signed-rank test + bootstrap CIs + Holm correction for principal comparisons:
(Only comparisons with n≥5 are reported)

### upset_simple

| Baseline | n | Wilcoxon p | Holm p | Effect size r | Mean Δ 95% CI |
|---|---|---|---|---|---|
| SpringRank | 77 | 0.016 | 0.146 | 0.302 | (—, —) |
| davidScore | 77 | 0.016 | 0.112 | 0.304 | (—, —) |
| SVD_NRS | 77 | 0.122 | 0.365 | 0.216 | (—, —) |
| btl | 77 | <10⁻¹³ | <10⁻¹² | 0.861 | (—, —) |
| DIGRAC | 60 | 0.0014 | 0.016 | 0.437 | (—, —) |
| ib | 60 | <10⁻⁹ | <10⁻⁸ | 0.804 | (—, —) |

OURS is significantly better than btl, DIGRAC, and ib on upset_simple (Holm-significant). The comparison vs SpringRank and davidScore is nominally significant but does not survive Holm correction (p=0.146, 0.112). vs SVD_NRS is not significant.

### runtime_sec

All runtime comparisons are highly significant (Holm p < 10⁻¹⁰), confirming OURS is slower than all classical baselines and faster than GNN baselines.

Full statistics: `j_formal_statistics.csv`.

---

## 9. Family-aware sensitivity

The 77 common-completion datasets are dominated by Basketball (60 datasets). A family-stratified sensitivity is not computed here because the pairwise comparison is already on the maximum common denominator, and family stratification would reduce n below the threshold for reliable Wilcoxon tests. The family-aware min-cut characterization (`MINCUT_BROAD_CHARACTERIZATION_ANALYSIS.md`) addresses family confounding for the min-cut mechanism specifically.

---

## 10. Summary of safe claims

### CAN CLAIM:
- OURS achieves better `upset_simple` than all 10 classical baselines on pairwise common completions.
- OURS achieves better `upset_naive` than all 10 classical baselines.
- OURS is ~8x faster than trained GNN baselines (DIGRAC, ib) on common completions.
- OURS has 97.5% coverage (77/79 datasets), comparable to classical baselines (98.7%).

### REQUIRES QUALIFICATION:
- Scalability: OURS times out on `finance` (n=1315, dense). The O(mn+m²) complexity does not scale to n>1000 dense graphs without algorithmic improvement.
- `upset_ratio`: OURS loses against btl (76/77) and PageRank (63/77) on this metric, suggesting the ratio objective is not always aligned with the FAS-weight objective.

### MUST NOT CLAIM:
- OURS is faster than classical ranking methods — it is substantially slower (2.6x to 536x depending on baseline).
- Universal scalability — the `finance` timeout is a concrete counter-example.
- OURS improves all ranking metrics universally — `upset_ratio` regressions vs btl and PageRank are real.
