#!/usr/bin/env python3
"""check_fence — advisory soft-fence scan (the pull-side companion to fs_guard).

ADVISORY ONLY: never blocks, always exits 0, never a write guard. Two scans:

1. `fence_breach` — `git status --porcelain -z -uall` over the project root; any changed path not under
   ANY framework's Rule-12 write root (and not an allowed meta path: plans/, docs/, .github/, tests/,
   e2e/, examples/, tools/, root .md/config) is surfaced (severity warn). Catches the writes fs_guard
   cannot intercept (raw LLM Write, LLM-composed bodies).
2. `unbalanced_fence` — markdown code-fence (```) parity over a given file or the changed .md set; an
   odd fence count is a warn (a likely truncated/garbled doc).

Deterministic, no LLM. Degrades to empty (never raises) outside a git work tree.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

# Dual import: usable both as a package module (from .) and as a direct CLI (`check_fence.py`).
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from platform_lib import paths, fs_guard
else:
    from . import paths
    from . import fs_guard

# Repo-relative POSIX prefixes that are legitimately writable by tooling/docs (not domain content).
_ALLOWED_META_PREFIXES = (
    "plans/", "docs/", ".github/", "tests/", "e2e/", "examples/", "tools/",
    ".claude/", "assets/",
)
# All framework roots as repo-relative POSIX prefixes (derived from Rule-12 via fs_guard).
def _domain_prefixes() -> list[str]:
    prefixes = []
    for fw in fs_guard.FRAMEWORK_WRITE_ROOTS:
        for root in fs_guard.allowed_roots(fw):
            try:
                rel = root.relative_to(paths.ROOT.resolve())
            except ValueError:
                continue
            prefixes.append(str(rel).replace("\\", "/").rstrip("/") + "/")
    return prefixes


def _porcelain_paths(root: Path) -> list[str]:
    """Repo-relative POSIX paths of every changed file. [] if not a git work tree (advisory degrades)."""
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain", "-z", "-uall"],
            cwd=str(root), capture_output=True, text=True,
        )
    except (OSError, FileNotFoundError):
        return []
    if proc.returncode != 0:
        return []
    paths_out: list[str] = []
    fields = proc.stdout.split("\x00")
    i = 0
    while i < len(fields):
        rec = fields[i]
        if not rec:
            i += 1
            continue
        status, path = rec[:2], rec[3:]
        paths_out.append(path)
        if status and status[0] in ("R", "C"):  # rename/copy: next field is the origin path
            i += 1
            if i < len(fields) and fields[i]:
                paths_out.append(fields[i])
        i += 1
    return paths_out


def scan_changes(root: Path) -> list[dict]:
    """One `fence_breach` warn per changed path outside every domain root + allowed meta prefix."""
    allowed = tuple(_domain_prefixes()) + _ALLOWED_META_PREFIXES
    findings = []
    for rel in _porcelain_paths(Path(root)):
        posix = rel.replace("\\", "/")
        if any(posix == p.rstrip("/") or posix.startswith(p) for p in allowed):
            continue
        findings.append({
            "check": "fence_breach", "severity": "warn", "file": posix,
            "detail": f"{posix} changed outside every Rule-12 domain root + allowed meta path. "
                      f"Advisory — confirm this write belongs here.",
        })
    return findings


def scan_fence_balance(md_path: Path) -> list[dict]:
    """One `unbalanced_fence` warn if a markdown file has an odd number of ``` fences."""
    try:
        text = md_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    count = sum(1 for line in text.splitlines() if line.lstrip().startswith("```"))
    if count % 2 != 0:
        return [{
            "check": "unbalanced_fence", "severity": "warn", "file": str(md_path),
            "detail": f"{count} code-fence markers (odd) — likely a truncated or garbled markdown doc.",
        }]
    return []


def main() -> int:
    ap = argparse.ArgumentParser(description="Advisory soft-fence scan (never gates).")
    ap.add_argument("--root", default=str(paths.ROOT))
    ap.add_argument("--fence-file", help="also check markdown fence balance for this file")
    args = ap.parse_args()

    findings = scan_changes(Path(args.root))
    if args.fence_file:
        findings += scan_fence_balance(Path(args.fence_file))
    print(json.dumps({"findings": findings, "count": len(findings)}, ensure_ascii=False, indent=2))
    return 0  # advisory: always 0


if __name__ == "__main__":
    sys.exit(main())
