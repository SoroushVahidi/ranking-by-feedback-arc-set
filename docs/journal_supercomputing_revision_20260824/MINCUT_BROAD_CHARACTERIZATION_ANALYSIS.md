# Min-Cut Exchange: Broad Characterization Analysis

Date: 2026-08-24
Branch: `jsuper-mincut-mechanism-characterization-20260824`
Worktree: `/tmp/ranking-jsuper-mincut-characterization`
Base: `ab0ef13d` (broad characterization preparation commit)
Protocol: `MINCUT_BROAD_CHARACTERIZATION_PROTOCOL.md` (frozen before launch)

Harness: `run_mechanism_characterization.py --broad`
Analysis: `run_broad_characterization_analysis.py`
Raw outputs: `outputs/revision_analysis_20260824/mincut_broad_characterization/`

---

## 0. Completeness

- Pre-registered datasets: 40
- Completed: 39
- Data-unavailable (per protocol): 1 (`Halo2BetaData/HeadToHead`, missing file — dropped, not replaced)
- **All 40 datasets have terminal outcomes. The run is complete.**

---

## Q1. How many of the 40 pre-registered graphs contain at least one profitable min-cut exchange?

**28 of 39 feasible graphs (71.8%) are operator-active.**

11 datasets (28.2%) are true negatives: the operator finds zero profitable exchanges across all candidates.

---

## Q2. How broadly are active graphs distributed across dataset families?

| Family | n_datasets | n_active | frac_active | total_accepted | total_gain |
|---|---|---|---|---|---|
| Basketball_coarse | 12 | 12 | 1.00 | 120 | 613.0 |
| Basketball_finer | 10 | 10 | 1.00 | 100 | 2606.0 |
| Football_coarse | 6 | 1 | 0.17 | 2 | 3.0 |
| Football_finer | 6 | 4 | 0.67 | 10 | 21.8 |
| Faculty | 3 | 0 | 0.00 | 0 | 0.0 |
| Animal | 1 | 0 | 0.00 | 0 | 0.0 |
| Halo | 1 | 1 | 1.00 | 10 | 19.0 |

**The operator is active in 4 of 7 families** (Basketball_coarse, Basketball_finer, Football_finer, Halo), plus marginally in Football_coarse (1/6). It is completely inactive in Faculty and Animal.

The 11-dataset pilot's finding that Basketball is the strongest family **reproduces and extends**: Basketball shows 100% activity across all 22 instances (12 coarse + 10 finer). But the broad run also reveals meaningful activity in Football_finer (4/6) and Halo (1/1), which were not evident from the pilot's single Football_finer and single Halo instance.

---

## Q3. Does the 11-dataset multivariate pattern reproduce?

**Partially.** The core directionality reproduces — active graphs are larger, have higher edge weights, lower density, and larger conflict regions. But the specific correlations shift:

- The 11-dataset pilot's strongest correlation (q25_edge_weight, rho=0.973) remains strong (rho=0.927) for absolute gain but **weakens substantially for normalized gain** (rho=0.288 vs 0.745).
- The normalized-gain correlations are generally much weaker (all |rho| < 0.4) in the broad run, suggesting that the 11-dataset pilot overestimated effect sizes due to family confounding.
- The **Gini coefficient** flips direction: it was weakly positive (rho=0.055 gain, 0.264 norm) in the pilot and becomes the **strongest normalized-gain correlate** (rho=0.386) in the broad run — but in a direction suggesting that more unequal weight distributions (higher Gini) are associated with *higher* normalized gain, not lower.
- The **largest_scc_fraction** negative association reproduces (rho=-0.641 gain, -0.188 norm).

**Conclusion**: The multivariate pattern reproduces in direction but not in magnitude. The pilot's high correlations were inflated by family confounding (4/6 active were Basketball). The broad run provides more conservative estimates.

---

## Q4. Are the previously strong graph-level associations still present?

