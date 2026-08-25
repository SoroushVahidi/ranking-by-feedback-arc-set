# Manuscript Pass 2 Diff Summary

Date: 2026-08-25  
Baseline HEAD before pass 2: `a04af55a`  
Working file: `manuscript/revision_20260825/source/main_ik.tex`

## Related Work changes

- Restructured into: FAS/MWFAS; ranking; statistical/spectral; GNN; local-ratio/add-back lineage; relation to VK25.
- Explicit prior vs fidelity vs secondary min-cut novelty separation.
- Added compact comparison Table `tab:novelty_separation`.

## Method changes

- Renamed section to **Method and Theory**.
- Canonical pipeline: Phase~A (prior) → Phase~B exact reachability (fidelity) → optional min-cut (new) → Phase~C (prior).
- Removed INS1/2/3 as headline method variants; retained as historical topo-proxy comparison.
- Unified Algorithm~\ref{alg:ours_canonical}; consolidated parameter Table `tab:parameters`.

## Theory inserted

- Prop. ranking↔MWFAS optimum-value equivalence (many-to-many).
- Prop. exact reachability add-back (acyclicity, monotone, one-pass, single-edge inclusion-minimal).
- Prop. min-cut exchange (acyclicity, $\Delta<0$, finite termination; no global opt/ratio).
- Remark: **no DF03 guarantee for premature practical runs**.
- Prop. identity-fallback multiplicative unboundedness (OPT$>0$ construction).
- Complexity corrected to $O(mn+m^2)$ for audited Phase~A; budget ≠ asymptotics.

## INS framing

Method no longer presents INS multipass as quality innovations. Results section untouched (still submitted wording).

## DF03 wording

Idealized vs practical split; explicit non-inheritance under timeout/fallback.

## Min-cut subsection

Dedicated optional secondary repair with algorithm + proofs.

## Not changed (deferred)

Abstract; Experimental Results narrative/tables; Conclusion; response letter.

## Build

- Command: `latexmk -pdf -interaction=nonstopmode -halt-on-error main_ik.tex`
- Pages: **19**
- PDF: `manuscript/revision_20260825/source/main_ik.pdf`
