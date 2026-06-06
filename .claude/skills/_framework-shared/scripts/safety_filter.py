#!/usr/bin/env python3
"""safety_filter — the non-removable drop rules for the framework pack.

Distribution must NEVER ship secrets, machine-local runtime, or real-character PII. These rules are applied
as a hard backstop AFTER the manifest include globs, so an include glob can never accidentally pull a dropped
class. The rule list is deliberately broad and not overridable by the manifest.
"""

import re

# Substrings / suffixes that are ALWAYS dropped, whatever the include globs say.
_DROP_DIR_SEGMENTS = (
    "/.git/", "/__pycache__/", "/.venv/", "/node_modules/", "/.models/", "/.cache/",
    "/.claude/telemetry/", "/.claude/cache/runtime/", "/.claude/skills/.venv/",
    # Stray plan/report artifacts misfiled under .claude/scripts/ — these are working notes
    # (validation reports naming real characters), not shippable toolkit code.
    "/.claude/scripts/plans/",
    # real-character PII — the toolkit ships the SKILLS, never the live corpus. docs/references is
    # dropped here too: its clinical theory files carry §4 Case Studies naming the real characters
    # (DSM / trauma / SI analysis tied to named people) — same PII class as profiles/materials/graph.
    "/docs/profiles/", "/docs/materials/", "/docs/graph/", "/docs/references/",
)
_DROP_SUFFIX = (".key", ".pem", ".p12", ".pfx", ".pyc")
_SECRET_NAME = re.compile(r"(^|/)(\.env(\.[^/]*)?|credentials[^/]*|[^/]*secret[^/]*)$", re.I)
# .env.example is documentation, not a secret — explicitly kept.
_KEEP = re.compile(r"(^|/)\.env\.example$", re.I)


def is_dropped(arcname: str) -> tuple[bool, str]:
    """Return (dropped, rule) for a repo-relative POSIX path. True ⇒ must not ship."""
    p = "/" + arcname.strip("/")
    if _KEEP.search(arcname):
        return False, ""
    for seg in _DROP_DIR_SEGMENTS:
        if seg in p:
            return True, f"dir-segment {seg!r}"
    if p.endswith(_DROP_SUFFIX):
        return True, "secret/binary suffix"
    if _SECRET_NAME.search(arcname):
        return True, "secret name"
    return False, ""