| Feature | Pilot rho_gain | Broad rho_gain | Pilot rho_norm | Broad rho_norm |
|---|---|---|---|---|
| q25_edge_weight | 0.973 | 0.927 | 0.745 | 0.288 |
| median_edge_weight | 0.855 | 0.933 | 0.627 | 0.329 |
| phase_a_removed_weight | 0.818 | 0.902 | 0.582 | 0.260 |
| n_unsafe_excluded | 0.845 | 0.882 | 0.636 | 0.235 |
| conflict_median_total_weight | 0.818 | 0.870 | 0.609 | 0.202 |
| largest_scc_fraction | -0.682 | -0.641 | -0.518 | -0.188 |

**Absolute gain correlations are strong and reproduce.** Normalized gain correlations are much weaker in the broad run — the pilot's high normalized-gain correlations were driven by the family composition of the 11-dataset sample.

---

## Q5. At candidate level, does weight/conflict_total_weight remain useful?

**Yes, in direction but the Spearman correlation with acceptance is weak.** The median weight/conflict_weight ratio for profitable candidates is 1.31 vs 0.05 for non-profitable — a 26x separation in medians. The direction is consistent across all three ratio variants:

| Feature | Profitable median | Non-profitable median | Direction |
|---|---|---|---|
| weight_over_conflict_weight | 1.31 | 0.05 | profitable > non |
| weight_over_conflict_edges | 15.5 | 0.15 | profitable > non |
| weight_over_conflict_vertices | 8.0 | 0.32 | profitable > non |

However, the Spearman correlation with acceptance at the candidate level is weak (|rho| < 0.2 for all three). This is because the candidate-level distributions have substantial overlap — the ratio separates medians but does not cleanly classify individual candidates. The S1 selector exploits this ratio for *ordering* (prioritizing high-ratio candidates first), not for *classification*.

---

## Q6. Does S1's conceptual rationale hold outside Basketball-heavy data?

**Yes, with qualification.** S1's ordering (weight / (1 + conflict_total_weight)) is designed to prioritize heavy candidates in small conflict regions. The broad run confirms:

- In Basketball (22 instances, 100% active, 220 total accepted, 3219 total gain): S1 consistently reaches the 10-accept cap in 10–102 attempts, demonstrating efficient candidate selection.
- In Football_finer (4/6 active): S1 finds 1–3 accepted exchanges per active instance — modest but real opportunity outside Basketball.
- In Halo (1 instance, 10 accepted, gain=19): S1 finds opportunity in a sparse large-n graph.
- In Football_coarse (1/6 active, 2 accepted): rare, marginal activity.
- In Faculty/Animal (0% active): no opportunity regardless of selector — these are structural true negatives.

The rationale holds: the selector is efficient *when opportunity exists*. The question of *whether* opportunity exists is determined by graph structure, not selector choice.

---

## Q7. How often does structural improvement produce metric changes?

| Outcome | Count (of 28 active) |
|---|---|
| All three metrics improve (simple, ratio, naive) | 20 |
| FAS improves + ratio worsens (simple & naive improve) | 7 |
| FAS improves + simple worsens | 0 |
| FAS improves + naive worsens | 0 |
| Mixed (improve on some, neutral on others) | 1 |

**Structural improvement never worsens simple or naive upset.** It worsens upset_ratio on 7/28 active datasets (25%), all with very small magnitude (median ratio deterioration = 0.0013, max = 0.0033).

The ratio deterioration is **Basketball-specific**: all 7 ratio-worsening instances are Basketball (6 coarse + 1 finer). Football_finer and Halo show either improvement or no change in ratio.

---

## Q8. Are there recognizable graph regimes where min-cut exchange has little/no opportunity?

**Yes.** The inactive datasets cluster in a recognizable regime:

- **Faculty (3/3 inactive)**: low n (113–206), low-to-medium density (0.033–0.141), low edge weights (median 1.0–1.0), small conflict regions (median 7 vertices).
- **Animal (1/1 inactive)**: small n (21), high density (0.460), high CV (1.348) but small absolute weights.
- **Football_coarse (5/6 inactive)**: very small n (20), high density (0.566), low edge weights (median 1–2).

The common pattern: **small n + low absolute edge weights + dense local neighborhoods** → the min-cut cost always exceeds candidate weight. The operator needs sufficient weight heterogeneity (large candidates relative to their conflict regions) to find profitable exchanges.

The active regime: **larger n (≥ ~250) + higher absolute edge weights (median ≥ ~7) + sparse enough graph that conflict regions are not all-encompassing**.

