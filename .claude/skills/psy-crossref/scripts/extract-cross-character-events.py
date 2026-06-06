#!/usr/bin/env python3
"""Extract timeline events that mention other characters and compare for shared events."""
import os
import sys
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.paths import (
    ALL_CHARS, CHAR_DISPLAY, character_dir, CHARACTER_PAIRS, CHAR_SEARCH_ALIASES,
)
from platform_lib.markdown_parser import extract_timeline_events, find_cross_references
from platform_lib.formatters import markdown_table, print_table

PAIRS = CHARACTER_PAIRS
CHAR_ALIASES = CHAR_SEARCH_ALIASES


def get_cross_events(char_slug: str, target_slug: str) -> list[dict]:
    """Get events from char's timeline/overview.md that mention target."""
    timeline = character_dir(char_slug) / "timeline/overview.md"
    target_names = CHAR_ALIASES.get(target_slug, [])
    refs = find_cross_references(timeline, target_names)
    events = extract_timeline_events(timeline)

    # Match refs by line number to events (approximate by date context)
    ref_lines = {r["line"] for r in refs}
    matched = []
    # Also mark events that contain target name directly
    for ev in events:
        if any(alias.lower() in ev["event"].lower() for alias in target_names):
            ev["mentions"] = True
            matched.append(ev)
    return matched


def compare_pair(char1: str, char2: str) -> list[list[str]]:
    rows = []
    events1 = get_cross_events(char1, char2)
    events2 = get_cross_events(char2, char1)

    dates1 = {e["date"]: e["event"] for e in events1}
    dates2 = {e["date"]: e["event"] for e in events2}
    all_dates = sorted(set(list(dates1.keys()) + list(dates2.keys())))

    d1 = CHAR_DISPLAY[char1]
    d2 = CHAR_DISPLAY[char2]

    for date in all_dates:
        ev1 = dates1.get(date, "")
        ev2 = dates2.get(date, "")
        if ev1 and ev2:
            match = "MATCH" if abs(len(ev1) - len(ev2)) < 80 else "PARTIAL"
        elif ev1:
            match = f"Only {d1}"
        else:
            match = f"Only {d2}"
        rows.append([date, ev1[:60] or "-", ev2[:60] or "-", match])
    return rows


def main():
    # Derive the short --pair keys from the canonical roster (key = each slug's last name token) so
    # this scales to any character set instead of a hardcoded 3-character literal (which would reject
    # the synthetic roster and any 4th character).
    pair_map = {f"{c1.split('-')[-1]}-{c2.split('-')[-1]}": (c1, c2) for c1, c2 in PAIRS}

    parser = argparse.ArgumentParser(description="Extract cross-character timeline events")
    parser.add_argument("--pair", choices=sorted(pair_map), help="Filter to specific pair")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    pairs = [pair_map[args.pair]] if args.pair else PAIRS

    if args.json:
        import json
        result = {}
        for c1, c2 in pairs:
            key = f"{CHAR_DISPLAY[c1]}-{CHAR_DISPLAY[c2]}"
            rows = compare_pair(c1, c2)
            result[key] = [{"date": r[0], c1: r[1], c2: r[2], "match": r[3]} for r in rows]
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    for c1, c2 in pairs:
        d1, d2 = CHAR_DISPLAY[c1], CHAR_DISPLAY[c2]
        print(f"\n## {d1} ↔ {d2}")
        rows = compare_pair(c1, c2)
        if not rows:
            print("_(no cross-character events found)_")
        else:
            print_table(["Date", f"{d1} TIMELINE", f"{d2} TIMELINE", "Status"], rows)


if __name__ == "__main__":
    main()
