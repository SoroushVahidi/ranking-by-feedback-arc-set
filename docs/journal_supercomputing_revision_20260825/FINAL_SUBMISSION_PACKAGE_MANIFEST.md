# Final Submission Package Manifest

Date: 2026-08-25

## Package root

`manuscript/final_submission_package/`  
Archive: `manuscript/final_submission_package.zip`

## Included (submission-appropriate only)

| Path | Role |
|---|---|
| `main_ik.pdf` | Final manuscript PDF (17 pp) |
| `response_to_reviewers.pdf` | Response letter PDF (6 pp) |
| `manuscript/main_ik.tex` | Manuscript source |
| `manuscript/references.bib` | Bibliography |
| `figures/fig_runtime_vs_edges.pdf` | Figure 1 |
| `figures/fig_structural_ablation.pdf` | Figure 2 |
| `response/response_to_reviewers.tex` | Response source |

## Excluded by design

- `submitted_original/`
- `docs/` audits
- CSVs, scripts, experiment outputs
- git metadata
- `.aux`/`.log`/`.fls`/`.fdb_latexmk`
- PNG figure duplicates
- internal Markdown matrices

## Layout note

`main_ik.tex` uses `\graphicspath{{../figures/}}`, so compile from `manuscript/` with sibling `figures/` directory (as packaged).
