#!/usr/bin/env bash
set -euo pipefail

# Create a local checkpoint commit without pushing
# Usage: checkpoint.sh ["message"]

MSG=${1:-"WIP: checkpoint"}

git add -A
git commit -m "$MSG" || echo "No changes to commit"

echo "Checkpoint created locally: $MSG"

