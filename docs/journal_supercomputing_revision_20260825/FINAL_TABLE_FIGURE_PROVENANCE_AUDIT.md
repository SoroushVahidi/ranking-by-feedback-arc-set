# Final Table / Figure Provenance Audit

Date: 2026-08-25

| Label | Caption gist | Source | Script/filter | Denominator | Reproduced | Referenced |
|---|---|---|---|---|---|---|
| `tab:novelty_separation` | Novelty vs DF03/VK25 | manual, lineage audits | — | — | Yes | Yes |
| `tab:parameters` | Parameters/termination | method design | — | — | Yes | Yes |
| `tab:dataset_suite_summary` | Family counts | suite inventory | 80-suite; exclude `_AUTO` | intended 80 | Yes | Yes |
| `tab:pairwise_quality_simple` | upset_simple W/T/L | `f_pairwise_common_completion.csv` (+ Holm export) | archived OURS_MFAS vs baseline | 77 or 60 | Yes | Yes |
| `tab:pairwise_quality_ratio` | upset_ratio W/T/L | same | same | 77 or 60 | Yes | Yes |
| `tab:runtime_wtl` | runtime W/T/L | `e1_runtime_wtl.csv` | archived OURS_MFAS | 77 or 60 | Yes | Yes |
| `tab:ablation_primary` | A0–A6 paired tests | `primary_pairwise_statistics.csv` | non-Finance | 77 or 33 | Yes | Yes |
| `fig:runtime_vs_edges` | A4 time vs m | structural ablation | non-Finance A4 | ≤77 | Yes (PDF in package) | Yes |
| `fig:ablation` | A0–A6 medians | structural ablation | unpaired descriptive | non-Finance | Yes | Yes |

## Negative checks

| Check | Status |
|---|---|
| No stale submitted Table 4/5 aggregation | Pass (protocol statement) |
| No BTL/DavidScore swap | Pass (tables + captions) |
| No `_AUTO/...1985adj` in suite | Pass |
| OURS_MFAS/INS3 duplicate disclosed | Pass |
| No denominator mixing | Pass (protocol) |
| Captions agree with values | Pass after archived-OURS caption clarity |

Figures: PDF only in submission package (PNG not required).
