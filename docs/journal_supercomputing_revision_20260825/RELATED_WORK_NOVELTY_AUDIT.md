# Related-Work / Novelty Audit (Pass 2)

Date: 2026-08-25

## Must NOT be claimed as new — status in revised LaTeX

| Claim | Status in revised text |
|---|---|
| Local-ratio cycle breaking | Marked **prior** (DF03/VK25); used, not invented |
| Exact cycle-safe reinsertion | Marked **prior**; “fidelity restore” after topo-proxy weakening |
| Weight-prioritized add-back | Marked **prior** (DF03 suggestion / VK25) |
| Ternary / order-preserving refinement | Marked **prior lineage** (VK25) |
| Multipass INS2/INS3 as core innovation | **De-emphasized**; historical submitted variants only |

## Supported new / clarified claims present

| Claim | Supported by |
|---|---|
| Formal ranking↔MWFAS optimum-value equivalence | Prop.~\ref{prop:rank_mwfas} + audit doc |
| DF03 does not transfer to premature practical runs | Remark~\ref{rem:no_df03_timeout} |
| Fallback identity ordering unbounded multiplicative gap | Prop.~\ref{prop:fallback} |
| Implementation complexity $O(mn+m^2)$ | Complexity subsection + `COMPLEXITY_AUDIT.md` |
| Weighted min-cut exchange (secondary) | Prop.~\ref{prop:mincut} + Alg.~\ref{alg:mincut_exchange} |
| Expanded classical/GNN evaluation (positioned; tables deferred) | Intro + Related Work table |

## Table~\ref{tab:novelty_separation}

Compares DF03 / VK25 / this work on verified dimensions only. No fabricated prior-art cells.

## Residual risk (Results still submitted text)

Experimental Results / Conclusion still use submitted INS-centric language. Deferred to pass 3; Method/Related Work now consistent with revised positioning.
