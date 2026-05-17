#!/bin/bash
# Push with auto-rebase on failure
# Env: PROJECT_DIR, LUCAS_DRY_RUN

set -e
if [ -z "$PROJECT_DIR" ]; then
  PROJECT_DIR=$(git rev-parse --show-toplevel)
fi
cd "$PROJECT_DIR"

BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Dry run
if [ "$LUCAS_DRY_RUN" = "true" ]; then
  echo "=== DRY RUN: PUSH ==="
  echo "Would push '$BRANCH' to origin"
  echo "If rejected: would attempt git pull --rebase + retry"
  exit 0
fi

# Safety: never push to protected branches
case "$BRANCH" in
  main|master|develop|release/*)
    echo "ERROR: Cannot push directly to protected branch '$BRANCH'"
    exit 1
    ;;
esac

echo "=== PUSH ==="

# First attempt
if git push origin "$BRANCH" 2>&1; then
  echo "Push OK."
  exit 0
fi

echo "Push rejected. Attempting rebase..."

# Rebase attempt
if ! git pull --rebase origin "$BRANCH" 2>&1; then
  # Check for rebase in progress (conflict)
  GIT_DIR=$(git rev-parse --git-dir)
  if [ -d "$GIT_DIR/rebase-merge" ] || [ -d "$GIT_DIR/rebase-apply" ]; then
    echo "CONFLICT detected during rebase. Aborting."
    git rebase --abort
    echo "ERROR: Rebase conflicts. Resolve manually then run /lucas:git --push"
    exit 1
  fi
  echo "ERROR: Pull --rebase failed."
  exit 1
fi

echo "Rebase OK. Retrying push..."

# Second attempt
if git push origin "$BRANCH" 2>&1; then
  echo "Push OK after rebase."
  exit 0
fi

echo "ERROR: Push failed after rebase. Check remote state manually."
exit 1
