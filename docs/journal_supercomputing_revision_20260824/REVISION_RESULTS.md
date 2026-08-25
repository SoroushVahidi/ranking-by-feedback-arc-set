# Revision Results (populated only with actually-obtained results)

Date: 2026-08-24
Branch: `journal-supercomputing-major-revision-20260824`
Command: `python GNNRank-main/scripts/paper/run_phase_ablation.py`
Raw output: `GNNRank-main/outputs/ablation/phase_ablation_results.csv` (390 rows),
`GNNRank-main/outputs/ablation/phase_ablation_summary.md` (auto-generated
aggregate, reproduced/interpreted below)

All numbers in this document are read directly from the CSV produced by the
run above; none are hand-typed or assumed. Reproduce with the command above
(deterministic given the same environment — see `tests/test_reachability_addback.py`
determinism tests — except for the exact `removed_phaseA` counts on `finance`,
explained in §4, which are wall-clock-dependent because that one dataset hits
the per-run time budget during Phase A itself).

## 1. Suite coverage

- 79 of 80 canonical datasets attempted (2 excluded up front with documented,
  mechanical reasons — see `REVISION_EXPERIMENT_PLAN.md`).
- 78 successfully loaded and run. One additional load failure discovered
  during execution: `Halo2BetaData/HeadToHead` — its on-disk layout differs
  from both the default `load_real_data()` path and the `<name>/adj.npz`
  fallback (`GNNRank-main/data/Halo2BetaData/HeadToHead/adj.npz` does not
  exist; per earlier preflight inspection its data lives at
  `_AUTO/Halo2BetaData__HeadToHeadadj/adj.npz`, a third layout not covered by
  the harness's fallback). Recorded as a load failure in the CSV
  (`status=load_failed`), not silently skipped. **Blocker for next pass**: add
  this third fallback path or reuse the `_AUTO` naming convention directly.
- Net: **78/80 canonical datasets** carry actual A0/A1_topo/A2_topo/B1_reach/B2_reach
  results in this pass.

## 2. Does the legacy topo add-back genuinely improve the ranking? (core reviewer question, re: A1_topo vs A0)

**No, not reliably.** Paired `upset_simple` comparison, `A1_topo` vs `A0`
(Phase-A-only), n=78 datasets:

- **28 datasets improve, 13 tie exactly, 37 datasets get WORSE.**
- Mean delta ≈ **+0.000051** (i.e., very slightly worse on average),
  median delta = 0.000000.

This is a direct, quantitative confirmation of the reviewer's central concern:
the deployed add-back mechanism is not a reliable improvement step under the
metric the paper reports. It changes the permutation on 67/78 datasets (86%)
but the resulting change is worse about as often as it is better — consistent
with the diagnosis in `ADDBACK_DIAGNOSIS.md` that topo add-back's forward/
backward test is a structural byproduct of one arbitrary topological order, not
an optimization step targeting upset_simple (or any objective) at all.

## 3. Does reachability add-back genuinely improve the ranking, and is it different from topo add-back?

**Yes, substantially and consistently, with two honestly-reported exceptions.**

Paired `upset_simple` comparison, `B1_reach` vs `A0`, n=78:

- **74 datasets improve, 2 tie, 2 get worse.**
- Mean delta ≈ **-0.008627**, median delta ≈ **-0.008329** (upset_simple is
  bounded in [0,1], so this is a meaningful shift, not noise near machine
  epsilon — contrast with topo's ±0.00005 mean).

Paired `upset_simple` comparison, `B1_reach` vs `A1_topo` (direct head-to-head
against the legacy mechanism), n=78:

- **73 datasets improve, 3 tie, 2 get worse.**
- Mean delta ≈ **-0.008576**, median delta ≈ **-0.008833**.

Edges restored (suite totals): `A1_topo` restores **84,857** edges across the
suite; `B1_reach` restores **87,369** — reach restores strictly more edges on
**39/78** datasets (tied, generally at 0, on the rest — see §5).
`B1_reach` changes the final permutation vs. `A0` on **76/78** datasets
(97%), vs. `A1_topo`'s 67/78 (86%).

Because Phase C (`refine_scores_ratio_ternary`) is order-preserving by
construction (verified by
`tests/test_reachability_addback.py::TestPhaseToggles::test_phase_c_toggle_changes_scores`),
`upset_simple` — which depends only on the induced order — is byte-for-byte
identical between `A1_topo`/`A2_topo` and between `B1_reach`/`B2_reach`. This
is expected, not a bug; it means Phase C cannot be responsible for, or against,
the differences reported here.

### The two reachability regressions, examined honestly

1. **`Football_data_England_Premier_League/finerEngland_...`**: delta ≈
   **+0.000887** — negligible in absolute terms (upset_simple ∈ [0,1]),
   plausibly within the noise floor of a small (n=20) near-complete graph
   where greedy edge order can break ties differently than topo add-back.
2. **`Halo2BetaData`** (n=602, m=5010): delta ≈ **+0.248737** — **not**
   negligible. `A0` upset_simple = 0.1767, `A1_topo` = 0.1735 (a small
   improvement), `B1_reach` = 0.4255 (dramatically worse). Direct inspection
   of the run (`phase_ablation_results.csv`, `dataset==Halo2BetaData`) shows
   `B1_reach` restores *more* edges than `A1_topo` (910 vs 743) — consistent
   with the suite-wide pattern that reachability is strictly more permissive
   — but here the additional 167 restored edges collectively push the induced
   ranking to a substantially worse `upset_simple`. **This is a genuine,
   important counter-example, not an artifact**: restoring more edges (i.e.
   satisfying more of the exact cycle-safety condition) is not the same as
   improving the ranking objective, because the greedy descending-weight
   insertion order optimizes for cycle-safety and edge count, not for
   `upset_simple` directly. This is precisely the failure mode that Section
   F's proposed exchange/escape mechanism is meant to address (see §7) — it
   is recorded here as motivating evidence for that follow-up, not swept
   under the rug.

## 4. Finance: a genuine execution blocker, not evidence of "no effect"

`finance` (n=1315, m=1,729,225, density≈1.0 — a near-complete graph) shows
`upset_simple` **identical across all five phase modes** (0.499973) and
`edges_restored=0` for every add-back configuration, including `B1_reach`
(`reach_checked=0`). Inspecting the meta fields: Phase A's local-ratio
cycle-peeling loop (a pure-Python iterative DFS-based procedure) does not
converge within the 60-second per-run budget used in this pass on a graph
this dense; it consumes the *entire* budget before Phase B ever starts (Phase
B's own time check fires immediately, `reach_checked=0`). The exact
`removed_phaseA` count differs slightly across the five runs (58,114 /
58,151 / 60,090 / 61,979 / 61,097) because how far the cycle-peeling loop gets
before the wall-clock cutoff is itself wall-clock-dependent — this is expected
under a hard time budget and is not a determinism bug in the algorithm proper
(`ours_mfas_rmfa`'s core logic remains deterministic given a fixed *edge
count processed*; what varies here is how many edges get processed before an
external, real-time clock cutoff).

**Conclusion for finance: this pass produced no evidence either way about
whether reachability add-back helps on this dataset**, because neither
add-back mechanism got to run at all. The per-family breakdown's "Finance:
tie, delta=0.000000" line must not be read as "reach add-back is neutral on
dense graphs" — it reflects an unmet compute budget, not a result. Rerunning
with a substantially larger time budget (or, better, a non-pure-Python /
vectorized Phase-A implementation) is a recorded next step (see §7). This
matches this task's own contingency instruction: "If an experiment cannot be
executed in the environment, implement and validate the harness and clearly
record the blocker" — the harness is validated (it ran cleanly and recorded
exactly what happened) and the blocker is recorded here rather than hidden or
papered over with a fabricated result.

## 5. Where reach and topo restore exactly the same edges (the other 39/78 "not strictly more" cases)

On the 39 datasets where `B1_reach` does not restore strictly more edges than
`A1_topo`, inspection of `reach_rejected_reachable` and
`reinserted_per_pass` in the CSV shows these are predominantly graphs where
Phase A's kept DAG already admits few or no independent (mutually
unreachable) branches — i.e., the graph is "path-like" enough post-Phase-A
that one topological order captures most of the safe reinsertions, so the two
methods coincide. This is consistent with the theoretical relationship
established in `REACHABILITY_ADDBACK_DESIGN.md`: reachability add-back is
always at least as permissive as topo add-back (it accepts a superset of what
topo would accept, since "forward in one fixed order" implies "not
reachable", never the converse) — the two methods only *provably* differ when
the Phase-A DAG has genuine structural slack (multiple valid topological
orders), which is common but not universal in this dataset suite.

## 6. Runtime overhead

Median runtime per dataset (excluding `finance`'s pathological case, which
saturates the 60s cap for every mode and dominates the `max` column):

| Mode | Median (s) | Max (s, incl. finance cap) |
|---|---|---|
| A0 | 0.1584 | 60.59 |
| A1_topo | 0.1639 | 60.73 |
| A2_topo | 0.2634 | 60.73 |
| B1_reach | 0.2509 | 62.60 |
| B2_reach | 0.3520 | 62.55 |

Reachability add-back's median overhead vs. topo add-back is small in
absolute terms (≈0.09s without refinement, ≈0.09s with) and dominated, on the
largest non-pathological datasets (`Basketball_temporal/*`, n≈300-351), by
the dense `O(n^2)` incremental-reachability-matrix updates described in
`REACHABILITY_ADDBACK_DESIGN.md` — well within the method's stated
sub-second-per-dataset performance envelope on this suite.

## 7. Direct answers to the Section-O stopping-point questions

1. **Does it restore more edges than old Topo-AddBack?** Yes, suite-wide
   (87,369 vs 84,857), and strictly more on 39/78 individual datasets (never
   strictly fewer on any dataset — consistent with the permissiveness
   argument in §5/`REACHABILITY_ADDBACK_DESIGN.md`).
2. **Does it change the final ranking on a meaningful number of datasets?**
   Yes — 76/78 (97%) vs. Phase-A-only, compared to topo's 67/78 (86%).
3. **Does it improve upset metrics?** Yes, strongly, on `upset_simple`:
   74/78 improve vs. A0 (mean Δ≈-0.0086), 73/78 improve vs. A1_topo directly.
   (This pass measured `upset_simple` as the primary comparison metric per
   the experiment plan; `upset_ratio`/`upset_naive` paired statistics are
   present in the raw CSV — `outputs/ablation/phase_ablation_results.csv` —
   for follow-up analysis but are not separately summarized here.)
4. **Does it improve weighted FAS cost?** Not directly measured in this pass
   (no explicit "sum of removed edge weights" column was computed) —
   `kept_final`/`removed_phaseA` counts are in the CSV and a weighted-FAS
   column can be added cheaply as a follow-up; recorded as next work.
5. **Which regimes benefit?** Every family benefits on average except
   `Finance` (blocked, §4) and the single `Halo` dataset (a genuine
   regression, §3). Basketball (both coarse and finer, 30+30 datasets),
   Faculty (3/3), Animal (1/1), and Football (10/12, 2 negligible/no
   regressions) all show consistent improvement.
6. **What runtime overhead does it introduce?** Small — see §6.
7. **Is exchange search justified?** The `Halo2BetaData` regression (§3) is
   concrete, non-hypothetical evidence that greedy reachability add-back can
   overshoot on `upset_simple` even while being strictly more
   cycle-permissive, which is exactly the failure mode Section F's exchange
   mechanism targets. **Recommendation: yes, worth prototyping next**, but it
   was not implemented in this pass (see `REVISION_EXPERIMENT_PLAN.md`
   "Explicitly deferred") — this pass's job was to first establish whether
   plain reachability add-back materially changes the picture, which it does.

## 8. Overall verdict for this pass

Reachability-aware add-back is **not** merely densifying the same DAG/order.
It (a) restores more edges than the legacy mechanism on a large share of
datasets and never fewer, (b) changes the induced ranking far more often
(97% vs 86% of datasets), and (c) — critically, since (a) and (b) alone would
not answer the reviewer's concern — **it improves the reported upset_simple
metric on the large majority of datasets (74-73 of 78, depending on the
comparison), with a mean improvement roughly two orders of magnitude larger
than the legacy mechanism's (near-zero, slightly negative) average effect.**
The legacy topo add-back, by contrast, is shown here to be close to a coin
flip on this metric (28 better / 37 worse), which is itself a significant,
previously-undocumented finding directly relevant to the reviewer's stated
concern.

This is not an unqualified win: one dataset (`Halo2BetaData`) regresses
substantially, and one dataset (`finance`) produced no evidence in either
direction due to a compute-budget limitation that must be fixed before any
claim is made about dense/near-complete graphs. Both are reported explicitly
above rather than omitted.

**Recommendation:** the manuscript's Phase-B description and Table/ablation
material should be revised to (i) present `OURS_MFAS_REACH` as the primary
add-back mechanism going forward, replacing or standing alongside the legacy
topo variant with a clear statement that the latter is not a reliable
improvement step, (ii) report the `Halo2BetaData`-style regression risk
honestly as motivation for the exchange-mechanism follow-up, and (iii) flag
the `finance`/near-complete-graph regime as needing a dedicated,
better-budgeted experiment before either add-back mechanism's behavior there
can be characterized. See `MANUSCRIPT_CHANGE_MAP.md` for the section-by-section
breakdown.

## 9. Remaining reviewer-critical experiments (not attempted this pass)

Per `REVISION_EXPERIMENT_PLAN.md` "Explicitly deferred": Sections F
(exchange-move prototype), G (deeper canonical-value spot checks beyond the
5-value verification already done — see `REVIEWER_TECHNICAL_AUDIT.md`), H
(direct classical-baseline runtime W/T/L/Pareto tables), I (timeout-safe
common-completion analysis), J (Wilcoxon/bootstrap/Holm statistical testing),
K (systematic scale/density stratification beyond the per-family breakdown in
§3/§5), L (broader sensitivity grid beyond the insertion-strategy axis this
pass directly provides). Also: fix the `Halo2BetaData/HeadToHead` loader gap
(§1) and re-run `finance` with either a much larger time budget or a
vectorized Phase A before drawing any conclusion about dense/near-complete
graphs (§4).
