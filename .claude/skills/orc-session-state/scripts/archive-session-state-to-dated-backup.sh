#!/bin/bash
# Archive current session state.json to .claude/session-state/archive/{YYYYMMDD-HHmm}.json
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
STATE_FILE="$PROJECT_ROOT/.claude/session-state/state.json"
ARCHIVE_DIR="$PROJECT_ROOT/.claude/session-state/archive"

if [ ! -f "$STATE_FILE" ]; then
    echo "No state.json found at: $STATE_FILE"
    exit 0
fi

mkdir -p "$ARCHIVE_DIR"

TIMESTAMP=$(date +"%Y%m%d-%H%M")
DEST="$ARCHIVE_DIR/${TIMESTAMP}.json"

cp "$STATE_FILE" "$DEST"
echo "Archived: $STATE_FILE → $DEST"

# List recent archives
echo ""
echo "Recent archives:"
ls -lt "$ARCHIVE_DIR"/*.json 2>/dev/null | head -5 | awk '{print "  " $NF}'
