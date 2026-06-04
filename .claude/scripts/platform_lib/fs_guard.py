#!/usr/bin/env python3
"""fs_guard — per-framework write-jail for SCRIPT-driven disk writes.

Turns the Rule-12 domain-boundary table ("No domain writes outside its boundary") from a convention
into a mechanism. A framework script that resolves its target through `assert_under(path, framework)`
BEFORE opening the file cannot write outside its declared root(s) — `..` traversal, symlink escape,
and prefix look-alikes (`docs/profiles-x`) are all defeated by resolve-then-contain.

The allowed roots are derived from `paths.py` (which derives from the project ROOT); the AUTHORITATIVE
spec for which root belongs to which framework is the Domain Boundaries table in
`docs/rules/12-orc-orchestration.md`. Keep the two in sync — the table is the source of truth.

Honesty caveat (mirrors the boundary's real reach): this is a SCRIPT-path guard. It raises before a
script write lands outside the fence. It CANNOT stop a raw LLM `Write`, nor an LLM composing a body
directly to disk — those are governed by the prose boundary rule + the advisory `check_fence` scan +
the CI cross-root-write invariant, not by this assert.
"""

from pathlib import Path

from . import paths

# Per-framework allowed write roots — the single mechanism mirror of Rule-12's Domain Boundaries table.
# PSY owns docs/graph/ (knowledge-graph tier); ORC/COM share .claude/. GRO writes growth/ which lives
# under docs/profiles/ (the fence contains it to the profile tree; growth-only is the skill convention).
_CLAUDE_DIR = paths.ROOT / ".claude"
FRAMEWORK_WRITE_ROOTS = {
    "MAT": [paths.MATERIALS],
    "PSY": [paths.PROFILES, paths.REFERENCES, paths.GRAPH],
    "CRE": [paths.ASSETS],
    "GRO": [paths.PROFILES],
    "ORC": [_CLAUDE_DIR],
    "COM": [_CLAUDE_DIR],
}


class FenceError(Exception):
    """Raised when a script-driven write would land outside the framework's Rule-12 root(s)."""


def allowed_roots(framework: str) -> list[Path]:
    """Resolved allowed write roots for a framework (upper-case key: MAT/PSY/CRE/GRO/ORC/COM)."""
    fw = framework.upper()
    if fw not in FRAMEWORK_WRITE_ROOTS:
        raise FenceError(f"unknown framework {framework!r}; known: {sorted(FRAMEWORK_WRITE_ROOTS)}")
    return [r.resolve() for r in FRAMEWORK_WRITE_ROOTS[fw]]


def assert_under(path, framework: str) -> Path:
    """Return the resolved `path` if it is contained under one of `framework`'s Rule-12 write roots,
    else raise `FenceError`. Raises BEFORE any write, so a blocked target never touches disk.

    `path` may be relative to the project ROOT or absolute; both are resolved (collapsing `..` and
    following symlinks on existing components). The boundary directory itself counts as in-fence."""
    roots = allowed_roots(framework)
    target = Path(path)
    if not target.is_absolute():
        target = paths.ROOT / target
    resolved = target.resolve(strict=False)

    for root in roots:
        if resolved == root or resolved.is_relative_to(root):
            return resolved

    pretty = ", ".join(str(r) for r in roots)
    raise FenceError(
        f"refusing to write outside the {framework.upper()} boundary: {resolved} is not under any of "
        f"[{pretty}]. Per Rule 12, {framework.upper()} writes only there."
    )
