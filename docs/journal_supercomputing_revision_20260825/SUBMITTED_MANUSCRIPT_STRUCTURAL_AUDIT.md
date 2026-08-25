# Submitted Manuscript Structural Audit

Date: 2026-08-25  
Source: `manuscript/submitted_original/source/main_ik.tex` (20 pp. reconstructed PDF)

## Confirmation: reviewed manuscript

Title matches exactly:  
“Scalable and Training-Free Ranking from Pairwise Comparisons via Acyclic Graph Construction”.

Recognizable submitted features present: MWFAS formulation; local-ratio cycle breaking (CI03); OURS-MFAS / INS1 / INS2 / INS3; ~80-dataset evaluation; classical + GNNRank comparisons; Finance timeout discussion; upset metrics; best-in-suite GNN runtime tables.

**Verdict: ZIP matches the reviewed manuscript.**

## Structural outline

| Block | Location / notes |
|---|---|
| Abstract | After `\maketitle` |
| Keywords | Custom `\keywords` |
| **Introduction** (`sec:intro`) | Includes definitions + nested Related Works |
| — Definitions | Ranking Problem; MWFAS |
| — Ranking/MWFAS subsection | Pipeline preview; INS1/2/3 named |
| — Related Works | Pairwise ranking baselines; MWFAS literature |
| **Framework / Method** (`sec:framework`) | Phase 1, Phase 2 INS, scores, Phase C |
| Theory/complexity remarks | Interleaved; DF03 guarantee referenced |
| **Experiments** (`sec:exp`) | Protocol, datasets (~80), methods, budgets |
| Results / tables | Classical + GNN comparisons; runtime tables |
| Runtime/scalability | GNN speedups; Finance bottleneck |
| Limitations | Dense Finance; finer basketball tail |
| Conclusion | Restates scalable/training-free + INS |
| Bibliography | `references.bib` / `apalike` |

## Algorithms / formal items

- Algorithm environments for Phase 1 / add-back (algorithm2e)
- Definitions: Ranking Problem; MWFAS
- No numbered theorems/propositions in submitted text (guarantee cited from CI03)

## Tables / figures

- Multiple `table` environments with booktabs (classical/GNN/runtime summaries)
- **No** `\includegraphics` figures in the ZIP

## Major numerical / claim themes in submitted text

- Competitive with classical baselines; substantial runtime advantage vs GNNRank
- “Scalable” framing throughout Abstract/Intro/Conclusion
- INS1/2/3 presented as useful multi-pass recovery mechanism
- ~80 instances under 1800 s budgets
- Best-in-suite GNN runtime comparisons (median ~10× speedup in one table)
- Finance non-completion under 1800 s acknowledged
- Approximation guarantee attributed to underlying CI03 local-ratio (with disclaimers)

## Novelty claims requiring later correction (paper-wide; Intro first)

See reviewer matrix and Introduction rewrite: prior local-ratio/add-back lineage; topo-proxy fidelity; no general timeout guarantee; classical slower-than; SpringRank competitiveness; BTL upset_ratio; INS multipass de-emphasis; no universal scalability.
