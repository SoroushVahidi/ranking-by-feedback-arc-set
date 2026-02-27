# Artifact inconsistencies audit (repo-wide, final)

## Dataset counts and set differences (paper suite)

- `leaderboard_per_method.csv`: **81** unique datasets.
- `leaderboard_compute_matched.csv`: **80** unique datasets.
- `leaderboard_oracle_envelopes.csv`: **81** unique datasets.

- leaderboard − compute_matched: ['ERO/p5K5N350eta10styleuniform']
- compute_matched − leaderboard: []

## Table denominators vs current CSV counts

- Table 1 denominators: [81] (expect 81)
- Table 2 denominators: [80] (expect 80)
- OK: denominators match.

## Coverage helper consistency

OK: `leaderboard_compute_matched_coverage.csv` matches recompute from `leaderboard_per_method.csv`.

## “78 datasets” stale narration

- `run_full.sh` still prints `"78 datasets, all methods, $TRIALS trials each"` (narrative only; artifacts use 81/80).

## OURS rerun artifacts

- The temporary trials1 OURS files for England_2009_2010 were removed from `result_arrays/` so they no longer affect leaderboards/tables.
- England_2009_2010 trials1 file (should be missing now): (missing)
