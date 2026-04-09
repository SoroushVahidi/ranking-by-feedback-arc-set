#!/usr/bin/env bash
# Run all GitHub-related tasks from the terminal.
# Usage (from repo root):
#   cd "/path/to/ranking by feedback arc set"
#   chmod +x do_everything_from_terminal.sh
#   ./do_everything_from_terminal.sh [option]
#
# Options:
#   (none)     - Show menu and run selected steps
#   sync       - Sync this repo (ranking-by-feedback-arc-set) to GitHub, exclude big files
#   readmes    - Push READMEs to all other GitHub repos (clone/update, copy README, commit, push)
#   all        - Run sync then readmes

set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

run_sync() {
  echo "========== 1. Sync this repo (ranking-by-feedback-arc-set) to GitHub =========="
  bash GNNRank-main/sync_to_github.sh
  git add -A
  git status
  echo ""
  read -p "Commit and push this repo? [y/N] " -n 1 -r
  echo
  if [[ $REPLY =~ ^[yY]$ ]]; then
    git commit -m "Sync from wulver; ignore large outputs/data" || true
    git push origin main || git push origin master || echo "Push failed (check remote and branch)."
  fi
}

run_readmes() {
  echo "========== 2. Push READMEs to all other GitHub repos =========="
  REPOS_DIR="${REPOS_DIR:-$ROOT/../github_repos_to_update}"
  export REPOS_DIR
  bash "$ROOT/github_readmes/push_readmes_to_github.sh"
}

case "${1:-}" in
  sync)   run_sync ;;
  readmes) run_readmes ;;
  all)   run_sync; run_readmes ;;
  *)
    echo "Usage: $0 { sync | readmes | all }"
    echo ""
    echo "  sync    - Sync this repo to GitHub (remove big files from tracking, commit, push)"
    echo "  readmes - Clone/update all other repos, copy READMEs from github_readmes/, commit, push"
    echo "  all     - Run sync then readmes"
    echo ""
    echo "Set REPOS_DIR to change where other repos are cloned (default: ../github_repos_to_update)."
    echo "Example: REPOS_DIR=~/my_clones $0 readmes"
    exit 0
    ;;
esac
