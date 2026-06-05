#!/usr/bin/env python3
"""Verify shared events appear in BOTH profiles' timeline/overview.md and relationships/family.md."""
import os
import sys
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.paths import (
    CHAR_DISPLAY, character_dir, list_relationship_files, CHARACTER_PAIRS, CHAR_SEARCH_ALIASES,
)
from platform_lib.markdown_parser import find_cross_references
from platform_lib.formatters import print_table, print_json

PAIRS = CHARACTER_PAIRS
CHAR_ALIASES = CHAR_SEARCH_ALIASES

CHECK_FILES = ["timeline/overview.md", "relationships/family.md"]


def check_pair(char1: str, char2: str) -> list[dict]:
    """For each file type, check if char1 mentions char2 and vice versa."""
    results = []
    aliases1 = CHAR_ALIASES.get(char1, [])
    aliases2 = CHAR_ALIASES.get(char2, [])

    for fname in CHECK_FILES:
        file1 = character_dir(char1) / fname
        file2 = character_dir(char2) / fname

        # Does char1's file mention char2?
        refs_1_mentions_2 = find_cross_references(file1, aliases2)
        # Does char2's file mention char1?
        refs_2_mentions_1 = find_cross_references(file2, aliases1)

        c1_has = len(refs_1_mentions_2) > 0
        c2_has = len(refs_2_mentions_1) > 0
        bidirectional = c1_has and c2_has

        results.append({
            "file": fname,
            "char1": CHAR_DISPLAY[char1],
            "char2": CHAR_DISPLAY[char2],
            "char1_mentions_char2": c1_has,
            "char2_mentions_char1": c2_has,
            "bidirectional": bidirectional,
            "char1_ref_count": len(refs_1_mentions_2),
            "char2_ref_count": len(refs_2_mentions_1),
        })
    return results


def check_mirror_relationships(char1: str, char2: str) -> list[dict]:
    """Check that cross-relationship mirror files both exist and reference each other."""
    results = []
    file1 = character_dir(char1) / f"relationships/{char2}.md"
    file2 = character_dir(char2) / f"relationships/{char1}.md"
    aliases1 = CHAR_ALIASES.get(char1, [])
    aliases2 = CHAR_ALIASES.get(char2, [])

    f1_exists = file1.exists()
    f2_exists = file2.exists()
    c1_refs = find_cross_references(file1, aliases2) if f1_exists else []
    c2_refs = find_cross_references(file2, aliases1) if f2_exists else []

    results.append({
        "file": f"relationships/{{mirror}}",
        "char1": CHAR_DISPLAY[char1],
        "char2": CHAR_DISPLAY[char2],
        "char1_mentions_char2": len(c1_refs) > 0,
        "char2_mentions_char1": len(c2_refs) > 0,
        "bidirectional": f1_exists and f2_exists and len(c1_refs) > 0 and len(c2_refs) > 0,
        "char1_ref_count": len(c1_refs),
        "char2_ref_count": len(c2_refs),
        "detail": f"{char1}/relationships/{char2}.md ↔ {char2}/relationships/{char1}.md",
    })
    return results


def main():
    parser = argparse.ArgumentParser(description="Check bidirectional references between character profiles")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--only-issues", action="store_true", help="Show only non-bidirectional entries")
    args = parser.parse_args()

    all_results = []
    for c1, c2 in PAIRS:
        all_results.extend(check_pair(c1, c2))
        all_results.extend(check_mirror_relationships(c1, c2))

    if args.only_issues:
        all_results = [r for r in all_results if not r["bidirectional"]]

    if args.json:
        print_json(all_results)
        return

    headers = ["File", "Pair", f"C1→C2 (refs)", f"C2→C1 (refs)", "Bidirectional"]
    rows = []
    for r in all_results:
        pair_str = f"{r['char1']} ↔ {r['char2']}"
        c1_str = f"{'YES' if r['char1_mentions_char2'] else 'NO'} ({r['char1_ref_count']})"
        c2_str = f"{'YES' if r['char2_mentions_char1'] else 'NO'} ({r['char2_ref_count']})"
        bidi = "OK" if r["bidirectional"] else "MISSING"
        rows.append([r["file"], pair_str, c1_str, c2_str, bidi])

    print("\n## Bidirectional Reference Check\n")
    print_table(headers, rows)

    issues = [r for r in all_results if not r["bidirectional"]]
    if issues:
        print(f"\n**{len(issues)} issue(s) found** — missing bidirectional references.")
    else:
        print("\n**All references are bidirectional.**")


if __name__ == "__main__":
    main()
