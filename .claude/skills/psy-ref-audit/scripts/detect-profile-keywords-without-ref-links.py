#!/usr/bin/env python3
"""Detect clinical/psychological keywords in profiles that appear as plain text
(not markdown links) — helps distinguish real missing refs from normal keyword usage.

Outputs: keyword, file, line_no, context, has_ref_file, is_linked
"""
import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.paths import ALL_CHARS, CHAR_DISPLAY, character_dir, REFERENCES, resolve_character
from platform_lib.clinical_terms import build_reference_index, scan_file_for_clinical_terms
from platform_lib.formatters import print_table, print_json, eprint

LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')


def scan_profile_for_unlinked_terms(char: str, ref_index: dict) -> list[dict]:
    slug = resolve_character(char)
    display = CHAR_DISPLAY[slug]
    cdir = character_dir(slug)
    if not cdir.exists():
        return []
    results = []
    for f in sorted(cdir.rglob("*.md")):
        content = f.read_text(encoding="utf-8", errors="replace")
        lines = content.split("\n")
        linked_refs = set()
        for m in LINK_PATTERN.finditer(content):
            href = m.group(2)
            linked_refs.add(Path(href).stem.lower())

        for theory_name, ref_data in ref_index.items():
            ref_stem = Path(ref_data["file"]).stem.lower()
            for term in ref_data.get("key_terms", []):
                if len(term) < 6:
                    continue
                for i, line in enumerate(lines):
                    if re.search(r'\b' + re.escape(term) + r'\b', line, re.IGNORECASE):
                        in_link = bool(re.search(
                            r'\[[^\]]*' + re.escape(term) + r'[^\]]*\]\(',
                            line, re.IGNORECASE
                        ))
                        results.append({
                            "character": display,
                            "file": f.relative_to(cdir).as_posix(),
                            "line": i + 1,
                            "term": term,
                            "theory": theory_name[:50],
                            "is_linked": in_link,
                            "has_ref_file": (REFERENCES / ref_data["file"]).exists(),
                            "context": line.strip()[:80],
                        })
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Detect profile keywords without ref links (gathering only)")
    parser.add_argument("--char", help="Character slug or name")
    parser.add_argument("--all", action="store_true", help="All characters")
    parser.add_argument("--unlinked-only", action="store_true",
                        help="Only show terms NOT in markdown links")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    ref_index = build_reference_index(REFERENCES)
    chars = ALL_CHARS if args.all else ([args.char] if args.char else ALL_CHARS)

    all_results = []
    for c in chars:
        all_results.extend(scan_profile_for_unlinked_terms(c, ref_index))

    if args.unlinked_only:
        all_results = [r for r in all_results if not r["is_linked"]]

    if args.json:
        print_json(all_results[:100])
    else:
        linked = sum(1 for r in all_results if r["is_linked"])
        unlinked = sum(1 for r in all_results if not r["is_linked"])
        eprint(f"[OK] {len(all_results)} term hits: {linked} linked, {unlinked} unlinked (plain text)")
        rows = [[r["character"], r["file"], str(r["line"]), r["term"][:25],
                 "Y" if r["is_linked"] else "N", r["context"][:50]]
                for r in all_results[:50]]
        print_table(["Char", "File", "Line", "Term", "Linked?", "Context"], rows)


if __name__ == "__main__":
    main()
