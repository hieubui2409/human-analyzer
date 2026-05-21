#!/usr/bin/env python3
"""Check if profile-lite cache is valid by comparing git hashes."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))

from platform_lib.profile_stats import cache_status_table
from platform_lib.formatters import print_table, eprint


def main():
    rows = cache_status_table()
    table_rows = [
        [
            r["character"],
            "VALID" if r["cache_valid"] else "STALE",
            str(r["full_lines"]),
            str(r["lite_lines"]),
            r["reduction"],
        ]
        for r in rows
    ]
    headers = ["Character", "Cache Status", "Full Lines", "Lite Lines", "Reduction"]
    print_table(headers, table_rows)

    stale = [r for r in rows if not r["cache_valid"]]
    if stale:
        eprint(f"[WARN] {len(stale)} cache(s) stale: {', '.join(r['character'] for r in stale)}")
    else:
        eprint("[OK] All caches valid")


if __name__ == "__main__":
    main()
