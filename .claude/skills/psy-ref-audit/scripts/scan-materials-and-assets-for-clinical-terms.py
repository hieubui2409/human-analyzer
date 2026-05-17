#!/usr/bin/env python3
"""Scan docs/materials/ and assets/ for raw clinical terms. Supports --discover flag."""
import os
import sys
import argparse
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))

from platform_lib.clinical_terms import scan_file_for_clinical_terms
from platform_lib.paths import MATERIALS, ASSETS
from platform_lib.formatters import print_table, eprint

SCAN_EXTENSIONS = {".md", ".txt", ".text"}


def scan_dir(directory: Path) -> list[list[str]]:
    rows = []
    if not directory.exists():
        return rows
    for fpath in sorted(directory.rglob("*")):
        if fpath.suffix.lower() not in SCAN_EXTENSIONS:
            continue
        rel = str(fpath.relative_to(directory.parent))
        hits = scan_file_for_clinical_terms(fpath)
        for h in hits:
            ctx = h["context"].replace("|", "\\|")
            rows.append([rel, str(h["line"]), h["term"], ctx[:80]])
    return rows


def main():
    parser = argparse.ArgumentParser(
        description="Scan materials/assets for raw clinical terms (for --discover blind spots)"
    )
    parser.add_argument(
        "--discover", action="store_true",
        help="Show summary count per term for blind spot analysis"
    )
    parser.add_argument(
        "--materials-only", action="store_true", help="Scan docs/materials/ only"
    )
    parser.add_argument(
        "--assets-only", action="store_true", help="Scan assets/ only"
    )
    args = parser.parse_args()

    rows = []
    if not args.assets_only:
        rows.extend(scan_dir(MATERIALS))
    if not args.materials_only:
        rows.extend(scan_dir(ASSETS))

    headers = ["File", "Line", "Term", "Context"]
    print_table(headers, rows)

    if args.discover and rows:
        from collections import Counter
        counts = Counter(r[2] for r in rows)
        print("\n## Term Frequency (--discover)")
        print_table(["Term", "Count"], [[t, str(c)] for t, c in counts.most_common(20)])

    eprint(f"[OK] {len(rows)} clinical term hits in materials/assets")


if __name__ == "__main__":
    main()
