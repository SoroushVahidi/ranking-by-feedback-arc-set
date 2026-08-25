# Min-Cut Exchange: Manuscript Evidence Synthesis

Date: 2026-08-24
Branch: `jsuper-runtime-coverage-final-20260824` (this document)
Source branches: `jsuper-mincut-mechanism-characterization-20260824` @ `904332b2`,
`jsuper-mincut-selector-pilot-20260824` @ `eac81a32`

**No new min-cut experiments were run in this task.** This document synthesizes
manuscript-safe facts from completed work on the characterization and selector
branches.

---

## 1. Mathematical operator

Given a kept DAG D (output of Phase A + reachability add-back) and an excluded
edge e = (u, v) with v reaching u in D (so plain exact-reachability add-back
rejects it):

1. Compute a minimum-capacity directed v→u edge cut C in D, where capacities
   = kept-edge weights.
2. If w(C) < w(e) (strictly, beyond numerical tolerance 1e-9), accept the
   exchange: D' = (D \ C) ∪ {e}.
3. Otherwise reject; D is unchanged.

**Properties:**
- The accepted exchange strictly decreases the total removed-edge weight
  (weighted-FAS objective) by w(e) − w(C) > 0.
- The resulting D' is acyclic by construction (removing C breaks all v→u paths,
  so adding (u,v) creates no cycle).
- The operator is a strict-improvement local search step on the weighted-FAS
  objective, not a heuristic relaxation.

Reference: `MINCUT_WEIGHTED_EXCHANGE_RESEARCH_QUESTION.md`,
`mincut_exchange_prototype.py` (prototype, not wired into production).

---

## 2. Correctness

- **70 unit tests** in `tests/test_mincut_exchange_prototype.py` — all passing.
  Tests cover: acyclicity preservation, strict-improvement rule, numerical
  tie rejection, zero-weight edges, self-loop rejection, path-absent case,
  multi-exchange termination, determinism.
- **Deterministic backend**: `preflow_push` flow function explicitly pinned
  (not relying on networkx's internal default).
- **Real-data revalidation**: all accepted exchanges in the broad
  characterization (280 accepted across 28 active datasets) are verified
  by the operator's own acyclicity check (`_toposort_kahn_from_edges` returns
  non-None after every accepted exchange).
- **No mutation of input state**: the operator returns a new `kept` array on
  acceptance and never mutates the input — confirmed by tests and by code
  inspection.

Reference: `MINCUT_EXCHANGE_PROTOTYPE_NOTES.md`.

---

## 3. Broad characterization results

**Protocol**: 40 datasets pre-registered in
`MINCUT_BROAD_CHARACTERIZATION_PROTOCOL.md`, frozen before launch. Dataset
selection based on structural criteria only (family, n, density, weight
dispersion) — never on min-cut outcomes.

**Completion**: 39/40 datasets have terminal outcomes (1 data-availability
skip: `Halo2BetaData/HeadToHead`, missing file — dropped per protocol, not
replaced).

**Primary comparison**: P1 (Phase A + reachability) vs P2 (P1 + min-cut
exchange with S1 ordering, budget K=300, max 10 accepted exchanges).

### Activity

| Metric | Value |
|---|---|
| Operator-active datasets | 28/39 (71.8%) |
| True-negative datasets | 11/39 (28.2%) |
| Total accepted exchanges | 280 |
| Active families | 4/7 (Basketball_coarse, Basketball_finer, Football_finer, Halo) |
| Inactive families | 3/7 (Faculty, Animal, Football_coarse) |

### Ranking effects (28 active datasets)

| Metric | Result |
|---|---|
| FAS improves + simple improves | 28/28 (100%) |
| FAS improves + naive improves | 28/28 (100%) |
| FAS improves + ratio improves | 20/28 (71.4%) |
| FAS improves + ratio worsens | 7/28 (25.0%) — all Basketball, median Δ=0.0013 |
| FAS improves + simple worsens | 0/28 (0%) |
| FAS improves + naive worsens | 0/28 (0%) |

**Simple and naive upset never worsen.** Ratio worsens on 7 Basketball
datasets with negligible magnitude (max 0.0033). This is Basketball-specific,
not a systematic tradeoff.

### Reproduction

11/11 overlapping datasets (pilot + broad) match exactly on accepted count,
structural gain, and all three ranking metrics. See
`reproduction_or_overlap_check.csv`.

Reference: `MINCUT_BROAD_CHARACTERIZATION_ANALYSIS.md`.

---

## 4. Selector (S1)

