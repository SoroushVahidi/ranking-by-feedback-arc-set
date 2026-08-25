# Springer / Journal of Supercomputing Preprint & AI-Disclosure Policy Audit

Date: 2026-08-24
Method: direct web search + WebFetch against Springer Nature's own policy pages this pass. The
JOS-specific submission-guidelines page (`link.springer.com/journal/11227/submission-guidelines`)
returned an authentication wall (redirects to `idp.springer.com/authorize`) and could not be
fetched unauthenticated in this pass — flagged as UNKNOWN below rather than assumed from the
general Springer Nature policy alone.

## 1. Allowed submission status (preprints)

**CONFIRMED** (Springer Nature general policy, `support.springernature.com`, fetched directly this
pass): *"Posting of preprints is not considered to be a prior publication and will not jeopardize
being considered for publication in Springer Nature journals."* Preprints may be posted "at any
time during the peer review process." The Journal of Supercomputing is a Springer Nature journal,
so this general policy applies absent a JOS-specific override — **but a JOS-specific override was
not independently checked** due to the authentication wall above. **Verdict: arXiv:2412.16181's
existence does not, by itself, disqualify the JOS manuscript from submission or publication.**

## 2. Required disclosure / citation

**PARTIALLY CONFIRMED / PARTIALLY UNKNOWN.** A secondary summary found earlier in this overall
revision effort (see the general-Springer WebSearch result gathered on the sibling
`jsuper-revision-novelty-theory-20260824` branch) stated: *"Authors should disclose details of
preprint posting, including DOI and licensing terms, upon submission of the manuscript or at any
other point during consideration."* This pass's direct fetch of
`support.springernature.com/.../6000258807-preprints` did **not** surface this specific disclosure
requirement in the retrieved excerpt (the tool's extraction explicitly noted *"details aren't
provided in this excerpt"* for disclosure/DOI/licensing specifics). **Given the conflicting
completeness of the two passes, treat the DOI/licensing disclosure requirement as likely-true but
not independently re-confirmed by this document's own fetch — recommend the authors verify
directly via Springer's author-facing submission portal (which requires login) or by contacting
the journal editorial office before submission**, rather than relying solely on this audit.

**No source found in either pass (this one or the sibling's) that states whether the *submitted
manuscript's own text* must cite the preprint.** This is standard academic practice regardless of
publisher policy (self-citation of directly overlapping prior work, especially one's own, is
expected to avoid the appearance of undisclosed overlap) and is independently recommended by this
audit's own scientific-novelty analysis (`REVISED_CONTRIBUTION_POSITIONING.md` item 10) —
**recommended regardless of whether it is formally mandated**, since not citing arXiv:2412.16181
would itself be a red flag to a reviewer who finds it (as this audit did, via ordinary literature
search), independent of any publisher-policy requirement.

## 3. Scientific-novelty expectations — separate from permissibility

**This is a distinct question from §1/§2 and must not be conflated with them** (per the task's own
explicit instruction). Springer's preprint policy governs *whether the submission is administratively
permissible*; it says nothing about whether the *editorial board or reviewers* will judge the work
sufficiently novel relative to the preprint to merit journal publication. That is a peer-review
judgment call, addressed separately in `DISTINCTNESS_AND_NEW_WORK_VERDICT.md` in this same
directory — **not** resolved by the preprint policy being permissive. A submission can be
administratively eligible (per §1) while still being rejected on novelty grounds by reviewers who
find it too incremental relative to the preprint — these are independent gates.

## 4. AI/LLM-assistance disclosure

**CONFIRMED** (Springer Nature general AI policy, via WebSearch this pass): generative-AI tools
cannot be listed as authors; **use of AI in drafting text must be disclosed** in the manuscript's
Methods section (or equivalent, e.g. Acknowledgements for some formats); AI-assisted **copy
editing** specifically does not need to be declared (a narrower exemption than general drafting
assistance).

**Directly relevant finding**: both [VK25] v2 and v3 already contain such a disclosure — v2: *"In
writing this paper, ChatGPT was used to assist with generating text [27]"* (end of §4, before
Data/Code Availability); v3: a more prominent, separately-headed *"Acknowledgment. Portions of the
text in this manuscript were drafted with the assistance of large language models (LLMs),
including ChatGPT [27]. All content was reviewed and verified by the authors."* — **this
disclosure exists and appears compliant with the general policy as summarized above.**

**However, this audit independently found evidence relevant to the "reviewed and verified"
claim**: v3's body text contains at least two citation-attribution errors not present in v2
(misattributing reference [10] in-text as "Chakrabarti and Imamura" when the actual bibliography
entry for [10] is unchanged and remains Demetrescu & Finocchi; misattributing reference [6] in-text
as "Chen and Ghosh" when the bibliography entry is Chakrabarti, Ghosh, McGregor, and Vorotnikova —
see `DF03_PRIMARY_THEOREM_VERIFICATION.md` and `PRIOR_WORK_OVERLAP_MATRIX.md` row 2 for the
concrete evidence). **This is stated as a factual observation about the preprint, not as an
allegation about the JOS manuscript** (which this repository does not contain the text of) — but
it is directly relevant background the authors should be aware of: **if the JOS manuscript's own
text was drafted or revised with similar LLM assistance, the same category of citation-attribution
error is a concrete, demonstrated risk in this specific project's writing process, and its own
in-text citations (especially of [DF03], [VK25] itself, and the classical baselines) should be
independently checked against their actual bibliography entries before submission** — this audit
recommends that check as a fast, cheap, high-value next step (see final report).

## Summary

| Question | Verdict |
|---|---|
| Does the arXiv preprint block JOS submission? | **No** — confirmed by Springer's general preprint policy |
| Is disclosure of the preprint required at submission? | **Likely yes** (DOI/licensing details), but not independently re-confirmed by this pass's own fetch; verify directly before submission |
| Must the manuscript cite the preprint? | Not confirmed as a formal publisher requirement, but strongly recommended regardless, for scientific-integrity and reviewer-risk reasons |
| Is administrative permissibility the same as sufficient novelty? | **No — explicitly separate questions**; permissibility is favorable (§1), novelty sufficiency is a peer-review judgment addressed in `DISTINCTNESS_AND_NEW_WORK_VERDICT.md` |
| Is AI-assistance disclosure required? | **Yes**, and [VK25] already provides one; **the JOS manuscript's own citations should be independently spot-checked** given a demonstrated citation-attribution error found in [VK25] v3 during this audit |
