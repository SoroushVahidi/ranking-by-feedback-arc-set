# Response to Reviewers (Markdown mirror)

**Authoritative upload file:** `manuscript/revision_20260825/response_to_reviewers.tex`  
**Manuscript:** Training-Free Ranking from Pairwise Comparisons via Acyclic Graph Construction  
**Branch HEAD at drafting:** `c109f0d3` (then response commit)

This mirror summarizes the LaTeX letter for repository reading. Prefer the `.tex` / compiled PDF for journal submission.

## Editor cover note (summary)

Major revision addressing Reviewers 1–4: title without “Scalable”; exact reachability add-back; secondary min-cut; canonical baseline rebuild; classical runtime honesty; ablation/sensitivity/family-aware stats; DF03/ranking–MWFAS theory; de-duplication.

## Reviewer 1

| # | Concern | Response gist | Manuscript refs |
|---|---|---|---|
| 1 | Novelty/positioning | Intro/Related Work rewrite; novelty table; no wholly-new pipeline claim; title change | §§1–1.2; Table 1 |
| 2 | Ablation/sensitivity | A0–A6; A0→A2 76/0/1; A1→A2 32/0/1; P2/P3 inert; zero_tol stable; Finance boundary | §§3.6–3.8; Table 7; Figs 1–2 |
| 3 | Pseudocode | Unified Algorithm 1 + parameter table | §§2.3, 2.8; Alg. 1; Table 2 |
| 4 | Theory/complexity/DF03/fallback | Prop. 1 equivalence; O(mn+m²); no DF03 under premature stop; Prop. 4 fallback | §§2.2, 2.9–2.11 |
| 5 | Future work | New Limitations/Future Work | §§4–6 |

## Reviewer 2

| # | Concern | Response gist | Refs |
|---|---|---|---|
| 1 | Novelty | Same positioning as R1.1 | Table 1 |
| 2 | Add-back | Proxy weakness; reachability; INS de-emphasized; min-cut secondary | §§2.5–2.6, 3.7–3.9 |
| 3 | GNN protocol | End-to-end trained; not inference-only; GPU ledger unavailable | §3.1 |
| 4 | Timeout bias | Common-completion primary; coverage; Finance separated | §§3.1, 3.4–3.5 |
| 5 | Oracle best-in-suite | De-emphasized; not deployable | §3.1; Tables 4–5 |
| 6 | Statistics/dependence | Wilcoxon/Holm/bootstrap; family-aware; SpringRank LOFO; BTL ratio | §§3.2–3.3 |
| 7 | Deterministic repeats | Runtime/timeout variability only | §§3.1, 4 |
| 8 | Scalable | Title changed; Finance boundary | Title; §§3.5–3.6 |
| 9 | Presentation | Protocol consolidation; repetition audit | Throughout |

## Reviewer 3

| # | Concern | Response gist | Refs |
|---|---|---|---|
| 1 | Ineffective INS/add-back | Own error; OURS≡INS3 topo-proxy; reachability 76/0/1 & 32/0/1 | §§2.5, 3.7 |
| 2 | Table 4/5 inconsistency | Stale aggregation; single canonical rebuild; SpringRank 0.802724 | §3.1; Tables 4–5 |
| 3 | Classical runtime | OURS slower than classical; ~8× vs trained GNN only | §3.4; Table 6 |
| 4 | Accuracy–runtime | Metric-specific; no universal dominance | Abstract; §§3.2–3.4, 5 |

## Reviewer 4

| # | Concern | Response gist | Refs |
|---|---|---|---|
| 1 | What is new | Prior/new separation + Table 1 | §§1–2 |
| 2 | DF03 guarantee | Idealized vs practical; no inheritance under timeout | §2.9; Prop. 4 |
| 3 | Multipass INS | P2/P3 nearly inert; not core | §§2, 3.8 |
| 4 | GNN protocol | Same as R2.3 | §3.1 |
| 5 | “Scalable” | Removed from title | Title |
| 6 | Writing/repetition | Intro rewrite + de-duplication | Throughout |
| 7 | Backbone/cycle ablations | A0–A6; C0/C1 small effect | §§3.7–3.8 |

## Coverage

See `RESPONSE_LETTER_COVERAGE_MATRIX.md` (100% answered).
