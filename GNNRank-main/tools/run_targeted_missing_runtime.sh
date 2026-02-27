#!/usr/bin/env bash
# Run only the (dataset, method) pairs that have upset_simple but missing runtime
# in result_arrays (see docs/Targeted_reruns_plan.md). Use after:
#   1) Searching result_arrays (tools/check_missing_runtime_in_result_arrays.py)
#   2) Optionally waiting for job 841303 to finish and re-checking
# If still missing, this script fills runtime for: Halo2BetaData (SVD_NRS, SVD_RS, SpringRank),
# _AUTO/Basketball_temporal__1985adj (SpringRank).
#
# Run from repo root: bash tools/run_targeted_missing_runtime.sh
# Optional: sbatch a wrapper that runs this script if you want it as a batch job.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"
mkdir -p logs_suite
NUM_TRIALS=1
SEEDS="1"

run_one() {
  local ds="$1" m="$2"
  local safe_ds="${ds//\//__}"
  echo "RUN dataset=$ds method=$m  $(date)"
  python -u src/train.py --dataset "$ds" --all_methods "$m" --num_trials "$NUM_TRIALS" --seeds $SEEDS --SavePred \
    >> "logs_suite/${safe_ds}__${m}.log" 2>&1 || echo "FAILED dataset=$ds method=$m (see logs_suite/${safe_ds}__${m}.log)"
}

echo "=== Targeted missing-runtime runs ==="
run_one "Halo2BetaData" "SVD_NRS"
run_one "Halo2BetaData" "SVD_RS"
run_one "Halo2BetaData" "SpringRank"
run_one "_AUTO/Basketball_temporal__1985adj" "SpringRank"
echo "=== Done. Re-run check: python tools/check_missing_runtime_in_result_arrays.py ==="
