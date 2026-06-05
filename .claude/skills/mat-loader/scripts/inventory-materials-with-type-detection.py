#!/usr/bin/env python3
"""Walk docs/materials/ and output an inventory with file type detection."""
import os
import sys
import re
import argparse
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.paths import MATERIALS, ALL_CHARS, CHAR_DISPLAY
from platform_lib.formatters import print_table, print_json

TIMESTAMP_RE = re.compile(r"\b(\d{1,2}:\d{2}(:\d{2})?)\b")
EPISTOLARY_RE = re.compile(r"(Kính gửi|Dear|Thân gửi|Gửi|Kính mến)", re.IGNORECASE)
MESSENGER_RE = re.compile(r"^\s*(\[?\d{1,2}:\d{2}\]?|\d{2}/\d{2}/\d{4})\s+.{1,60}$", re.MULTILINE)
ARTICLE_RE = re.compile(r"(Theo |Nguồn:|Source:|Published|Đăng ngày|VnExpress|Tuổi Trẻ|Báo)", re.IGNORECASE)


def detect_type(filepath: Path) -> str:
    """Guess content type from file content heuristics."""
    try:
        text = filepath.read_text(encoding="utf-8", errors="replace")[:3000]
    except Exception:
        return "unknown"

    lines = text.splitlines()
    timestamp_lines = sum(1 for l in lines if TIMESTAMP_RE.search(l))
    if timestamp_lines > 5:
        return "transcript"
    if EPISTOLARY_RE.search(text):
        return "letter"
    messenger_matches = len(MESSENGER_RE.findall(text))
    if messenger_matches > 3:
        return "conversation"
    if ARTICLE_RE.search(text):
        return "news"
    if filepath.suffix in (".pdf", ".docx"):
        return "document"
    return "note"


def scan_character(char_slug: str) -> list[dict]:
    mat_dir = MATERIALS / char_slug
    if not mat_dir.exists():
        return []
    results = []
    # C1-MAT-10b: use rglob to capture nested materials (was iterdir — missed subdirs)
    for f in sorted(mat_dir.rglob("*")):
        if f.is_dir():
            continue
        stat = f.stat()
        lines = 0
        try:
            lines = len(f.read_text(encoding="utf-8", errors="replace").splitlines())
        except Exception:
            pass
        results.append({
            "character": CHAR_DISPLAY.get(char_slug, char_slug),
            "filename": f.name,
            "lines": lines,
            "size_kb": round(stat.st_size / 1024, 1),
            "modified_date": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d"),
            "type_guess": detect_type(f),
        })
    return results


def main():
    parser = argparse.ArgumentParser(description="Inventory docs/materials/ with type detection")
    parser.add_argument("--character", help="Filter to specific character (slug or alias)")
    parser.add_argument("--type", choices=["transcript", "letter", "conversation", "news", "note", "document"],
                        help="Filter by detected type")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    chars = ALL_CHARS
    if args.character:
        from platform_lib.paths import resolve_character
        chars = [resolve_character(args.character)]

    all_items = []
    for c in chars:
        all_items.extend(scan_character(c))

    if args.type:
        all_items = [i for i in all_items if i["type_guess"] == args.type]

    if args.json:
        print_json(all_items)
        return

    print(f"\n## Materials Inventory ({len(all_items)} files)\n")
    if not all_items:
        print("_(no materials found)_")
        return

    headers = ["Character", "Filename", "Lines", "Size (KB)", "Modified", "Type"]
    rows = [[i["character"], i["filename"], str(i["lines"]),
             str(i["size_kb"]), i["modified_date"], i["type_guess"]] for i in all_items]
    print_table(headers, rows)

    # Summary by type
    type_counts: dict[str, int] = {}
    for i in all_items:
        type_counts[i["type_guess"]] = type_counts.get(i["type_guess"], 0) + 1
    print("\n### Type Summary\n")
    for t, count in sorted(type_counts.items()):
        print(f"- **{t}**: {count} file(s)")


if __name__ == "__main__":
    main()
