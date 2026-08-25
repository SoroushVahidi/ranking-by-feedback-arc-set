# Introduction Revision Diff

Date: 2026-08-25  
Working file: `manuscript/revision_20260825/source/main_ik.tex`  
Baseline: `manuscript/submitted_original/source/main_ik.tex`  
Full patch: `introduction_revision.gitdiff`

## Paragraphs removed / replaced

- Opening “fundamental task… learning-based methods…” framing that implied this paper first develops a practical MWFAS ranking pipeline under upset metrics.
- Claim that the ranking–feedback connection “has not been developed into a practical… pipeline” (conflicts with [VK25]).
- “Favorable accuracy–runtime trade-offs on large comparison graphs” without classical/GNN qualification.
- Subsection “Ranking Problem and MWFAS” that presented INS1/2/3 as the concrete contribution preview.
- Closing Related Works sentence that restated an undifferentiated “practical ranking pipeline” contribution.

## Paragraphs rewritten

- Motivation: pairwise ranking → cycles → MWFAS; NP-hard; training-free objective.
- Explicit non-claim: not a new general MWFAS approximation algorithm.
- Explicit lineage: [VK25] + [CI03] for local-ratio, exact cycle-safe add-back, refinement.
- Equivalence paragraph: optimum-value equivalence; many-to-many correspondence; to be proved.
- New subsection **Scope, lineage, and contributions** with four numbered items.
- Empirical summary: competitive vs SpringRank/davidScore/SVD_NRS; BTL stronger on `upset_ratio`; slower than classical; faster than trained GNN end-to-end; Finance dense boundary.
- Related Works closing pointer to the contribution list (survey body left intact).

## Contribution claims changed

| Before (implicit) | After |
|---|---|
| Practical scalable MWFAS ranking pipeline + INS variants | Formalization / guarantee boundaries |
| — | Implementation-fidelity (topo proxy → exact reachability) |
| — | Secondary weighted min-cut exchange |
| Side-by-side classical+GNN eval as the novelty envelope | Expanded empirical validation (not 77→80 as novelty) |

## Claims softened

- Runtime vs classical: now **slower** than lightweight classical.
- Runtime vs GNN: **trained end-to-end** protocol only.
- Quality vs SpringRank family: **competitive**, not uniformly superior.
- BTL `upset_ratio`: advantage to BTL stated.
- Scalability: sparse/moderate density; Finance boundary.
- Dataset growth: not primary novelty.
- Approximation: timeout does **not** inherit nontrivial general guarantee.

## New theory positioning

Ranking–MWFAS optimum-value equivalence and DF03 transfer boundaries are listed as contribution (1); deferred detailed proofs remain for later section rewrites.

## Min-cut positioning

Contribution (3): secondary structural repair with monotone weighted-objective improvement; regime-specific empirics — **not** in submitted Method yet (next revision task).

## Runtime / scalability wording

Intro now avoids unqualified “scalable” for our method; uses qualified “Scalability is strong on…”; Related Works still uses “scalable” for SpringRank (baseline description, unchanged).

## Bibliography

Added verified `@article{VK25}` (arXiv:2412.16181v3) for the required prior-work citation.
