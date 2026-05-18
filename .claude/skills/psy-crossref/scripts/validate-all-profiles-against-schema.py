"""Validate all character profiles against universal-profile-schema for psy:crossref."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import ALL_CHARS, CHAR_DISPLAY
from platform_lib.profile_validator import validate_character, validate_all


def main():
    parser = argparse.ArgumentParser(description="Validate all profiles against schema")
    parser.add_argument("--character", "-c", help="Single character slug")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    fmt = "json" if args.json else "text"

    if args.character:
        results = validate_character(args.character)
        ok = sum(1 for r in results if r["status"] == "OK")
        issues = sum(1 for r in results if r["status"] != "OK")

        if args.json:
            print(json.dumps({args.character: results}, indent=2, ensure_ascii=False))
        else:
            display = CHAR_DISPLAY.get(args.character, args.character)
            print(f"\n{'='*60}")
            print(f"  {display} ({args.character})")
            print(f"{'='*60}")
            for entry in results:
                icon = {"OK": "✓", "MISSING": "✗", "EMPTY": "○", "ERROR": "!", "INVALID": "⚠"}.get(
                    entry["status"], "?"
                )
                if entry["status"] == "OK":
                    print(f"  {icon} {entry['file']}")
                else:
                    print(f"  {icon} {entry['file']} [{entry['status']}]")
                    for err in entry["errors"]:
                        print(f"      → {err}")
            print(f"\n  {ok} OK | {issues} issues")

        sys.exit(1 if issues > 0 else 0)

    report = validate_all(output_format=fmt)

    total_issues = 0
    for slug, results in report.items():
        total_issues += sum(1 for r in results if r["status"] != "OK")

    sys.exit(1 if total_issues > 0 else 0)


if __name__ == "__main__":
    main()
