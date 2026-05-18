"""Inventory all materials with frontmatter status for mat:loader --list/--status."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import ALL_CHARS, CHAR_DISPLAY, MATERIALS
from platform_lib.materials_classifier import (
    EVIDENCE_TIERS,
    inventory_character_with_frontmatter,
)


def main():
    parser = argparse.ArgumentParser(description="Inventory materials with frontmatter status")
    parser.add_argument("--character", "-c", help="Single character slug")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--status", "-s", help="Filter by processing_status")
    args = parser.parse_args()

    chars = [args.character] if args.character else ALL_CHARS
    report = {}
    for slug in chars:
        items = inventory_character_with_frontmatter(slug)
        if args.status:
            items = [i for i in items if i["processing_status"] == args.status]
        report[slug] = items

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return

    total = 0
    for slug, items in report.items():
        display = CHAR_DISPLAY.get(slug, slug)
        print(f"\n{'='*70}")
        print(f"  {display} ({slug}) — {len(items)} materials")
        print(f"{'='*70}")
        print(f"  {'File':<40s} {'Type':<16s} {'Tier':<4s} {'Status':<12s} {'FM':<4s}")
        print(f"  {'-'*40} {'-'*16} {'-'*4} {'-'*12} {'-'*4}")

        for item in items:
            total += 1
            tier = f"T{item['evidence_tier']}"
            fm = "✓" if item["has_frontmatter"] else "✗"
            name = item["name"][:38]
            print(f"  {name:<40s} {item['type']:<16s} {tier:<4s} {item['processing_status']:<12s} {fm:<4s}")

    print(f"\n  TOTAL: {total} materials across {len(chars)} character(s)")


if __name__ == "__main__":
    main()
