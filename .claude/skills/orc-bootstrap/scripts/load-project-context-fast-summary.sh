#!/bin/bash
# Fast project context loader: git log, character INDEX.md heads, profile stats.
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
CHARS=("character-a:Nhân vật A" "character-b:Nhân vật B" "character-c:Nhân vật C")
for entry in "${CHARS[@]}"; do
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
done

echo "### Profile File Stats"
total_files=0
total_lines=0
for entry in "${CHARS[@]}"; do
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
done
echo ""
echo "**Total**: $total_files files, $total_lines lines across all characters"
echo ""

echo "### References"
ref_count=$(find "$PROJECT_ROOT/docs/references" -name "*.md" ! -name "INDEX.md" | wc -l)
echo "- $ref_count theory reference files in docs/references/"

echo ""
echo "### Assets"
asset_count=$(find "$PROJECT_ROOT/assets" -type f 2>/dev/null | wc -l)
echo "- $asset_count asset files in assets/"
