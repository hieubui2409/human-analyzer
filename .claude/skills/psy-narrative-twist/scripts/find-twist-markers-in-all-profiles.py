#!/usr/bin/env python3
"""Grep all profile files for twist/disputed/uncertain markers and output a table."""
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.paths import ALL_CHARS, CHAR_DISPLAY, character_dir, PROFILE_FILES
from platform_lib.formatters import print_table

MARKER_PATTERN = re.compile(
    r'(⚠️\s*TWIST|⚠TWIST|\[DISPUTED[^\]]*\]|\[UNCERTAIN[^\]]*\]|\[TWIST[^\]]*\])',
    re.IGNORECASE
)

MARKER_TYPE_MAP = {
    'twist': 'TWIST',
    'disputed': 'DISPUTED',
    'uncertain': 'UNCERTAIN',
}


def classify_marker(raw: str) -> str:
    r = raw.lower()
    for k, v in MARKER_TYPE_MAP.items():
        if k in r:
            return v
    return 'OTHER'


def scan_profiles() -> list[dict]:
    results = []
    for slug in ALL_CHARS:
        display = CHAR_DISPLAY.get(slug, slug)
        cdir = character_dir(slug)
        for fname in PROFILE_FILES:
            fpath = cdir / fname
            if not fpath.exists():
                continue
            lines = fpath.read_text(encoding='utf-8').splitlines()
            for lineno, line in enumerate(lines, 1):
                for m in MARKER_PATTERN.finditer(line):
                    context = line.strip()[:100]
                    results.append({
                        'character': display,
                        'file': fname,
                        'line': lineno,
                        'marker_type': classify_marker(m.group()),
                        'raw_marker': m.group()[:40],
                        'content': context,
                    })
    return results


def main():
    hits = scan_profiles()
    if not hits:
        print("No twist/disputed/uncertain markers found in any profile files.")
        return

    print(f"\n## Narrative Twist Markers ({len(hits)} found)\n")
    headers = ["Character", "File", "Line", "Type", "Content"]
    rows = [
        [h['character'], h['file'], str(h['line']), h['marker_type'], h['content']]
        for h in hits
    ]
    print_table(headers, rows)


if __name__ == "__main__":
    main()
