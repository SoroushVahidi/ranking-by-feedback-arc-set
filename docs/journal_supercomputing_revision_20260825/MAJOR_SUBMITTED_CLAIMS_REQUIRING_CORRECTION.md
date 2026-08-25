# Major Submitted Claims Requiring Correction

Date: 2026-08-25  
Source scan: `manuscript/submitted_original/source/main_ik.tex`

| Claim theme | Where it appears | Required correction |
|---|---|---|
| OURS faster / favorable vs classical | Intro/Results runtime framing | OURS is **slower** than lightweight classical (SpringRank/BTL/PageRank/…); only claim speed vs **trained GNN end-to-end** |
| Universal / unqualified “scalable” | Abstract, Intro, Conclusion, Framework | Qualify: strong on evaluated sparse/moderately dense; Finance = large dense boundary |
| INS2/INS3 as quality innovations | Intro, Method, Conclusion | Multipass is weak vs exact reachability; do not present as major quality innovations |
| Exact reachability reinsertion as newly invented | Implied novelty of Phase 2 | Prior in DF03 / VK25; this paper’s finding is **implementation fidelity** |
| Timeout-bounded practice inherits DF03 guarantee | Framework opening | Audit: guarantee does **not** transfer unconditionally; no nontrivial general early-stop guarantee |
| Best-in-suite as competitor | Results runtime tables | Post-hoc oracle envelope only |
| 10 deterministic repetitions ⇒ ranking robustness | Protocol (if claimed) | Shows determinism, not ranking robustness |
| Universal beat of SpringRank/davidScore/SVD_NRS | Results storytelling | Family-aware: **competitive**, not robustly superior |
| OURS beats BTL on upset_ratio | Any residual claim | **False direction**: BTL stronger on upset_ratio across families |
| 77→80 as major novelty | Scope language | Not a major contribution |

Intro rewrite in this pass corrects positioning for these themes; remaining sections deferred.
