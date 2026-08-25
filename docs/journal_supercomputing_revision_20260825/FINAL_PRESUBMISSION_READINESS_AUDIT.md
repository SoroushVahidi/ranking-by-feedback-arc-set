# Final Presubmission Readiness Audit

Date: 2026-08-25  
Branch: `jsuper-manuscript-major-revision-20260825`  
Worktree: `/tmp/ranking-jsuper-manuscript-major-revision`

## Verdict

**READY_AFTER_MINOR_AUTHOR_CHECK**

## Why not READY_FOR_RESUBMISSION

Exact JoS decision-email wording is **EXACT_REVIEWER_TEXT_UNAVAILABLE_LOCALLY**.  
The response letter is complete against preserved matrices (25/25), but the author must once overlay the publisher email before upload.

## Blockers (author-only; not scientific)

1. Confirm response letter against the JoS decision email (verbatim text not stored in-repo).
2. Confirm comfort with Tables 4–6 reporting archived topo-proxy `OURS_MFAS` while recommending the reachability-aware pipeline (now explicitly disclosed in Abstract/Protocol/Results/Conclusion and the response letter).

## What is complete

| Area | Status |
|---|---|
| Manuscript science / experiments closed | Yes |
| Theory audits | Pass |
| Numerical forensic | NO_UNTRACEABLE_NUMERICAL_CLAIMS |
| Response↔manuscript promises | NO_RESPONSE_PROMISES_MISSING_FROM_MANUSCRIPT |
| Reviewer coverage | 25/25 |
| Clean package + isolated build | Pass |
| submitted_original immutable | Pass |
| No GPU/SLURM/experiments this pass | Pass |

## Build artifacts

| Artifact | Pages | SHA256 |
|---|---:|---|
| `manuscript/revision_20260825/source/main_ik.pdf` | 17 | `837999e0367aa58d9e3dd06109b8e37dc6bf7bc2a138f05efdff52afffc5e61d` |
| `manuscript/revision_20260825/response_to_reviewers.pdf` | 6 | `7117e29f0c8341ee170fd118c527dad9f2dd2902498b45102d52fcebcb16c059` |
| `manuscript/final_submission_package.zip` | — | `18a46ad432ba753f2f2994c10b6d761bb811999830914c8e75a44b5d229e19c2` |

Build: `latexmk -pdf -interaction=nonstopmode -halt-on-error` (XeLaTeX via latexmk).  
Warnings: minor overfull boxes; algorithm2e UTF-8 (pre-existing). No undefined refs/citations.
