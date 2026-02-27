#!/usr/bin/env bash
# Build all paper artifacts in order. Idempotent; prints output paths.
# Run from repo root: bash tools/build_all_paper_artifacts.sh
set -e
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"
PY="${PYTHON:-python}"

echo "=== build_all_paper_artifacts.sh (idempotent) ==="
echo "REPO_ROOT=$REPO_ROOT"
echo ""

echo "--- 1) build_leaderboard_csvs.py ---"
"$PY" tools/build_leaderboard_csvs.py
echo ""

echo "--- 2) validate_paper_artifacts.py (pre-tables) ---"
"$PY" tools/validate_paper_artifacts.py || { echo "Validation failed (pre)." >&2; exit 1; }
echo ""

echo "--- 3) build_paper_tables.py ---"
"$PY" tools/build_paper_tables.py
echo ""

echo "--- 4) build_paper_figs.py ---"
"$PY" tools/build_paper_figs.py
echo ""

echo "--- 5) validate_paper_artifacts.py (post-artifacts) ---"
"$PY" tools/validate_paper_artifacts.py || { echo "Validation failed (post)." >&2; exit 1; }
echo ""

echo "=== Output paths ==="
echo "CSVs:     $REPO_ROOT/paper_csv/leaderboard_per_method.csv"
echo "          $REPO_ROOT/paper_csv/leaderboard_oracle_envelopes.csv"
echo "          $REPO_ROOT/paper_csv/leaderboard_compute_matched.csv"
echo "          $REPO_ROOT/paper_csv/leaderboard_compute_matched_coverage.csv"
echo "          $REPO_ROOT/paper_csv/missingness_audit.csv"
echo "Tables:   $REPO_ROOT/paper_tables/table1_main_leaderboard.{csv,tex}"
echo "          $REPO_ROOT/paper_tables/table2_compute_matched.{csv,tex}"
echo "          $REPO_ROOT/paper_tables/table3_missingness_audit.{csv,tex}"
echo "Figures:  $REPO_ROOT/paper_figs/accuracy_vs_runtime_scatter.{png,pdf}"
echo "          $REPO_ROOT/paper_figs/coverage_vs_time_budget_curve.{png,pdf}"
echo "          $REPO_ROOT/paper_figs/ours_vs_baseline_winloss.{png,pdf}"
echo "Report:   $REPO_ROOT/docs/Artifact_validation_report.md"
echo "Done."
