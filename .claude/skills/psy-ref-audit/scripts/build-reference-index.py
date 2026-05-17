#!/usr/bin/env python3
"""Parse docs/references/INDEX.md → JSON map of {theory_name: {file, category, key_terms[]}}."""
import os
import sys
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))

from platform_lib.clinical_terms import build_reference_index
from platform_lib.paths import REFERENCES
from platform_lib.formatters import print_json, eprint


def main():
    parser = argparse.ArgumentParser(description="Build reference index from docs/references/INDEX.md")
    parser.add_argument("--pretty", action="store_true", default=True, help="Pretty-print JSON (default)")
    parser.add_argument("--compact", action="store_true", help="Compact JSON output")
    args = parser.parse_args()

    index = build_reference_index(REFERENCES)
    if not index:
        eprint(f"[WARN] No entries found. Check {REFERENCES / 'INDEX.md'}")
        sys.exit(1)

    print_json(index, pretty=not args.compact)
    eprint(f"[OK] {len(index)} theories indexed from {REFERENCES / 'INDEX.md'}")


if __name__ == "__main__":
    main()
