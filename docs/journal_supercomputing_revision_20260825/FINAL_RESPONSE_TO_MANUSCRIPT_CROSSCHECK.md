# Final Response ↔ Manuscript Cross-Check

Date: 2026-08-25

## Required result

**NO_RESPONSE_PROMISES_MISSING_FROM_MANUSCRIPT**

## Spot-checked response claims

| Response claim | Verified in `main_ik.tex` / PDF | OK? |
|---|---|---|
| Title without “Scalable” | Title page | Yes |
| Intro rewrite + Related Work + Table 1 | §§1–1.2; `tab:novelty_separation` | Yes |
| Algorithm 1 + Table 2 parameters | `alg:ours_canonical`; `tab:parameters` | Yes |
| Prop 1 ranking↔MWFAS (no bijection) | `prop:rank_mwfas` | Yes |
| Prop 3 min-cut; Prop 4 fallback; DF03 remark | Props/Remark present §§2.6, 2.9–2.10 | Yes |
| Complexity O(mn+m²) | §2.11 | Yes |
| Reachability Phase B + INS historical | §§2.5, 3.1 | Yes |
| Tables 4–5 quality; Table 6 runtime; Table 7 ablation | labels `tab:pairwise_quality_*`, `tab:runtime_wtl`, `tab:ablation_primary` | Yes |
| Figs 1–2 runtime/ablation | `fig:runtime_vs_edges`, `fig:ablation` | Yes |
| Coverage 77/79, 61/79; classical slower; ~8× GNN | §3.4 | Yes |
| A0→A2 76/0/1; A1→A2 32/0/1 | Table 7 | Yes |
| Finance boundary times | §3.5 | Yes |
| Family-aware / BTL ratio / SpringRank LOFO | §3.3 | Yes |
| Limitations + Future Work | §§4, 6 | Yes |
| Archived OURS_MFAS for Tables 4–6; reachability in ablation | Protocol + quality intro (presubmission fix) | Yes |
| A0–A6 defined in response at first use | R1 C2 | Yes |

## Reverse check (major manuscript changes mentioned)

Title, Intro, Related Work, novelty table, reachability, INS de-emphasis, min-cut, ranking↔MWFAS, fallback, DF03, unified pseudocode, parameters, corrected baselines, classical runtime, timeout/common-completion, statistics, family-aware, ablations, sensitivity, Finance, Limitations, Future Work, repetition cleanup — all represented where reviewer-relevant.

## Section numbering used in letter

Matches PDF: §1 Intro; §2 Method/Theory (2.2 equivalence … 2.11 complexity); §3 Experiments (3.1 protocol … 3.9 min-cut empirics); §4 Limitations; §5 Conclusion; §6 Future Work.
