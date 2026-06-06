"""Gather material-claim ↔ profile OVERLAP candidates for mat:indexer --contradictions.

GOLDEN RULE #4 split:
  - SCRIPT (here, deterministic): for each date/name/event-tagged material claim, find
    which profile files mention the SAME terms. Emits OVERLAP (shared terms → a candidate
    the LLM should read for agreement/contradiction) or NO_OVERLAP (claim's terms absent
    from the profile → a coverage candidate). It does NOT decide CONFIRMS/CONTRADICTS —
    term co-occurrence says nothing about whether the two AGREE. That is an LLM judgment.
  - LLM (downstream, see SKILL.md): read each OVERLAP candidate's material line + profile
    file and adjudicate CONFIRMS / EXTENDS / CONTRADICTS.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import ALL_CHARS, CHAR_DISPLAY, CHAR_SEARCH_ALIASES, MATERIALS, PROFILES, PROFILE_FILES, resolve_character

# Load the shared roster token set (display names + full-name aliases + pii_extra) at
# import time so claim extraction picks up any new character automatically. Falls back to
# an empty list when the roster is absent (toolkit-only consumer pack).
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools" / "anonymize"))
try:
    from pii_tokens import tokens_only as _pii_tokens_only
    _pii_tokens: list[str] = _pii_tokens_only()
except ImportError:
    _pii_tokens = []

# Flatten all search aliases from the roster for name detection.
_roster_name_tokens: list[str] = []
for _slug, _aliases in CHAR_SEARCH_ALIASES.items():
    _roster_name_tokens.extend(_aliases)
# Merge: roster aliases + pii_extra tokens (deduped, preserving order).
_seen: set[str] = set()
_all_name_tokens: list[str] = []
for _t in _roster_name_tokens + _pii_tokens:
    if _t not in _seen:
        _seen.add(_t)
        _all_name_tokens.append(_t)

# Institution/org names that are corpus-stable but not roster-derived.
_ORG_TOKENS = ["One Mount", "VinSmart", "ĐHBK", "Bách Khoa"]

DATE_PATTERN = re.compile(
    r"(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2}|\d{2}/\d{4})"
)

# Build the name detection pattern from the live roster + static org tokens.
# When the roster is absent (empty toolkit pack), fall back to org tokens only.
_name_alts = [re.escape(t) for t in _all_name_tokens + _ORG_TOKENS if t]
if _name_alts:
    NAME_PATTERN = re.compile(r"(?:" + "|".join(_name_alts) + r")", re.IGNORECASE)
else:
    # No tokens at all — match nothing (re that never fires).
    NAME_PATTERN = re.compile(r"(?!)", re.IGNORECASE)
EVENT_PATTERN = re.compile(
    r"(?:chuyển việc|nghỉ việc|nhận việc|tốt nghiệp|kết nghĩa|phỏng vấn"
    r"|scholarship|mentor|crisis|conflict|reconcil)",
    re.IGNORECASE,
)


def extract_claims(filepath: Path) -> list[dict]:
    """Extract date-tagged claims from a material file (skip frontmatter)."""
    try:
        text = filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []

    fm_end = text.find("\n---", 3)
    if text.startswith("---") and fm_end > 0:
        text = text[fm_end + 4:]

    claims = []
    for i, line in enumerate(text.splitlines(), 1):
        line_s = line.strip()
        if not line_s or len(line_s) < 10:
            continue
        dates = DATE_PATTERN.findall(line_s)
        names = NAME_PATTERN.findall(line_s)
        events = EVENT_PATTERN.findall(line_s)
        if dates or names or events:
            claims.append({
                "line": i,
                "text": line_s[:150],
                "dates": dates,
                "names": names,
                "events": events,
            })
    return claims


def find_profile_mentions(slug: str, search_terms: list[str]) -> list[dict]:
    """Search profile files for matching terms."""
    matches = []
    char_dir = PROFILES / slug
    if not char_dir.exists():
        return []

    for relpath in PROFILE_FILES:
        fpath = char_dir / relpath
        if not fpath.exists():
            continue
        try:
            text = fpath.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for term in search_terms:
            if term.lower() in text.lower():
                matches.append({"file": relpath, "term": term})
    return matches


def analyze_character(slug: str) -> list[dict]:
    """Detect potential contradictions for a character."""
    mdir = MATERIALS / slug
    if not mdir.exists():
        return []

    results = []
    for fpath in sorted(mdir.rglob("*.md")):
        if fpath.is_dir():
            continue
        claims = extract_claims(fpath)
        for claim in claims:
            search_terms = claim["dates"] + claim["names"] + claim["events"]
            if not search_terms:
                continue
            profile_hits = find_profile_mentions(slug, search_terms)
            # Deterministic signal only — NOT a CONFIRMS/CONTRADICTS verdict.
            signal = "OVERLAP" if profile_hits else "NO_OVERLAP"
            results.append({
                "material": fpath.name,
                "claim": claim["text"],
                "dates": claim["dates"],
                "signal": signal,
                "shared_terms": sorted({h["term"] for h in profile_hits}),
                "profile_refs": [h["file"] for h in profile_hits],
                "needs_llm_adjudication": bool(profile_hits),
            })
    return results


def main():
    parser = argparse.ArgumentParser(description="Detect contradictions between materials and profiles")
    parser.add_argument("--character", "-c", help="Single character slug")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    chars = [resolve_character(args.character)] if args.character else ALL_CHARS
    report = {}
    for slug in chars:
        report[slug] = analyze_character(slug)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return

    for slug, results in report.items():
        display = CHAR_DISPLAY.get(slug, slug)
        overlaps = sum(1 for r in results if r["signal"] == "OVERLAP")
        print(f"\n{'='*70}")
        print(f"  {display} ({slug}) — {len(results)} tagged claims, {overlaps} OVERLAP candidates")
        print(f"{'='*70}")

        for r in results[:30]:
            icon = {"OVERLAP": "≈", "NO_OVERLAP": "→"}.get(r["signal"], "?")
            print(f"  {icon} [{r['signal']}] {r['claim'][:80]}")
            if r["profile_refs"]:
                print(f"      shared terms {r['shared_terms'][:3]} in: {', '.join(r['profile_refs'][:3])}")
            print()
        print("  [advisory] OVERLAP = shared terms only — LLM reads each to judge "
              "CONFIRMS/EXTENDS/CONTRADICTS.")


if __name__ == "__main__":
    main()
