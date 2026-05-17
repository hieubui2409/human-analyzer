#!/usr/bin/env python3
"""Count lines in each profile file per character.
Used by --stats to compare full vs lite profile sizes."""
import os
import sys
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.paths import ALL_CHARS, CHAR_DISPLAY, character_dir, PROFILE_FILES, PROFILE_CACHE
from platform_lib.markdown_parser import count_lines
from platform_lib.formatters import print_json, print_table


def count_for_character(slug: str) -> dict:
    cdir = character_dir(slug)
    display = CHAR_DISPLAY[slug]
    file_counts = {}
    total = 0

    # Count all .md files, not just standard profile files
    all_mds = sorted(cdir.glob("*.md"))
    for md in all_mds:
        lc = count_lines(md)
        file_counts[md.name] = lc
        total += lc

    # Lite cache comparison
    lite_total = 0
    lite_file = PROFILE_CACHE / f"{slug}-lite.md" if PROFILE_CACHE else None
    if lite_file and lite_file.exists():
        lite_total = count_lines(lite_file)

    return {
        "character": display,
        "slug": slug,
        "files": file_counts,
        "total_lines": total,
        "lite_lines": lite_total,
        "compression_ratio": round(lite_total / total, 3) if total > 0 and lite_total > 0 else None,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Count lines per profile file per character (full vs lite comparison)"
    )
    parser.add_argument("--character", help="Specific character alias (default: all)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--totals-only", action="store_true", help="Show only totals, not per-file breakdown")
    args = parser.parse_args()

    from platform_lib.paths import resolve_character
    if args.character:
        targets = [resolve_character(args.character)]
    else:
        targets = ALL_CHARS

    results = [count_for_character(slug) for slug in targets]

    if args.json:
        print_json(results)
        return

    # Per-file breakdown table
    if not args.totals_only:
        print("\n## Profile Line Counts (per file)\n")
        headers = ["Character", "File", "Lines"]
        rows = []
        for r in results:
            for fname, lc in sorted(r["files"].items()):
                rows.append([r["character"], fname, str(lc)])
            rows.append([r["character"], "─── TOTAL ───", str(r["total_lines"])])
            rows.append(["", "", ""])
        print_table(headers, rows)

    # Summary table
    print("\n## Summary: Full vs Lite\n")
    sum_headers = ["Character", "Total Lines (full)", "Lite Lines", "Compression Ratio"]
    sum_rows = []
    for r in results:
        lite_str = str(r["lite_lines"]) if r["lite_lines"] else "N/A (no cache)"
        ratio_str = f"{r['compression_ratio']:.1%}" if r["compression_ratio"] else "N/A"
        sum_rows.append([r["character"], str(r["total_lines"]), lite_str, ratio_str])
    print_table(sum_headers, sum_rows)

    grand_total = sum(r["total_lines"] for r in results)
    print(f"\n**Grand total lines (all characters, all files):** {grand_total}")


if __name__ == "__main__":
    main()
