#!/usr/bin/env python3
"""Parse timeline/overview.md for all characters, check date consistency:
- Ages align with DOB from identity/core.md
- No future dates
- Chronological ordering
- Cross-character events have matching dates
Output: inconsistencies with file/line references."""
import os
import sys
import argparse
import re
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.paths import ALL_CHARS, CHAR_DISPLAY, character_dir, CHARACTER_PAIRS, CHAR_SEARCH_ALIASES
from platform_lib.markdown_parser import extract_timeline_events
from platform_lib.formatters import print_json, print_table

TODAY = date.today()

# DOB fallback — hardcoded since we parse identity/core.md dynamically
DOB_FALLBACK = {
    "character-a": date(1997, 9, 24),
    "character-b": date(2008, 2, 18),
    "character-c": date(2007, 5, 14),
}


def parse_dob_from_identity(char_dir: Path) -> date | None:
    identity = char_dir / "identity/core.md"
    if not identity.exists():
        return None
    text = identity.read_text(encoding="utf-8")
    # Look for patterns like: 24/09/1997 or 1997-09-24
    for pat in [r"(\d{2}/\d{2}/\d{4})", r"(\d{4}-\d{2}-\d{2})"]:
        m = re.search(pat, text)
        if m:
            raw = m.group(1)
            try:
                if "/" in raw:
                    return datetime.strptime(raw, "%d/%m/%Y").date()
                else:
                    return datetime.strptime(raw, "%Y-%m-%d").date()
            except ValueError:
                continue
    return None


def parse_event_date(date_str: str) -> date | None:
    """Convert event date string to date object. Returns None if unparseable.

    NOTE: mixed-precision dates are coerced to a full date (MM/YYYY → day 1, YYYY → Jan 1),
    so an OUT_OF_ORDER flag between e.g. "2026" and "03/2026" is a deterministic OVER-FLAG,
    not a confirmed error. This is acceptable per the gather-not-judge principle: the script
    surfaces the candidate, the LLM adjudicates whether the ordering is actually wrong.
    """
    date_str = date_str.strip()
    formats = ["%d/%m/%Y", "%Y-%m-%d", "%m/%Y", "%Y"]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.date()
        except ValueError:
            continue
    return None


def check_character_timeline(slug: str) -> list[dict]:
    issues = []
    cdir = character_dir(slug)
    display = CHAR_DISPLAY[slug]
    timeline_file = cdir / "timeline/overview.md"

    if not timeline_file.exists():
        return [{"slug": slug, "character": display, "type": "MISSING_FILE",
                 "file": "timeline/overview.md", "line": 0, "detail": "timeline/overview.md not found"}]

    dob = parse_dob_from_identity(cdir) or DOB_FALLBACK.get(slug)
    events = extract_timeline_events(timeline_file)

    parsed_dates = []
    lines = timeline_file.read_text(encoding="utf-8").splitlines()

    for ev in events:
        ev_date = parse_event_date(ev["date"])
        if ev_date is None:
            continue

        line_no = 0
        for i, l in enumerate(lines, 1):
            if ev["date"] in l:
                line_no = i
                break

        # Check: future date
        if ev_date > TODAY:
            issues.append({
                "slug": slug, "character": display, "type": "FUTURE_DATE",
                "file": "timeline/overview.md", "line": line_no,
                "detail": f"Date {ev['date']} is in the future ({ev['event'][:60]})",
            })

        # Check: date before DOB
        if dob and ev_date < dob:
            # Allow if it's clearly a family/historical event
            if ev_date.year >= dob.year - 30:
                issues.append({
                    "slug": slug, "character": display, "type": "BEFORE_DOB",
                    "file": "timeline/overview.md", "line": line_no,
                    "detail": f"Date {ev['date']} is before DOB {dob} ({ev['event'][:60]})",
                })

        parsed_dates.append((ev_date, line_no, ev["event"]))

    # Check chronological ordering
    for i in range(1, len(parsed_dates)):
        prev_date, prev_line, prev_ev = parsed_dates[i - 1]
        curr_date, curr_line, curr_ev = parsed_dates[i]
        if curr_date < prev_date:
            issues.append({
                "slug": slug, "character": display, "type": "OUT_OF_ORDER",
                "file": "timeline/overview.md", "line": curr_line,
                "detail": f"Date {curr_date} appears after {prev_date} (line {prev_line})",
            })

    return issues


def check_cross_character_date_alignment() -> list[dict]:
    """Find events in one char's timeline that reference another char, compare dates."""
    issues = []
    char_events: dict[str, list] = {}
    char_aliases = CHAR_SEARCH_ALIASES

    for slug in ALL_CHARS:
        tf = character_dir(slug) / "timeline/overview.md"
        char_events[slug] = extract_timeline_events(tf) if tf.exists() else []

    # All dyad pairs (was hand-listed with only 2 of 3 → missed hoa↔chiến date conflicts).
    for c1, c2 in CHARACTER_PAIRS:
        aliases2 = char_aliases[c2]
        for ev in char_events[c1]:
            for alias in aliases2:
                if alias.lower() in ev["event"].lower():
                    ev_date = parse_event_date(ev["date"])
                    # Find matching event in c2 timeline within ±90 days
                    if ev_date is None:
                        continue
                    found_match = False
                    for ev2 in char_events[c2]:
                        ev2_date = parse_event_date(ev2["date"])
                        if ev2_date and abs((ev2_date - ev_date).days) <= 90:
                            # Any mention of c1 in c2's event?
                            for alias1 in char_aliases[c1]:
                                if alias1.lower() in ev2["event"].lower():
                                    found_match = True
                                    break
                    if not found_match:
                        issues.append({
                            "slug": c1, "character": CHAR_DISPLAY[c1], "type": "CROSS_EVENT_UNMATCHED",
                            "file": "timeline/overview.md", "line": 0,
                            "detail": f"{ev['date']}: '{ev['event'][:60]}' mentions {CHAR_DISPLAY[c2]} but no matching event in {CHAR_DISPLAY[c2]}'s timeline",
                        })
                    break

    return issues


def main():
    parser = argparse.ArgumentParser(
        description="Check timeline/overview.md date consistency across all characters"
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--skip-cross", action="store_true", help="Skip cross-character alignment check")
    args = parser.parse_args()

    all_issues = []
    for slug in ALL_CHARS:
        all_issues.extend(check_character_timeline(slug))

    if not args.skip_cross:
        all_issues.extend(check_cross_character_date_alignment())

    if args.json:
        print_json(all_issues)
        return

    print(f"\n## Timeline Date Consistency Check\n")
    if not all_issues:
        print("No issues found. All timelines are consistent.")
        return

    print(f"**{len(all_issues)} issue(s) found:**\n")
    headers = ["Character", "Type", "File", "Line", "Detail"]
    rows = [
        [i["character"], i["type"], i["file"], str(i["line"]), i["detail"][:80]]
        for i in all_issues
    ]
    print_table(headers, rows)


if __name__ == "__main__":
    main()
