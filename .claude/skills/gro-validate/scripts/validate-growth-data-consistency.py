"""Validate growth data consistency across GRO profile files."""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import (
    ALL_CHARS, CHAR_DISPLAY, GRO_PROFILE_FILES, MATERIALS, PROFILES, resolve_character,
    list_relationship_files,
)
from platform_lib.markdown_parser import extract_frontmatter, parse_iso_date


REQUIRED_FM_FIELDS = ["character", "domain", "type", "tags", "last_updated", "updated_by", "confidence"]
PSY_BOUNDARY_TERMS = [
    "defense mechanism", "cơ chế phòng vệ", "attachment style", "gắn bó",
    "trauma response", "phản ứng chấn thương", "therapeutic", "trị liệu",
    "DSM", "ICD-11 diagnosis", "personality disorder", "rối loạn nhân cách",
]
VALID_CONFIDENCE = ["high", "medium", "low", "unverified"]
VALID_DOMAINS = ["growth"]
VALID_TYPES = ["data"]


class Finding:
    def __init__(self, check: str, status: str, detail: str, file: str = ""):
        self.check = check
        self.status = status
        self.detail = detail
        self.file = file

    def to_dict(self):
        return {"check": self.check, "status": self.status, "detail": self.detail, "file": self.file}


def validate_frontmatter(slug: str) -> list[Finding]:
    """Check frontmatter schema for all 4 growth files."""
    findings = []
    char_dir = PROFILES / slug

    for rel_path in GRO_PROFILE_FILES:
        fpath = char_dir / rel_path
        if not fpath.exists():
            findings.append(Finding("Frontmatter", "FAIL", f"File missing: {rel_path}", rel_path))
            continue

        fm = extract_frontmatter(fpath)
        if not fm:
            findings.append(Finding("Frontmatter", "FAIL", f"No frontmatter found", rel_path))
            continue

        for field in REQUIRED_FM_FIELDS:
            if field not in fm:
                findings.append(Finding("Frontmatter", "FAIL", f"Missing field: {field}", rel_path))

        if fm.get("character") != slug:
            findings.append(Finding("Frontmatter", "FAIL",
                                    f"character={fm.get('character')}, expected={slug}", rel_path))

        if fm.get("domain") not in VALID_DOMAINS:
            findings.append(Finding("Frontmatter", "FAIL",
                                    f"domain={fm.get('domain')}, expected=growth", rel_path))

        if fm.get("type") not in VALID_TYPES:
            findings.append(Finding("Frontmatter", "WARN",
                                    f"type={fm.get('type')}, expected=data", rel_path))

        if fm.get("confidence") and fm["confidence"] not in VALID_CONFIDENCE:
            findings.append(Finding("Frontmatter", "WARN",
                                    f"Invalid confidence: {fm['confidence']}", rel_path))

        updated_by = fm.get("updated_by", "")
        if updated_by and not updated_by.startswith("gro:"):
            findings.append(Finding("Frontmatter", "WARN",
                                    f"updated_by={updated_by}, expected gro:* prefix", rel_path))

    if not findings:
        findings.append(Finding("Frontmatter", "PASS", "All 4 growth files have valid frontmatter"))

    return findings


def validate_psy_boundary(slug: str) -> list[Finding]:
    """Check that growth files don't contain psychological interpretations."""
    findings = []
    char_dir = PROFILES / slug

    for rel_path in GRO_PROFILE_FILES:
        fpath = char_dir / rel_path
        if not fpath.exists():
            continue

        text = fpath.read_text(encoding="utf-8").lower()
        violations = []
        for term in PSY_BOUNDARY_TERMS:
            if term.lower() in text:
                violations.append(term)

        if violations:
            findings.append(Finding("PSY Boundary", "WARN",
                                    f"PSY terms found: {', '.join(violations[:3])}", rel_path))

    if not findings:
        findings.append(Finding("PSY Boundary", "PASS", "No boundary violations detected"))

    return findings


