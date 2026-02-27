# Ours rerun justification (proposal only, no runs yet)

We changed OURS code; current OURS leaderboard rows are **stale** relative to the latest source (`src/ours_mfas.py` is newer than all OURS logs). A small, targeted rerun would verify that the main claims remain valid under the updated implementation.

Triggers for rerun necessity (from spec):
- (i) **Staleness**: current OURS results were generated before the latest OURS code change (confirmed by file vs log mtimes).
- (ii) **Timeouts/missingness**: some OURS variants hit timeouts or lack runtime on a few datasets (e.g., finance).
- (iii) **Headline sensitivity**: on several datasets, OURS is within a few percentage points of the best classical method, so small changes could flip wins/losses.

## Proposed dataset shortlist (<= 8 datasets)

| dataset | best OURS method | OURS upset_simple | best classical (method, upset_simple) | oracle (method, upset_simple) | reason for inclusion |
|---------|------------------|-------------------|----------------------------------------|-------------------------------|----------------------|
| Football_data_England_Premier_League/England_2009_2010 | OURS_MFAS | 0.634 | SpringRank (0.610) | SpringRank (0.610) | OURS within 0.024 of best classical |
| Football_data_England_Premier_League/England_2012_2013 | OURS_MFAS | 0.889 | SVD_NRS (0.863) | SVD_NRS (0.863) | OURS within 0.026 of best classical |

## Time budget per dataset

- Use the same non-GNN time budget as in the paper for compute-matched runs (1800 seconds wall-clock per dataset), enforced via the existing training/timeout settings.
- Single seed / single trial per (dataset, OURS variant) on this shortlist.

## Expected information gain

- Verify that updated OURS implementation does not degrade main-paper wins vs classical baselines on tight-margin datasets.
- Quantify any systematic improvement/degradation for OURS across the shortlist, to be summarized via `tools/compare_ours_before_after.py`.
- Confirm that OURS timeouts/missingness on important datasets (e.g., finance) are stable or improved under the new code.

## Stopping rule

- Run datasets in the order given in the table above.
- **Primary stop condition**: stop once either (a) 6 datasets have completed, or (b) after the first 4 completed datasets, the median Δ upset_simple (new - old) has absolute value < 0.01 and there are no new wins vs best classical.
- If severe degradation is observed early (e.g., 2 or more clear losses vs old OURS on tight-margin datasets), stop immediately and investigate before rerunning further datasets.