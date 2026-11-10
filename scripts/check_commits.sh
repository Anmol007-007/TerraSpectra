#!/usr/bin/env bash
# check_commits.sh — Count commits made today on this branch vs main
# Usage: bash scripts/check_commits.sh [--min N]
# Exits 0 if commit count >= min (default 52), 1 otherwise.

set -euo pipefail

MIN_COMMITS=${2:-52}
if [[ "${1:-}" == "--min" ]]; then
    MIN_COMMITS="${2}"
fi

BRANCH=$(git rev-parse --abbrev-ref HEAD)
BASE_BRANCH="main"

# Count commits on current branch not in main, authored today
TODAY=$(date +%Y-%m-%d)
COUNT=$(git log "${BASE_BRANCH}..${BRANCH}" \
    --oneline \
    --after="${TODAY} 00:00:00" \
    --before="${TODAY} 23:59:59" \
    2>/dev/null | wc -l | tr -d ' ')

echo "Branch: ${BRANCH}"
echo "Commits today (since ${BASE_BRANCH}): ${COUNT}"
echo "Required: ${MIN_COMMITS}"

if [[ "${COUNT}" -ge "${MIN_COMMITS}" ]]; then
    echo "PASS — ${COUNT} >= ${MIN_COMMITS}"
    exit 0
else
    echo "FAIL — ${COUNT} < ${MIN_COMMITS}"
    exit 1
fi

