# Response Letter Theory Audit

Date: 2026-08-25

| Reviewer concern | Response claim | Manuscript item | Supporting doc | Strength check |
|---|---|---|---|---|
| Ranking–MWFAS relation | Optimum-value equality; many-to-many | Prop.~\ref{prop:rank_mwfas} (Prop. 1) | `RANKING_MWFAS_EQUIVALENCE.md` | Not stronger than Prop. 1 |
| Exact add-back | Acyclicity / one-pass / single-edge inclusion-minimal | Prop.~\ref{prop:reachability_addback} | `REACHABILITY_ADDBACK_DESIGN.md` | Not claiming global MWFAS opt |
| Min-cut | Strict weighted-FAS improvement; no global opt/ratio | Prop.~\ref{prop:mincut} | `MINCUT_MANUSCRIPT_EVIDENCE_SYNTHESIS.md` | Explicitly secondary |
| DF03 | No auto-inheritance under premature practical runs | Remark~\ref{rem:no_df03_timeout} §2.9 | `APPROXIMATION_GUARANTEE_AUDIT.md` | Matches manuscript |
| Fallback | No nontrivial multiplicative bound | Prop.~\ref{prop:fallback} | same | OPT>0 construction |
| Complexity | Audited Phase A O(mn+m²) | §2.11 | `COMPLEXITY_AUDIT.md` | Idealized full completion |

**Rule satisfied:** no response-letter theorem claim exceeds the manuscript.
