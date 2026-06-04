"""Identify materials with missing or incomplete CRAAP scores needing re-evaluation."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import ALL_CHARS, CHAR_DISPLAY, MATERIALS, resolve_character
# Use the YAML-based parser: craap_score is a nested mapping (currency/relevance/
# authority/accuracy/purpose/total), which the line-based markdown parser cannot read.
from platform_lib.materials_classifier import extract_frontmatter

CRAAP_FIELDS = ["currency", "relevance", "authority", "accuracy", "purpose", "total"]


def check_craap(fm: dict) -> list[str]:
    """Return list of CRAAP issues found in frontmatter."""
    issues = []
    craap = fm.get("craap_score")
    if craap is None:
        issues.append("missing craap_score block")
        return issues
    if not isinstance(craap, dict):
        issues.append("craap_score is not a mapping")
        return issues
    missing_fields = [f for f in CRAAP_FIELDS if craap.get(f) is None]
    if missing_fields:
        issues.append(f"missing fields: {', '.join(missing_fields)}")
    # Verify total matches sum
    components = ["currency", "relevance", "authority", "accuracy", "purpose"]
    try:
        calc_total = sum(int(craap[f]) for f in components if craap.get(f) is not None)
        declared = craap.get("total")
        if declared is not None and int(declared) != calc_total:
            issues.append(f"total mismatch: declared={declared}, calculated={calc_total}")
    except (TypeError, ValueError):
        issues.append("non-numeric score values")
    return issues


def scan_character(slug: str, missing_only: bool, raw_only: bool) -> list[dict]:
    mat_dir = MATERIALS / slug
    if not mat_dir.exists():
        return []
    results = []
    for f in sorted(mat_dir.rglob("*.md")):
        text = f.read_text(encoding="utf-8")
        fm = extract_frontmatter(f) or {}
        status = fm.get("processing_status", "unknown")

        if raw_only and status != "raw":
            continue

        reasons = []
        if not fm:
            reasons.append("no frontmatter")
        else:
            if status == "raw":
                reasons.append("processing_status is raw")
            craap_issues = check_craap(fm)
            reasons.extend(craap_issues)

        if not reasons:
            continue
        if missing_only:
            # Only include if CRAAP block entirely missing
            if not any("missing craap_score" in r or "no frontmatter" in r for r in reasons):
                continue

        craap_total = None
        if fm:
            craap = fm.get("craap_score")
            if isinstance(craap, dict):
                craap_total = craap.get("total")

        results.append({
            "name": f.name,
            "slug": slug,
            "status": status,
            "craap_total": craap_total,
            "reasons": reasons,
        })
    return results


def main():
    parser = argparse.ArgumentParser(description="Identify materials needing CRAAP rescore")
    parser.add_argument("--character", "-c", help="Character slug or alias")
    parser.add_argument("--missing-only", action="store_true",
                        help="Only show files with no craap_score at all")
    parser.add_argument("--raw-only", action="store_true",
                        help="Only show files with processing_status: raw")
    parser.add_argument("--json", dest="json_out", action="store_true", help="JSON output")
    args = parser.parse_args()

    chars = [resolve_character(args.character)] if args.character else ALL_CHARS

    all_results: dict[str, list[dict]] = {}
    for slug in chars:
        items = scan_character(slug, args.missing_only, args.raw_only)
        all_results[slug] = items

    if args.json_out:
        print(json.dumps(all_results, indent=2, ensure_ascii=False))
        return

    print(f"\n{'='*70}")
    print("  Rescore Audit Report")
    print(f"{'='*70}")

    total_flagged = 0
    for slug, items in all_results.items():
        display = CHAR_DISPLAY.get(slug, slug)
        total = sum(1 for f in (MATERIALS / slug).rglob("*.md")) if (MATERIALS / slug).exists() else 0
        print(f"\n  {display} ({slug}) — {len(items)}/{total} need rescore")
        if not items:
            print("    All materials have complete CRAAP scores.")
            continue
        print(f"\n  {'File':<40s} {'Status':<12s} {'Score':<8s} Reasons")
        print(f"  {'-'*40} {'-'*12} {'-'*8} {'-'*30}")
        for item in items:
            score_str = f"{item['craap_total']}/25" if item["craap_total"] is not None else "—"
            reason_str = "; ".join(item["reasons"])
            print(f"  {item['name'][:38]:<40s} {item['status']:<12s} {score_str:<8s} {reason_str}")
        total_flagged += len(items)

    print(f"\n  TOTAL FLAGGED: {total_flagged} materials need rescore")
    print(f"\n  Next step: run `mat:loader --ingest <file>` for each flagged material")


if __name__ == "__main__":
    main()
