#!/usr/bin/env python3
"""Check profile-lite cache freshness and compression ratios per character."""
import os
import sys
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))

from platform_lib.profile_stats import cache_status_table, cache_is_valid
from platform_lib.paths import ALL_CHARS, CHAR_DISPLAY
from platform_lib.formatters import print_table, eprint


def main():
    parser = argparse.ArgumentParser(
        description="Check profile-lite cache freshness and compression ratios"
    )
    parser.add_argument(
        "--regen-needed", action="store_true",
        help="Exit with code 1 if any cache is stale (useful for CI/pre-flight)"
    )
    args = parser.parse_args()

    rows = cache_status_table()

    table_rows = []
    for r in rows:
        status_icon = "VALID" if r["cache_valid"] else "STALE - REGEN NEEDED"
        table_rows.append([
            r["character"],
            status_icon,
            str(r["full_lines"]),
            str(r["lite_lines"]),
            r["reduction"],
        ])

    headers = ["Character", "Cache Status", "Full Lines", "Lite Lines", "Compression"]
    print_table(headers, table_rows)

    stale = [r for r in rows if not r["cache_valid"]]
    valid = [r for r in rows if r["cache_valid"]]

    print(f"\n## Summary")
    print(f"- Valid caches: {len(valid)}/{len(rows)}")
    print(f"- Stale caches: {len(stale)}/{len(rows)}")

    if stale:
        print(f"\n## Action Required")
        for r in stale:
            print(f"- Run `psy:profile-lite --character {r['character'].lower()}` to regenerate")
        eprint(f"[WARN] {len(stale)} stale cache(s): {', '.join(r['character'] for r in stale)}")
        if args.regen_needed:
            sys.exit(1)
    else:
        eprint("[OK] All profile-lite caches are fresh")


if __name__ == "__main__":
    main()
