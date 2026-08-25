# Final Exact Reviewer Comment Audit

Date: 2026-08-25  
Worktree: `/tmp/ranking-jsuper-manuscript-major-revision`  
HEAD at audit start: `f0733efb` (pre-presubmission fixes)

## Verdict on local verbatim JoS decision email

**EXACT_REVIEWER_TEXT_UNAVAILABLE_LOCALLY**

Searched thoroughly in:
- `docs/journal_supercomputing_revision_20260824/` and `...20260825/`
- `manuscript/revision_20260825/`, `manuscript/submitted_original/`
- related worktrees under `/tmp/ranking-jsuper-*`
- agent transcripts for pasted decision-letter markers
- home Downloads/Documents/Mail (no JoS decision artifact found)

No single file contains the publisher’s verbatim Reviewer 1–4 report text.

## Strongest preserved evidence used

| Source | Role |
|---|---|
| `REVIEWER_TO_LATEX_CHANGE_MATRIX.md` | concern → manuscript location |
| `REVIEWER_MASTER_MATRIX.md` / `REVIEWER_TECHNICAL_AUDIT.md` | technical concern inventory |
| `NOVELTY_THEORY_REVIEWER_MAP.md` | R1/R2/R4 novelty/theory issues |
| `REVIEWER_EXPERIMENT_RESPONSE_TEMPLATE.md` / `REVIEWER_ABLATION_FINAL_ANALYSIS.md` | experimental sub-requests |
| User structured R1(5)/R2(9)/R3(4)/R4(7) outlines across revision passes | numbering used in response letter |

Comment boxes in `response_to_reviewers.tex` are concise restatements of those preserved concerns.

## Coverage (25/25)

| Reviewer | # | Strongest preserved concern | Response location | Manuscript address | Sub-requests answered? | Mismatch | Status |
|---|---:|---|---|---|---|---|---|
| R1 | 1 | Novelty vs DF03/VK25 | R1 C1 | §§1–1.2; Table 1; title | Yes | None | ANSWERED |
| R1 | 2 | Stage ablation + sensitivity + scale | R1 C2 | §§3.1, 3.5–3.8; Table 7; Figs 1–2 | Yes (A0/A1/A2/A4; P; zero_tol; refine; Finance) | None | ANSWERED |
| R1 | 3 | Full pseudocode/parameters | R1 C3 | §§2.3, 2.8; Alg 1; Table 2 | Yes | None | ANSWERED |
| R1 | 4 | Theory/complexity/DF03/fallback | R1 C4 | §§2.2, 2.9–2.11; Props 1,4 | Yes | None | ANSWERED |
| R1 | 5 | Future work/applications | R1 C5 | §§4–6 | Yes (directions, not evaluated domains) | None | ANSWERED |
| R2 | 1 | Novelty | R2 C1 | Table 1; §§1–2 | Yes | None | ANSWERED |
| R2 | 2 | Add-back contribution | R2 C2 | §§2.5–2.6, 3.7–3.9 | Yes | None | ANSWERED |
| R2 | 3 | GNN timing fairness | R2 C3 | §3.1, §3.4 | Yes | None | ANSWERED |
| R2 | 4 | Timeout/missingness bias | R2 C4 | §§3.1, 3.4–3.5 | Yes | None | ANSWERED |
| R2 | 5 | Oracle best-in-suite | R2 C5 | §3.1; Tables 4–5 captions | Yes | None | ANSWERED |
| R2 | 6 | Stats / Basketball dependence | R2 C6 | §§3.2–3.3 | Yes | None | ANSWERED |
| R2 | 7 | Deterministic repetitions | R2 C7 | §§3.1, 4 | Yes | None | ANSWERED |
| R2 | 8 | “Scalable” | R2 C8 | Title; §§3.5–3.6, 4 | Yes | None | ANSWERED |
| R2 | 9 | Presentation/repetition | R2 C9 | Throughout; §§3.1, 4–5 | Yes | None | ANSWERED |
| R3 | 1 | Ineffective INS/add-back | R3 C1 | §§2.5, 3.1, 3.7–3.8 | Yes | None | ANSWERED |
| R3 | 2 | Table 4/5 inconsistency | R3 C2 | §3.1; Tables 4–5 | Yes | None | ANSWERED |
| R3 | 3 | Classical runtime | R3 C3 | §3.4; Table 6 | Yes | None | ANSWERED |
| R3 | 4 | Accuracy–runtime honesty | R3 C4 | Abstract; §§3.2–3.4, 5 | Yes | None | ANSWERED |
| R4 | 1 | What is scientifically new | R4 C1 | §§1–2; Table 1 | Yes | None | ANSWERED |
| R4 | 2 | DF03 inheritance | R4 C2 | §§2.9–2.10, 4 | Yes | None | ANSWERED |
| R4 | 3 | Multipass INS oversold | R4 C3 | §§2, 3.1, 3.8 | Yes | None | ANSWERED |
| R4 | 4 | GNN protocol | R4 C4 | §3.1 | Yes | None | ANSWERED |
| R4 | 5 | Scalable oversell | R4 C5 | Title; §§3.5–3.6, 4 | Yes | None | ANSWERED |
| R4 | 6 | Writing/repetition | R4 C6 | Throughout | Yes | None | ANSWERED |
| R4 | 7 | Backbone/cycle ablations | R4 C7 | §§3.7–3.8; Table 7 | Yes | None | ANSWERED |

**TOTAL: 25/25 ANSWERED.**

## Author action required

Paste the JoS decision email beside the response letter once before upload to confirm no publisher-only sub-bullet was missed.


## Author-provided verbatim Reviewer 3 text (decision-email correspondence)

Source: **author-provided verbatim reviewer text from the decision-email correspondence** (not a file originally stored in this repository).

> First, the weight-prioritized add-back stage (INS1/INS2/INS3) is the principal algorithmic increment over Demetrescu and Finocchi (2003), yet OURS-MFAS and OURS-MFAS-INS3 report digit-identical values across all six columns of Table 4, with INS1 slightly worse than no add-back at all. This is algorithmically explicable — accepting only arcs that are forward with respect to a fixed topological order cannot alter the set of rankings that order permits — but it means the paper's flagship contribution yields no measurable benefit in its present form.

> if the author can reconcile the tables, adopt a reachability-aware insertion rule so that the add-back stage genuinely contributes, and add runtime comparisons against the training-free baselines, I think this work has every prospect of becoming a solid contribution

Status after this pass: **CLOSED** in manuscript (OURS-Reach headline tables + ablation history + classical runtimes).
