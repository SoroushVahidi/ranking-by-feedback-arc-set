# Introduction Rewrite Plan

Date: 2026-08-24

This is a structural plan, not a full manuscript rewrite. It is built to
directly resolve Reviewer 4's "introduction/positioning problem" as diagnosed
in `NOVELTY_THEORY_REVIEWER_MAP.md`: the positioning problem plausibly stems
from not clearly differentiating this manuscript from the authors' own
closely related prior arXiv paper [VK25] (arXiv:2412.16181, "Minimum
Weighted Feedback Arc Sets for Ranking from Pairwise Comparisons," Vahidi &
Koutis) — see `NOVELTY_LITERATURE_MATRIX.md` for the full discovery and
evidence.

## Recommended structure

1. **Problem/motivation.** Ranking from pairwise comparisons; why
   inconsistency (cycles in the comparison graph) is intrinsic to real data.
2. **Limitation of training-dependent ranking.** GNN-based approaches
   (GNNRank/He et al. 2022 and successors) require training, hyperparameter
   tuning, and GPU/compute resources disproportionate to the problem size for
   many practical settings.
3. **The MWFAS viewpoint.** State the ranking-MWFAS connection *with the
   formal proposition* from `RANKING_MWFAS_EQUIVALENCE.md` (exact equality of
   optimum values, many-to-many solution correspondence — not the informal
   assertion [VK25] made). Cite [VK25] explicitly here as the paper that
   first proposed using this connection operationally for ranking via a
   local-ratio heuristic, and cite [DF03] as the origin of that heuristic.
4. **Precise gap.** State plainly, in one place: (a) [VK25] asserted the
   MWFAS connection informally without proof — this manuscript supplies one;
   (b) [VK25]'s own Algorithm 1 specifies an *exact* reachability-based
   cycle-safety test for edge reinsertion, but the accompanying/evolved
   codebase implements a strictly weaker proxy — this manuscript diagnoses
   that gap and (pending the sibling workstream's final status) reports a
   corrected implementation; (c) [VK25]'s evaluation used a smaller,
   GNN-baseline-only benchmark with no dense/near-complete-graph case — this
   manuscript evaluates against ten classical baselines plus GNN methods
   across 80 datasets including a dense stress case; (d) [VK25] made no
   complexity or approximation-guarantee analysis of its own implementation —
   this manuscript audits both precisely, including a proof that the
   implementation's timeout fallback carries no error bound in general
   (`APPROXIMATION_GUARANTEE_AUDIT.md`).
5. **What this work does.** The three (or four) contribution bullets from
   `NOVELTY_VERDICT.md`, verbatim or lightly adapted.
6. **Explicit limits of contribution.** State once, precisely — per the
   task's own instruction not to repeat "we do not claim a new approximation
   guarantee" multiple times: *"We do not claim a new approximation
   algorithm for MWFAS; Phase A directly reuses the local-ratio heuristic of
   [DF03] as already adopted in [VK25]. Our contribution is (i) a formal
   correctness/complexity audit of that heuristic's shipped, time-budgeted
   implementation, showing its approximation guarantee does not
   unconditionally transfer, (ii) a diagnosis and fix for a fidelity gap in
   the edge-reinsertion step relative to [VK25]'s own specification, and
   (iii) a substantially larger empirical evaluation."* One sentence, one
   place, not repeated.
7. **Contribution bullets.** Restate 5's bullets as a compact itemized list
   for skimmability (standard practice), without re-arguing them.

## Title recommendation

The task asks whether "Scalable" should remain, citing finance's timeout,
dense-graph limitations, and "O(n² refinement memory" as reasons to
reconsider. Per `COMPLEXITY_AUDIT.md`, the O(n²) *memory* characterization is
**not accurate for the current/legacy pipeline** (Phase C is O(m) memory;
the only O(n²) memory structure in this project is the sibling branch's
bounded, opt-in reachability matrix). The genuine scalability caveat, however
— confirmed directly from source and empirically on `finance` — is **Phase
A's O(mn+m²) worst-case time on dense graphs**, which is real and already
manifests as a hard timeout on the one near-complete-graph dataset in the
current suite. "Scalable" is therefore not simply safe, but the *specific*
failure mode is narrower (dense/near-complete graphs; sparse and
moderate-density graphs, which is most of the current 80-suite, remain fast
— sub-second per dataset per the sibling branch's ablation runtimes) than the
task's framing suggests.

Three alternatives, strongest to safest:

1. **"Scalable and Training-Free Ranking from Pairwise Comparisons via
   Acyclic Graph Construction"** (current title, unchanged). Defensible if
   the manuscript adds an explicit scope qualifier in the abstract/intro
   ("scalable to sparse and moderately dense comparison graphs; dense,
   near-complete graphs remain an open scalability challenge, discussed in
   §[complexity section]") rather than silently dropping the dense case or
   implying unconditional scalability. This keeps the title's strongest,
   most attention-getting claim intact and is honest as long as the caveat
   is stated once, clearly, near the claim — consistent with how the
   approximation-guarantee caveat should also be handled (§6 above).

2. **"Fast, Training-Free Ranking from Pairwise Comparisons via Acyclic
   Graph Construction"** — replaces "Scalable" with "Fast," which is
   supported unconditionally by the sibling branch's own measured runtimes
   (sub-second per dataset except `finance`) without needing a scope
   qualifier, since "fast" does not imply "scales to arbitrarily dense
   graphs" the way "scalable" can be read to. Slightly weaker rhetorically.

3. **"Training-Free Ranking from Pairwise Comparisons via Local-Ratio
   Acyclic Graph Construction"** — drops the scalability claim from the
   title entirely and instead names the specific technique (local-ratio),
   which is both accurate and appropriately modest given §Novelty verdict's
   finding that the core algorithmic technique is inherited, not new. Safest
   option; also most directly signals to a reader (and reviewer) that the
   paper is not over-claiming a new algorithm, which may pre-empt exactly the
   novelty pushback already received.

**Recommendation: option 1 (keep "Scalable"), paired with the explicit scope
qualifier described above**, because the underlying evidence (sub-second
runtimes on 77/78 successfully-completed datasets in the current suite) does
support "scalable" as a practical, if not universal, claim, and softening the
title risks under-selling a genuinely fast method over one dataset's known
limitation that can instead be stated as a precise, bounded caveat. Option 2
is a reasonable fallback if editorial/reviewer pressure specifically targets
the word "Scalable" itself rather than the underlying claim.
