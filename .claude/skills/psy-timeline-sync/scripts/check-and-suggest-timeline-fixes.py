"""Extract dates from timeline files, cross-compare shared events, report mismatches."""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import ALL_CHARS, CHAR_DISPLAY, PROFILES, resolve_character

# Known shared events: (event_label, [character_slugs], keyword_patterns)
SHARED_EVENTS = [
    ("Kết nghĩa (sworn brothers)", ["character-a", "character-b"],
     [r"kết\s*nghĩa", r"sworn\s*brother", r"sworn brother"]),
    ("First meeting Nhân vật A-Nhân vật B", ["character-a", "character-b"],
     [r"gặp.*[Hh]òa", r"gặp.*[Hh]oa", r"first met.*[Hh]oa", r"[Hh]òa.*gặp"]),
    ("Gambling crisis", ["character-a", "character-b"],
     [r"cờ\s*bạc", r"gambl", r"casino", r"khủng\s*hoảng"]),
    ("Scholarship X F15 interview", ["character-a", "character-c"],
     [r"Scholarship X", r"F15", r"phỏng\s*vấn.*học\s*bổng"]),
    ("Mentoring sessions", ["character-a", "character-c"],
     [r"mentor", r"cố\s*vấn"]),
]

DATE_PATTERNS = [
    (r"\b(\d{4})-(\d{2})-(\d{2})\b", "{year}-{month:02d}"),  # YYYY-MM-DD
    (r"\b(\d{2})/(\d{4})\b", "{month:02d}/{year}"),           # MM/YYYY
    (r"\b(0[1-9]|1[0-2])/(\d{4})\b", "{month:02d}/{year}"),
    (r"\b(T\d{1,2})/(\d{4})\b", "T{month}/{year}"),           # Vietnamese quarter
    (r"(?:tháng\s*|month\s*)(\d{1,2}).*?(\d{4})", "{month:02d}/{year}"),
    (r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+(\d{4})", "{year}"),
    (r"\b(\d{4})\b", "{year}"),  # Year only — lowest precision
]


def extract_dates_near_pattern(text: str, patterns: list[str]) -> list[str]:
    """Find dates within 100 chars of a matching keyword."""
    found_dates = []
    for kw in patterns:
        for m in re.finditer(kw, text, re.IGNORECASE | re.UNICODE):
            context = text[max(0, m.start() - 80): m.end() + 80]
            for dpat, _ in DATE_PATTERNS:
                dm = re.search(dpat, context)
                if dm:
                    found_dates.append(dm.group(0))
                    break
    return list(dict.fromkeys(found_dates))  # preserve order, deduplicate


def read_timeline_files(slug: str) -> dict[str, str]:
    """Read all timeline-related files for a character."""
    char_dir = PROFILES / slug
    files = {
        "timeline/overview.md": char_dir / "timeline" / "overview.md",
        "timeline/state-timeline.md": char_dir / "timeline" / "state-timeline.md",
        "milestones.md": char_dir / "milestones.md",
    }
    result = {}
    for label, path in files.items():
        if path.exists():
            result[label] = path.read_text(encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser(description="Check timeline consistency across characters")
    parser.add_argument("--character", "-c", help="Check single character only")
    parser.add_argument("--all", action="store_true", help="Check all characters (default)")
    parser.add_argument("--json", dest="json_out", action="store_true", help="JSON output")
    args = parser.parse_args()

    chars = [resolve_character(args.character)] if args.character else ALL_CHARS

    # Load timeline text per character
    char_timelines: dict[str, dict[str, str]] = {}
    for slug in chars:
        char_timelines[slug] = read_timeline_files(slug)

    results = []
    for event_label, involved_chars, kw_patterns in SHARED_EVENTS:
        # Only check characters that are both in scope and involved
        scope = [c for c in involved_chars if c in chars]
        if len(scope) < 2:
            continue

        char_dates: dict[str, list[str]] = {}
        for slug in scope:
            all_text = "\n".join(char_timelines.get(slug, {}).values())
            dates = extract_dates_near_pattern(all_text, kw_patterns)
            char_dates[slug] = dates

        # Compare: if all have same date → MATCH; any differ → MISMATCH; any empty → MISSING
        all_dates = [char_dates.get(s, []) for s in scope]
        flat = [d for dlist in all_dates for d in dlist]

        if not flat:
            status = "MISSING"
            note = "Event not found in any timeline"
        elif any(not d for d in all_dates):
            status = "MISSING"
            missing = [CHAR_DISPLAY[s] for s in scope if not char_dates.get(s)]
            note = f"Missing in: {', '.join(missing)}"
        else:
            # Check if all dates agree (compare first date per char)
            first_dates = [dlist[0] for dlist in all_dates if dlist]
            if len(set(first_dates)) == 1:
                status = "MATCH"
                note = first_dates[0]
            else:
                status = "MISMATCH"
                parts = [f"{CHAR_DISPLAY[s]}: {char_dates[s][0]}" for s in scope if char_dates.get(s)]
                note = " | ".join(parts)

        results.append({
            "event": event_label,
            "characters": scope,
            "status": status,
            "note": note,
            "char_dates": {s: char_dates.get(s, []) for s in scope},
        })

    if args.json_out:
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return

    print(f"\n{'='*70}")
    print("  Timeline Sync Report")
    print(f"{'='*70}")
    print(f"  Scope: {', '.join(CHAR_DISPLAY.get(c, c) for c in chars)}")
    print()

    # Summary table
    print(f"  {'Event':<35s} {'Status':<10s} {'Details'}")
    print(f"  {'-'*35} {'-'*10} {'-'*30}")
    for r in results:
        marker = "✓" if r["status"] == "MATCH" else ("✗" if r["status"] == "MISMATCH" else "?")
        print(f"  {r['event'][:33]:<35s} {marker} {r['status']:<8s} {r['note']}")

    # Mismatch detail
    mismatches = [r for r in results if r["status"] == "MISMATCH"]
    if mismatches:
        print(f"\n  {'='*60}")
        print("  MISMATCHES — Action Required")
        print(f"  {'='*60}")
        for r in mismatches:
            print(f"\n  Event: {r['event']}")
            for slug in r["characters"]:
                dates = r["char_dates"].get(slug, [])
                print(f"    {CHAR_DISPLAY.get(slug, slug)}: {dates or 'NOT FOUND'}")
            print(f"    Suggested fix: Verify against docs/materials/ and align to correct date")
            print(f"    Priority: HIGH")

    # Summary stats
    counts = {"MATCH": 0, "MISMATCH": 0, "MISSING": 0}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1

    print(f"\n  Summary: {counts['MATCH']} MATCH | {counts['MISMATCH']} MISMATCH | {counts['MISSING']} MISSING")

    if counts["MISMATCH"] == 0 and counts["MISSING"] == 0:
        print("  All shared events consistent.")
    else:
        print(f"  Action needed: {counts['MISMATCH']} mismatches, {counts['MISSING']} missing entries")


if __name__ == "__main__":
    main()
