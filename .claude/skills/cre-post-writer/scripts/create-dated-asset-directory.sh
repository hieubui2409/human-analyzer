#!/bin/bash
# Create a dated asset directory with empty template files.
# Usage: ./create-dated-asset-directory.sh <platform> <slug>
# Example: ./create-dated-asset-directory.sh facebook ban-ve-giao-duc

set -euo pipefail

PLATFORM="${1:-}"
SLUG="${2:-}"

if [[ -z "$PLATFORM" || -z "$SLUG" ]]; then
    echo "Usage: $0 <platform> <slug>" >&2
    echo "  platform: facebook | linkedin | instagram | tiktok | youtube | twitter | blog" >&2
    echo "  slug: kebab-case description (e.g. ban-ve-giao-duc)" >&2
    exit 1
fi

# Find project root by walking up to CLAUDE.md
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$SCRIPT_DIR"
for i in $(seq 1 8); do
    if [[ -f "$ROOT/CLAUDE.md" && -d "$ROOT/docs/profiles" ]]; then
        break
    fi
    ROOT="$(dirname "$ROOT")"
done

if [[ ! -f "$ROOT/CLAUDE.md" ]]; then
    echo "ERROR: Cannot find project root (no CLAUDE.md + docs/profiles)" >&2
    exit 1
fi

ASSETS_DIR="$ROOT/assets"
DATE_PREFIX="$(date +%y%m%d)"
DIR_NAME="${DATE_PREFIX}-${SLUG}"
TARGET="$ASSETS_DIR/$PLATFORM/$DIR_NAME"

if [[ -d "$TARGET" ]]; then
    echo "Directory already exists: $TARGET" >&2
    exit 0
fi

mkdir -p "$TARGET/images"

# post.md template
cat > "$TARGET/post.md" <<EOF
<!-- Platform: $PLATFORM | Slug: $SLUG | Created: $(date +%Y-%m-%d) -->

[DRAFT - Write post content here]

EOF

# post.txt (plain text version)
cat > "$TARGET/post.txt" <<EOF
[DRAFT - Plain text version of post]

EOF

# image-prompts.txt template
cat > "$TARGET/image-prompts.txt" <<EOF
# Image Prompts for: $SLUG
# Platform: $PLATFORM
# Created: $(date +%Y-%m-%d)

## Prompt 1
[Describe the image you want to generate]

## Style Notes
- Style:
- Mood:
- Colors:

EOF

echo "$TARGET"
