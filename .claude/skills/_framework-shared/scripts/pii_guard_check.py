#!/usr/bin/env python3
"""pii_guard_check — birth-time decision for the PII write-guard hook.

Given a target path (repo-relative or absolute) and the text about to be written (stdin), decide
whether the write would bake a real-name token into a SHIPPED-CLASS file (one the public toolkit pack
distributes). Emits a JSON verdict the thin .cjs hook maps to a block (exit 2) or pass (exit 0).

Shipped-class = matches a pack.manifest include glob AND is not dropped by safety_filter. The corpus
(docs/profiles, docs/materials, docs/graph, docs/references) is where real names BELONG, and is dropped
by safety_filter, so writes there never trip the guard. Path-pattern matched (not selection membership)
so a brand-new file that does not yet exist on disk is still classified correctly.

Tokens are the COLLISION-FREE scanner set (pii_tokens.scan_tokens: slugs + multi-word full names +
extras) — the SAME set the ship-time scan_pack_pii gate uses. Bare display names are deliberately
excluded there because they collide with everyday Vietnamese words; a blocking write-guard on them would
storm with false positives. So the guard matches case-sensitive, word-boundary, only on forms that
cannot collide with ordinary prose. Roster absent (consumer pack) ⇒ empty set ⇒ guard no-ops.

Usage:
  pii_guard_check.py --path <file> [--profiles-dir <dir>]   # text to scan on stdin
  prints a JSON object; exit code is always 0 (the .cjs maps the verdict to the hook protocol).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import build_pack  # noqa: E402  (sibling — reused only for _load_manifest, the DRY manifest source)
import pii_tokens  # noqa: E402  (sibling — collision-free scanner token set)
import safety_filter  # noqa: E402  (sibling — the non-removable corpus/secret drop rules)

REPO = Path(__file__).resolve().parents[4]  # scripts → _framework-shared → skills → .claude → repo


def _to_relposix(target: str) -> str | None:
    """Repo-relative POSIX path, or None if the target lies outside the repo (then: not our concern)."""
    p = Path(target)
    try:
        rel = (p if p.is_absolute() else (REPO / p)).resolve().relative_to(REPO)
    except ValueError:
        return None
    return rel.as_posix()


def _glob_to_re(pattern: str) -> re.Pattern:
    """Translate a manifest include glob to a regex. `**` (or `**/`) spans path segments; a lone `*`
    stays within one segment; `?` is a single non-slash char. Anchored full-match."""
    out, i, n = [], 0, len(pattern)
    while i < n:
        c = pattern[i]
        if c == "*":
            if pattern[i + 1:i + 2] == "*":          # ** — cross-segment
                i += 2
                if pattern[i:i + 1] == "/":
                    i += 1
                out.append(".*")
            else:                                    # * — within a segment
                i += 1
                out.append("[^/]*")
        elif c == "?":
            i += 1
            out.append("[^/]")
        else:
            i += 1
            out.append(re.escape(c))
    return re.compile("^" + "".join(out) + "$")


def is_shipped_class(relposix: str) -> bool:
    """True iff the path would ship: matches an include glob and is not safety-dropped (corpus/secret)."""
    dropped, _ = safety_filter.is_dropped(relposix)
    if dropped:
        return False
    includes = build_pack._load_manifest().get("include", [])
    return any(_glob_to_re(pat).match(relposix) for pat in includes)


def find_tokens(text: str, tokens) -> list:
    """Forbidden tokens present in `text`, matched case-sensitive + word-boundary (scan_pack_pii parity)."""
    return [tok for tok in tokens
            if re.search(r"(?<!\w)" + re.escape(tok) + r"(?!\w)", text)]


def check(target: str, text: str, profiles_dir=None) -> dict:
    rel = _to_relposix(target)
    if rel is None:
        return {"block": False, "reason": "outside-repo"}
    if not is_shipped_class(rel):
        return {"block": False, "reason": "not-shipped-class", "path": rel}
    if not pii_tokens.roster_present(profiles_dir):
        return {"block": False, "reason": "roster-absent", "path": rel}
    tokens = pii_tokens.scan_tokens(profiles_dir)
    hits = find_tokens(text, tokens)
    if not hits:
        return {"block": False, "reason": "clean", "path": rel}
    return {"block": True, "reason": "pii-token", "path": rel, "tokens": hits}


def main() -> int:
    ap = argparse.ArgumentParser(description="Birth-time PII write-guard decision (READ-ONLY).")
    ap.add_argument("--path", required=True, help="target file path (repo-relative or absolute)")
    ap.add_argument("--profiles-dir", default=None, help="override roster dir (test seam)")
    args = ap.parse_args()
    text = sys.stdin.read()
    print(json.dumps(check(args.path, text, args.profiles_dir), ensure_ascii=False))
    return 0  # the .cjs shim owns the block/pass exit code; this always exits clean


if __name__ == "__main__":
    raise SystemExit(main())