S1 = `candidate_weight / (1 + conflict_region_total_weight)`

- **Selected as best** from 6 predefined selectors (S0–S5) in a frozen 66-pair
  pilot (11 datasets × 6 selectors).
- **Efficiency**: ~8x higher gain/attempt and ~10x higher gain/second than S0
  (descending-weight baseline). Doubles total accepted exchanges (202 vs 108
  across the pilot).
- **Generalization**: S1 wins in 5/7 families in the pilot. The broad
  characterization confirms S1 reaches the 10-accept cap efficiently in all
  active Basketball instances (10–102 attempts) and finds the available
  exchanges in Football_finer and Halo.
- **Rationale**: S1 prioritizes heavy candidates in small conflict regions —
  exactly the candidates most likely to yield w(C) < w(e). The candidate-level
  analysis confirms: profitable candidates have median
  weight/conflict-weight ratio 1.31 vs 0.05 for non-profitable.

Reference: `MINCUT_SELECTOR_PILOT_ANALYSIS.md`,
`MINCUT_MECHANISM_CHARACTERIZATION.md`.

---

## 5. Regime classification

**Mechanism value**: `USEFUL_REGIME_SPECIFIC_MECHANISM`

- Active in 4/7 families (not Basketball-only).
- But strongly regime-dependent: 100% active in sparse large-n families
  (Basketball, Halo), 0% in small/dense/low-weight families (Faculty, Animal,
  Football_coarse).
- Structural gains are meaningful in the active regime (median 48.5–267.0
  depending on family) but zero outside it.

**Pattern**: `MULTIVARIATE_PATTERN_LIKELY`

- No single graph-level feature cleanly separates active from inactive.
- Graph scale (n, m), weight magnitude (median, quantiles), and density/SCC
  structure jointly determine activity.
- The S1 selector captures this multivariate structure in a principled way.

---

## 6. Important limitations

1. **Not production-ready**: the operator is a research prototype in a
   standalone module (`mincut_exchange_prototype.py`), not wired into
   `ours_mfas.py` or `comparison.py`. It adds a networkx dependency not
   present in the production pipeline.

2. **Not universal**: 3/7 families are completely inactive. The operator
   should not be presented as a universal ranking improvement.

3. **Accept cap**: all runs stop at MAX_ACCEPTED_EXCHANGES=10. The full
   opportunity frontier is not measured.

4. **Pre-mincut features only**: selector features are computed once against
   the P1 kept-set, not dynamically updated during sequential exchange.

5. **Scale bounded**: largest active dataset is n=602 (Halo2Beta). No data
   on n > 602.

6. **upset_ratio deterioration**: occurs on 7/28 active Basketball datasets
   (small magnitude). Must be reported transparently, not hidden.

7. **Family confounding**: 22/39 broad-run datasets are Basketball. The
   family-aggregated analysis (7 points) is more conservative but has low n.

---

## 7. What NOT to claim

- Do NOT claim the min-cut exchange is production-ready.
- Do NOT claim universal ranking improvement.
- Do NOT claim novelty as proven solely from absence of close prior art for
  the exchange operator (the concept of exchange-based local search for FAS
  exists for tournaments — see `MINCUT_EXCHANGE_PRIOR_ART_CHECKLIST.md`).
- Do NOT claim the min-cut exchange is faster than classical methods (it
  adds computation on top of the base MFAS pipeline).
- Do NOT use the min-cut results as the paper's headline conclusion — they
  are secondary to the main MFAS + reachability add-back contribution.

---

## 8. What CAN be stated in the manuscript

1. A weighted min-cut exchange operator for feedback arc sets, with a
   strict-improvement acceptance rule and proven acyclicity preservation.
2. A conflict-normalized candidate selector (S1) that efficiently identifies
   profitable exchanges.
3. Broad characterization showing the operator is active on 28/39 feasible
   real-world graphs across 4/7 families, with structural gains and
   consistent simple/naive upset improvement.
4. A regime-specific activation pattern (large n, sufficient weight
   magnitude, sparse structure) that is scientifically interpretable.
5. Honest reporting of the upset_ratio deterioration on Basketball and the
   inactivity on 3 families.

Reference: `MINCUT_BROAD_CHARACTERIZATION_ANALYSIS.md`,
`MINCUT_MECHANISM_CHARACTERIZATION.md`,
`MINCUT_SELECTOR_PILOT_ANALYSIS.md`,
`MINCUT_EXCHANGE_PROTOTYPE_NOTES.md`.
