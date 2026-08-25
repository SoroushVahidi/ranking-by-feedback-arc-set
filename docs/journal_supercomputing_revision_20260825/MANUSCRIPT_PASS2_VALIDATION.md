# Manuscript Pass-2 Validation

Date: 2026-08-25

| Check | Result |
|---|---|
| Branch / worktree | `jsuper-manuscript-major-revision-20260825` @ `/tmp/ranking-jsuper-manuscript-major-revision` |
| `submitted_original/` unchanged | Pass (`git diff` empty; ZIP SHA256 preserved) |
| Revision builds | Pass (`latexmk -pdf`, exit 0) |
| Undefined citations | None |
| Undefined references | None |
| Theorem labels unique | Pass |
| Bib keys exist | Pass (incl. `VK25`) |
| No claim practical timeout inherits DF03 | Pass (Remark~\ref{rem:no_df03_timeout}) |
| No claim min-cut global optimum | Pass |
| No claim reachability reinsertion newly invented | Pass (fidelity / prior) |
| Unsupported novelty (local-ratio / exact add-back / weight order / ternary as new) | Not claimed in Method/Related Work |
| New experiments | **None** |

## Warnings

- **PRE_EXISTING:** algorithm2e UTF-8; experimental table overfull/underfull boxes.
- **NEW (minor):** Overfull `\hbox` (~6.18pt) in DF03 idealized/practical paragraph (`main_ik.tex` ~341).
