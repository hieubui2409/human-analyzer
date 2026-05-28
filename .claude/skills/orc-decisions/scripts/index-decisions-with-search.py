#!/usr/bin/env python3
"""Scan .claude/decisions/ to build a searchable index of decision records with frontmatter metadata."""
import os
import sys
import argparse
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.paths import DECISIONS, resolve_character
from platform_lib.markdown_parser import extract_frontmatter, extract_sections, count_lines
from platform_lib.formatters import print_table, print_json

DECISIONS_DIR = DECISIONS


def load_decisions(decisions_dir: Path) -> list[dict]:
    """Load all decision records from directory."""
    if not decisions_dir.exists():
        return []
    results = []
    for f in sorted(decisions_dir.glob("*.md")):
        fm = extract_frontmatter(f)
        sections = extract_sections(f, level=2)
        summary = ""
        for key in ["Summary", "Decision", "Context", "Quyết định"]:
            if key in sections:
                summary = sections[key][:120].replace("\n", " ").strip()
                break
        results.append({
            "file": f.name,
            "date": fm.get("date", fm.get("Date", "")),
            "character": fm.get("character", fm.get("Character", "")),
            "category": fm.get("category", fm.get("Category", "")),
            "status": fm.get("status", fm.get("Status", "open")),
            "title": fm.get("title", fm.get("Title", f.stem)),
            "summary": summary,
            "lines": count_lines(f),
            "path": str(f),
        })
    return results


def filter_decisions(decisions: list[dict], search: str = "", character: str = "") -> list[dict]:
    if character:
        try:
            slug = resolve_character(character)
            decisions = [d for d in decisions if slug in d["character"].lower() or
                         character.lower() in d["character"].lower()]
        except ValueError:
            decisions = [d for d in decisions if character.lower() in d["character"].lower()]
    if search:
        q = search.lower()
        decisions = [d for d in decisions if
                     q in d["title"].lower() or q in d["summary"].lower() or
                     q in d["category"].lower() or q in d["character"].lower()]
    return decisions


def main():
    parser = argparse.ArgumentParser(description="Index and search decision records from .claude/decisions/")
    parser.add_argument("--search", help="Search query (matches title, summary, category, character)")
    parser.add_argument("--character", help="Filter by character name or slug")
    parser.add_argument("--list", action="store_true", help="List all decisions")
    parser.add_argument("--status", choices=["open", "closed", "pending"], help="Filter by status")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    decisions = load_decisions(DECISIONS_DIR)

    if not decisions:
        print(f"No decision records found in {DECISIONS_DIR}")
        print("Create records in .claude/decisions/*.md with YAML frontmatter (date, character, category, status, title)")
        sys.exit(0)

    if args.status:
        decisions = [d for d in decisions if d["status"].lower() == args.status]

    if args.search or args.character:
        decisions = filter_decisions(decisions, search=args.search or "", character=args.character or "")

    if args.json:
        print_json(decisions)
        return

    print(f"\n## Decision Index ({len(decisions)} record(s))\n")
    if not decisions:
        print("_(no matching records)_")
        return

    headers = ["Date", "Title", "Character", "Category", "Status", "Lines"]
    rows = [[d["date"], d["title"][:50], d["character"], d["category"], d["status"], str(d["lines"])]
            for d in decisions]
    print_table(headers, rows)

    if args.search or args.character:
        print(f"\n**Filter applied:** search=`{args.search or ''}` character=`{args.character or ''}`")


if __name__ == "__main__":
    main()
