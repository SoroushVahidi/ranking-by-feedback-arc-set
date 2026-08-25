# Final Canonical Method Alignment Audit

Date: 2026-08-25

## Alignment verdict

**CANONICAL_METHOD_ALIGNMENT_RESOLVED**

## Global readiness verdict

**READY_AFTER_MINOR_AUTHOR_CHECK**

(Exact full JoS decision email still not stored locally; Reviewer 3 critical algorithm/table issue is closed using author-supplied verbatim text.)

## Evidence

- Canonical method = A4 = OURS-Reach
- Headline Tables 4–6 rebuilt from `a4_gnnrank_metrics.csv` + leaderboard baselines
- Ablation retains A0–A6 / INS history including 76/0/1 and 32/0/1
- Runtime: slower than most classical; ~37–45× vs trained GNN end-to-end
- BTL still stronger on upset_ratio
- Min-cut not in headline tables

## Reviewer 3 status

**CLOSED** — reachability-aware insertion is Method + principal tables; classical runtimes included; tables reconciled.

## CANONICAL_METHOD_MATCHES_HEADLINE_TABLES

**PASS**
