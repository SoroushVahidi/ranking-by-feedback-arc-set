# Experiment Interpretation Rules

Date: 2026-08-25
Branch: `jsuper-reviewer-ablation-scale-20260825`

Predefined rules for interpreting ablation results. These rules are fixed
BEFORE any results are inspected.

---

## 1. What counts as material improvement

A config B is a **material improvement** over config A on a given metric if:

1. **Paired median delta** is in the favorable direction (negative for upset metrics, positive for structural gain), AND
2. **W/T/L record** favors B (more wins than losses), AND
3. **Bootstrap 95% CI** of the paired delta excludes zero, OR the Wilcoxon p-value (before Holm) is < 0.05.

If only conditions 1-2 are met but not 3, the improvement is **directional but not statistically significant** — report it as such.

## 2. How ties are treated

- For upset metrics: a tie is counted when |delta| < 1e-9.
- For runtime: a tie is counted when |delta| < 0.005s (5ms).
- Ties are reported separately from wins and losses in all W/T/L tables.
- A config with many ties and few wins is reported as "no material difference" not as "marginally better."

## 3. How timeouts are reported

- Timeout = the method did not complete within the per-config time budget.
- Timeouts are reported as TIMEOUT in the completion matrix, not as a fabricated runtime or penalty.
- A dataset where the method timed out is EXCLUDED from pairwise metric comparisons (not counted as a loss).
- The exclusion count and reason are reported adjacent to each pairwise comparison.
- Finance is always reported explicitly as a stress case regardless of outcome.

## 4. How negative sensitivities are reported

- If a sensitivity variant (e.g., R3 with 4x refinement passes) produces WORSE metrics than the canonical setting, this is reported as a negative sensitivity — not suppressed.
- If a sensitivity variant produces no change (all ties), this is reported as "insensitive to this parameter" — the desired outcome for stability claims.
- If the zero_tol grid produces different Phase-A removed weights, this is reported as numerical instability — not hidden.

## 5. No post-hoc suppression

- All predefined configurations will be reported, regardless of outcome.
- If a config makes the method look bad (e.g., A1 legacy topo add-back showing near-random upset_simple), this is reported honestly.
- If the min-cut exchange (A5/A6) shows no improvement on some families, this is reported.
- No configuration is removed from the output because its results are unfavorable.
- No new configuration is added after seeing results.

## 6. Family-awareness qualification

- Basketball datasets (60+ of 78) dominate the sample. Family-level summaries are reported.
- pairwise statistics on the full sample are qualified with "dominated by Basketball."
- A family-aggregated sensitivity (each family = one point) is provided as a supplementary analysis.
- No claim of "independent replicates" is made for Basketball year-to-year variations without qualification.

## 7. Primary comparison interpretation

| Comparison | Question | Expected direction | If unexpected |
|---|---|---|---|
| A0 vs A2 | Does reachability help beyond Phase A? | A2 better on upset_simple | If not, reachability add-back is ineffective |
| A1 vs A2 | Does exact reachability improve on topo proxy? | A2 better than A1 | If not, topo proxy is sufficient |
| A2 vs A5 | Does min-cut improve beyond safe restoration? | A5 better on structural objective | If not, min-cut adds no value |
| A4 vs A6 | Does min-cut help after refinement? | A6 better or equal | If worse, min-cut conflicts with refinement |
| A0 vs A4 | What does full pipeline contribute? | A4 much better | If not, pipeline stages are ineffective |
| P0 vs P1/P2/P3 | Do extra passes help? | P1=P2=P3 (no change) | If P2/P3 add edges, multipass is not useless |

## 8. Scalability interpretation

- Runtime is plotted against n, m, m*n, and density.
- No theoretical curve is fit to the empirical data.
- The finance timeout is reported as a hard scalability boundary.
- If runtime appears to scale sub-quadratically on the evaluated suite, this is noted as empirical observation, not a complexity claim.
- The complexity claim (O(mn+m²)) is stated from the complexity audit, not from fitting.