def validate_evidence_markers(slug: str) -> list[Finding]:
    """Check for proper evidence markers in growth files."""
    findings = []
    char_dir = PROFILES / slug

    for rel_path in GRO_PROFILE_FILES:
        fpath = char_dir / rel_path
        if not fpath.exists():
            continue

        text = fpath.read_text(encoding="utf-8")
        has_source = bool(re.search(r'\[Source:', text))
        has_unverified = "[UNVERIFIED]" in text
        has_limited = "[LIMITED DATA]" in text
        has_private = "[PRIVATE]" in text

        markers = []
        if has_source:
            markers.append("[Source]")
        if has_unverified:
            markers.append("[UNVERIFIED]")
        if has_limited:
            markers.append("[LIMITED DATA]")
        if has_private:
            markers.append("[PRIVATE]")

        if markers:
            findings.append(Finding("Evidence", "PASS",
                                    f"Markers present: {', '.join(markers)}", rel_path))
        else:
            findings.append(Finding("Evidence", "WARN",
                                    "No evidence markers found (expected [Source:], [UNVERIFIED], etc.)",
                                    rel_path))

    return findings


def validate_cross_file_consistency(slug: str) -> list[Finding]:
    """Check consistency across growth files."""
    findings = []
    char_dir = PROFILES / slug

    career_file = char_dir / "growth" / "career-path.md"
    comp_file = char_dir / "growth" / "competencies.md"
    mentoring_file = char_dir / "growth" / "mentoring-map.md"

    if career_file.exists() and comp_file.exists():
        career_text = career_file.read_text(encoding="utf-8").lower()
        comp_text = comp_file.read_text(encoding="utf-8").lower()

        career_mentions_skills = any(kw in career_text for kw in ["skill", "kỹ năng", "competenc"])
        comp_mentions_career = any(kw in comp_text for kw in ["career", "nghề", "role", "vai trò"])

        if career_mentions_skills and comp_mentions_career:
            findings.append(Finding("Cross-file", "PASS",
                                    "Career ↔ Competency cross-references present"))
        else:
            findings.append(Finding("Cross-file", "WARN",
                                    "Weak cross-referencing between career-path and competencies"))

    if mentoring_file.exists():
        mentoring_text = mentoring_file.read_text(encoding="utf-8")
        rel_files = list_relationship_files(slug)
        rel_names = [f.stem for f in rel_files]

        mentioned_in_mentoring = []
        for name in rel_names:
            if name.replace("-", " ") in mentoring_text.lower() or name in mentoring_text.lower():
                mentioned_in_mentoring.append(name)

        if rel_names and mentioned_in_mentoring:
            findings.append(Finding("Cross-file", "PASS",
                                    f"Mentoring map references relationships: {', '.join(mentioned_in_mentoring)}"))
        elif rel_names:
            findings.append(Finding("Cross-file", "WARN",
                                    f"Mentoring map doesn't reference relationship files: {', '.join(rel_names)}"))

    if not findings:
        findings.append(Finding("Cross-file", "PASS", "Cross-file checks passed"))

    return findings


def validate_staleness(slug: str, stale_days: int = 90) -> list[Finding]:
    """Check for stale growth files (>stale_days since last_updated)."""
    findings = []
    char_dir = PROFILES / slug

    from datetime import datetime, timedelta
    now = datetime.now()
    stale_threshold = now - timedelta(days=stale_days)

    for rel_path in GRO_PROFILE_FILES:
        fpath = char_dir / rel_path
        if not fpath.exists():
            continue

        fm = extract_frontmatter(fpath) or {}
        last_updated = fm.get("last_updated", "")
        if isinstance(last_updated, str):
            last_updated = last_updated.strip('"')

        # C1-LIB-10: use canonical parse_iso_date instead of inline strptime
        try:
            d = parse_iso_date(str(last_updated)) if last_updated else None
            if d is None:
                raise ValueError("no date")
            from datetime import datetime as _dt
            updated_dt = _dt(d.year, d.month, d.day)
            if updated_dt < stale_threshold:
                days_old = (now - updated_dt).days
                findings.append(Finding("Staleness", "WARN",
                                        f"Last updated {days_old} days ago ({last_updated})", rel_path))
        except (ValueError, TypeError):
            findings.append(Finding("Staleness", "WARN",
                                    f"Cannot parse last_updated: {last_updated!r}", rel_path))

    if not findings:
        findings.append(Finding("Staleness", "PASS", f"All growth files are current (<{stale_days} days)"))

    return findings


