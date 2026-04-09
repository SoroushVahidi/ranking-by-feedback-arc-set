#!/usr/bin/env bash
# Push READMEs to all SoroushVahidi GitHub repos from the terminal.
# Usage:
#   cd "/path/to/ranking by feedback arc set/github_readmes"
#   ./push_readmes_to_github.sh [--dry-run] [--repos-dir /path/to/clones]
#
# Set REPOS_DIR to where repos are or should be cloned (default: ../github_repos_to_update).
# Requires: git, and your GitHub auth (SSH or HTTPS with token) for push.

set -e
GITHUB_USER="SoroushVahidi"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPOS_DIR="${REPOS_DIR:-$WORKSPACE_ROOT/../github_repos_to_update}"
DRY_RUN=false
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    --repos-dir=*) REPOS_DIR="${arg#*=}" ;;
    --repos-dir) shift; REPOS_DIR="$1" ;;
  esac
done

mkdir -p "$REPOS_DIR"

# Repo name -> README source file (relative to github_readmes/)
declare -A MAP
MAP[A-new-approach-for-denoising-salt-and-pepper-noise]=denoising-salt-pepper.md
MAP[A-new-approach-for-Image-resize-implemented-in-matlab]=image-resize-matlab.md
MAP[bfsbased_node_classification]=bfsbased-node-classification.md
MAP[Code-for-minimum-distance-linear-codes-problem]=minimum-distance-linear-codes.md
MAP[combinatorial-opt-agent]=combinatorial-opt-agent.README.md
MAP[Computing-the-Margin-of-Victory-in-IRV-Elections]=irv-margin-victory.md
MAP[CS301-004-Spring-2021-NJIT-Introduction-to-data-science-]=cs301-data-science.md
MAP[Design-exploration-for-Graph-partitioning-into-triangles-problem]=graph-partition-triangles.md
MAP[diameter-of-polygon]=diameter-polygon.md
MAP[Fairness-Maximization-among-Offline-Agents-in-Online-Matching-Markets]=fairness-online-matching.md
MAP[Hybrid-Interval-Based-Refinement-for-Large-Scale-Weighted-Feedback-Arc-Set]=hybrid-interval-fas.md
MAP[IRV_Fairness]=irv-fairness.md
MAP[Jigsaw-puzzle-game-solver]=jigsaw-puzzle-solver.md
MAP[LeetCode_Solutions]=leetcode-solutions.md
MAP[Maximum-weight-connected-subgraph-problem]=max-weight-connected-subgraph.md
MAP[Meta-coding-puzzles]=meta-coding-puzzles.md
MAP[minimum-feedback-challenge]=minimum-feedback-challenge.md
MAP[njit_scheduling]=njit-scheduling.md
MAP[parallel-longest-common-subsequence]=parallel-lcs.md
MAP[Ranking_with_MWFAS]=ranking-with-mwfas.md
MAP[Scheduling-problem]=scheduling-problem.md
MAP[STVPoll-Soroush]=stvpoll-soroush.md
MAP[sudoku-example]=sudoku-example.md
MAP[tropical-connected]=tropical-connected.md
MAP[uva]=uva.md
MAP[weighted-minfas-codes]=weighted-minfas-codes.md

clone_or_update() {
  local repo="$1"
  local dir="$REPOS_DIR/$repo"
  if [[ ! -d "$dir/.git" ]]; then
    echo "  Clone $repo..."
    if ! $DRY_RUN; then
      git clone "https://github.com/$GITHUB_USER/$repo.git" "$dir" || { echo "  Clone failed (network or repo missing)."; return 1; }
    fi
  else
    echo "  Pull $repo..."
    if ! $DRY_RUN; then
      (cd "$dir" && git pull --rebase || true)
    fi
  fi
  return 0
}

copy_readme() {
  local repo="$1"
  local src="$2"
  local dir="$REPOS_DIR/$repo"
  if [[ ! -f "$SCRIPT_DIR/$src" ]]; then
    echo "  SKIP $repo: file $src not found"
    return 1
  fi
  if ! $DRY_RUN; then
    cp "$SCRIPT_DIR/$src" "$dir/README.md"
  fi
  echo "  Copy $src -> $repo/README.md"
  return 0
}

commit_and_push() {
  local repo="$1"
  local dir="$REPOS_DIR/$repo"
  if $DRY_RUN; then
    echo "  [dry-run] would commit and push $repo"
    return 0
  fi
  (cd "$dir" && git add README.md && git diff --cached --quiet && { echo "  No changes $repo"; return 0; } || true)
  (cd "$dir" && git commit -m "docs: update README for users" && git push origin "$(git branch --show-current)" || echo "  Push failed or no changes: $repo")
}

# ranking-by-feedback-arc-set: use workspace root README.md
update_ranking_repo() {
  local repo="ranking-by-feedback-arc-set"
  local dir="$REPOS_DIR/$repo"
  clone_or_update "$repo"
  if [[ -f "$WORKSPACE_ROOT/README.md" ]]; then
    if ! $DRY_RUN; then
      cp "$WORKSPACE_ROOT/README.md" "$dir/README.md"
    fi
    echo "  Copy workspace root README.md -> $repo/README.md"
  else
    echo "  SKIP $repo: $WORKSPACE_ROOT/README.md not found"
    return 1
  fi
  commit_and_push "$repo"
}

echo "README source dir: $SCRIPT_DIR"
echo "Repos dir: $REPOS_DIR"
echo "Dry run: $DRY_RUN"
echo ""

for repo in "${!MAP[@]}"; do
  readme_file="${MAP[$repo]}"
  echo "--- $repo ---"
  clone_or_update "$repo" || { echo "  Skip $repo (clone failed)."; echo ""; continue; }
  [[ -d "$REPOS_DIR/$repo" ]] || { echo "  Skip $repo (no dir)."; echo ""; continue; }
  copy_readme "$repo" "$readme_file" && commit_and_push "$repo"
  echo ""
done

echo "--- ranking-by-feedback-arc-set (root README) ---"
update_ranking_repo
echo ""
echo "Done. Check $REPOS_DIR and GitHub."
