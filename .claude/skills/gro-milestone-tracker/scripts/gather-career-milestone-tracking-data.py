"""Gather career milestones from milestones.md and career-path.md for tracking."""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import ALL_CHARS, CHAR_DISPLAY, PROFILES, resolve_character
from platform_lib.markdown_parser import extract_sections, extract_frontmatter


STATUS_PATTERNS = {
    "achieved": re.compile(r'✅|achieved|đạt được|hoàn thành|completed', re.IGNORECASE),
    "planned": re.compile(r'🔄|planned|dự kiến|kế hoạch|target|mục tiêu', re.IGNORECASE),
    "missed": re.compile(r'❌|missed|bỏ lỡ|thất bại|failed', re.IGNORECASE),
    "in_progress": re.compile(r'🔶|in.progress|đang|ongoing|current', re.IGNORECASE),
}


def _is_table_header_or_separator(col1: str) -> bool:
    """Check if a table row is a header or separator line."""
    stripped = col1.strip().strip("*").lower()
    if all(c in "-: " for c in stripped):
        return True
    header_terms = {"field", "description", "milestone", "mốc", "sự kiện",
                    "event", "date", "period", "status", "giai đoạn",
                    "năm", "tuổi", "insight", "câu hỏi", "nguồn gốc", "ý nghĩa"}
    return stripped in header_terms


def parse_milestone_table(text: str) -> list[dict]:
    """Parse milestone table rows from markdown (line-by-line to avoid cross-line matching)."""
    milestones = []
    row_pattern = re.compile(r'\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|')

    for line in text.splitlines():
        match = row_pattern.search(line)
        if not match:
            continue

        col1 = match.group(1).strip().strip("*")
        col2 = match.group(2).strip()
        col3 = match.group(3).strip()

        if _is_table_header_or_separator(col1):
            continue

        status = "unknown"
        full_text = f"{col1} {col2} {col3}"
        for status_name, pattern in STATUS_PATTERNS.items():
            if pattern.search(full_text):
                status = status_name
                break

        milestones.append({
            "description": col1[:60],
            "date_or_period": col2[:30],
            "detail": col3[:60],
            "status": status,
        })

    return milestones


def extract_milestones(slug: str) -> dict:
    """Extract milestones from milestones.md."""
    ms_file = PROFILES / slug / "milestones.md"
    result = {"exists": False, "milestones": [], "lines": 0}

    if not ms_file.exists():
        return result

    text = ms_file.read_text(encoding="utf-8")
    result["exists"] = True
    result["lines"] = len(text.splitlines())
    result["milestones"] = parse_milestone_table(text)
    return result


def extract_career_milestones(slug: str) -> list[dict]:
    """Extract career-specific milestones from growth/career-path.md."""
    cp_file = PROFILES / slug / "growth" / "career-path.md"
    if not cp_file.exists():
        return []

    text = cp_file.read_text(encoding="utf-8")
    career_milestones = []

    row_pattern = re.compile(r'\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|')
    for line in text.splitlines():
        match = row_pattern.search(line)
        if not match:
            continue

        col1 = match.group(1).strip().strip("*")
        col2 = match.group(2).strip()
        col3 = match.group(3).strip()

        if _is_table_header_or_separator(col1):
            continue

        is_career = any(kw in f"{col1} {col2} {col3}".lower()
                        for kw in ["job", "career", "work", "salary", "lương", "công ty",
                                   "company", "role", "position", "intern", "thực tập"])
        if is_career:
            career_milestones.append({
                "description": col1[:60],
                "period": col2[:30],
                "detail": col3[:60],
            })

    return career_milestones[:10]


def extract_achievements_as_milestones(slug: str) -> list[str]:
    """Extract verified achievements as completed milestones."""
    ach_file = PROFILES / slug / "identity" / "achievements.md"
    if not ach_file.exists():
        return []

    text = ach_file.read_text(encoding="utf-8")
    achievements = []
    for line in text.splitlines():
        if "|" in line and any(kw in line.lower() for kw in ["giải", "award", "scholarship",
                                                               "học bổng", "rank", "hạng"]):
            clean = line.strip().strip("|").strip()
            if clean and not clean.startswith("-"):
                achievements.append(clean[:80])

    return achievements[:10]


def gather_character(slug: str) -> dict:
    """Gather all milestone data for one character."""
    ms = extract_milestones(slug)
    achieved = sum(1 for m in ms["milestones"] if m["status"] == "achieved")
    planned = sum(1 for m in ms["milestones"] if m["status"] == "planned")
    missed = sum(1 for m in ms["milestones"] if m["status"] == "missed")
    in_progress = sum(1 for m in ms["milestones"] if m["status"] == "in_progress")

    return {
        "slug": slug,
        "display": CHAR_DISPLAY.get(slug, slug),
        "milestones": ms,
        "career_milestones": extract_career_milestones(slug),
        "achievements": extract_achievements_as_milestones(slug),
        "counts": {
            "total": len(ms["milestones"]),
            "achieved": achieved,
            "planned": planned,
            "missed": missed,
            "in_progress": in_progress,
            "unknown": len(ms["milestones"]) - achieved - planned - missed - in_progress,
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Gather career milestone tracking data")
    parser.add_argument("--character", "-c", help="Character slug or alias")
    parser.add_argument("--json", dest="json_out", action="store_true", help="JSON output")
    parser.add_argument("--pending-only", action="store_true", help="Show only planned/unachieved")
    args = parser.parse_args()

    chars = [resolve_character(args.character)] if args.character else ALL_CHARS
    results = {slug: gather_character(slug) for slug in chars}

    if args.json_out:
        print(json.dumps(results, indent=2, ensure_ascii=False, default=str))
        return

    for slug, data in results.items():
        display = data["display"]
        counts = data["counts"]

        print(f"\n{'='*70}")
        print(f"  {display} ({slug}) — Milestone Tracking")
        print(f"{'='*70}")

        print(f"\n  Total: {counts['total']} | Achieved: {counts['achieved']} | "
              f"Planned: {counts['planned']} | Missed: {counts['missed']}")

        ms_list = data["milestones"]["milestones"]
        if args.pending_only:
            ms_list = [m for m in ms_list if m["status"] in ("planned", "in_progress", "unknown")]

        if ms_list:
            print(f"\n  {'Description':<40s} {'Date':<15s} {'Status'}")
            print(f"  {'-'*40} {'-'*15} {'-'*10}")
            for m in ms_list[:15]:
                icon = {"achieved": "✓", "planned": "○", "missed": "✗",
                        "in_progress": "◐", "unknown": "?"}.get(m["status"], "?")
                print(f"  {icon} {m['description']:<38s} {m['date_or_period']:<15s} {m['status']}")

        career_ms = data["career_milestones"]
        if career_ms and not args.pending_only:
            print(f"\n  [Career Milestones from career-path.md]")
            for cm in career_ms[:5]:
                print(f"    - {cm['description']}: {cm['period']}")

    print(f"\n{'='*70}")
    print(f"  Summary: {len(results)} characters gathered")
    print(f"  Next: LLM analyzes milestone trajectory, on-track assessment")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
