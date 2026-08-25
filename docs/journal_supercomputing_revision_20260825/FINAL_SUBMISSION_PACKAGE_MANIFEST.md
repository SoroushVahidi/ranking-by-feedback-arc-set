# Final Submission Package Manifest

Date: 2026-08-25  
Branch: `jsuper-runtime-provenance-fix-20260825`

## Package root

`manuscript/final_submission_package/`  
Archive: `manuscript/final_submission_package.zip`

## Included (submission-appropriate only)

| Path | Role |
|---|---|
| `main_ik.pdf` | Final manuscript PDF (18 pp) |
| `response_to_reviewers.pdf` | Response letter PDF (7 pp) |
| `cover_letter_revision.pdf` | Revision cover letter PDF (1 pp) |
| `manuscript/main_ik.tex` | Manuscript source |
| `manuscript/references.bib` | Bibliography |
| `figures/fig_runtime_vs_edges.pdf` | Figure 1, corrected `runtime_algorithm_sec` provenance |
| `figures/fig_structural_ablation.pdf` | Figure 2 |
| `response_to_reviewers/response_to_reviewers.tex` | Response source |
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
| Manuscript | `MANUSCRIPT_CLEAN_BUILD = PASS` | 18 |
| Response | `RESPONSE_CLEAN_BUILD = PASS` | 7 |
| Cover letter | `COVER_LETTER_CLEAN_BUILD = PASS` | 1 |

`SELF_CONTAINED_CLEAN_BUILD = PASS`  
No absolute paths; no symlinks required.

## Layout note

`main_ik.tex` uses `\graphicspath{{../figures/}}`, so compile from the package's
`manuscript/` directory with the sibling package-root `figures/` directory.

## Artifact hashes

| Artifact | Pages | SHA256 |
|---|---:|---|
| `manuscript/main_ik.pdf` | 18 | `6bac0dc2e2c2d177ddf7b07155104fca2c46d44be23fea22a09002cdc03e9686` |
| `response_to_reviewers/response_to_reviewers.pdf` | 7 | `091ff0a14df81de52adfbf62dddd824e485077673969197dbc77af61f28b549a` |
| `cover_letter/cover_letter_revision.pdf` | 1 | `667b5fb4f041a0952bb5adb66e2b024e30c70c0841f9df14ab9f40cd416749e0` |
| `final_submission_package.zip` | -- | `87cdbd4a894d6c2eab11836bb291b7b31815b8af11825ab88ef4671ebeda6f92` |

## Denominator note

Authoritative suite: intended 80 / loadable 78 (missing ERO + Halo2BetaData/HeadToHead); coverage 77/78, 78/78, 61/78.

## Cover letter

Addresses Professor Hamid R. Arabnia (Editor-in-Chief); includes Manuscript ID `feb25704-187e-4f95-8640-5e8c1ca26a94` and final title.
