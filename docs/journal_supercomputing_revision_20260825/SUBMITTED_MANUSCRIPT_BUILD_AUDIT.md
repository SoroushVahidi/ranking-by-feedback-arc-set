# Submitted Manuscript Build Audit

Date: 2026-08-25

## Environment

| Item | Value |
|---|---|
| Compiler driver | `latexmk` |
| Engine | XeLaTeX (via latexmk default in this environment) |
| Bibliography | `bibtex` + `apalike` |
| Command | `latexmk -pdf -interaction=nonstopmode -halt-on-error main_ik.tex` |
| Working directory | `manuscript/submitted_original/source/` |

## Result

| Item | Value |
|---|---|
| Build | **SUCCESS** (exit 0) |
| PDF | preserved as `manuscript/submitted_original/submitted_reconstructed.pdf` |
| PDF SHA256 | `da38129b3e5c3e3ec5c0d8c86754da4e58faa5e1e6ceb972ddb4d1565f82961b` |
| Page count | **20** |
| Source modifications required | **None** |

## Warnings (PRE_EXISTING)

- Overfull/underfull `\hbox` in long tables/paragraphs
- `algorithm2e.sty` Invalid UTF-8 byte warnings (package encoding)
- No fatal errors; citations resolved in pristine build

Generated auxiliaries were removed from `submitted_original/source/` after freezing the PDF so that directory retains only the three submitted files.