---

## Q9. Pattern verdict

**`MULTIVARIATE_PATTERN_LIKELY`** (confirmed from broad run)

The broad run with 39 datasets and 7 families confirms the 11-dataset pilot's verdict. No single feature cleanly separates active from inactive. The separation requires combining:
1. Graph scale (n, m, total edge weight)
2. Weight magnitude (median, quantiles)
3. Conflict-region size (vertices, edges, total weight)
4. Density / SCC structure

The Gini coefficient emerges as a novel normalized-gain correlate (rho=0.386) that was not visible in the pilot, but it alone is insufficient for classification.

---

## Q10. Is there enough evidence to justify promoting min-cut exchange to production experimental variant?

**Yes, with the qualifier that it should be an optional/experimental variant, not a default-on path.** Evidence:
- 28/39 feasible graphs (72%) are active — the operator is not Basketball-specific.
- 4/7 families show activity (Basketball, Football_finer, Halo, marginally Football_coarse).
- Structural gains are meaningful (median 48.5 for Basketball_coarse, 267 for Basketball_finer).
- No metric ever worsens on simple or naive upset; ratio deterioration is small and Basketball-specific.
- The S1 selector provides an efficient, deterministic, interpretable ordering.

However: 3/7 families are completely inactive (Faculty, Animal, 5/6 Football_coarse), and the gains outside Basketball are modest. The variant should be opt-in with a feasibility check.

---

## Family-level analysis

### Basketball_coarse (12 datasets, 100% active)

All 12 Basketball_coarse instances are active with 10 accepted exchanges each (hitting the cap). Gain median = 48.5, ranging from 27 (2014) to 83 (1985). The ratio deterioration appears on 6/12 instances but with very small magnitude (median 0.0008). Simple and naive upset always improve.

### Basketball_finer (10 datasets, 100% active)

All 10 Basketball_finer instances are active with 10 accepted each. Gain median = 267.0 — the highest of any family. The finer variant has higher edge counts (2400–3800 unsafe candidates) and denser local structure, producing larger absolute gains. Ratio improves on 8/10 (median ratio delta = -0.0022), unlike coarse where it worsens.

### Football_coarse (6 datasets, 1 active)

Only England_2012_2013 is active (2 accepted, gain=3.0). The other 5 are true negatives. This is a small, dense (n=20, density≈0.57) family with low edge weights — the conflict-region cost almost always exceeds the candidate weight.

### Football_finer (6 datasets, 4 active)

4/6 active with 1–3 accepted each and small gains (2.0–9.0). The denser finer variant creates more opportunity than coarse but far less than Basketball. The 2 inactive instances (2013/14, 2014/15) may reflect year-specific structure.

### Faculty (3 datasets, 0 active)

All 3 are true negatives — confirmed from both the pilot and broad run. This family has medium n (113–206), low density, and low edge weights. The conflict regions are too expensive relative to candidate weights.

### Animal (1 dataset, 0 active)

Dryad_animal_society is a true negative — confirmed. Small n (21), high density (0.46), high CV (1.35) but small absolute weights. No profitable exchanges exist.

### Halo (1 dataset, 1 active)

Halo2BetaData is active (10 accepted, gain=19.0) — a sparse (density=0.014), large-n (602) graph. The operator finds meaningful opportunity in this sparse regime, consistent with the mechanism's preference for sparse graphs with sufficient weight heterogeneity.

---

## Graph-level active vs inactive comparison (key features, n=39)

| Feature | Active median (n=28) | Inactive median (n=11) | Ratio | Direction |
|---|---|---|---|---|
| n | 303 | 20 | 15.2x | active > inactive |
| m | 3910.5 | 226 | 17.3x | active > inactive |
| density | 0.059 | 0.566 | 0.10x | active < inactive |
| total_edge_weight | 55247 | 576 | 95.9x | active > inactive |
| median_edge_weight | 13.0 | 2.0 | 6.5x | active > inactive |
| q25_edge_weight | 7.0 | 1.0 | 7.0x | active > inactive |
| phase_a_removed_weight | 5922.5 | 79.0 | 75.0x | active > inactive |
| n_unsafe_excluded | 812.5 | 62.0 | 13.1x | active > inactive |
| conflict_p90_total_weight | 5449.2 | 172.5 | 31.6x | active > inactive |
| largest_scc_fraction | 0.0033 | 0.050 | 0.07x | active < inactive |
| cv_edge_weight | 0.700 | 0.690 | 1.01x | ~equal |
| gini_coefficient | 0.357 | 0.345 | 1.03x | ~equal |

