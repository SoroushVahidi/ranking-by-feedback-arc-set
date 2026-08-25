# Phase-B Add-Back Diagnosis (JOS Major Revision)

Date: 2026-08-24
Branch: `journal-supercomputing-major-revision-20260824`
Source verified: `GNNRank-main/src/ours_mfas.py`, `GNNRank-main/src/comparison.py`, `tests/test_audit.py`

## 1. What the current (legacy) Phase B actually does

Implementation: `_addback_desc_weight_multi()` in `GNNRank-main/src/ours_mfas.py`
(lines ~217-282, pre-revision).

For each of up to `insertion_passes` passes (INS1=1, INS2=2, INS3=3):

1. Compute **one** topological order `topo` of the *current* kept-edge DAG via
   Kahn's algorithm (`_toposort_kahn_from_edges`), and derive `pos[v]` = index of
   `v` in that order.
2. Scan all Phase-A-removed edges once, in **stable descending original weight**
   order (`np.argsort(-w, kind="mergesort")`).
3. For a removed edge `(u, v)`: accept (`kept[e] = True`) iff `pos[u] < pos[v]`
   ("forward" in the fixed order `topo`); otherwise reject permanently for this
   pass.
4. Repeat for the next pass (INS2, INS3), recomputing `topo` from the
   now-larger kept set at the start of each pass.

**This confirms the reviewer's characterization exactly.** Adding any edge that
is forward w.r.t. one fixed topological order trivially preserves that order as
a valid topological order of the new graph (a classical, correct, but
*conservative* sufficient condition for acyclicity). The actual
necessary-and-sufficient condition for "`u -> v` is safe to add" is: **`v` does
not already reach `u`** in the kept graph. "Forward in one fixed order" is
strictly stronger than "does not create a cycle" whenever the DAG admits more
than one valid topological order (i.e. whenever there exist two nodes with no
path between them either way) — which is common in these sparse/medium-density
real graphs (basketball, faculty, football, animal, finance).

### Why INS1 -> INS2 -> INS3 produces little additional change

Because each pass re-derives `topo` from Kahn's algorithm, which is
deterministic given the edge insertion order used to build adjacency lists
(row-major by original edge id), the recomputed order after pass 1 is either
identical to the previous order restricted to already-kept edges, or differs
only in ways forced by the specific edges added in pass 1. Empirically (see
`REVISION_RESULTS.md`), the reinserted-edge count collapses to 0 after the
first pass on the overwhelming majority of datasets (`break_reason ==
"no_change"`), because a topological order compatible with the previous kept
set is very likely to remain a valid order after adding more forward edges to
it, leaving no further forward-but-previously-topologically-unreachable edges
to add. INS2/INS3 exist to catch the rare case where the newly recomputed
order exposes additional forward edges; they do not, and structurally cannot,
recover edges that are safe by reachability but backward in every order Kahn's
algorithm happens to produce from that specific tie-breaking rule.

## 2. Duplicate `OURS_MFAS` / `OURS_MFAS_INS3` naming

Confirmed directly from source (`GNNRank-main/src/comparison.py:365-390`):

```python
def ours_MFAS(scores_matrix, variant: str = "INS3", ...):
    ...
def ours_MFAS_INS3(scores_matrix, **kwargs):
    return ours_MFAS(scores_matrix, variant="INS3", **kwargs)
```

`ours_MFAS()` called with no `variant` argument defaults to `"INS3"`, which is
**exactly** what `ours_MFAS_INS3()` does. The two functions are behaviorally
identical (same code path, same `insertion_passes=3`). This is already
intentionally documented and pinned down by existing tests
(`tests/test_audit.py::TestBaselineLabelAudit::test_ours_mfas_default_variant_is_ins3`,
`::test_ours_variants_have_distinct_variant_labels`), i.e. it is a known,
tested-as-expected behavior, not an accidental bug — but it does mean that
every leaderboard/table that lists both `OURS_MFAS` and `OURS_MFAS_INS3` as
separate rows (e.g. `GNNRank-main/scripts/paper/run_phase_ablation.py`'s old
hardcoded variant list, `GNNRank-main/tools/build_leaderboard_csvs.py`'s
`OURS_METHODS` list, `scripts/paper/generate_paper_tables.py`) is reporting the
**same underlying run twice under two labels**. This inflates the apparent
number of "OURS variants" evaluated and is worth flagging explicitly to
reviewers as a labeling/reporting redundancy rather than two independent
algorithmic configurations — the true distinct configurations are
`{OURS_MFAS_INS1, OURS_MFAS_INS2, OURS_MFAS_INS3}` (`OURS_MFAS` is a fourth
label for the same numbers as `OURS_MFAS_INS3`), and now, from this revision,
`{OURS_MFAS_REACH}`.

**Disposition for this revision:** left as-is functionally (changing the
default would silently alter the meaning of every existing script that calls
`ours_MFAS()` without `variant=`, which the task instructions explicitly ask
us not to do — "preserve existing algorithm variants rather than silently
replacing them"). The recommendation for the manuscript text and any future
cleanup PR is to treat `OURS_MFAS` as an alias of `OURS_MFAS_INS3` in prose and
avoid double-counting it as an independent configuration in result tables.

## 3. Instrumentation added

`ours_mfas_rmfa()`'s returned `meta` dict (both add-back modes) now reports,
per run: `removed_phaseA`, `kept_after_phaseA`, `kept_final`,
`reinserted_per_pass`, `changed_edges_per_pass`, `break_reason`,
`time_phase1_sec`, `time_phase2_sec`, `time_phaseC_sec`, `runtime_sec`. The
reachability path additionally reports `reach_candidates`, `reach_checked`,
`reach_inserted`, `reach_rejected_reachable`, `reach_dense_matrix_used`,
`reach_break_reason`. The extended `run_phase_ablation.py` harness further
computes, per dataset: whether the final permutation differs from the
Phase-A-only permutation, and the three upset variants (`upset_simple`,
`upset_ratio`, `upset_naive`).

## 4. Direct answers to Section-B questions

1. **Does old Phase B merely add edges compatible with the already-selected
   order?** Yes — confirmed from source: it tests `pos[u] < pos[v]` against a
   single order per pass, which is precisely "compatible with the
   already-selected order," not an exact cycle-safety test.
2. **On how many datasets does it actually change the final permutation
   (vs Phase-A-only)?** See `REVISION_RESULTS.md` for the measured count over
   the full loadable suite.
3. **On how many datasets does it improve each objective?** See
   `REVISION_RESULTS.md`.
4. **What incremental benefit is obtained by INS1 -> INS2 -> INS3?** Existing
   repo diagnostics (`GNNRank-main/diagnose_ins_passes.py`) plus the
   `reinserted_per_pass` field confirm pass-2/pass-3 reinsertion counts are
   typically 0 (`break_reason == "no_change"`) once the first pass has run;
   see `REVISION_RESULTS.md` for suite-wide counts.
