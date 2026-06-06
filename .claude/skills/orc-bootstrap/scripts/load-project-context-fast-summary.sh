#!/bin/bash
# Fast project context loader: git log, character INDEX.md heads, profile stats.
# Character roster is derived dynamically from docs/profiles/characters.yaml via the
# venv python (paths.CHAR_DISPLAY), so no display names are hardcoded here.
set -euo pipefail

PROJECT_ROOT="${LUCAS_PROJECT_ROOT:-$(cd "$(dirname "$0")/../../../.." && pwd)}"

echo "## Project Context — $(date '+%Y-%m-%d %H:%M')"
echo ""

echo "### Recent Commits (last 15)"
echo '```'
git -C "$PROJECT_ROOT" log --oneline -15 2>/dev/null || echo "(git unavailable)"
echo '```'
echo ""

echo "### Character Index (quick ref)"
PROFILES="$PROJECT_ROOT/docs/profiles"

# Emit "slug:display" lines from the roster, one per character.
# Falls back to slug-only when the roster file or venv is absent.
_VENV_PY="$PROJECT_ROOT/.claude/skills/.venv/bin/python3"
_ROSTER="$PROJECT_ROOT/docs/profiles/characters.yaml"

if [ -f "$_VENV_PY" ] && [ -f "$_ROSTER" ]; then
    CHAR_PAIRS=$("$_VENV_PY" - "$_ROSTER" <<'PYEOF'
import sys
from pathlib import Path

roster_path = Path(sys.argv[1])
try:
    import yaml
    data = yaml.safe_load(roster_path.read_text(encoding="utf-8")) or {}
    for slug, info in (data.get("characters") or {}).items():
        display = (info or {}).get("display") or slug
        print(f"{slug}:{display}")
except Exception:
    # yaml unavailable or malformed — fall through to slug-only fallback below
    pass
PYEOF
    ) 2>/dev/null || true
else
    CHAR_PAIRS=""
fi

# If the python step produced nothing, fall back to listing profile subdirs.
if [ -z "$CHAR_PAIRS" ]; then
    if [ -d "$PROFILES" ]; then
        CHAR_PAIRS=$(find "$PROFILES" -maxdepth 1 -mindepth 1 -type d ! -name '.*' | sort | \
            while IFS= read -r d; do slug=$(basename "$d"); echo "${slug}:${slug}"; done)
    fi
fi

while IFS= read -r entry; do
    [ -z "$entry" ] && continue
    slug="${entry%%:*}"
    display="${entry##*:}"
    index_file="$PROFILES/$slug/INDEX.md"
    if [ -f "$index_file" ]; then
        echo "#### $display ($slug)"
        head -3 "$index_file"
        echo ""
    else
        echo "#### $display — INDEX.md missing"
        echo ""
    fi
done <<< "$CHAR_PAIRS"

echo "### Profile File Stats"
total_files=0
total_lines=0
while IFS= read -r entry; do
    [ -z "$entry" ] && continue
    slug="${entry%%:*}"
    display="${entry##*:}"
    char_dir="$PROFILES/$slug"
    if [ -d "$char_dir" ]; then
        nfiles=$(find "$char_dir" -name "*.md" | wc -l)
        nlines=$(find "$char_dir" -name "*.md" -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}')
        echo "- **$display**: $nfiles files, $nlines lines"
        total_files=$((total_files + nfiles))
        total_lines=$((total_lines + nlines))
    else
        echo "- **$display**: profile dir missing"
    fi
done <<< "$CHAR_PAIRS"
echo ""
echo "**Total**: $total_files files, $total_lines lines across all characters"
echo ""

echo "### References"
ref_count=$(find "$PROJECT_ROOT/docs/references" -name "*.md" ! -name "INDEX.md" | wc -l)
echo "- $ref_count theory reference files in docs/references/"

echo ""
echo "### Growth (GRO)"
while IFS= read -r entry; do
    [ -z "$entry" ] && continue
    slug="${entry%%:*}"
    display="${entry##*:}"
    growth_dir="$PROFILES/$slug/growth"
    if [ -d "$growth_dir" ]; then
        gfiles=$(find "$growth_dir" -name "*.md" | wc -l)
        echo "- **$display**: $gfiles growth files"
    fi
done <<< "$CHAR_PAIRS"

echo ""
echo "### Assets"
asset_count=$(find "$PROJECT_ROOT/assets" -type f 2>/dev/null | wc -l)
echo "- $asset_count asset files in assets/"
