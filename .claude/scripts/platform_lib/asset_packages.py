"""Shared helpers for resolving CRE asset-package files (Rule 03 manifest).

Rule 03 makes post.md the source of truth and post.txt its publish-ready mirror
(identical content; post.md wins on conflict). Scripts that read "the post" should
therefore accept either form rather than hard-coding post.txt — this is the single
place that encodes that precedence so the readers cannot drift.
"""
from pathlib import Path

# Source-of-truth first (Rule 03), then the publish-ready mirror.
POST_FORMS = ("post.md", "post.txt")


def resolve_post_source(asset_dir: Path) -> Path | None:
    """Return the post file to read for an asset package, or None if absent.

    Prefers post.md (source of truth) and falls back to post.txt (publish mirror).
    """
    for name in POST_FORMS:
        candidate = asset_dir / name
        if candidate.exists():
            return candidate
    return None
