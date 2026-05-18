"""Find stale materials by processing status for mat:indexer --stale."""
import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import ALL_CHARS, CHAR_DISPLAY, MATERIALS
from platform_lib.materials_classifier import extract_frontmatter


def find_stale(slug: str, stale_days: int = 7) -> list[dict]:
    """Find materials with processing_status=raw and last_updated older than stale_days."""
    mdir = MATERIALS / slug
    if not mdir.exists():
        return []

    cutoff = datetime.now() - timedelta(days=stale_days)
    results = []

    for fpath in sorted(mdir.rglob("*.md")):
        if fpath.is_dir():
            continue
        fm = extract_frontmatter(fpath)
        if not fm:
            results.append({
                "file": fpath.name,
                "path": str(fpath.relative_to(MATERIALS)),
                "processing_status": "no_frontmatter",
                "last_updated": "unknown",
                "stale_days": -1,
            })
            continue

        status = fm.get("processing_status", "unknown")
        if status not in ("raw", "extracted"):
            continue

        last_updated = str(fm.get("last_updated", ""))
        try:
            updated_date = datetime.strptime(last_updated, "%Y-%m-%d")
            days_stale = (datetime.now() - updated_date).days
        except ValueError:
            days_stale = -1
            updated_date = None

        if updated_date is None or updated_date < cutoff:
            results.append({
                "file": fpath.name,
                "path": str(fpath.relative_to(MATERIALS)),
                "processing_status": status,
                "last_updated": last_updated or "unknown",
                "stale_days": days_stale,
            })

    return sorted(results, key=lambda x: x["stale_days"], reverse=True)


def main():
    parser = argparse.ArgumentParser(description="Find stale materials by processing status")
    parser.add_argument("--character", "-c", help="Single character slug")
    parser.add_argument("--days", "-d", type=int, default=7, help="Staleness threshold in days (default: 7)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    chars = [args.character] if args.character else ALL_CHARS
    report = {}
    for slug in chars:
        report[slug] = find_stale(slug, args.days)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return

    total = 0
    for slug, items in report.items():
        display = CHAR_DISPLAY.get(slug, slug)
        print(f"\n{'='*70}")
        print(f"  {display} ({slug}) — {len(items)} stale materials (>{args.days} days)")
        print(f"{'='*70}")

        if not items:
            print("  (none)")
            continue

        print(f"  {'File':<40s} {'Status':<14s} {'Updated':<12s} {'Days':<5s}")
        print(f"  {'-'*40} {'-'*14} {'-'*12} {'-'*5}")

        for item in items:
            total += 1
            name = item["file"][:38]
            days = str(item["stale_days"]) if item["stale_days"] >= 0 else "?"
            print(f"  {name:<40s} {item['processing_status']:<14s} {item['last_updated']:<12s} {days:<5s}")

    print(f"\n  TOTAL: {total} stale materials")


if __name__ == "__main__":
    main()
