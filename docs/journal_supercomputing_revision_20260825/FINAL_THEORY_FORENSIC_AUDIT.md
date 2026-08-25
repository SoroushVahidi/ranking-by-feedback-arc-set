# Final Theory Forensic Audit

Date: 2026-08-25

Cross-read Props/Remark in `main_ik.tex` against `THEORY_CLAIM_AUDIT.md` and supporting docs.

| Item | Required property | Manuscript status |
|---|---|---|
| Ranking ↔ MWFAS | Optimum-value equality only; many-to-many; no bijection | **Pass** (Prop 1 + explicit sentence) |
| Reachability add-back | DAG preserve; monotone; one-pass; single-edge inclusion-minimal; no global opt | **Pass** (Prop 2) |
| Min-cut exchange | Cut $v\to u$; acyclicity; $\Delta=w(C)-w(e)$; strict improve; finite term; no approx/global opt | **Pass** (Prop 3) |
| DF03 | Idealized vs practical; no auto-inherit under premature stop | **Pass** (Remark `rem:no_df03_timeout`) |
| Fallback | OPT>0; multiplicative unbounded; additive noted | **Pass** (Prop 4 proof) |
| Complexity | $O(mn+m^2)$ audited Phase A; no average-case theorem from wall-clock | **Pass** (§2.11) |

**Logical gaps requiring correction this pass:** none.

No theorem in response letter is stronger than the manuscript.
