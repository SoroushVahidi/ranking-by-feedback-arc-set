# Theory Claim Audit (Pass 2)

Date: 2026-08-25  
Source: `manuscript/revision_20260825/source/main_ik.tex`

| Manuscript statement | Source / proof | Prior / new | Env | Confidence | Reviewer concern |
|---|---|---|---|---|---|
| $\mathrm{OPT}_{\mathrm{rank}}=\mathrm{OPT}_{\mathrm{MWFAS}}$ (value equivalence; many-to-many) | `RANKING_MWFAS_EQUIVALENCE.md`; Prop.~\ref{prop:rank_mwfas} | **New proof** (asserted in VK25) | Proposition | High | R1 theory |
| Exact reachability add-back preserves acyclicity; monotone; one-pass; single-edge inclusion-minimal | `REACHABILITY_ADDBACK_DESIGN.md`; Prop.~\ref{prop:reachability_addback} | **Prior mechanism**; **new formalization** of properties | Proposition | High | R1/general add-back |
| Min-cut exchange: acyclicity, $\Delta=w(C)-w(e)<0$, finite termination; no global opt / no ratio | `MINCUT_MANUSCRIPT_EVIDENCE_SYNTHESIS.md`; Prop.~\ref{prop:mincut} | **New secondary** | Proposition | High | Novelty / secondary algo |
| Idealized DF03 $\lambda$-guarantee applies only under published completion assumptions | `DF03_PRIMARY_THEOREM_VERIFICATION.md`, `APPROXIMATION_GUARANTEE_AUDIT.md` | **Implementation qualification** | Remark | High | R4 guarantee |
| **No DF03 guarantee for premature practical runs** | Same | **Negative / qualification** | Remark~\ref{rem:no_df03_timeout} | High | R4 |
| Identity fallback: $L(R_{\mathrm{fb}})/\mathrm{OPT}$ unbounded for all $M$ | `APPROXIMATION_GUARANTEE_AUDIT.md` §3.1; Prop.~\ref{prop:fallback} | **New negative result** | Proposition | High | R1 fallback bound |
| Phase~A unbudgeted complexity $O(mn+m^2)$ for audited impl. | `COMPLEXITY_AUDIT.md` | **Corrected claim** | Complexity § | High | R1 complexity |
| Wall-clock budget ≠ average-case complexity | Same | Qualification | Text | High | R1/R4 |
| Local-ratio Phase~A is prior | DF03 / VK25 | **Prior** | Method | High | Novelty |
| Exact cycle-safe / weight-ordered reinsertion prior | DF03 / VK25 | **Prior**; fidelity restore | Method | High | Novelty |
| Ternary/order-preserving refinement prior lineage | VK25 | **Prior** | Method | High | Novelty |
| INS multipass topo-proxy is historical | Ablation + lineage | Not novelty | Method | High | R3/ablation |

## Explicit flags

- **Prior work:** Phase~A, exact add-back idea, weight order, refinement.
- **New proof:** ranking↔MWFAS value equivalence; add-back propositions; min-cut propositions; fallback impossibility.
- **Negative result:** fallback multiplicative unboundedness; no DF03 under timeout.
- **Implementation qualification:** $O(mn+m^2)$; timeout/fallback/forced-progress vs idealized DF03.
