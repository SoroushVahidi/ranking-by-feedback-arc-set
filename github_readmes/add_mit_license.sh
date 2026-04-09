#!/usr/bin/env bash
# Add MIT LICENSE to all SoroushVahidi repos that don't have a license.
# Uses existing clones in REPOS_DIR (same as push_readmes_to_github.sh).
# Usage:
#   cd "/path/to/ranking by feedback arc set"
#   ./github_readmes/add_mit_license.sh

set -e
GITHUB_USER="SoroushVahidi"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPOS_DIR="${REPOS_DIR:-$WORKSPACE_ROOT/../github_repos_to_update}"
LICENSE_SRC="$SCRIPT_DIR/MIT_LICENSE.txt"

# Repos without a license (from API: license is null)
NO_LICENSE_REPOS=(
  A-new-approach-for-denoising-salt-and-pepper-noise
  A-new-approach-for-Image-resize-implemented-in-matlab
  bfsbased_node_classification
  Code-for-minimum-distance-linear-codes-problem
  Computing-the-Margin-of-Victory-in-IRV-Elections
  CS301-004-Spring-2021-NJIT-Introduction-to-data-science-
  Design-exploration-for-Graph-partitioning-into-triangles-problem
  diameter-of-polygon
  Fairness-Maximization-among-Offline-Agents-in-Online-Matching-Markets
  Hybrid-Interval-Based-Refinement-for-Large-Scale-Weighted-Feedback-Arc-Set
  IRV_Fairness
  Jigsaw-puzzle-game-solver
  LeetCode_Solutions
  Maximum-weight-connected-subgraph-problem
  Meta-coding-puzzles
  njit_scheduling
  parallel-longest-common-subsequence
  Scheduling-problem
  STVPoll-Soroush
  tropical-connected
  uva
)

if [[ ! -f "$LICENSE_SRC" ]]; then
  echo "Error: $LICENSE_SRC not found"
  exit 1
fi

echo "Repos dir: $REPOS_DIR"
echo "Adding MIT LICENSE to repos that don't have one..."
echo ""

for repo in "${NO_LICENSE_REPOS[@]}"; do
  dir="$REPOS_DIR/$repo"
  echo "--- $repo ---"
  if [[ ! -d "$dir/.git" ]]; then
    echo "  Clone $repo..."
    git clone "https://github.com/$GITHUB_USER/$repo.git" "$dir" || { echo "  Clone failed."; continue; }
  fi
  if [[ -f "$dir/LICENSE" ]] || [[ -f "$dir/LICENSE.md" ]]; then
    echo "  Already has LICENSE, skip"
    continue
  fi
  cp "$LICENSE_SRC" "$dir/LICENSE"
  (cd "$dir" && git add LICENSE && git status -s)
  (cd "$dir" && git commit -m "Add MIT license" && git push origin "$(git branch --show-current)") || echo "  Commit/push failed."
  echo ""
done

echo "Done."
