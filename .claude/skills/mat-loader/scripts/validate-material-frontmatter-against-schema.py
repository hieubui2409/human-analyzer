"""Validate material frontmatter against MAT schema for mat:loader --ingest validation."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import ALL_CHARS, CHAR_DISPLAY, MATERIALS, resolve_character
from platform_lib.materials_classifier import validate_material_frontmatter


def main():
    parser = argparse.ArgumentParser(description="Validate material frontmatter against schema")
    parser.add_argument("--character", "-c", help="Single character slug")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    chars = [resolve_character(args.character)] if args.character else ALL_CHARS
    all_results = {}
    total_files = 0
    total_valid = 0
    total_invalid = 0

    for slug in chars:
        mdir = MATERIALS / slug
        if not mdir.exists():
            continue
        results = []
        for fpath in sorted(mdir.rglob("*.md")):
            if fpath.is_dir():
                continue
            total_files += 1
            errors = validate_material_frontmatter(fpath)
            entry = {
                "file": str(fpath.relative_to(MATERIALS)),
                "status": "VALID" if not errors else "INVALID",
                "errors": errors,
            }
            if errors:
                total_invalid += 1
            else:
                total_valid += 1
            results.append(entry)
        all_results[slug] = results

    if args.json:
        print(json.dumps(all_results, indent=2, ensure_ascii=False))
        sys.exit(1 if total_invalid > 0 else 0)

    for slug, results in all_results.items():
        display = CHAR_DISPLAY.get(slug, slug)
        print(f"\n{'='*60}")
        print(f"  {display} ({slug})")
        print(f"{'='*60}")

        for entry in results:
            icon = "✓" if entry["status"] == "VALID" else "✗"
            print(f"  {icon} {entry['file']}")
            for err in entry["errors"]:
                print(f"      → {err}")

    print(f"\n{'='*60}")
    print(f"  TOTAL: {total_files} files | {total_valid} valid | {total_invalid} invalid")
    print(f"{'='*60}")
    sys.exit(1 if total_invalid > 0 else 0)


if __name__ == "__main__":
    main()