def validate_growth_file_counts() -> list:
    """Assert all 12 growth files (4×3) exist."""
    findings = []
    expected_total = len(GRO_PROFILE_FILES) * len(ALL_CHARS)
    missing = []
    for slug in ALL_CHARS:
        for rel in GRO_PROFILE_FILES:
            if not (PROFILES / slug / rel).exists():
                missing.append(f"{slug}/{rel}")
    if missing:
        findings.append(Finding("File Count", "FAIL",
            f"Expected {expected_total} growth files, missing {len(missing)}: {', '.join(missing)}"))
    else:
        findings.append(Finding("File Count", "PASS",
            f"All {expected_total} growth files present (4×3)"))
    return findings


def validate_character(slug: str, stale_days: int = 90) -> dict:
    """Run all validation checks for one character."""
    all_findings = []
    all_findings.extend(validate_frontmatter(slug))
    all_findings.extend(validate_psy_boundary(slug))
    all_findings.extend(validate_evidence_markers(slug))
    all_findings.extend(validate_cross_file_consistency(slug))
    all_findings.extend(validate_staleness(slug, stale_days=stale_days))

    pass_count = sum(1 for f in all_findings if f.status == "PASS")
    warn_count = sum(1 for f in all_findings if f.status == "WARN")
    fail_count = sum(1 for f in all_findings if f.status == "FAIL")
    total = len(all_findings)
    score = round((pass_count / total) * 100) if total else 0

    return {
        "slug": slug,
        "display": CHAR_DISPLAY.get(slug, slug),
        "pass": pass_count,
        "warn": warn_count,
        "fail": fail_count,
        "score": score,
        "findings": [f.to_dict() for f in all_findings],
    }


def main():
    parser = argparse.ArgumentParser(description="Validate GRO growth data consistency")
    parser.add_argument("--character", "-c", help="Character slug or alias")
    parser.add_argument("--all", dest="all_chars", action="store_true",
                        help="Validate all characters (default when no --character given)")
    parser.add_argument("--json", dest="json_out", action="store_true", help="JSON output")
    parser.add_argument("--fix", action="store_true", help="Include fix suggestions (LLM-only)")
    parser.add_argument("--stale-days", type=int, default=90, dest="stale_days",
                        help="Days threshold for staleness warning (default: 90)")
    args = parser.parse_args()

    chars = [resolve_character(args.character)] if args.character else ALL_CHARS
    file_count_findings = validate_growth_file_counts()
    results = {slug: validate_character(slug, stale_days=args.stale_days) for slug in chars}
    has_fail = any(f.status == "FAIL" for f in file_count_findings)

    if args.json_out:
        output = {
            "file_count": [f.to_dict() for f in file_count_findings],
            "characters": results,
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
        if has_fail:
            sys.exit(1)
        return

    for f in file_count_findings:
        icon = "✓" if f.status == "PASS" else "✗"
        print(f"\n  {icon} {f.check}: {f.detail}")

    print(f"\n{'='*70}")
    print(f"  GRO Validation Report")
    print(f"{'='*70}")

    print(f"\n  {'Character':<12s} {'Pass':<6s} {'Warn':<6s} {'Fail':<6s} {'Score'}")
    print(f"  {'-'*12} {'-'*6} {'-'*6} {'-'*6} {'-'*5}")
    for slug, data in results.items():
        print(f"  {data['display']:<12s} {data['pass']:<6d} {data['warn']:<6d} "
              f"{data['fail']:<6d} {data['score']}/100")

    for slug, data in results.items():
        print(f"\n  {'─'*60}")
        print(f"  {data['display']} — Findings")
        print(f"  {'─'*60}")

        print(f"\n  {'#':<4s} {'Check':<16s} {'Status':<7s} {'File':<28s} Detail")
        print(f"  {'-'*4} {'-'*16} {'-'*7} {'-'*28} {'-'*30}")
        for i, f in enumerate(data["findings"], 1):
            icon = {"PASS": "✓", "WARN": "~", "FAIL": "✗"}.get(f["status"], "?")
            file_str = f["file"][:26] if f["file"] else "—"
            print(f"  {icon} {i:<3d} {f['check']:<16s} {f['status']:<7s} "
                  f"{file_str:<28s} {f['detail'][:50]}")

    if args.fix:
        print(f"\n  {'─'*60}")
        print(f"  Fix suggestions require LLM analysis of findings above.")
        print(f"  Re-run with gro:validate --fix to get LLM-powered suggestions.")

    print(f"\n{'='*70}")
    print(f"  Total: {len(results)} characters validated")
    print(f"{'='*70}")

    if has_fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
