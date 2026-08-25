# Targeted Reachability Rerun Plan

Date: 2026-08-25

Runtime provenance update (2026-08-25): the statement below that ablation-harness
`runtime_total_sec` was usable is superseded for manuscript-facing ablation runtime.
`runtime_total_sec` remains useful as a harness diagnostic, but the corrected
single-invocation algorithm quantity is `runtime_algorithm_sec`; see
`RUNTIME_PROVENANCE_AUDIT.md`.

## What is missing

Structural ablation `A4` rows contain `upset_simple` / `upset_naive` / `upset_ratio` computed by
`run_mincut_cap_audit._upset_*` (weight-fraction / absolute-weight / pairwise ratio helpers).

Principal baseline tables use GNNRank `calculate_upsets` styles (`simple` / `naive` / `ratio`) from
`leaderboard_per_method.csv`. These are **not interchangeable** (verified on Basketball/1985:
ablation A4 `upset_simple≈0.100` vs leaderboard SpringRank `≈0.762` under the GNNRank simple style).

Therefore existing A4 CSV **cannot** regenerate Tables 4–5 against classical/GNN baselines.

Completion status remains usable from existing A4 rows for runtime/coverage. The
ablation-harness `runtime_total_sec` field is now treated only as a harness diagnostic;
for manuscript-facing ablation runtime, use `runtime_algorithm_sec`.

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
