#!/usr/bin/env python3
"""Parse all profile files for [CONFIDENTIAL: {person}] tags, extract restricted person names.
Output: list of names that MUST NOT appear in assets/."""
import os
import sys
import argparse
import re
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.paths import ALL_CHARS, CHAR_DISPLAY, character_dir, PROFILES
from platform_lib.formatters import print_json, print_table

# Match [CONFIDENTIAL: SomeName] or [CONFIDENTIAL:SomeName]
CONFIDENTIAL_TAG_RE = re.compile(r"\[CONFIDENTIAL:\s*([^\]]+)\]", re.IGNORECASE)
# Also match broader privacy tags
PRIVATE_TAG_RE = re.compile(r"\[(PRIVATE|ANONYMIZE)\]", re.IGNORECASE)


def extract_from_file(filepath: Path, char_slug: str) -> list[dict]:
    if not filepath.exists():
        return []
    results = []
    lines = filepath.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines, 1):
        for m in CONFIDENTIAL_TAG_RE.finditer(line):
            person_name = m.group(1).strip()
            results.append({
                "character": CHAR_DISPLAY.get(char_slug, char_slug),
                "file": filepath.name,
                "line_no": i,
                "tag_type": "CONFIDENTIAL",
                "restricted_name": person_name,
                "context": line.strip()[:100],
            })
        for m in PRIVATE_TAG_RE.finditer(line):
            results.append({
                "character": CHAR_DISPLAY.get(char_slug, char_slug),
                "file": filepath.name,
                "line_no": i,
                "tag_type": m.group(1).upper(),
                "restricted_name": "(unlabeled private content)",
                "context": line.strip()[:100],
            })
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Extract confidential person names from all profile files for privacy guard"
    )
    parser.add_argument("--character", help="Limit to one character (alias or canonical)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--names-only", action="store_true",
                        help="Print only the unique restricted names (one per line)")
    args = parser.parse_args()

    from platform_lib.paths import resolve_character
    if args.character:
        targets = [resolve_character(args.character)]
    else:
        targets = ALL_CHARS

    all_entries = []
    for slug in targets:
        cdir = character_dir(slug)
        for md_file in sorted(cdir.glob("*.md")):
            all_entries.extend(extract_from_file(md_file, slug))

    # Unique restricted names
    unique_names = sorted({e["restricted_name"] for e in all_entries
                           if e["tag_type"] == "CONFIDENTIAL"})

    if args.names_only:
        for name in unique_names:
            print(name)
        return

    if args.json:
        print_json({
            "restricted_names": unique_names,
            "total_tags": len(all_entries),
            "entries": all_entries,
        })
        return

    print(f"\n## Confidential Names Extracted from Profiles\n")
    print(f"These names MUST NOT appear unredacted in assets/:\n")
    for name in unique_names:
        print(f"  - {name}")

    print(f"\n**{len(all_entries)} tag(s) found** across {len(targets)} character(s).\n")

    if all_entries:
        headers = ["Character", "File", "L#", "Tag Type", "Restricted Name", "Context"]
        rows = [
            [e["character"], e["file"], str(e["line_no"]), e["tag_type"],
             e["restricted_name"][:30], e["context"][:50]]
            for e in all_entries
        ]
        print_table(headers, rows)

    if not unique_names:
        print("\n**No [CONFIDENTIAL: name] tags found.** Either profiles are clean or tags not yet applied.")


if __name__ == "__main__":
    main()
