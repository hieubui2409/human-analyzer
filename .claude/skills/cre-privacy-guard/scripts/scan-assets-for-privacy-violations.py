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
from platform_lib.privacy_tags import load_confidential_names

# Load project-specific forbidden tokens (display names + pii_extra like org/program names)
# from the shared roster source. Returns [] when the roster is absent (toolkit-only pack),
# so the scanner degrades gracefully to generic pattern detection only.
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools" / "anonymize"))
try:
    from pii_tokens import tokens_only as _pii_tokens_only
    _PROJECT_SPECIFIC_TOKENS: list[str] = _pii_tokens_only()
except ImportError:
    _PROJECT_SPECIFIC_TOKENS = []

# Rule-09 privacy tags — leaking any of these into published content is a CRITICAL breach.
# CONFIDENTIAL carries an optional ": {person}" payload (the real grammar in the corpus),
# so the regex must match both the bare and the named form.
PRIVACY_TAG_PATTERNS = [
    (re.compile(r'\[PRIVATE\]', re.IGNORECASE), "CRITICAL", "PRIVATE tag"),
    (re.compile(r'\[CONFIDENTIAL(?::[^\]]*)?\]', re.IGNORECASE), "CRITICAL", "CONFIDENTIAL tag"),
    (re.compile(r'\[ANONYMIZE\]', re.IGNORECASE), "CRITICAL", "ANONYMIZE tag"),
    # Publication-readiness markers — not Rule-09 privacy tags, but finding them inside a
    # published asset means unpublishable content leaked, so the guard still flags them.
    (re.compile(r'\[DO NOT PUBLISH\]', re.IGNORECASE), "HIGH", "DO NOT PUBLISH tag"),
    (re.compile(r'\[DRAFT\]', re.IGNORECASE), "MEDIUM", "DRAFT tag"),
]

# Non-character org/location tokens that are corpus-constant (not roster-derived):
# Bách Khoa, ĐHBK, One Mount are institution names out of scope for the PII roster
# but still worth flagging in assets as identity-adjacent location/org signals.
_STATIC_LOCATION_PATTERNS = [
    re.compile(r'\bBách\s+Khoa\b', re.IGNORECASE),
    re.compile(r'\bĐHBK\b'),
    re.compile(r'\bOne\s+Mount\b', re.IGNORECASE),
]

# Project-specific tokens from the roster (display names + pii_extra) as compiled patterns.
# When the roster is absent, _PROJECT_SPECIFIC_TOKENS is [] and this list is empty.
_ROSTER_LOCATION_PATTERNS = [
    re.compile(rf'(?<!\w){re.escape(tok)}(?!\w)', re.IGNORECASE)
    for tok in _PROJECT_SPECIFIC_TOKENS
    if len(tok) >= 2
]

LOCATION_PATTERNS = _STATIC_LOCATION_PATTERNS + _ROSTER_LOCATION_PATTERNS

