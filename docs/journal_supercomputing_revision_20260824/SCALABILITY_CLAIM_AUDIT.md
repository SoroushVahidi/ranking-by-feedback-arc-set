# Scalability Claim Audit

Date: 2026-08-24
Branch: `jsuper-runtime-coverage-final-20260824`

Based on `CLASSICAL_RUNTIME_FINAL.md` (E1/E2 evidence).

## MUST NOT CLAIM

1. **"OURS is faster than classical ranking methods"** — OURS is 2.6x to 536x slower than all 10 classical baselines on pairwise common completions. The median runtime ratio is always >1 (OURS is always slower on the median).

2. **"Universal scalability"** — OURS times out on `finance` (n=1315, m=1,729,225, density≈1.0). The O(mn+m²) Phase A does not complete within 1800s. This is a concrete, honest counter-example.

3. **"OURS scales to arbitrary graph sizes"** — no evidence beyond n=602 for successful OURS runs.

## CAN CLAIM

1. **"OURS achieves strong runtime advantage relative to trained GNN baselines"** — 60/60 wins vs DIGRAC and ib, median ratio ~0.12x (8x faster), bootstrap CI excludes 1. Supported by Holm-corrected p < 10⁻¹⁰.

2. **"OURS completes on most evaluated graphs"** — 77/79 (97.5%) coverage, comparable to classical baselines (98.7%). The only timeout is `finance`.

3. **"OURS achieves better ranking quality (upset_simple, upset_naive) than all classical baselines on pairwise common completions"** — W/T/L records favor OURS against all 10 classical baselines on upset_simple and upset_naive.

## REQUIRES QUALIFICATION

1. **Scalability** — must be stated as "scales to n≤602 in the evaluated suite" with explicit acknowledgment of the `finance` timeout.

2. **Large/dense graphs** — the `finance` case (n=1315, density≈1.0) is a known boundary. Any scalability claim must note this limitation and reference the O(mn+m²) complexity analysis (`COMPLEXITY_AUDIT.md`).

3. **Refinement complexity** — Phase C (ternary-search ratio refinement) adds O(m·passes) time. Runtime figures include refinement; a no-refinement variant would be faster but with worse ratio metrics.

4. **upset_ratio** — OURS loses against btl (1/77 wins) and PageRank (14/77 wins) on upset_ratio. Any claim about ranking quality must distinguish upset_simple/naive (OURS wins) from upset_ratio (mixed results).
