#!/usr/bin/env python3
"""Find where a given fact string appears across profile files."""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.paths import ALL_CHARS, CHAR_DISPLAY, character_dir, PROFILE_FILES, resolve_character
from platform_lib.formatters import print_table


def search_fact(fact: str, char_slugs: list) -> list[dict]:
    results = []
    fact_lower = fact.lower()
    for slug in char_slugs:
        display = CHAR_DISPLAY.get(slug, slug)
        cdir = character_dir(slug)
        for fname in PROFILE_FILES:
            fpath = cdir / fname
            if not fpath.exists():
                continue
            lines = fpath.read_text(encoding='utf-8').splitlines()
            for lineno, line in enumerate(lines, 1):
                if fact_lower in line.lower():
                    results.append({
                        'character': display,
                        'file': fname,
                        'line': lineno,
                        'context': line.strip()[:120],
                    })
    return results


def main():
    parser = argparse.ArgumentParser(description="Find where a fact appears across profile files")
    parser.add_argument("--fact", required=True, help="Fact string to search for")
    parser.add_argument("--character", default=None, help="Limit to one character (or omit for all)")
    args = parser.parse_args()

    if args.character:
        slug = resolve_character(args.character)
        char_slugs = [slug]
    else:
        char_slugs = ALL_CHARS

    hits = search_fact(args.fact, char_slugs)

    scope = args.character or "all characters"
    print(f"\n## Fact Scope: \"{args.fact}\" in {scope}\n")
    if not hits:
        print("_No occurrences found._")
        return

    print(f"Found in **{len(hits)}** location(s):\n")
    headers = ["Character", "File", "Line", "Context"]
    rows = [[h['character'], h['file'], str(h['line']), h['context']] for h in hits]
    print_table(headers, rows)


if __name__ == "__main__":
    main()
