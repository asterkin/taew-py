#!/usr/bin/env bash
set -euo pipefail

# Close an issue: bump version, build (unless skipped), commit, push, PR, merge, sync main, close issue
# Usage: issue-close.sh [-i <issue-number>] [-m "commit message"] [--skip-build] [--major] [--no-bump]

ISSUE_NUMBER=""
COMMIT_MSG=""
SKIP_BUILD="false"
BUMP_TYPE=""  # Will be: major, minor, patch, or none

while [[ $# -gt 0 ]]; do
  case "$1" in
    -i|--issue)
      ISSUE_NUMBER="$2"; shift 2 ;;
    -m|--message)
      COMMIT_MSG="$2"; shift 2 ;;
    --skip-build)
      SKIP_BUILD="true"; shift ;;
    --major)
      BUMP_TYPE="major"; shift ;;
    --no-bump)
      BUMP_TYPE="none"; shift ;;
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

# Function: Get issue labels from GitHub
get_issue_labels() {
  local issue_num="$1"
  gh issue view "$issue_num" --json labels --jq '.labels[].name' 2>/dev/null || echo ""
}

# Function: Parse current version from a file
get_version_from_file() {
  local file="$1"
  local pattern="$2"
  grep -E "$pattern" "$file" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1
}

# Function: Determine bump type from issue labels
determine_bump_type() {
  local labels="$1"

  # If already set via flag, return it
  if [[ -n "$BUMP_TYPE" ]]; then
    echo "$BUMP_TYPE"
    return
  fi

  # Check labels for bump type
  if echo "$labels" | grep -q "^enhancement$"; then
    echo "minor"
  elif echo "$labels" | grep -q "^bug$"; then
    echo "patch"
  elif echo "$labels" | grep -q "^documentation$"; then
    echo "none"
  else
    # Default to patch for unlabeled issues
    echo "patch"
  fi
}

# Function: Calculate new version
bump_version() {
  local current="$1"
  local bump_type="$2"

  if [[ "$bump_type" == "none" ]]; then
    echo "$current"
    return
  fi

  IFS='.' read -r major minor patch <<< "$current"

  case "$bump_type" in
    major)
      echo "$((major + 1)).0.0"
      ;;
    minor)
      echo "$major.$((minor + 1)).0"
      ;;
    patch)
      echo "$major.$minor.$((patch + 1))"
      ;;
    *)
      echo "$current"
      ;;
  esac
}

# Function: Update version in a file
update_version_in_file() {
  local file="$1"
  local old_version="$2"
  local new_version="$3"

  if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS requires empty string after -i
    sed -i '' "s/$old_version/$new_version/g" "$file"
  else
    sed -i "s/$old_version/$new_version/g" "$file"
  fi
}

# Version bumping logic
REPO_ROOT=$(git rev-parse --show-toplevel)
PYPROJECT_FILE="$REPO_ROOT/pyproject.toml"
INIT_FILE="$REPO_ROOT/taew/__init__.py"

# Get issue labels and determine bump type
labels=$(get_issue_labels "$ISSUE_NUMBER")
bump_type=$(determine_bump_type "$labels")

if [[ "$bump_type" != "none" ]]; then
  # Get current version from both files
  current_version=$(get_version_from_file "$PYPROJECT_FILE" '^version\s*=')

  if [[ -z "$current_version" ]]; then
    echo "Warning: Could not parse version from $PYPROJECT_FILE" >&2
  else
    # Calculate new version
    new_version=$(bump_version "$current_version" "$bump_type")

    if [[ "$new_version" != "$current_version" ]]; then
      echo "Bumping version: $current_version → $new_version ($bump_type)"

      # Update both files
      update_version_in_file "$PYPROJECT_FILE" "$current_version" "$new_version"
      update_version_in_file "$INIT_FILE" "$current_version" "$new_version"

      echo "Updated version in:"
      echo "  - pyproject.toml"
      echo "  - taew/__init__.py"
    fi
  fi
else
  echo "Skipping version bump (bump type: $bump_type)"
fi

if [[ "$SKIP_BUILD" != "true" ]]; then
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
gh pr merge --squash --delete-branch --admin

# Sync main and close the issue
git switch main 2>/dev/null || git checkout main
git pull origin main
gh issue close "$ISSUE_NUMBER" -c "Merged via PR"

# Final summary
echo "Closed issue #$ISSUE_NUMBER and merged changes into main"
if [[ "$bump_type" != "none" && -n "$new_version" && "$new_version" != "$current_version" ]]; then
  echo "Version bumped: $current_version → $new_version ($bump_type)"
fi
