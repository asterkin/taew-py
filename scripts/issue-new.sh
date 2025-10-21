#!/usr/bin/env bash
set -euo pipefail

# Create a new GitHub issue, assign to @me, create and push a branch
# Usage: issue-new.sh -t "Title" [-b "Body"] [-l feature|bug|refactor]

usage() {
  echo "Usage: $0 -t <title> [-b <body>] [-l <label>]" >&2
  exit 1
}

TITLE=""
BODY=""
LABEL=""
while getopts ":t:b:l:" opt; do
  case $opt in
    t) TITLE="$OPTARG" ;;
    b) BODY="$OPTARG" ;;
    l) LABEL="$OPTARG" ;;
    *) usage ;;
  esac
done
shift $((OPTIND-1))

[[ -n "$TITLE" ]] || usage

slugify() {
  tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g;s/^-+//;s/-+$//'
}

# Prepare arguments for the gh issue create command
create_args=(--title "$TITLE" --assignee @me)
[[ -n "$BODY" ]] && create_args+=(--body "$BODY")
[[ -n "$LABEL" ]] && create_args+=(--label "$LABEL")

# Create the issue and capture the output URL
issue_url=$(gh issue create "${create_args[@]}")

# Extract the issue number from the URL (it's the last part)
issue_number=$(echo "$issue_url" | awk -F'/' '{print $NF}')

# The title is already in our $TITLE variable
issue_title="$TITLE"

branch_slug=$(printf %s "$issue_title" | slugify)
branch_name="$issue_number-$branch_slug"

git checkout -b "$branch_name"
git push -u origin "$branch_name"

echo "Created issue #$issue_number and branch $branch_name"
echo "$issue_url"