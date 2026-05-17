#!/usr/bin/env python3
"""List all published content across asset platforms with metadata."""
import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.paths import ASSETS
from platform_lib.formatters import print_table


def get_word_count(text: str) -> int:
    return len(text.split())


def get_first_line(text: str) -> str:
    for line in text.splitlines():
        clean = line.strip().lstrip('#').strip()
        if clean and not clean.startswith('<!--'):
            return clean[:70]
    return "(no title)"


def parse_date_from_slug(slug: str) -> str:
    m = re.match(r'^(\d{6})', slug)
    if m:
        d = m.group(1)
        return f"20{d[:2]}-{d[2:4]}-{d[4:6]}"
    return "unknown"


def scan_platform(platform_dir: Path) -> list[dict]:
    entries = []
    for slug_dir in sorted(platform_dir.iterdir()):
        if not slug_dir.is_dir():
            continue
        for fname in ["post.md", "post.txt"]:
            post_file = slug_dir / fname
            if post_file.exists():
                text = post_file.read_text(encoding='utf-8', errors='replace')
                entries.append({
                    "platform": platform_dir.name,
                    "date": parse_date_from_slug(slug_dir.name),
                    "slug": slug_dir.name,
                    "file": fname,
                    "words": get_word_count(text),
                    "title": get_first_line(text),
                })
                break
    return entries


def main():
    parser = argparse.ArgumentParser(description="List published content across asset platforms")
    parser.add_argument("--platform", default=None, help="Platform name (or omit for all)")
    parser.add_argument("--all", action="store_true", help="Scan all platforms")
    args = parser.parse_args()

    if not ASSETS.exists():
        print(f"Assets directory not found: {ASSETS}")
        sys.exit(1)

    if args.platform and args.platform != "all":
        pdir = ASSETS / args.platform
        if not pdir.exists():
            print(f"Platform not found: {pdir}")
            sys.exit(1)
        platforms = [pdir]
    else:
        platforms = [d for d in sorted(ASSETS.iterdir()) if d.is_dir()]

    all_entries = []
    for pdir in platforms:
        all_entries.extend(scan_platform(pdir))

    if not all_entries:
        print("No published content found.")
        return

    print(f"\n## Content Inventory ({len(all_entries)} posts)\n")
    headers = ["Platform", "Date", "Slug", "Words", "Title (proxy)"]
    rows = [
        [e["platform"], e["date"], e["slug"], str(e["words"]), e["title"]]
        for e in all_entries
    ]
    print_table(headers, rows)

    # Summary by platform
    from collections import Counter
    counts = Counter(e["platform"] for e in all_entries)
    print("\n### By Platform")
    for plat, count in sorted(counts.items()):
        print(f"- {plat}: {count} post(s)")


if __name__ == "__main__":
    main()
