# Manuscript Pass-3 Validation

Date: 2026-08-25

| Check | Result |
|---|---|
| `submitted_original/` unchanged | Pass |
| Revision builds | Pass (`latexmk -pdf`) |
| Undefined citations/refs | None |
| Table 4/5 replaced by pairwise canonical tables | Pass |
| Denominators 80/79/77/60 consistent in protocol | Pass |
| `_AUTO` excluded | Pass |
| No OURS-faster-than-classical | Pass |
| No universal superiority | Pass |
| No oracle-as-deployable headline | Pass |
| Finance statuses present | Pass |
| Common-completion n cross-checked vs CSV | Pass |
| New experiments | **None** |

## Build
- Command: `latexmk -pdf -interaction=nonstopmode -halt-on-error main_ik.tex`
- Pages: 17
- PDF: `manuscript/revision_20260825/source/main_ik.pdf`
- Warnings: minor overfull (~6–17pt) PRE_EXISTING/algorithm2e UTF-8; no catastrophic table overflow after split
