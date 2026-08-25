# Canonical Method ↔ Table Alignment Audit

Date: 2026-08-25

## Canonical revised method (from Method + protocol)

| Question | Answer |
|---|---|
| Is canonical main method A2? | **No** (A2 = reachability without Phase C refinement) |
| Is it A4? | **Yes** — Phase A + exact reachability add-back + Phase C refinement |
| Are A5/A6 optional/secondary? | **Yes** — min-cut off in headline tables |
| Principal table method name | **OURS-Reach** (= internal config A4) |

Verified from `STRUCTURAL_VARIANTS` in `run_reviewer_ablation.py` and revised `main_ik.tex` Methods paragraph.

## Principal table decision

**OPTION A (implemented):** Replace Tables 4–6 with OURS-Reach (A4) under GNNRank `calculate_upsets` metrics.

Legacy OURS_MFAS / INS retained only in ablation/history.

## Min-cut placement

**Decision:** min-cut **not** in principal Tables 4–6; only ablation + §3.9.

## CANONICAL_METHOD_MATCHES_HEADLINE_TABLES

**PASS**
