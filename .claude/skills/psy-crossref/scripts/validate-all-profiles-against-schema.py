"""Validate all character profiles against the authoritative JSON schemas for psy:crossref.

Uses the shared `schema_validator` engine (Draft-7 `.schema.json` — the source of truth)
instead of the retired `profile_validator` (which checked a hard-coded field list against
the now non-authoritative universal-profile-schema.yaml). Filesystem-level checks the
schema engine can't express — file presence, emptiness, and character-slug match — stay here.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import ALL_CHARS, CHAR_DISPLAY, PROFILES, PROFILE_FILES, resolve_character
from platform_lib import schema_validator as sv

# status icons preserved from the previous validator for stable CLI output
ICONS = {"OK": "✓", "MISSING": "✗", "EMPTY": "○", "ERROR": "!", "INVALID": "⚠"}


def validate_character(slug: str) -> list[dict]:
    """Per-file {file, status, errors} for one character (OK/MISSING/EMPTY/ERROR/INVALID)."""
    cdir = PROFILES / slug
    if not cdir.exists():
        return [{"file": slug, "status": "MISSING", "errors": ["character directory not found"]}]

    results = []
    for relpath in PROFILE_FILES:
        fpath = cdir / relpath
        entry = {"file": str(relpath), "status": "OK", "errors": []}

        if not fpath.exists():
            entry.update(status="MISSING", errors=["file not found"])
            results.append(entry)
            continue
        if not fpath.read_text(encoding="utf-8").strip():
            entry.update(status="EMPTY", errors=["file is empty (no frontmatter)"])
            results.append(entry)
            continue

        # Authoritative schema contract (SKIP = no schema covers this file → treat as OK).
        res = sv.validate_file(fpath)
        if res["status"] == "FAIL":
            entry["status"] = "INVALID"
            entry["errors"] = [f"{v['field']}: {v['message']}" for v in res["violations"]]

        # Cross-file check the schema can't do: frontmatter character must match the dir slug.
        fm = sv.parse_frontmatter(fpath)
        if fm and fm.get("character") not in (None, slug):
            entry["status"] = "INVALID"
            entry["errors"].append(f"character mismatch: expected {slug}, got {fm.get('character')}")

        results.append(entry)
    return results


def _print_character(slug: str, results: list[dict]) -> int:
    display = CHAR_DISPLAY.get(slug, slug)
    print(f"\n{'='*60}\n  {display} ({slug})\n{'='*60}")
    issues = 0
    for entry in results:
        icon = ICONS.get(entry["status"], "?")
        if entry["status"] == "OK":
            print(f"  {icon} {entry['file']}")
        else:
            issues += 1
            print(f"  {icon} {entry['file']} [{entry['status']}]")
            for err in entry["errors"]:
                print(f"      → {err}")
    return issues


def main():
    parser = argparse.ArgumentParser(description="Validate all profiles against authoritative schema")
    parser.add_argument("--character", "-c", help="Single character slug")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    slugs = [resolve_character(args.character)] if args.character else ALL_CHARS
    report = {slug: validate_character(slug) for slug in slugs}

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        total_issues = sum(1 for rs in report.values() for r in rs if r["status"] != "OK")
        sys.exit(1 if total_issues > 0 else 0)

    total_issues = 0
    for slug, results in report.items():
        issues = _print_character(slug, results)
        ok = sum(1 for r in results if r["status"] == "OK")
        total_issues += issues
        print(f"\n  {ok} OK | {issues} issues")
    sys.exit(1 if total_issues > 0 else 0)


if __name__ == "__main__":
    main()
