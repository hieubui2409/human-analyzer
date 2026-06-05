"""Extract dates from timeline files, cross-compare shared events, report mismatches."""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import ALL_CHARS, CHAR_DISPLAY, PROFILES, resolve_character

# Known shared events: (event_label, [character_slugs], keyword_patterns)
#
# PRECISION RULES for keyword_patterns:
#   1. Patterns must identify the SPECIFIC EVENT, not a bare topic keyword.
#      Include cohort markers (e.g. "F15"), role qualifiers, or named participants
#      so that distinct events sharing a broad topic word are NOT conflated.
#   2. For the Scholarship X F15 interview, require "F15" in pattern — this
#      excludes Nhân vật A's unrelated F5 scholarship hits from 2015.
#   3. For the Nhân vật A→Nhân vật C mentoring, require both names to appear near each
#      other — this excludes generic mentoring entries that involve other people.
SHARED_EVENTS = [
    ("Kết nghĩa (sworn brothers)", ["character-a", "character-b"],
     [r"kết\s*nghĩa", r"sworn\s*brother", r"sworn brother"]),
    ("First meeting Nhân vật A-Nhân vật B", ["character-a", "character-b"],
     [r"gặp.*[Hh]òa", r"gặp.*[Hh]oa", r"first met.*[Hh]oa", r"[Hh]òa.*gặp"]),
    ("Gambling crisis", ["character-a", "character-b"],
     [r"cờ\s*bạc", r"gambl", r"casino", r"khủng\s*hoảng"]),
    # Require "F15" AND a phỏng-vấn / interview / selection marker so we match only
    # the interview event, not cohort-label references ("Scholar F15", "mentee F15")
    # that appear later in a 2026 mentoring context.
    # In Nhân vật A's files this event is not explicitly dated (he was the interviewer
    # but records it as a footnote), so MISSING is the honest result for him.
    ("Scholarship X F15 interview", ["character-a", "character-c"],
     [r"Scholarship X\s*F15",
      r"F15.*phỏng\s*vấn", r"phỏng\s*vấn.*F15",
      r"F15.*interview", r"interview.*F15",
      r"Nhân vật A\s+là\s+interviewer", r"interviewer.*F15"]),
    # Require both the mentor/mentee role AND the other character's name in proximity
    # so generic "mentor" entries (Nhân vật A mentoring other people in 2021+) are excluded.
    # Patterns cover both perspectives:
    #   - Nhân vật A's files: "mentoring Nhân vật C", "mentor.*Nhân vật C", "Nhân vật C.*mentor"
    #   - Nhân vật C's files: "mentee của Nhân vật A", "Nhân vật A làm mentor", "Nhân vật A.*mentor"
    ("Mentoring sessions (Nhân vật A→Nhân vật C)", ["character-a", "character-c"],
     [r"mentor.*[Cc]hiến", r"[Cc]hiến.*mentor",
      r"mentoring\s+Nguyễn\s+Bách\s+Nhân vật C",
      r"mentee.*[Hh]iếu", r"[Hh]iếu.*mentor",
      r"cố\s*vấn.*[Cc]hiến", r"[Cc]hiến.*cố\s*vấn"]),
]

# Ordered most-precise → least-precise. The original second tuple element (format
# templates) was dead code — extraction appended the raw match, so "2026-03" and
# "03/2026" (same month) compared unequal → false MISMATCH. Dates are now normalized
# to a single canonical key (YYYY-MM, YYYY-Tq, or YYYY) for comparison.
_MONTH_ABBR = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}

DATE_PATTERNS = [
    r"\b\d{4}-\d{2}-\d{2}\b",                              # YYYY-MM-DD
    r"\bT\d{1,2}/\d{4}\b",                                 # Vietnamese quarter Tq/YYYY
    r"\b\d{1,2}/\d{4}\b",                                  # MM/YYYY
    r"(?:tháng\s*|month\s*)\d{1,2}.*?\d{4}",               # tháng N ... YYYY
    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}",  # Mon YYYY
    r"\b\d{4}\b",                                          # year only — lowest precision
]


def normalize_date(raw: str) -> str:
    """Collapse a matched date string to a canonical comparable key.

    YYYY-MM-DD / MM/YYYY / 'tháng N ... YYYY' / 'Mon YYYY' → YYYY-MM;
    Tq/YYYY → YYYY-Tq; bare year → YYYY. Unparseable → stripped raw.
    """
    s = raw.strip()
    if m := re.match(r"(\d{4})-(\d{2})-\d{2}$", s):
        return f"{m.group(1)}-{m.group(2)}"
    if m := re.match(r"T(\d{1,2})/(\d{4})$", s):
        return f"{m.group(2)}-T{int(m.group(1))}"
    if m := re.match(r"(\d{1,2})/(\d{4})$", s):
        return f"{m.group(2)}-{int(m.group(1)):02d}"
    if m := re.search(r"(?:tháng\s*|month\s*)(\d{1,2}).*?(\d{4})", s, re.IGNORECASE):
        return f"{m.group(2)}-{int(m.group(1)):02d}"
    if m := re.match(r"([A-Za-z]{3})[a-z]*\.?\s+(\d{4})$", s):
        mon = _MONTH_ABBR.get(m.group(1).lower())
        return f"{m.group(2)}-{mon:02d}" if mon else m.group(2)
    if m := re.match(r"(\d{4})$", s):
        return m.group(1)
    return s


def _extract_date_from_text(text: str) -> str | None:
    """Return the first date found in `text` using DATE_PATTERNS, normalized.

    Tries patterns from most-precise to least-precise, stopping at first match.
    """
    for dpat in DATE_PATTERNS:
        dm = re.search(dpat, text)
        if dm:
            return normalize_date(dm.group(0))
    return None


def _line_containing(full_text: str, match_start: int) -> str:
    """Return the complete line that contains position match_start in full_text."""
    line_start = full_text.rfind("\n", 0, match_start) + 1  # +1 skips the \n itself
    line_end = full_text.find("\n", match_start)
    if line_end == -1:
        line_end = len(full_text)
    return full_text[line_start:line_end]


def extract_dates_near_pattern(text: str, patterns: list[str]) -> list[str]:
    """Find dates near a matching keyword, normalized + deduplicated.

    Strategy (same-line-first):
      1. Try to find a date ON THE SAME LINE as the keyword match. This avoids
         pulling in dates from neighbouring table rows or list items that happen
         to fall within the 80-char sliding window.
      2. If the line contains no date, fall back to ±80-char context around the
         match position.

    The same-line-first heuristic prevents a keyword in one table cell from
    grabbing dates that belong to a different cell on an adjacent row.
    """
    found_dates: list[str] = []
    for kw in patterns:
        for m in re.finditer(kw, text, re.IGNORECASE | re.UNICODE):
            # Prefer: date on the same line as the keyword
            line = _line_containing(text, m.start())
            date = _extract_date_from_text(line)
            if date is None:
                # Fallback: ±80-char context window
                context = text[max(0, m.start() - 80): m.end() + 80]
                date = _extract_date_from_text(context)
            if date is not None:
                found_dates.append(date)
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