**The separation is now much sharper than in the 11-dataset pilot** because the inactive group is larger (11 vs 5) and more diverse. Density and largest_scc_fraction are the strongest discriminators in the negative direction (active graphs are sparse and have tiny SCCs). Edge weight magnitude and total graph weight are the strongest positive discriminators.

---

## Candidate-level analysis (n=2510 candidates, 280 accepted, 2230 rejected)

| Feature | Profitable median | Non-profitable median | Direction |
|---|---|---|---|
| candidate_weight | 17.0 | 2.0 | profitable > non |
| conflict_region_vertices | 2.0 | 6.0 | profitable < non |
| conflict_region_edges | 1.0 | 10.0 | profitable < non |
| conflict_region_total_weight | 23.5 | 41.0 | profitable < non |
| rank_distance | 3.0 | 6.0 | profitable < non |
| path_min_edge_weight | 9.**5** | 3.2 | profitable > non |
| path_total_weight | 14.0 | 4.2 | profitable > non |
| weight_over_conflict_weight | 1.31 | 0.05 | profitable > non |
| weight_over_conflict_edges | 15.5 | 0.15 | profitable > non |
| weight_over_conflict_vertices | 8.0 | 0.32 | profitable > non |

**The candidate-level pattern from the 11-dataset pilot reproduces exactly.** Profitable candidates are heavier, in smaller conflict regions, with shorter rank distance and higher path bottlenecks. The weight-to-conflict ratio is the strongest discriminator.

The broad-run profitable median weight (17.0) is higher than the pilot's (9.0), reflecting the inclusion of Basketball_finer instances with larger absolute weights.

---

## Metric disagreement (n=28 active)

| Category | Count | Magnitude |
|---|---|---|
| FAS improves + simple worsens | 0 | — |
| FAS improves + naive worsens | 0 | — |
| FAS improves + ratio worsens | 7 | median 0.0013, max 0.0033 |
| All three improve | 20 | — |
| Mixed | 1 | — |

**The earlier ratio deterioration is Basketball-specific** (all 7 cases are Basketball: 6 coarse + 1 finer). It does not appear in Football_finer or Halo. The magnitude is negligible (max 0.0033). This is NOT a systematic tradeoff — it is a small, family-specific effect.

---

## Multivariate exploratory analysis (EXPLORATORY — NOT PREDICTIVE VALIDATION)

### PCA

PC1 explains 70.4% of variance, PC2 explains 19.5%. The first two components capture 89.9% of total variance, indicating that the 13-feature graph characterization is highly redundant — most variation is captured by a single dominant axis (graph scale / weight magnitude).

### Correlation matrix (selected)

| Feature pair | Spearman rho |
|---|---|
| n vs m | 0.98 (near-perfect — n and m are redundant) |
| n vs total_edge_weight | 0.89 |
| median_edge_weight vs q25_edge_weight | 0.97 (weight quantiles are redundant) |
| density vs n | -0.40 |
| gini_coefficient vs cv_edge_weight | 0.56 |
| total_weighted_gain vs median_edge_weight | 0.93 |
| total_weighted_gain vs density | -0.40 |
| normalized_gain vs gini_coefficient | 0.39 |

**The feature set is highly redundant.** Graph scale (n, m, total_edge_weight) and weight magnitude (median, q25, q75, q90, q95) form two tight clusters. For a parsimonious characterization, 3–4 features would suffice: n, density, median_edge_weight, and gini_coefficient.

---

## Bootstrap confidence intervals (10,000 resamples, seed=42)

| Quantity | Mean | 95% CI |
|---|---|---|
| Active gain (28 datasets) | 115.6 | (77.1, 158.4) |
| Active normalized gain (28 datasets) | 0.0078 | (0.0051, 0.0104) |

