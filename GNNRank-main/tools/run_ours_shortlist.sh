
#!/usr/bin/env bash
# Run ONLY OURS on the datasets listed in docs/Ours_rerun_shortlist.md.
# This script does not launch automatically in any pipeline; run manually via:
#   bash tools/run_ours_shortlist.sh
#
# Design decisions:
# - Uses the "best OURS method" column from docs/Ours_rerun_shortlist.md so it
#   stays in sync with the shortlist file (no hard-coded dataset list here).
# - Runs a single seed / single trial per (dataset, method), with the same
#   time budget and train.py settings as the main paper runs.
# - Writes logs under logs_suite/, and results under result_arrays/ so that
#   tools/build_leaderboard_csvs.py will pick them up afterwards.
#
# Hard constraints (enforced by construction):
# - Only OURS methods are run.
# - No classical or GNN methods are touched.

set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

SHORTLIST_FILE="docs/Ours_rerun_shortlist.md"
if [[ ! -f "$SHORTLIST_FILE" ]]; then
  echo "Shortlist file $SHORTLIST_FILE not found." >&2
  exit 1
fi

mkdir -p logs_suite
NUM_TRIALS=1
SEEDS="1"  # OURS is effectively deterministic; one seed suffices.

# Parse markdown table: skip header separator line, then grab dataset (col 2)
# and best OURS method (col 3).
mapfile -t DATASET_METHOD_ROWS < <(grep '^|' "$SHORTLIST_FILE" | tail -n +3)

if [[ ${#DATASET_METHOD_ROWS[@]} -eq 0 ]]; then
  echo "No datasets found in shortlist table (docs/Ours_rerun_shortlist.md)." >&2
  exit 1
fi

run_one() {
  local ds="$1" m="$2"
  local safe_ds="${ds//\//__}"
  echo "RUN dataset=$ds method=$m  $(date)"
  python -u src/train.py --dataset "$ds" --all_methods "$m" --num_trials "$NUM_TRIALS" --seeds $SEEDS --SavePred     >> "logs_suite/${safe_ds}__${m}.log" 2>&1 || echo "FAILED dataset=$ds method=$m (see logs_suite/${safe_ds}__${m}.log)"
}

for line in "${DATASET_METHOD_ROWS[@]}"; do
  # Split markdown row on '|' and trim whitespace around fields.
  IFS='|' read -r _ ds m _ <<<"$line"
  ds="${ds## }"; ds="${ds%% }"
  m="${m## }"; m="${m%% }"
  if [[ -z "$ds" || -z "$m" ]]; then
    continue
  fi
  # Sanity check: enforce OURS-only methods
  if [[ "$m" != OURS_MFAS* ]]; then
    echo "Skipping non-OURS method in shortlist: dataset=$ds method=$m" >&2
    continue
  fi
  run_one "$ds" "$m"
done

echo "Done. After runs finish, regenerate artifacts with:
  bash tools/build_all_paper_artifacts.sh" >&2
