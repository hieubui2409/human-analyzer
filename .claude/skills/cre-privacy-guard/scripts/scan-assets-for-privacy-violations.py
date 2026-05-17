#!/usr/bin/env python3
"""Scan assets/ for privacy violations: tags, restricted names, clinical terms, locations."""
import os
import sys
import re
import argparse
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))

from platform_lib.clinical_terms import COMPILED_PATTERNS
from platform_lib.paths import ASSETS
from platform_lib.formatters import print_table, severity_badge, eprint

# Privacy tags that must not appear in published assets
PRIVACY_TAG_PATTERNS = [
    (re.compile(r'\[PRIVATE\]', re.IGNORECASE), "HIGH", "PRIVATE tag"),
    (re.compile(r'\[CONFIDENTIAL\]', re.IGNORECASE), "HIGH", "CONFIDENTIAL tag"),
    (re.compile(r'\[ANONYMIZE\]', re.IGNORECASE), "HIGH", "ANONYMIZE tag"),
    (re.compile(r'\[DRAFT\]', re.IGNORECASE), "MEDIUM", "DRAFT tag"),
    (re.compile(r'\[DO NOT PUBLISH\]', re.IGNORECASE), "HIGH", "DO NOT PUBLISH tag"),
]

# Protected location references (specific enough to be identifying)
LOCATION_PATTERNS = [
    re.compile(r'\bQuảng\s+Bình\b', re.IGNORECASE),
    re.compile(r'\bBách\s+Khoa\b', re.IGNORECASE),
    re.compile(r'\bĐHBK\b'),
    re.compile(r'\bOne\s+Mount\b', re.IGNORECASE),
    re.compile(r'\bVietSeeds\b', re.IGNORECASE),
]

SCAN_EXTENSIONS = {".md", ".txt", ".text"}


def scan_file(fpath: Path, rel_base: Path) -> list[list[str]]:
    violations = []
    try:
        lines = fpath.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return violations
    rel = str(fpath.relative_to(rel_base))

    for i, line_text in enumerate(lines, 1):
        # Privacy tags
        for pat, sev, label in PRIVACY_TAG_PATTERNS:
            if pat.search(line_text):
                violations.append([
                    severity_badge(sev), rel, str(i), label,
                    line_text.strip()[:60],
                ])

        # Raw clinical terms in published content
        for cpat in COMPILED_PATTERNS:
            for m in cpat.finditer(line_text):
                violations.append([
                    severity_badge("MEDIUM"), rel, str(i), f"clinical: {m.group()}",
                    line_text.strip()[:60],
                ])
                break  # one violation per line per pattern is enough

        # Protected locations
        for lpat in LOCATION_PATTERNS:
            if lpat.search(line_text):
                violations.append([
                    severity_badge("LOW"), rel, str(i), f"location: {lpat.pattern}",
                    line_text.strip()[:60],
                ])
                break

    return violations


def main():
    parser = argparse.ArgumentParser(
        description="Scan assets dir for privacy violations before publishing"
    )
    parser.add_argument("--dir", default=str(ASSETS), help="Directory to scan (default: assets/)")
    parser.add_argument(
        "--severity", choices=["HIGH", "MEDIUM", "LOW", "all"], default="all",
        help="Filter by severity"
    )
    args = parser.parse_args()

    scan_root = Path(args.dir)
    if not scan_root.exists():
        eprint(f"[ERR] Directory not found: {scan_root}")
        sys.exit(1)

    all_violations: list[list[str]] = []
    for fpath in sorted(scan_root.rglob("*")):
        if fpath.suffix.lower() not in SCAN_EXTENSIONS:
            continue
        all_violations.extend(scan_file(fpath, scan_root))

    if args.severity != "all":
        badge = severity_badge(args.severity)
        all_violations = [v for v in all_violations if v[0] == badge]

    headers = ["Severity", "File", "Line", "Violation", "Context"]
    print_table(headers, all_violations)

    high = sum(1 for v in all_violations if v[0] == severity_badge("HIGH"))
    med = sum(1 for v in all_violations if v[0] == severity_badge("MEDIUM"))
    low = sum(1 for v in all_violations if v[0] == severity_badge("LOW"))
    eprint(f"[OK] {len(all_violations)} violations — HIGH={high} MEDIUM={med} LOW={low}")
    if high > 0:
        sys.exit(2)  # Non-zero exit for HIGH violations to block publishing pipelines


if __name__ == "__main__":
    main()
