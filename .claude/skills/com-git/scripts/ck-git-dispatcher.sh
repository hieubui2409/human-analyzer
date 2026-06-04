#!/bin/bash
# ck-git-dispatcher — Main git dispatcher for ck-marketing project
# Usage: ck-git-dispatcher.sh [FLAGS] [-m "msg"]
# Flags: --commit --push --sync --all --dry-run
# Default (no flags): --commit --push
#
# NOTE: --commit is typically called by Claude directly (not via this dispatcher)
# because Claude handles smart file selection + user confirmation via AskUserQuestion.
# This dispatcher is used for --push, --sync, and --all mode.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PROJECT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# Parse args
FLAGS=()
COMMIT_MSG=""
STAGE_ALL=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --commit|--push|--sync)
      FLAGS+=("$1"); shift ;;
    --all)
      STAGE_ALL=true; shift ;;
    --dry-run)
      DRY_RUN=true; shift ;;
    -m)
      COMMIT_MSG="$2"; shift 2 ;;
    --help|-h)
      echo "Usage: ck-git-dispatcher.sh [--commit] [--push] [--sync] [--all] [--dry-run] [-m 'msg']"
      echo ""
      echo "Flags:"
      echo "  --commit     Stage and commit files"
      echo "  --push       Push to remote with auto-rebase on rejection"
      echo "  --sync       Pull --rebase from remote"
      echo "  --all        Stage all changes (used with --commit)"
      echo "  --dry-run    Preview actions without executing"
      echo "  -m 'msg'     Custom commit message"
      echo ""
      echo "Default (no flags): --commit --push"
      exit 0
      ;;
    *)
      shift ;;
  esac
done

# Default: --commit --push
if [ ${#FLAGS[@]} -eq 0 ]; then
  FLAGS=("--commit" "--push")
fi

# commit.sh needs either --all or an explicit LUCAS_FILES list (env, set by Claude after
# smart file selection). If --commit is requested with neither, fail fast with guidance
# instead of letting commit.sh emit a cryptic "No files specified" exit 1.
for flag in "${FLAGS[@]}"; do
  if [ "$flag" = "--commit" ] && [ "$STAGE_ALL" != "true" ] && [ -z "$LUCAS_FILES" ]; then
    echo "ERROR: --commit needs files. Pass --all to stage everything, or set LUCAS_FILES" >&2
    echo "       (space-separated paths) before calling. Claude normally selects files and" >&2
    echo "       calls commit.sh directly; the dispatcher is mainly for --push/--sync/--all." >&2
    exit 1
  fi
done

export LUCAS_COMMIT_MSG="$COMMIT_MSG"
export LUCAS_STAGE_ALL="$STAGE_ALL"
export LUCAS_DRY_RUN="$DRY_RUN"
export LUCAS_FILES="${LUCAS_FILES:-}"

# Execute flags sequentially, stop on failure
EXIT_CODE=0
for flag in "${FLAGS[@]}"; do
  case "$flag" in
    --commit) bash "$SCRIPT_DIR/commit.sh" || EXIT_CODE=$? ;;
    --push)   bash "$SCRIPT_DIR/push-with-auto-rebase.sh"   || EXIT_CODE=$? ;;
    --sync)   bash "$SCRIPT_DIR/sync-pull-rebase.sh"   || EXIT_CODE=$? ;;
  esac
  [ $EXIT_CODE -ne 0 ] && break
done

exit $EXIT_CODE
