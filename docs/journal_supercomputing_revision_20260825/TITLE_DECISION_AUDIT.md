# Title Decision Audit

Date: 2026-08-25

## Current (submitted / Pass 1–3) title
“Scalable and Training-Free Ranking from Pairwise Comparisons via Acyclic Graph Construction”

## Alternatives considered
1. Keep current title  
2. “Training-Free Ranking from Pairwise Comparisons via Acyclic Graph Construction”  
3. “Training-Free Ranking from Pairwise Comparisons via MWFAS-Inspired Acyclic Graph Construction”  
4. “Fast Training-Free Ranking …” (rejected: “fast” still oversells vs classical)

## Recommendation
**Option 2** — remove “Scalable”.

## Reasoning
- Reviewers 2 and 4 questioned unqualified scalability.
- Evidence supports strong practical timing on sparse/moderately dense evaluated graphs, but Finance is an explicit large-dense failure/timeout boundary.
- “Training-Free” remains accurate and distinctive.
- “MWFAS-Inspired” is accurate but lengthens the title; Related Work/Method already carry that positioning.
- Attractiveness remains adequate without “Scalable”.

## Action taken
Title updated to Option 2 in `main_ik.tex`. Body uses “scalability boundary” / “empirical scale” language rather than “scalable alternative.”
