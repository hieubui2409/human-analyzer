"""Archive materials matching filter criteria by setting processing_status: archived."""
import argparse
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import ALL_CHARS, CHAR_DISPLAY, MATERIALS, resolve_character
from platform_lib.materials_classifier import extract_frontmatter
from platform_lib.errors import emit_error


def parse_frontmatter_date(val) -> date | None:
    if not val:
        return None
    try:
        return datetime.strptime(str(val), "%Y-%m-%d").date()
    except ValueError:
        return None


def scan_materials(slug: str) -> list[dict]:
    mat_dir = MATERIALS / slug
    if not mat_dir.exists():
        return []
    results = []
    for f in sorted(mat_dir.rglob("*.md")):
        fm = extract_frontmatter(f) or {}
        results.append({
            "path": f,
            "name": f.name,
            "slug": slug,
            "tier": fm.get("evidence_tier", ""),
            "status": fm.get("processing_status", ""),
            "captured_date": fm.get("captured_date", ""),
            "has_frontmatter": bool(fm),
            "frontmatter": fm,
            # raw_text is read on-demand in apply mode only (avoid wasted I/O in dry-run)
        })
    return results


def matches_filters(item: dict, before_date: date | None, tier: str | None, status: str | None) -> bool:
    if tier and item["tier"] != tier:
        return False
    if status and item["status"] != status:
        return False
    if before_date:
        item_date = parse_frontmatter_date(item["captured_date"])
        if item_date is None or item_date >= before_date:
            return False
    return True


def update_frontmatter_field(text: str, field: str, value: str) -> str:
    """Update a specific frontmatter field value in YAML block."""
    lines = text.split("\n")
    in_fm = False
    fm_start = fm_end = -1
    for i, line in enumerate(lines):
        if line.strip() == "---":
            if not in_fm:
                in_fm = True
                fm_start = i
            else:
                fm_end = i
                break
    if fm_start == -1 or fm_end == -1:
        return text
    for i in range(fm_start + 1, fm_end):
        if lines[i].startswith(f"{field}:"):
            lines[i] = f"{field}: {value}"
            return "\n".join(lines)
    # Field not found — insert before closing ---
    lines.insert(fm_end, f"{field}: {value}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Archive materials by filter criteria")
    parser.add_argument("--character", "-c", help="Character slug or alias")
    parser.add_argument("--before-date", help="Archive files with captured_date before YYYY-MM-DD")
    parser.add_argument("--tier", help="Evidence tier to match (T1-T5)")
    parser.add_argument("--status", help="processing_status to match")
    parser.add_argument("--dry-run", action="store_true", default=True,
                        help="Preview only, no writes (default: True)")
    parser.add_argument("--apply", action="store_true",
                        help="Actually apply the archive (overrides --dry-run)")
    args = parser.parse_args()

    dry_run = not args.apply

    before_date = None
    if args.before_date:
        try:
            before_date = datetime.strptime(args.before_date, "%Y-%m-%d").date()
        except ValueError:
            emit_error("validation", f"invalid --before-date: {args.before_date!r}")
            print(f"ERROR: invalid --before-date format: {args.before_date!r} (expected YYYY-MM-DD)")
            sys.exit(1)

    chars = [resolve_character(args.character)] if args.character else ALL_CHARS

    matched: list[dict] = []
    for slug in chars:
        for item in scan_materials(slug):
            if item["status"] == "archived":
                continue
            if matches_filters(item, before_date, args.tier, args.status):
                matched.append(item)

    mode = "DRY RUN — no files modified" if dry_run else "APPLYING — files will be updated"
    print(f"\n{'='*70}")
    print(f"  Archive Preview ({mode})")
    print(f"{'='*70}")

    filters_desc = []
    if args.character:
        filters_desc.append(f"character={args.character}")
    if args.tier:
        filters_desc.append(f"tier={args.tier}")
    if args.status:
        filters_desc.append(f"status={args.status}")
    if before_date:
        filters_desc.append(f"before-date={before_date}")
    print(f"  Filters: {', '.join(filters_desc) or 'none (all non-archived)'}")
    print()

    if not matched:
        print("  No materials match the given filters.")
        return

    print(f"  {'File':<42s} {'Char':<8s} {'Tier':<5s} {'Status':<12s} {'Captured Date'}")
    print(f"  {'-'*42} {'-'*8} {'-'*5} {'-'*12} {'-'*13}")
    for item in matched:
        display = CHAR_DISPLAY.get(item["slug"], item["slug"])
        print(f"  {item['name'][:40]:<42s} {display:<8s} {item['tier'] or '-':<5s} {item['status'] or '-':<12s} {item['captured_date'] or '-'}")

    today = date.today().isoformat()
    archived_count = 0
    if not dry_run:
        for item in matched:
            text = item["path"].read_text(encoding="utf-8")
            text = update_frontmatter_field(text, "processing_status", "archived")
            text = update_frontmatter_field(text, "last_updated", today)
            item["path"].write_text(text, encoding="utf-8")
            archived_count += 1

    print()
    if dry_run:
        print(f"  TOTAL: {len(matched)} files would be archived (run with --apply to execute)")
    else:
        print(f"  TOTAL: {archived_count} files archived successfully")


if __name__ == "__main__":
    main()
