#!/bin/bash
# Stage specific files + commit with conventional commit format
# Called by Claude after user confirms file selection.
#
# Env vars (set by Claude before calling):
#   PROJECT_DIR      — git root (auto-detected if not set)
#   LUCAS_COMMIT_MSG — full commit message (pre-built by Claude)
#   LUCAS_FILES      — space-separated file list to stage (used when NOT --all)
#   LUCAS_STAGE_ALL  — "true" to stage everything (--all mode)
#   LUCAS_DRY_RUN    — "true" to preview without committing

set -e
if [ -z "$PROJECT_DIR" ]; then
  PROJECT_DIR=$(git rev-parse --show-toplevel)
fi
cd "$PROJECT_DIR"

# Dry run
if [ "$LUCAS_DRY_RUN" = "true" ]; then
  echo "=== DRY RUN: COMMIT ==="
  if [ "$LUCAS_STAGE_ALL" = "true" ]; then
    echo "Would stage ALL changes (excluding .env/credentials/secrets)"
  elif [ -n "$LUCAS_FILES" ]; then
    echo "Would stage: $LUCAS_FILES"
  fi
  echo "Would commit with message:"
  echo "${LUCAS_COMMIT_MSG:-chore: update}"
  exit 0
fi

# Stage files
if [ "$LUCAS_STAGE_ALL" = "true" ]; then
  echo "Staging ALL changes (--all mode)..."
  git add -A

  # Unstage dangerous files
  EXCLUDE_PATTERNS=(".env" "credentials" "secret" ".key" ".pem")
  for pat in "${EXCLUDE_PATTERNS[@]}"; do
    git diff --cached --name-only | grep -i "$pat" | while read -r f; do
      git reset HEAD -- "$f" 2>/dev/null || true
      echo "EXCLUDED: $f"
    done
  done
elif [ -n "$LUCAS_FILES" ]; then
  echo "Staging selected files..."
  # shellcheck disable=SC2086
  git add $LUCAS_FILES
else
  echo "ERROR: No files specified. Set LUCAS_FILES or LUCAS_STAGE_ALL=true"
  exit 1
fi

# Check if anything is staged
if git diff --cached --quiet; then
  echo "=== NO CHANGES STAGED ==="
  exit 0
fi

# Format staged files with prettier (commit-time, replaces the per-edit PostToolUse
# hook so working edits don't trigger constant reflow). Non-fatal: skip if prettier
# is unavailable. --ignore-unknown skips file types prettier can't format.
if [ "$LUCAS_SKIP_FORMAT" != "true" ]; then
  STAGED=$(git diff --cached --name-only --diff-filter=ACM)
  if [ -n "$STAGED" ]; then
    echo "$STAGED" | xargs npx prettier --write --ignore-unknown >/dev/null 2>&1 || true
    # Re-stage whatever prettier rewrote (only files still present)
    echo "$STAGED" | while read -r f; do [ -f "$f" ] && git add -- "$f" || true; done
    echo "Formatted staged files with prettier."
  fi
fi

# Use pre-built message or fallback
if [ -z "$LUCAS_COMMIT_MSG" ]; then
  LUCAS_COMMIT_MSG="chore: update"
fi

# Commit
echo "=== COMMIT ==="
git commit -m "$(cat <<EOF
$LUCAS_COMMIT_MSG
EOF
)"
echo "Commit OK."
