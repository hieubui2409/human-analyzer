#!/usr/bin/env bash
# Install the framework toolkit from a pack tarball into a target project's .claude/.
# Usage: install.sh <pack.tar.gz> [target-dir]   (default target = current dir). Skip-existing by default;
# FORCE_OVERWRITE=1 to overwrite. Verifies MANIFEST.json is present; never auto-runs anything.
set -euo pipefail
PACK="${1:?usage: install.sh <pack.tar.gz> [target-dir]}"
TARGET="${2:-.}"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
tar xzf "$PACK" -C "$tmp"
[ -f "$tmp/MANIFEST.json" ] || { echo "error: MANIFEST.json missing — not a valid pack" >&2; exit 1; }
flags=(-a); [ "${FORCE_OVERWRITE:-0}" = "1" ] || flags+=(--ignore-existing)
cp -r "${flags[@]}" "$tmp"/. "$TARGET"/ 2>/dev/null || cp -r "$tmp"/. "$TARGET"/
echo "installed pack into $TARGET (FORCE_OVERWRITE=${FORCE_OVERWRITE:-0})"