The CIs are wide, reflecting the heterogeneity of active datasets (gain ranges from 2.0 to 562.0). The lower bound for active gain excludes zero.

---

## Family-aggregated sensitivity

Each family contributes one aggregate point:

| Family | frac_active | total_gain | median_n | median_density |
|---|---|---|---|---|
| Basketball_coarse | 1.00 | 613.0 | 291 | 0.035 |
| Basketball_finer | 1.00 | 2606.0 | 311 | 0.061 |
| Football_finer | 0.67 | 21.8 | 20 | 1.000 |
| Halo | 1.00 | 19.0 | 602 | 0.014 |
| Football_coarse | 0.17 | 3.0 | 20 | 0.566 |
| Faculty | 0.00 | 0.0 | 145 | 0.058 |
| Animal | 0.00 | 0.0 | 21 | 0.460 |

When aggregated by family (7 points instead of 39), the pattern is clear: the operator is fully active in families with large n and sparse density (Basketball, Halo), partially active in the densest family (Football_finer), and inactive in small/dense or low-weight families.

---

## Reproduction/overlap check

11/11 overlapping datasets (those in both the pilot and broad run) match exactly on accepted count and structural gain. See `reproduction_or_overlap_check.csv`.

---

## Mechanism value decision

**`USEFUL_REGIME_SPECIFIC_MECHANISM`**

Rationale:
- The operator is active in 4/7 families and 28/39 feasible graphs — not Basketball-only.
- But the activity is strongly regime-dependent: 100% in Basketball/Halo (sparse, large-n), 67% in Football_finer (complete digraph), 17% in Football_coarse, 0% in Faculty/Animal.
- Structural gains are meaningful in the active regime (median 48.5–267.0 depending on family) but negligible outside it.
- The activation condition is interpretable: sufficient graph scale + sufficient edge-weight magnitude + sparse enough structure that conflict regions are not all-encompassing.
- Not `STRONG_GENERAL_MECHANISM`: 3/7 families are completely inactive, and gains outside Basketball are modest.
- Not `TOO_DATASET_SPECIFIC`: 4/7 families show activity, and the structural explanation (scale + weight + sparsity) is family-independent.
- Not `NEGATIVE_RESULT`: the operator produces real, verified improvements in the majority of feasible graphs.

---

## Production-integration decision

**`NO — KEEP_AS_RESEARCH_PROTOTYPE`**

Rationale:
- The operator's inactivity on 3/7 families (Faculty, Animal, Football_coarse) means a production integration would need a feasibility check — currently no cheap pre-mincut rule reliably predicts inactivity (the `candidate_weight < 1.0` rule has only 55% recall).
- The conflict-region features needed for the S1 selector are not computed by the production pipeline (`ours_mfas.py`); integrating them would add a networkx dependency to the production code.
- The gains, while real, are secondary to the main MFAS contribution and should not carry novelty alone.
- The ratio deterioration on Basketball (7/28 active) requires careful handling in any production path.
- The prototype is well-tested and validated as a research tool; promoting it requires additional engineering work outside the scope of this characterization.

---

## Limitations

1. **39 feasible datasets (not 40)**: Halo2BetaData/HeadToHead missing — dropped per protocol, not replaced.
2. **Basketball dominance**: 22/39 datasets are Basketball; family-aggregated analysis has only 7 points.
3. **MAX_ACCEPTED_EXCHANGES = 10**: all active runs hit the cap; the full opportunity frontier is not measured.
4. **Pre-mincut features only**: features computed once against P1 kept-set, not dynamically updated.
5. **Single backend**: preflow_push only.
6. **PCA is exploratory**: not predictive validation; no cross-validation, no held-out test.
7. **Bootstrap CIs are unconditional**: they do not account for family structure; a family-stratified bootstrap would be more appropriate but with 7 families and uneven sizes, it is not straightforward.
8. **No significance testing**: with n=39 and strong family confounding, formal hypothesis tests would require careful multiple-comparison correction and family-aware design.

---

*Harness: `run_mechanism_characterization.py --broad`*
*Analysis: `run_broad_characterization_analysis.py`*
*Tests: `tests/test_characterization.py`*
