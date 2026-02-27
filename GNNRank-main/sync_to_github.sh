#!/bin/bash
# Remove large paths from git tracking so GitHub = wulver repo minus big files.
# Run from repo root: cd "/mmfs1/home/sv96/ranking by feedback arc set" && bash GNNRank-main/sync_to_github.sh
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "Removing large files/dirs from git tracking (files stay on disk)..."
git rm -r --cached GNNRank-main/result_arrays 2>/dev/null || true
git rm -r --cached GNNRank-main/slurm_logs 2>/dev/null || true
git rm -r --cached GNNRank-main/logs_suite 2>/dev/null || true
git rm --cached GNNRank-main/data/finance/finance_data.csv 2>/dev/null || true
git rm --cached GNNRank-main/data/finance/finance_data.npy 2>/dev/null || true
git rm --cached GNNRank-main/full_833614_metrics_best.csv 2>/dev/null || true
for f in GNNRank-main/data/finance/*.pk; do
  [ -f "$f" ] && git rm --cached "$f" 2>/dev/null || true
done
for f in GNNRank-main/full_*.out GNNRank-main/dryrun_*.out; do
  [ -f "$f" ] && git rm --cached "$f" 2>/dev/null || true
done
for f in GNNRank-main/*.err GNNRank-main/dryrun_*.err; do
  [ -f "$f" ] && git rm --cached "$f" 2>/dev/null || true
done

git add .gitignore GITHUB_SYNC.md GNNRank-main/sync_to_github.sh 2>/dev/null || true
git status
echo ""
echo "Then: git add -A && git commit -m 'Sync from wulver; ignore large outputs/data' && git push origin main"
