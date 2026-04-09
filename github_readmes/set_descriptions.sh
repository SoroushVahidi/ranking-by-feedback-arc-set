#!/usr/bin/env bash
# Set GitHub repo descriptions (About) for all SoroushVahidi repos via API.
# Requires: GITHUB_TOKEN with repo scope (Settings -> Developer settings -> Personal access tokens).
# Usage:
#   export GITHUB_TOKEN=ghp_xxxx
#   cd "/path/to/ranking by feedback arc set/github_readmes"
#   ./set_descriptions.sh
# Optional: ./set_descriptions.sh --dry-run

set -e
GITHUB_USER="SoroushVahidi"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DRY_RUN=false
[[ "$1" == --dry-run ]] && DRY_RUN=true

if [[ -z "$GITHUB_TOKEN" ]]; then
  echo "Error: set GITHUB_TOKEN (e.g. export GITHUB_TOKEN=ghp_xxxx)"
  exit 1
fi

while IFS= read -r line; do
  [[ "$line" =~ ^#.*$ ]] && continue
  [[ -z "$line" ]] && continue
  repo="${line%%|*}"
  desc="${line#*|}"
  # trim
  repo=$(echo "$repo" | xargs)
  desc=$(echo "$desc" | xargs)
  [[ -z "$repo" || -z "$desc" ]] && continue
  echo "--- $repo ---"
  if $DRY_RUN; then
    echo "  [dry-run] description: $desc"
    continue
  fi
  json_desc=$(printf '%s' "$desc" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))' 2>/dev/null) || json_desc="\"$desc\""
  resp=$(curl -s -w "\n%{http_code}" -X PATCH \
    -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/$GITHUB_USER/$repo" \
    -d "{\"description\":$json_desc}" 2>/dev/null) || true
  code=$(echo "$resp" | tail -1)
  if [[ "$code" == "200" ]]; then
    echo "  OK"
  else
    echo "  HTTP $code (may need repo scope or repo not found)"
  fi
done < <(grep -v '^#' "$SCRIPT_DIR/REPO_DESCRIPTIONS.txt" | grep '|')

echo "Done."
