# Canonical Reachability Coverage Audit

Date: 2026-08-25

## Config definitions (from code)

| ID | Meaning |
|---|---|
| A0 | Phase A only |
| A1 | Phase A + topo-proxy add-back |
| A2 | Phase A + exact reachability |
| A3 | topo-proxy + Phase C (submitted-like full) |
| A4 | reachability + Phase C (**canonical OURS-Reach**) |
| A5 | reachability + min-cut (no refine) |
| A6 | reachability + min-cut + refine |

## Coverage for A4 / OURS-Reach

| Item | Value |
|---|---|
| Structural A4 complete (non-Finance) | 77 |
| GNNRank-metric re-score complete | **77/77** (`a4_gnnrank_metrics.csv`) |
| Finance in headline quality | Excluded (stress/timeout) |
| Pairwise vs classical | n=77 |
| Pairwise vs DIGRAC/ib | n=60 |
| Metrics | upset_simple/naive/ratio + runtime |

## Existing-evidence note

Structural ablation upsets use a **different** helper than GNNRank `calculate_upsets`, so ablation CSVs alone were **insufficient** for Tables 4–5. A targeted CPU re-score of A4 under GNNRank metrics was required (no GPU/SLURM).

**CANONICAL_METHOD_MATCHES_HEADLINE_TABLES = PASS** after re-score + table rebuild.
