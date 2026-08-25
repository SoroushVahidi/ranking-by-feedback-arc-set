# Targeted Reachability Rerun Plan

Date: 2026-08-25

## What is missing

Structural ablation `A4` rows contain `upset_simple` / `upset_naive` / `upset_ratio` computed by
`run_mincut_cap_audit._upset_*` (weight-fraction / absolute-weight / pairwise ratio helpers).

Principal baseline tables use GNNRank `calculate_upsets` styles (`simple` / `naive` / `ratio`) from
`leaderboard_per_method.csv`. These are **not interchangeable** (verified on Basketball/1985:
ablation A4 `upset_simple≈0.100` vs leaderboard SpringRank `≈0.762` under the GNNRank simple style).

Therefore existing A4 CSV **cannot** regenerate Tables 4–5 against classical/GNN baselines.

Runtime (`runtime_total_sec`) and completion status **are** usable from existing A4 rows for
runtime/coverage, but for consistency we re-emit runtime from the same targeted A4 pass.

## Why existing outputs cannot answer headline quality tables

Metric definition mismatch between ablation harness and manuscript baseline protocol.

## Minimal campaign

| Field | Value |
|---|---|
| Config | `A4` = Phase A + `addback_mode=reach` + Phase C refinement; **min-cut OFF** |
| Datasets | 77 non-Finance A4-complete datasets from structural ablation |
| Metrics | GNNRank `calculate_upsets` simple/naive/ratio + wall runtime |
| Purpose | Headline Tables 4–6 for canonical **OURS-Reach** |
| Resource | Local CPU only (no GPU; no SLURM) |
| Est. wall | ~2–10 minutes for 77 graphs |

## SLURM

**Not recommended** — campaign is small and local-CPU sufficient.
