#!/usr/bin/env python3
"""Scan assets/ and framework dirs for privacy violations: tags, PII, clinical terms, locations."""
import json
import os
import sys
import re
import argparse
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))

from platform_lib.clinical_terms import COMPILED_PATTERNS
from platform_lib.paths import ASSETS, ROOT, PRIVACY_AUDIT
from platform_lib.formatters import print_table, severity_badge, eprint

PRIVACY_TAG_PATTERNS = [
    (re.compile(r'\[PRIVATE\]', re.IGNORECASE), "HIGH", "PRIVATE tag"),
    (re.compile(r'\[CONFIDENTIAL\]', re.IGNORECASE), "HIGH", "CONFIDENTIAL tag"),
    (re.compile(r'\[ANONYMIZE\]', re.IGNORECASE), "HIGH", "ANONYMIZE tag"),
    (re.compile(r'\[DRAFT\]', re.IGNORECASE), "MEDIUM", "DRAFT tag"),
    (re.compile(r'\[DO NOT PUBLISH\]', re.IGNORECASE), "HIGH", "DO NOT PUBLISH tag"),
]

LOCATION_PATTERNS = [
    re.compile(r'\bQuảng\s+Bình\b', re.IGNORECASE),
    re.compile(r'\bBách\s+Khoa\b', re.IGNORECASE),
    re.compile(r'\bĐHBK\b'),
    re.compile(r'\bOne\s+Mount\b', re.IGNORECASE),
    re.compile(r'\bVietSeeds\b', re.IGNORECASE),
]

PII_PATTERNS = [
    (re.compile(r'\b0[35789]\d{8}\b'), "HIGH", "Vietnamese phone"),
    (re.compile(r'[\w.+-]+@[\w-]+\.[\w.]+'), "HIGH", "email address"),
    (re.compile(r'\b0\d{11}\b'), "HIGH", "Vietnamese CCCD"),
]

DSM_ICD_PATTERN = re.compile(r'\b[FG]\d{2}(?:\.\d{1,2})?\b')

CLINICAL_EXPECTED_DIRS = ("psychology/", "references/")

CROSS_FRAMEWORK_DIRS = [
    str(ASSETS),
    str(ROOT / "docs" / "profiles"),
    str(ROOT / "docs" / "materials"),
    str(ROOT / "docs" / "graph"),
]

AUDIT_LOG = PRIVACY_AUDIT  # consolidated telemetry sink

SCAN_EXTENSIONS = {".md", ".txt", ".text"}


def _in_clinical_expected(fpath: Path) -> bool:
    """Check if file is in a directory where clinical/DSM terms are expected."""
    s = str(fpath)
    return any(d in s for d in CLINICAL_EXPECTED_DIRS)


def scan_file(fpath: Path, rel_base: Path) -> list[list[str]]:
    violations = []
    try:
        lines = fpath.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return violations
    rel = str(fpath.relative_to(rel_base))
    in_clinical_zone = _in_clinical_expected(fpath)

    for i, line_text in enumerate(lines, 1):
        for pat, sev, label in PRIVACY_TAG_PATTERNS:
            if pat.search(line_text):
                violations.append([
                    severity_badge(sev), rel, str(i), label,
                    line_text.strip()[:60],
                ])

        for ppat, psev, plabel in PII_PATTERNS:
            if ppat.search(line_text):
                violations.append([
                    severity_badge(psev), rel, str(i), f"pii: {plabel}",
                    line_text.strip()[:60],
                ])

        if not in_clinical_zone:
            for cpat in COMPILED_PATTERNS:
                for m in cpat.finditer(line_text):
                    violations.append([
                        severity_badge("MEDIUM"), rel, str(i), f"clinical: {m.group()}",
                        line_text.strip()[:60],
                    ])
                    break

            if DSM_ICD_PATTERN.search(line_text):
                violations.append([
                    severity_badge("HIGH"), rel, str(i), "DSM/ICD code leak",
                    line_text.strip()[:60],
                ])

        for lpat in LOCATION_PATTERNS:
            if lpat.search(line_text):
                violations.append([
                    severity_badge("LOW"), rel, str(i), f"location: {lpat.pattern}",
                    line_text.strip()[:60],
                ])
                break

    return violations


def scan_dirs(dirs: list[str], severity_filter: str = "all") -> tuple[list[list[str]], int]:
    """Scan multiple directories, return (violations, files_scanned)."""
    all_violations: list[list[str]] = []
    files_scanned = 0
    for d in dirs:
        scan_root = Path(d)
        if not scan_root.exists():
            eprint(f"[WARN] Directory not found, skipping: {scan_root}")
            continue
        for fpath in sorted(scan_root.rglob("*")):
            if fpath.suffix.lower() not in SCAN_EXTENSIONS:
                continue
            files_scanned += 1
            all_violations.extend(scan_file(fpath, scan_root))

    if severity_filter != "all":
        badge = severity_badge(severity_filter)
        all_violations = [v for v in all_violations if v[0] == badge]
    return all_violations, files_scanned


def append_audit_log(dirs: list[str], files_scanned: int, violations: list[list[str]]) -> None:
    """Append one JSONL line to the audit log."""
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    high = sum(1 for v in violations if v[0] == severity_badge("HIGH"))
    med = sum(1 for v in violations if v[0] == severity_badge("MEDIUM"))
    low = sum(1 for v in violations if v[0] == severity_badge("LOW"))
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scan_scope": dirs,
        "files_scanned": files_scanned,
        "findings_count": len(violations),
        "critical": high,
        "high": high,
        "medium": med,
        "low": low,
        "operator": "cre:privacy-guard",
    }
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Scan assets/framework dirs for privacy violations"
    )
    parser.add_argument("--dir", default=None, help="Single directory to scan (legacy)")
    parser.add_argument("--dirs", nargs="+", default=None, help="Multiple directories to scan")
    parser.add_argument("--cross-framework", action="store_true",
                        help="Scan assets/ + docs/profiles/ + docs/materials/ + docs/graph/")
    parser.add_argument("--audit-log", action="store_true", help="Append summary to JSONL audit log")
    parser.add_argument(
        "--severity", choices=["HIGH", "MEDIUM", "LOW", "all"], default="all",
        help="Filter by severity"
    )
    args = parser.parse_args()

    if args.cross_framework:
        dirs = CROSS_FRAMEWORK_DIRS
    elif args.dirs:
        dirs = args.dirs
    elif args.dir:
        dirs = [args.dir]
    else:
        dirs = [str(ASSETS)]

    all_violations, files_scanned = scan_dirs(dirs, args.severity)

    headers = ["Severity", "File", "Line", "Violation", "Context"]
    print_table(headers, all_violations)

    high = sum(1 for v in all_violations if v[0] == severity_badge("HIGH"))
    med = sum(1 for v in all_violations if v[0] == severity_badge("MEDIUM"))
    low = sum(1 for v in all_violations if v[0] == severity_badge("LOW"))
    eprint(f"[OK] {files_scanned} files scanned, {len(all_violations)} violations — HIGH={high} MEDIUM={med} LOW={low}")

    if args.audit_log:
        append_audit_log(dirs, files_scanned, all_violations)
        eprint(f"[LOG] Appended to {AUDIT_LOG}")

    if high > 0:
        sys.exit(2)


if __name__ == "__main__":
    main()
