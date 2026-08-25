# Family-Aware Baseline Analysis

Date: 2026-08-25  
Branch: `jsuper-final-experimental-gaps-20260825`  
Source: `GNNRank-main/paper_csv/leaderboard_per_method.csv` (existing; no algorithm reruns)  
Outputs: `outputs/revision_analysis_20260825/family_aware_baselines/`

Orientation: Δ = OURS_MFAS − baseline; for upset metrics **negative favors OURS**.

---

## 1. Why this analysis

Reviewer 2 questioned treating many related Basketball temporal graphs as
independent observations. Per-dataset n≈77 is Basketball-dominated
(~60/77). We freeze a family map and recompute conclusions under
equal-family weighting, LOFO, Basketball collapse, and hierarchical bootstrap.

## 2. Family mapping (frozen)

| Family | n datasets | Macro role |
|---|---:|---|
| Basketball_coarse | 31 | included |
| Basketball_finer | 30 | included |
| Football_coarse | 6 | included |
| Football_finer | 6 | included |
| Faculty | 3 | included |
| Halo | 2 | included |
| Animal | 1 | included |
| ERO | 1 | included_if_present (not in equal-family set of 7) |
| Finance | 1 | excluded from quality macros |

Canonical method selection: classical/OURS prefer
`trials10train_r100test_r100AllTrue`; DIGRAC/ib prefer the dominant
`K20…withdistFiedler…` config (not oracle best-in-suite).

## 3. Per-dataset vs equal-family (upset_simple)

| Baseline | Per-dataset n | W/T/L | med Δ | Equal-family mean of fam-medians | Fam W/T/L | Hier. CI≠0? |
|---|---:|---|---:|---:|---|---|
| SpringRank | 77 | 41/0/36 | −0.078 | −0.015 | 5/0/2 | **no** |
| davidScore | 77 | 40/1/36 | −0.024 | −0.050 | 4/0/3 | **no** |
| SVD_NRS | 77 | 40/2/35 | −0.025 | −0.103 | 5/0/2 | **no** |
| btl | 77 | 73/0/4 | −0.207 | −0.132 | 6/0/1 | yes |
| PageRank | 77 | 53/0/24 | −0.170 | −0.208 | 6/0/1 | yes |
| syncRank | 77 | 77/0/0 | −0.720 | −0.822 | 7/0/0 | yes |
| rankCentrality | 77 | 77/0/0 | −0.987 | −1.177 | 7/0/0 | yes |
| serialRank | 77 | 75/0/2 | −0.858 | −0.984 | 7/0/0 | yes |
| DIGRAC | 77 | 47/0/30 | −0.281 | −0.305 | 6/0/1 | yes |
| ib | 77 | 68/0/9 | −0.338 | −0.379 | 7/0/0 | yes |

**Unfavorable / weaken:** vs SpringRank and davidScore, per-dataset **mean** Δ is
positive (OURS worse on the mean) even when the median favors OURS; hierarchical
bootstrap CIs for equal-family means **include zero**. Competitive, not dominant.

## 4. Equal-family macro conclusions

- Strong baselines (syncRank, rankCentrality, serialRank, ib): equal-family still
  strongly favors OURS on upset_simple.  
- vs SpringRank/davidScore/SVD_NRS: direction still favors OURS on equal-family
  **means of family medians**, but **not** CI-robust.  
- **No sign flip** when removing all Basketball families from the equal-family
  mean (direction preserved for all 10 baselines).

## 5. LOFO (upset_simple)

Dropping individual families can move the SpringRank equal-family mean across
zero (e.g. drop Animal, Basketball_coarse, or Halo → mean becomes slightly
positive). Therefore **SpringRank superiority claims are LOFO-fragile** and must
be weakened to “competitive / mixed.”

btl / PageRank / GNN / spectral-centrality baselines remain OURS-favoring under
LOFO in this grid.

## 6. Basketball dependence

Collapsing Basketball into one meta-point (`basketball_collapsed_summary.csv`)
does not reverse the equal-family story for the strong wins. Basketball
inflates per-dataset n but is **not** the sole driver of OURS-vs-btl/GNN wins.
It **does** amplify fragile SpringRank/davidScore narratives if one only quotes
per-dataset medians without family weighting.

## 7. BTL upset_ratio disadvantage

Equal-family upset_ratio vs **btl**: mean of family medians **+0.102**, family
W/T/L **0/0/7** (OURS worse on every included family).  
**The BTL upset_ratio disadvantage remains and is not a Basketball artifact.**

## 8. Answers to required questions

| Question | Answer |
|---|---|
| Do principal ranking-quality conclusions survive equal-family weighting? | **Partially.** Strong wins (btl/PageRank/GNNs/centrality methods) survive. SpringRank/davidScore/SVD_NRS become **non-robust** (CI includes 0; LOFO fragile for SpringRank). |
| Which conclusions depend strongly on Basketball? | Per-dataset SpringRank/davidScore “win” storytelling; not the btl/GNN large-margin wins. |
| Is OURS still competitive vs SpringRank/davidScore/SVD_NRS/BTL? | **Yes competitive** vs SpringRank/davidScore/SVD_NRS; **clearly better** on upset_simple vs btl. |
| Does BTL upset_ratio disadvantage remain? | **Yes** (7/7 families). |
| Does any previously significant result disappear under family-aware treatment? | Claims of clear superiority vs SpringRank/davidScore **must be weakened**; Holm-significant vs btl/DIGRAC/ib on upset_simple remain directionally intact under equal-family. |
| Which claims must be weakened? | Any manuscript claim that OURS “significantly outperforms SpringRank/davidScore on upset_simple” without family qualification. |

## 9. Manuscript implications (evidence only; no rewrite here)

- Prefer **family-aware** or Basketball-collapsed reporting alongside per-dataset.  
- State OURS is **competitive** with SpringRank/davidScore, not uniformly superior.  
- Keep honest BTL upset_ratio loss.  
- Keep GNN upset_simple advantage under equal-family.
