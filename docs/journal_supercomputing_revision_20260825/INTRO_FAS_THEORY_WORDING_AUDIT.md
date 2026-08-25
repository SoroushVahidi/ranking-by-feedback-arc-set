# Introduction FAS-Theory Wording Audit

## Old claim (Introduction, `main_ik.tex`, Section 1, sentence preceding Proposition 1)

> "...the backward edges of any ranking form a feedback arc set of equal weight, and any
> feedback arc set induces a DAG whose topological orders realize that deleted weight as
> ranking disagreement."

## Why it was too strong

The clause "realize that deleted weight as ranking disagreement" asserts an **equality**
`L(R) = w(F)` for *every* feedback arc set `F` and *every* topological order `R` of
`(V, E \ F)`. This is false for an arbitrary (non-inclusion-minimal) feedback arc set: if
`F` contains an arc that is not actually a backward arc of any topological order of
`(V, E \ F)` (i.e., `F` deletes more than the minimum needed to break its cycles), the
realized ranking disagreement `L(R)` can be strictly less than `w(F)`.

The manuscript's own proof of Proposition 1 only ever establishes the **inequality**
direction for a general feedback arc set:

- Proof, `(OPT_rank <= OPT_MWFAS)` direction (`main_ik.tex` line 204): "Every retained arc
  is forward under `R`, so the set of backward arcs of `R` is contained in `F*`. Therefore
  `L(R) <= w(F*)`." — this is `<=`, not `=`, for a general `F`.
- Remark following the proof (`main_ik.tex` line 208): "If `F` is inclusion-minimal, then
  for every topological order `R` of `(V,E\F)` one has `L(R)=w(F)`. Optimal feedback arc
  sets under strictly positive weights are inclusion-minimal..." — equality is stated only
  under the explicit inclusion-minimality hypothesis, with optimal positive-weight FAS
  given as the leading example.

So the informal Introduction sentence claimed unconditional equality for *any* feedback
arc set, while the formal result (proof + remark) only supports `<=` in general and `=`
under inclusion-minimality. The two did not match.

## Corrected claim

> "...the backward edges of any ranking form a feedback arc set of equal weight, and any
> feedback arc set induces a DAG whose topological orders have ranking disagreement no
> greater than the deleted weight, with equality for an inclusion-minimal (in particular,
> optimal positive-weight) feedback arc set."

## Consistency with Proposition 1

- The "no greater than" clause matches the proof step at line 204 exactly (`L(R) <= w(F)`
  for the backward-arcs-of-`R` `subseteq` `F` argument, which holds for any feedback arc
  set `F`, not only the optimum).
- The "equality for an inclusion-minimal ... feedback arc set" clause matches the Remark
  at line 208 verbatim ("If `F` is inclusion-minimal, then for every topological order `R`
  of `(V,E\F)` one has `L(R)=w(F)`"), and the parenthetical "(in particular, optimal
  positive-weight)" matches the Remark's second sentence ("Optimal feedback arc sets under
  strictly positive weights are inclusion-minimal").
- No change was made to Proposition 1, its proof, or the Remark — the audit found the
  formal statements to be correct as written; only the informal Introduction sentence was
  out of step with them.

## Location of fix

`manuscript/revision_20260825/source/main_ik.tex`, Section 1 (Introduction), the sentence
immediately preceding the display of the ranking objective / MWFAS shared-optimum
discussion and Proposition 1.
