#!/usr/bin/env python3
"""Find hypothesis reports matching character+date and compare with current profile state."""
import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.paths import resolve_character, character_dir, CHAR_DISPLAY, REPORTS
from platform_lib.profile_stats import profile_file_inventory
from platform_lib.formatters import print_json


def find_hypothesis_reports(slug: str, date_filter: str) -> list[Path]:
    """Find hypothesis/arc report files matching character slug and date."""
    matches = []
    if not REPORTS.exists():
        return matches
    pattern = re.compile(rf"({slug}|hypothesis|arc).+{date_filter}", re.IGNORECASE)
    for f in REPORTS.iterdir():
        if f.is_file() and f.suffix == ".md" and pattern.search(f.name):
            matches.append(f)
    # Also search plan subdirs
    plans_dir = REPORTS.parent
    for subdir in plans_dir.iterdir():
        if subdir.is_dir() and subdir.name != "reports":
            for f in subdir.rglob("*.md"):
                if pattern.search(f.name):
                    matches.append(f)
    return sorted(set(matches))


def main():
    parser = argparse.ArgumentParser(description="Compare hypothesis report vs current profile")
    parser.add_argument("--character", required=True, help="Character name or alias")
    parser.add_argument("--date", required=True, help="Date filter YYYYMMDD or partial")
    args = parser.parse_args()

    slug = resolve_character(args.character)
    display = CHAR_DISPLAY.get(slug, slug)
    cdir = character_dir(args.character)

    reports = find_hypothesis_reports(slug, args.date)

    result = {
        "character": display,
        "date_filter": args.date,
        "hypothesis_reports_found": len(reports),
        "reports": [],
        "current_profile_inventory": profile_file_inventory(slug),
    }

    for rpath in reports:
        content = rpath.read_text(encoding="utf-8")
        result["reports"].append({
            "file": str(rpath),
            "name": rpath.name,
            "lines": len(content.splitlines()),
            "preview": content[:500].strip(),
        })

    if not reports:
        result["note"] = f"No hypothesis reports found for {display} matching date={args.date} in {REPORTS}"

    print_json(result)


if __name__ == "__main__":
    main()
