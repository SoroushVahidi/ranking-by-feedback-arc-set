# Novelty/Theory Reviewer Concern Map

Date: 2026-08-24

Classification legend: **A** = already answerable from current evidence (this
pass's documents); **B** = requires manuscript rewrite only; **C** = requires
new algorithmic evidence from the sibling reachability-add-back workstream;
**D** = requires a new experiment not yet run; **E** = requires literature
clarification / primary-source verification beyond this pass.

## Reviewer 1

**Issue 1 — Novelty.**
Classification: **A + B**. Answerable now: the novelty verdict is in
`NOVELTY_VERDICT.md`, grounded in `NOVELTY_LITERATURE_MATRIX.md`'s discovery
that the closest prior work is the authors' own [VK25] (arXiv:2412.16181),
not a third party. Requires a manuscript rewrite to (a) explicitly cite and
differentiate from [VK25] — its absence from the current bibliography, if
that is the case, would itself likely draw reviewer scrutiny for
self-overlap — and (b) reframe the contribution bullets per
`NOVELTY_VERDICT.md`'s recommended 3 bullets, dropping any implicit claim
that weight-prioritized or multi-pass add-back is a novel mechanism.

**Issue 3 — Readability / pseudocode.**
Classification: **A**. `CURRENT_PIPELINE_PSEUDOCODE.md` provides
publication-ready pseudocode for the *current* shipped method (not the
experimental reachability variant), plus a parameter table with defaults,
roles, and a per-parameter sensitivity-study recommendation. Ready to adapt
into the manuscript's methods section directly.

**Issue 4 — Theory / complexity.**
Classification: **A** (fully — the former **E** item below is now resolved).
`RANKING_MWFAS_EQUIVALENCE.md` supplies the formal proposition + proof the
manuscript needs (absent from [VK25]). `APPROXIMATION_GUARANTEE_AUDIT.md` and
`COMPLEXITY_AUDIT.md` give precise, code-verified verdicts on the
approximation-guarantee and complexity claims, including a worst-case
construction proving the timeout fallback has no error bound, and a corrected
O(mn+m²) worst-case time bound for Phase A (vs. the O(VE) claimed for the
abstract algorithm). **[RESOLVED during three-branch integration, 2026-08-24]**:
the primary-source theorem text of [DF03] was originally not extractable in
this pass (only a secondary characterization was obtained), flagged as an
**E** item needing direct verification. The sibling
`jsuper-prior-work-overlap-audit-20260824` branch subsequently obtained and
read the full primary text (`DF03_PRIMARY_THEOREM_VERIFICATION.md`, now
integrated), confirming the λ-approximation characterization and additionally
sharpening the approximation-guarantee verdict — see that document and the
update note added to `APPROXIMATION_GUARANTEE_AUDIT.md` §1/§4.

## Reviewer 2

**Issue 1 — Novelty.**
Classification: **A + B**. Same evidence base as Reviewer 1's Issue 1;
`NOVELTY_VERDICT.md` and `NOVELTY_LITERATURE_MATRIX.md` directly address
this. No additional experiment needed to *answer* the concern, only a
rewrite reflecting the corrected positioning.

## Reviewer 4

**"What exactly is scientifically new?"**
Classification: **A**. `NOVELTY_VERDICT.md`'s three contribution bullets are
the direct answer, each traceable to a specific artifact (expanded
benchmark/baseline set, fidelity-gap diagnosis + corrected implementation,
formal equivalence + guarantee audit).

**Approximation guarantee ambiguity.**
Classification: **A**, with the same **E** caveat as Reviewer 1 Issue 4.
`APPROXIMATION_GUARANTEE_AUDIT.md` resolves the ambiguity with a specific
verdict (B: applies only to an unbudgeted, idealized variant) and precise
recommended manuscript language, rather than leaving it ambiguous.

**Introduction / positioning problem.**
Classification: **B**. `INTRODUCTION_REWRITE_PLAN.md` proposes a concrete
structure addressing this directly, including explicit treatment of the
relationship to [VK25] (currently, per this audit, the introduction's
positioning problem is plausibly *caused by* not clearly differentiating
from the authors' own closely related prior arXiv paper — see
`NOVELTY_LITERATURE_MATRIX.md`).

**Novelty comparison table.**
Classification: **A**. `NOVELTY_LITERATURE_MATRIX.md` **is** this table,
built against the specifically-closest prior methods (not a generic
literature survey), with every cell sourced or marked UNKNOWN rather than
assumed.

## Concerns still dependent on new experiments or the add-back workstream (not resolved by this pass alone)

- The exact count of datasets in the current 80-suite where Phase A's
  wall-clock budget is exhausted before convergence (needed to fill in the
  `[N] of [M]` in `APPROXIMATION_GUARANTEE_AUDIT.md`'s recommended
  manuscript sentence) — requires a dedicated instrumentation pass recording
  a `phaseA_converged` flag per dataset, not performed in this audit.
  Classification: **D**.
- Whether the reachability-add-back workstream's empirical results (on the
  sibling branch) should be folded into this manuscript's headline
  contribution claims, or presented as a separate "correctness fix" finding
  — this is a manuscript-structure decision that depends on that
  workstream's final results, which this workstream does not have authority
  over per the concurrency rule. Classification: **C**.
- Verification of [DF03]'s primary-source theorem text (see Reviewer 1 Issue
  4 / Reviewer 4 approximation-guarantee item above). Classification: **E**.
- A full sensitivity grid beyond the insertion-strategy axis (per
  `CURRENT_PIPELINE_PSEUDOCODE.md`'s parameter table, most other parameters
  are argued theoretically negligible at current defaults, but this has not
  been empirically confirmed with a dedicated sweep). Classification: **D**,
  low priority per that document's own recommendation.
