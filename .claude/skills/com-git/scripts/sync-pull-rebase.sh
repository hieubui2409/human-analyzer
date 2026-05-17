#!/bin/bash
# Pull --rebase from remote with conflict detection and abort safety
# Env: PROJECT_DIR, LUCAS_DRY_RUN

set -e
if [ -z "$PROJECT_DIR" ]; then
  PROJECT_DIR=$(git rev-parse --show-toplevel)
fi
cd "$PROJECT_DIR"

BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Dry run
if [ "$LUCAS_DRY_RUN" = "true" ]; then
  echo "=== DRY RUN: SYNC ==="
  echo "Would pull --rebase origin '$BRANCH'"
  exit 0
fi

echo "=== SYNC ==="

if ! git pull --rebase origin "$BRANCH" 2>&1; then
  GIT_DIR=$(git rev-parse --git-dir)
  if [ -d "$GIT_DIR/rebase-merge" ] || [ -d "$GIT_DIR/rebase-apply" ]; then
    echo "CONFLICT detected during rebase. Aborting."
    git rebase --abort
    echo "ERROR: Rebase conflicts. Resolve manually."
    exit 1
  fi
  echo "ERROR: Sync failed."
  exit 1
fi

echo "Sync OK."
