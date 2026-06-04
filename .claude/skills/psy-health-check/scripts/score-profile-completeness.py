"""Score completeness of character profiles against the 25-file universal nested structure."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import ALL_CHARS, CHAR_DISPLAY, PROFILE_FILES, PROFILES, resolve_character, list_relationship_files


# Sections expected per file category (H2 markers to check)
EXPECTED_SECTIONS = {
    "INDEX.md": ["Character Overview", "Quick Reference", "Profile"],
    "CURRENT-STATE.md": ["Current State", "Status", "Assessment"],
    "milestones.md": ["Milestone", "Key Event"],
    "identity/core.md": ["Basic Info", "Education", "Career", "Family"],
    "identity/writing-voice.md": ["Tone", "Voice", "Style", "Theme"],
    "identity/achievements.md": ["Achievement", "Award", "Scholarship"],
    "identity/media-coverage.md": ["Media", "Press", "Coverage"],
    "psychology/core-wounds.md": ["Core Wound", "Wound Pattern"],
    "psychology/defense-mechanisms.md": ["Defense", "Mechanism", "Mature", "Neurotic"],
    "psychology/attachment-style.md": ["Attachment", "Style", "Pattern"],
    "psychology/growth-edges.md": ["Growth", "Edge", "Window"],
    "psychology/formulation.md": ["Presenting Problem", "Predisposing", "Precipitating", "Perpetuating"],
    "psychology/diagnostics.md": ["Big Five", "ICD", "Score", "Diagnostic"],
    "psychology/cultural-formulation.md": ["Cultural", "Context", "Factor"],
    "psychology/archetype.md": ["Archetype", "Jungian", "Shadow"],
    "relationships/family.md": ["Family", "Parent", "Relationship"],
    "timeline/overview.md": ["Timeline", "Event", "Date"],
    "timeline/state-timeline.md": ["Phase", "State", "Period"],
    "darkness/traumas.md": ["Trauma", "Event", "Impact"],
    "light/strengths-hope.md": ["Strength", "Hope", "Resilience"],
    "evidence/conversations.md": ["Conversation", "Evidence", "Quote"],
    "growth/career-path.md": ["Career Stage", "Role Salience", "Key Decisions"],
    "growth/competencies.md": ["Technical Skills", "Soft Skills", "Domain Knowledge"],
    "growth/learning-profile.md": ["Dominant Learning Style", "Cycle Strengths"],
    "growth/mentoring-map.md": ["Mentoring Relationships", "Career Functions"],
}

# Category groupings for display
CATEGORIES = {
    "Core": ["INDEX.md", "CURRENT-STATE.md", "milestones.md"],
    "Identity": ["identity/core.md", "identity/writing-voice.md",
                 "identity/achievements.md", "identity/media-coverage.md"],
    "Psychology": ["psychology/core-wounds.md", "psychology/defense-mechanisms.md",
                   "psychology/attachment-style.md", "psychology/growth-edges.md",
                   "psychology/formulation.md", "psychology/diagnostics.md",
                   "psychology/cultural-formulation.md", "psychology/archetype.md"],
    "Relationships": ["relationships/family.md"],
    "Timeline": ["timeline/overview.md", "timeline/state-timeline.md"],
    "Darkness/Light": ["darkness/traumas.md", "light/strengths-hope.md"],
    "Evidence": ["evidence/conversations.md"],
    "Growth": ["growth/career-path.md", "growth/competencies.md",
               "growth/learning-profile.md", "growth/mentoring-map.md"],
}

GRADE_MAP = [(95, "A+"), (90, "A"), (85, "A-"), (80, "B+"), (75, "B"),
             (70, "B-"), (65, "C+"), (60, "C"), (50, "D"), (0, "F")]


def validate_file_counts() -> dict:
    """Assert all 75 profile files (25×3) exist."""
    expected_per_char = len(PROFILE_FILES)
    expected_total = expected_per_char * len(ALL_CHARS)
    missing = []
    for slug in ALL_CHARS:
        for rel in PROFILE_FILES:
            if not (PROFILES / slug / rel).exists():
                missing.append(f"{slug}/{rel}")
    return {
        "expected": expected_total,
        "actual": expected_total - len(missing),
        "missing": missing,
        "pass": len(missing) == 0,
    }


def grade(score: float) -> str:
    for threshold, letter in GRADE_MAP:
        if score >= threshold:
            return letter
    return "F"


def score_file(char_dir: Path, rel_path: str) -> tuple[int, int, str]:
    """Return (score, line_count, status_label)."""
    fp = char_dir / rel_path
    if not fp.exists():
        return 0, 0, "MISSING"
    text = fp.read_text(encoding="utf-8")
    lines = [l for l in text.splitlines() if l.strip()]
    n = len(lines)
    if n == 0:
        # Empty file contributes nothing to completeness — score 0 so present/missing
        # tallies (score > 0) don't count it as a developed file (status still flags EMPTY).
        return 0, 0, "EMPTY"

    base = 40 if n < 50 else (70 if n < 100 else 90)

    # Check for expected H2 sections
    h2_found = sum(
        1 for kw in EXPECTED_SECTIONS.get(rel_path, [])
        if any(kw.lower() in line.lower() for line in lines[:60])
    )
    bonus = min(10, h2_found * 3)
    score = min(100, base + bonus)

    status = "Complete" if score >= 90 else ("Good" if score >= 70 else ("Thin" if score >= 40 else "Minimal"))
    return score, n, status


def assess_character(slug: str) -> dict:
    char_dir = PROFILES / slug
    files = []
    for rel in PROFILE_FILES:
        score, lines, status = score_file(char_dir, rel)
        files.append({
            "file": rel,
            "score": score,
            "lines": lines,
            "status": status,
        })

    # Score cross-relationship files (bonus, not penalized if missing)
    cross_rel_files = list_relationship_files(slug)
    for fpath in cross_rel_files:
        rel_path = f"relationships/{fpath.name}"
        score, lines, status = score_file(char_dir, rel_path)
        files.append({
            "file": rel_path,
            "score": score,
            "lines": lines,
            "status": status,
        })

    base_count = len(PROFILE_FILES)
    present = sum(1 for f in files if f["score"] > 0)
    overall = round(sum(f["score"] for f in files) / len(files)) if files else 0
    return {
        "slug": slug,
        "display": CHAR_DISPLAY.get(slug, slug),
        "overall": overall,
        "grade": grade(overall),
        "files_present": present,
        "files_total": len(files),
        "files_base": base_count,
        "files_cross_rel": len(cross_rel_files),
        "files_missing": base_count - sum(1 for f in files[:base_count] if f["score"] > 0),
        "files": files,
    }


def main():
    parser = argparse.ArgumentParser(description="Score character profile completeness")
    parser.add_argument("--character", "-c", help="Character slug or alias")
    parser.add_argument("--all", action="store_true", help="Score all characters (default)")
    parser.add_argument("--gaps-only", action="store_true", help="Show only files with score < 80")
    parser.add_argument("--json", dest="json_out", action="store_true", help="JSON output")
    args = parser.parse_args()

    chars = [resolve_character(args.character)] if args.character else ALL_CHARS
    file_count = validate_file_counts()
    assessments = [assess_character(slug) for slug in chars]
    has_fail = not file_count["pass"]

    if args.json_out:
        output = {"file_count_assertion": file_count, "assessments": assessments}
        print(json.dumps(output, indent=2, ensure_ascii=False))
        if has_fail:
            sys.exit(1)
        return

    if file_count["pass"]:
        print(f"\n  ✓ File count assertion PASS: {file_count['actual']}/{file_count['expected']} files present")
    else:
        print(f"\n  ✗ File count assertion FAIL: {file_count['actual']}/{file_count['expected']} files present")
        for m in file_count["missing"]:
            print(f"    Missing: {m}")

    print(f"\n{'='*70}")
    print("  Profile Health Report")
    print(f"{'='*70}")
    print()

    # Overall table
    print(f"  {'Character':<12s} {'Score':<8s} {'Present':<10s} {'Missing':<8s} {'Grade'}")
    print(f"  {'-'*12} {'-'*8} {'-'*10} {'-'*8} {'-'*5}")
    for a in assessments:
        total_str = f"{a['files_present']}/{a['files_total']}"
        print(f"  {a['display']:<12s} {a['overall']}/100   {total_str:<10s}  "
              f"{a['files_missing']:<8d} {a['grade']}")

    # Per-character detail
    for a in assessments:
        print(f"\n  {'─'*60}")
        print(f"  {a['display']} — Completeness Matrix")
        print(f"  {'─'*60}")

        for cat_name, cat_files in CATEGORIES.items():
            cat_items = [f for f in a["files"] if f["file"] in cat_files]
            if not cat_items:
                continue
            show = [f for f in cat_items if not args.gaps_only or f["score"] < 80]
            if not show:
                continue
            print(f"\n  [{cat_name}]")
            print(f"  {'File':<38s} {'Score':<7s} {'Lines':<7s} Status")
            print(f"  {'-'*38} {'-'*7} {'-'*7} {'-'*10}")
            for f in show:
                lines_str = str(f["lines"]) if f["lines"] else "—"
                print(f"  {f['file']:<38s} {f['score']:<7d} {lines_str:<7s} {f['status']}")

    # Gap summary
    all_gaps = []
    for a in assessments:
        for f in a["files"]:
            if f["score"] < 80:
                all_gaps.append((f["score"], a["display"], f["file"], f["status"]))
    all_gaps.sort()

    if all_gaps:
        print(f"\n  {'─'*60}")
        print(f"  Priority Gaps ({len(all_gaps)} files below 80)")
        print(f"  {'─'*60}")
        for score, display, fpath, status in all_gaps[:10]:
            print(f"  {display}/{fpath} — {status} (score={score})")
        if len(all_gaps) > 10:
            print(f"  ... and {len(all_gaps) - 10} more")
        print(f"\n  Next step: use `psy:wave` to fill gaps systematically")
    else:
        print(f"\n  All profile files score 80+. Profiles are well-developed.")

    if has_fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
