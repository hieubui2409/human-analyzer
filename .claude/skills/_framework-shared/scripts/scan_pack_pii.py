#!/usr/bin/env python3
"""scan_pack_pii — fail-closed PII / secret gate over the BUILT release tarball.

Builds the pack in memory (same selection as build_pack), then scans EVERY shipped member's bytes
(except the embedded MANIFEST.json) for:
  - real-name tokens — display names + multi-word full names + kebab slugs + org/program/location
    extras — loaded at runtime from the pack-excluded characters.yaml / pii-tokens.yaml via pii_tokens
    (NAME-FREE source: zero real names live in this file). NO carve-out — tests/ are scanned too.
  - secret material — private-key headers, AWS keys, generic long api_key/secret/token assignments.

Exit 1 (with the offending path + token/pattern) on any hit so a release pipeline fails closed.
When the roster is absent (a toolkit-only build) the name set is empty and only secrets are checked.

Engineer-kit footprint is a HARD failure: a shipped engineer-kit path, or any agent/hook file outside
the framework allow-list, fails the scan (an independent ratchet against re-broadening the manifest).
"""
import argparse
import io
import re
import sys
import tarfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_pack  # noqa: E402  (sibling in _framework-shared/scripts)
import pii_tokens  # noqa: E402  (sibling in _framework-shared/scripts)

# Secret material in file CONTENT (safety_filter already drops secret-named files; this catches
# secrets pasted inside an otherwise-innocuous shipped file). Kept conservative to avoid false hits.
_SECRET_PATTERNS = [
    (re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----"), "private-key header"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS access key id"),
    (re.compile(r"\bsk-[A-Za-z0-9]{32,}\b"), "OpenAI-style secret key"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"), "GitHub token"),
    (re.compile(r"(?i)\b(?:api[_-]?key|secret|password|token)\b\s*[:=]\s*['\"][A-Za-z0-9/+_-]{24,}['\"]"),
     "hardcoded credential assignment"),
]

# Engineer-kit footprint: dev tools that must not ship in the character toolkit (now a HARD failure).
_CK_HINTS = ("/.claude/skills/ck-", "/commands/ck", "ck:plan", "ck:cook")

# Independent allow-list (not derived from the manifest, so re-broadening the manifest to a glob is
# caught here): the ONLY agent/hook files the framework pack may contain. Toolkit identity, not PII.
_FRAMEWORK_AGENTS = {
    "psychologist.md", "content-strategist.md", "growth-analyst.md",
    "cross-validator.md", "profile-manager.md", "material-analyst.md",
}
_FRAMEWORK_HOOK_FILES = {
    "gateguard-profile-protect.cjs", "pii-guard-on-write.cjs",
    "detect-profile-drift-hook.cjs", "observe-framework-signal.cjs",
    "profile-edit-reminder.cjs", "rebuild-knowledge-graph.cjs", "write-framework-delta-compact-digest.cjs",
    "context-budget-gauge.cjs", "emit-session-summary.cjs",
    "track-script-execution.cjs", "track-skill-invocation.cjs",
    "lib/hook-config-utils.cjs", "lib/sensitivity-checker.cjs", "lib/telemetry-paths.cjs",
    "lib/hook-logger.cjs", "lib/bash-write-targets.cjs",
}


def _footprint_hit(arcname: str):
    """Return a hard-fail reason if `arcname` is an engineer-kit or non-framework agent/hook file."""
    if any(h in "/" + arcname for h in _CK_HINTS):
        return "engineer-kit (CK) path must not ship"
    if ".claude/agents/" in arcname and arcname.rsplit("/", 1)[-1] not in _FRAMEWORK_AGENTS:
        return "non-framework agent must not ship"
    if ".claude/hooks/" in arcname:
        rel = arcname.split(".claude/hooks/", 1)[1]
        if rel not in _FRAMEWORK_HOOK_FILES:
            return "non-framework hook must not ship"
    return None

# Binary/asset suffixes whose bytes are not scannable text — skipped (safety_filter already blocks secret types).
_SKIP_SUFFIX = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".woff", ".woff2", ".ttf")


def _iter_members(source_date_epoch: int = 0):
    """Yield (arcname, data_bytes) for every file in the freshly built pack except MANIFEST.json."""
    buf = io.BytesIO()
    build_pack.build(buf, source_date_epoch=source_date_epoch)
    buf.seek(0)
    with tarfile.open(fileobj=buf, mode="r:gz") as tar:
        for member in tar.getmembers():
            if not member.isfile() or member.name == "MANIFEST.json":
                continue
            f = tar.extractfile(member)
            if f is None:
                continue
            yield member.name, f.read()


def scan_text(arcname: str, text: str, tokens) -> list:
    """Return [(arcname, reason)] for every forbidden token / secret pattern found in `text`.

    Tokens are the COLLISION-FREE scanner set (slugs + full names + extras) and are matched
    word-boundary, CASE-SENSITIVE — bare display names are excluded upstream because they collide
    with everyday Vietnamese words, so case-sensitive matching here yields no prose false positives.
    """
    hits = []
    for tok in tokens:
        if re.search(r"(?<!\w)" + re.escape(tok) + r"(?!\w)", text):
            hits.append((arcname, f"real-name token {tok!r}"))
    for pat, label in _SECRET_PATTERNS:
        if pat.search(text):
            hits.append((arcname, f"secret: {label}"))
    return hits


def scan_pack(source_date_epoch: int = 0):
    """Return (hard_hits, ck_warnings). hard_hits = [(path, reason)]; ck_warnings = [path]."""
    tokens = pii_tokens.scan_tokens()
    hard_hits, ck_warnings = [], []  # ck_warnings retained for call-site compat (always empty now)
    for arcname, data in _iter_members(source_date_epoch):
        fp = _footprint_hit(arcname)
        if fp:
            hard_hits.append((arcname, fp))
        # A real-name slug/full-name baked into the PATH ships in the tarball even for binary
        # assets that skip content scanning — gate the arcname itself before any suffix skip.
        for tok in tokens:
            if re.search(r"(?<!\w)" + re.escape(tok) + r"(?!\w)", arcname):
                hard_hits.append((arcname, f"real-name token {tok!r} in path"))
        if arcname.endswith(_SKIP_SUFFIX):
            continue
        text = data.decode("utf-8", errors="ignore")
        hard_hits.extend(scan_text(arcname, text, tokens))
    return hard_hits, ck_warnings


def main() -> int:
    ap = argparse.ArgumentParser(description="Fail-closed PII/secret scan over the built release pack.")
    ap.add_argument("--source-date-epoch", type=int, default=0)
    args = ap.parse_args()

    tokens = pii_tokens.scan_tokens()
    if not tokens:
        if pii_tokens.roster_present():
            # File is on disk but yielded zero tokens (pyyaml missing or unparsed) — the name gate
            # would pass vacuously. Fail closed rather than ship a green check with no real coverage.
            print("\n❌ PII scan FAILED — characters.yaml is present but produced 0 name tokens "
                  "(pyyaml missing or unparsed). The name gate cannot run; refusing to pass vacuously.")
            return 1
        print("scan_pack_pii: roster absent — name set empty; scanning secrets only.")

    hard_hits, _ck_warnings = scan_pack(args.source_date_epoch)

    if hard_hits:
        print(f"\n❌ PII/secret scan FAILED — {len(hard_hits)} leak(s) in the built pack:")
        for path, reason in hard_hits:
            print(f"    {path}: {reason}")
        return 1

    print(f"✅ PII/secret scan PASSED — 0 real-name/secret leaks across the built pack "
          f"({len(tokens)} token(s) checked, no carve-out).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
