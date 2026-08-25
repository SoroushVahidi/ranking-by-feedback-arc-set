# Final Submission Package Manifest

Date: 2026-08-25  
Branch: `jsuper-manuscript-major-revision-20260825`

## Package root

`manuscript/final_submission_package/`  
Archive: `manuscript/final_submission_package.zip`

## Included (submission-appropriate only)

| Path | Role |
|---|---|
| `main_ik.pdf` | Final manuscript PDF (17 pp) |
| `response_to_reviewers.pdf` | Response letter PDF (6 pp) |
| `cover_letter_revision.pdf` | Revision cover letter PDF (1 pp) |
| `manuscript/main_ik.tex` | Manuscript source |
| `manuscript/references.bib` | Bibliography |
| `figures/fig_runtime_vs_edges.pdf` | Figure 1 |
| `figures/fig_structural_ablation.pdf` | Figure 2 |
| `response/response_to_reviewers.tex` | Response source |
| `cover_letter/cover_letter_revision.tex` | Cover letter source |

## Excluded by design

- `submitted_original/`
- `docs/` audits
- CSVs, scripts, experiment outputs
- git metadata
- `.aux`/`.log`/`.fls`/`.fdb_latexmk`
- PNG figure duplicates
- internal Markdown matrices

## Isolated clean builds

| Artifact | Status | Pages |
|---|---|---:|
| Manuscript | `MANUSCRIPT_CLEAN_BUILD = PASS` | 17 |
| Response | `RESPONSE_CLEAN_BUILD = PASS` | 6 |
| Cover letter | `COVER_LETTER_CLEAN_BUILD = PASS` | 1 |

`SELF_CONTAINED_CLEAN_BUILD = PASS`  
No absolute paths; no symlinks required.

## Layout note

`main_ik.tex` uses `\graphicspath{{../figures/}}`, so compile from `manuscript/` with sibling `figures/` directory (as packaged).

## Denominator note

Authoritative suite: intended 80 / loadable 78 (missing ERO + Halo2BetaData/HeadToHead); coverage 77/78, 78/78, 61/78.
