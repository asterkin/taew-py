#!/usr/bin/env bash
set -euo pipefail

# Assign existing issue to @me, create and push a branch
# Usage: issue-assign-branch.sh <issue-number>

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <issue-number>" >&2
  exit 1
fi

ISSUE_NUMBER="$1"

slugify() {
  tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g;s/^-+//;s/-+$//'
}

gh issue edit "$ISSUE_NUMBER" --assignee @me >/dev/null

out=$(gh issue view "$ISSUE_NUMBER" --json number,title --jq '.number|tostring+"\t"+.title')
title=${out#*$'\t'}

branch_slug=$(printf %s "$title" | slugify)
branch_name="$ISSUE_NUMBER-$branch_slug"

git checkout -b "$branch_name"
git push -u origin "$branch_name"

echo "Assigned issue #$ISSUE_NUMBER and created branch $branch_name"

