"""Profile statistics: line counts, file inventory, cache validation."""
import json
import subprocess
from pathlib import Path
from typing import Optional

from .paths import PROFILES, PROFILE_CACHE, PROFILE_FILES, ALL_CHARS, CHAR_DISPLAY


def profile_file_inventory(char_slug: str) -> list[dict]:
    """List all profile files for a character with line counts.

    Walks the nested profile tree (``rglob``) so the 22 files under identity/, psychology/,
    growth/, etc. are counted — not just the 3 root-level files. The ``file`` key is the
    path relative to the character dir (e.g. ``psychology/formulation.md``) so nested files
    with the same basename stay distinct.
    """
    char_dir = PROFILES / char_slug
    if not char_dir.exists():
        return []
    inventory = []
    for f in sorted(char_dir.rglob("*.md")):
        lines = len(f.read_text(encoding="utf-8").splitlines())
        inventory.append({"file": f.relative_to(char_dir).as_posix(), "lines": lines, "path": str(f)})
    return inventory


def all_profiles_summary() -> list[dict]:
    """Summary of all characters' profiles: file count, total lines."""
    summary = []
    for slug in ALL_CHARS:
        files = profile_file_inventory(slug)
        summary.append({
            "character": CHAR_DISPLAY.get(slug, slug),
            "slug": slug,
            "file_count": len(files),
            "total_lines": sum(f["lines"] for f in files),
            "files": files,
        })
    return summary


def git_hash_for_dir(directory: Path) -> Optional[str]:
    """Get latest git commit hash touching a directory."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%H", "--", str(directory)],
            capture_output=True, text=True, timeout=10,
        )
        return result.stdout.strip() or None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def has_uncommitted_changes(directory: Path) -> bool:
    """True if the directory has staged/unstaged/untracked changes in git."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", "--", str(directory)],
            capture_output=True, text=True, timeout=10,
        )
        return bool(result.stdout.strip())
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def cache_is_valid(char_slug: str) -> bool:
    """Check if profile-lite cache is still valid against git state.

    Invalidates on both committed changes (commit-hash mismatch) AND uncommitted
    working-tree edits — a commit-hash check alone would report a stale cache as valid
    while source files were edited but not yet committed.
    """
    meta_file = PROFILE_CACHE / f"{char_slug}-meta.json"
    if not meta_file.exists():
        return False
    try:
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False
    stored_hash = meta.get("git_hash")
    if not stored_hash:
        return False
    char_dir = PROFILES / char_slug
    if has_uncommitted_changes(char_dir):
        return False
    return stored_hash == git_hash_for_dir(char_dir)


def cache_status_table() -> list[dict]:
    """Build cache status for all characters."""
    rows = []
    for slug in ALL_CHARS:
        valid = cache_is_valid(slug)
        lite_file = PROFILE_CACHE / f"{slug}-lite.md"
        lite_lines = 0
        if lite_file.exists():
            lite_lines = len(lite_file.read_text(encoding="utf-8").splitlines())
        full_lines = sum(f["lines"] for f in profile_file_inventory(slug))
        rows.append({
            "character": CHAR_DISPLAY.get(slug, slug),
            "cache_valid": valid,
            "full_lines": full_lines,
            "lite_lines": lite_lines,
            "reduction": f"{((full_lines - lite_lines) / full_lines * 100):.0f}%" if full_lines > 0 else "N/A",
        })
    return rows
