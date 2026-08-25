# Response Letter Build Validation

Date: 2026-08-25

## Commands

```bash
cd manuscript/revision_20260825
latexmk -pdf -interaction=nonstopmode -halt-on-error response_to_reviewers.tex
```

Manuscript (unchanged this pass; prior Pass-4 build):

```bash
cd manuscript/revision_20260825/source
latexmk -pdf -interaction=nonstopmode -halt-on-error main_ik.tex
```

## Results

| Artifact | Path | Pages | Status |
|---|---|---:|---|
| Response letter | `manuscript/revision_20260825/response_to_reviewers.pdf` | 6 | Pass (exit 0) |
| Revised manuscript | `manuscript/revision_20260825/source/main_ik.pdf` | 17 | Pass (Pass-4; HEAD `c109f0d3`) |

## Warnings

- Minor overfull `\hbox` possible on long comment paraphrases; none fatal.
- No undefined references in response letter (no `\ref` used; human-readable section/table numbers).

## Visual inspection (response PDF, 6 pages)

| Check | Result |
|---|---|
| Editor cover note present | Pass |
| R1–R4 headings visible | Pass |
| Comment / Response / Changes structure | Pass |
| No overlapping text | Pass |
| Font size normal (11pt) | Pass |
| No broken equations | Pass (text-mode only) |
| Awkward mid-comment page splits | Acceptable (Comment 5 R1 ends p.3; R3 starts mid-page) |

## Consistency vs manuscript

| Topic | Match? |
|---|---|
| Title without Scalable | Yes |
| Novelty positioning | Yes |
| DF03 / fallback | Yes |
| Reachability / min-cut | Yes |
| Classical slower; GNN end-to-end ~8× | Yes |
| SpringRank 0.802724 | Yes |
| BTL upset_ratio stronger | Yes |
| Finance boundary | Yes |
| A0→A2 76/0/1; A1→A2 32/0/1 | Yes |
| Deterministic reps = runtime only | Yes |

**Manuscript fixes during response pass:** none.