# C1-CRE-08: Vietnamese phone (10-digit, starts 03/05/07/08/09) checked BEFORE CCCD.
# CCCD is any 12-digit number. Checked in order longest-match: phone first (10-digit
# is a strict subset of possible 12-digit strings, but word-boundary anchors separate
# them). Keeping phone first avoids double-fire on strings like "0987654321xx".
PII_PATTERNS = [
    (re.compile(r'\b0[35789]\d{8}\b'), "HIGH", "Vietnamese phone"),
    (re.compile(r'[\w.+-]+@[\w-]+\.[\w.]+'), "HIGH", "email address"),
    # C1-CRE-08: real 12-digit CCCD starts with province code (001-096), not 0-prefix.
    # Previous pattern \b0\d{11}\b was wrong (required leading 0). Fixed to \b\d{12}\b.
    (re.compile(r'\b\d{12}\b'), "HIGH", "Vietnamese CCCD"),
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


def _in_assets(fpath: Path) -> bool:
    """Published content lives under assets/ — only there is a real-name appearance a leak."""
    try:
        fpath.resolve().relative_to(ASSETS.resolve())
        return True
    except ValueError:
        return False


def _build_name_patterns(names: set[str]) -> list[tuple[re.Pattern, str]]:
    """Word-boundary matchers for each Rule-09 confidential person name."""
    pats = []
    for name in sorted(names):
        cleaned = name.strip()
        if len(cleaned) < 2:
            continue  # too short to match safely
        pats.append((re.compile(rf'(?<!\w){re.escape(cleaned)}(?!\w)', re.IGNORECASE), cleaned))
    return pats


def scan_file(fpath: Path, rel_base: Path,
              name_patterns: list[tuple[re.Pattern, str]] | None = None) -> list[list[str]]:
    violations = []
    try:
        lines = fpath.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return violations
    rel = str(fpath.relative_to(rel_base))
    in_clinical_zone = _in_clinical_expected(fpath)
    # Real-name leak detection applies only to published assets; profiles/materials are
    # expected to contain these names verbatim (that is where the tags are authored).
    check_names = bool(name_patterns) and _in_assets(fpath)

    for i, line_text in enumerate(lines, 1):
        for pat, sev, label in PRIVACY_TAG_PATTERNS:
            if pat.search(line_text):
                violations.append([
                    severity_badge(sev), rel, str(i), label,
                    line_text.strip()[:60],
                ])

        if check_names:
            for npat, person in name_patterns:
                if npat.search(line_text):
                    violations.append([
                        severity_badge("CRITICAL"), rel, str(i),
                        f"confidential-name leak: {person}",
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


def scan_dirs(dirs: list[str], severity_filter: str = "all",
              check_name_leaks: bool = True) -> tuple[list[list[str]], int]:
    """Scan multiple directories, return (violations, files_scanned)."""
    name_patterns = _build_name_patterns(load_confidential_names()) if check_name_leaks else None
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
            all_violations.extend(scan_file(fpath, scan_root, name_patterns))

    if severity_filter != "all":
        badge = severity_badge(severity_filter)
        all_violations = [v for v in all_violations if v[0] == badge]
    return all_violations, files_scanned


def append_audit_log(dirs: list[str], files_scanned: int, violations: list[list[str]]) -> None:
    """Append one JSONL line to the audit log."""
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    crit = sum(1 for v in violations if v[0] == severity_badge("CRITICAL"))
    high = sum(1 for v in violations if v[0] == severity_badge("HIGH"))
    med = sum(1 for v in violations if v[0] == severity_badge("MEDIUM"))
    low = sum(1 for v in violations if v[0] == severity_badge("LOW"))
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scan_scope": dirs,
        "files_scanned": files_scanned,
        "findings_count": len(violations),
        "critical": crit,
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
        "--severity", choices=["CRITICAL", "HIGH", "MEDIUM", "LOW", "all"], default="all",
        help="Filter by severity"
    )
    parser.add_argument("--no-name-leak-check", action="store_true",
                        help="Skip loading [CONFIDENTIAL: name] profile names (faster, tags-only)")
    args = parser.parse_args()

    if args.cross_framework:
        dirs = CROSS_FRAMEWORK_DIRS
    elif args.dirs:
        dirs = args.dirs
    elif args.dir:
        dirs = [args.dir]
    else:
        dirs = [str(ASSETS)]

    all_violations, files_scanned = scan_dirs(
        dirs, args.severity, check_name_leaks=not args.no_name_leak_check)

    headers = ["Severity", "File", "Line", "Violation", "Context"]
    print_table(headers, all_violations)

    crit = sum(1 for v in all_violations if v[0] == severity_badge("CRITICAL"))
    high = sum(1 for v in all_violations if v[0] == severity_badge("HIGH"))
    med = sum(1 for v in all_violations if v[0] == severity_badge("MEDIUM"))
    low = sum(1 for v in all_violations if v[0] == severity_badge("LOW"))
    eprint(f"[OK] {files_scanned} files scanned, {len(all_violations)} violations — "
           f"CRITICAL={crit} HIGH={high} MEDIUM={med} LOW={low}")

    if args.audit_log:
        append_audit_log(dirs, files_scanned, all_violations)
        eprint(f"[LOG] Appended to {AUDIT_LOG}")

    # Exit non-zero on any CRITICAL (Rule-09 leak) or HIGH finding — gates the publish pipeline.
    if crit > 0 or high > 0:
        sys.exit(2)


if __name__ == "__main__":
    main()
