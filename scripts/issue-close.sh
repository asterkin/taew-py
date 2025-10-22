#!/usr/bin/env bash
set -euo pipefail

# Close an issue: build (unless skipped), commit, push, PR, merge, sync main, close issue
# Usage: issue-close.sh [-i <issue-number>] [-m "commit message"] [--skip-build]

ISSUE_NUMBER=""
COMMIT_MSG=""
SKIP_BUILD="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    -i|--issue)
      ISSUE_NUMBER="$2"; shift 2 ;;
    -m|--message)
      COMMIT_MSG="$2"; shift 2 ;;
    --skip-build)
      SKIP_BUILD="true"; shift ;;
    *)
      echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

# Derive issue number from branch if not provided (expects <num>-slug)
if [[ -z "$ISSUE_NUMBER" ]]; then
  current_branch=$(git rev-parse --abbrev-ref HEAD)
  if [[ "$current_branch" =~ ^([0-9]+)- ]]; then
    ISSUE_NUMBER="${BASH_REMATCH[1]}"
  else
    echo "Cannot infer issue number from branch. Use -i <issue>." >&2
    exit 1
  fi
fi

if [[ "$SKIP_BUILD" != "true" ]]; then
  REPO_ROOT=$(git rev-parse --show-toplevel)
  if [[ -x "$REPO_ROOT/scripts/build-all.sh" ]]; then
    "$REPO_ROOT/scripts/build-all.sh"
  else
    echo "Skipping build (scripts/build-all.sh not found or not executable)" >&2
  fi
fi

git add -A
if [[ -z "$COMMIT_MSG" ]]; then
  COMMIT_MSG="Resolve #$ISSUE_NUMBER"
fi
git commit -m "$COMMIT_MSG" || echo "No changes to commit"

# Ensure branch has upstream
branch=$(git rev-parse --abbrev-ref HEAD)
git push -u origin "$branch" || git push || true

# Create PR if none exists
if ! gh pr view >/dev/null 2>&1; then
  gh pr create --fill --assignee @me
fi

# Merge PR and delete branch
gh pr merge --squash --delete-branch --auto

# Sync main and close the issue
git switch main 2>/dev/null || git checkout main
git pull origin main
gh issue close "$ISSUE_NUMBER" -c "Merged via PR"

echo "Closed issue #$ISSUE_NUMBER and merged changes into main"
