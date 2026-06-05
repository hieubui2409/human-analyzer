"""Gather career milestones from milestones.md and career-path.md for tracking."""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import ALL_CHARS, CHAR_DISPLAY, PROFILES, resolve_character
from platform_lib.markdown_parser import parse_table_rows


STATUS_PATTERNS = {
    "achieved": re.compile(r'✅|achieved|đạt được|hoàn thành|completed', re.IGNORECASE),
    "planned": re.compile(r'🔄|planned|dự kiến|kế hoạch|target|mục tiêu', re.IGNORECASE),
    "missed": re.compile(r'❌|missed|bỏ lỡ|thất bại|failed', re.IGNORECASE),
    "in_progress": re.compile(r'🔶|in.progress|đang|ongoing|current', re.IGNORECASE),
}


# Header-term vocabularies for column-aware table mapping. Substring-matched against
# lowercased header cells so labels like "Vai trò (Role)" or "Sự kiện" are recognised.
EVENT_HEADERS = ("sự kiện", "milestone", "mốc", "cột mốc", "event", "achievement", "description", "hoạt động")
DATE_HEADERS = ("năm", "year", "date", "period", "giai đoạn", "thời gian", "ngày")
DETAIL_HEADERS = ("impact", "tác động", "ý nghĩa", "ghi chú", "note", "status", "trạng thái")
# Any cell matching these marks a row as a header (so it is skipped as data).
_HEADER_HINTS = EVENT_HEADERS + DATE_HEADERS + DETAIL_HEADERS + (
    "tuổi", "age", "field", "insight", "câu hỏi", "nguồn gốc", "vai trò", "mức độ", "vị trí", "công ty")


def _is_header_row(low_cells: list[str]) -> bool:
    return any(any(term in cell for term in _HEADER_HINTS) for cell in low_cells)


def _col_index(low_cells: list[str], wanted: tuple) -> int | None:
    for i, cell in enumerate(low_cells):
        if any(term in cell for term in wanted):
            return i
    return None


def _cell(cells: list[str], idx, default: str = "") -> str:
    if idx is None or idx >= len(cells):
        return default
    return cells[idx].strip().strip("*").strip()


def _gather_status_signals(cells: list[str]) -> list[str]:
    """Return ALL matched status keywords found across the row cells.
    Leaves final achieved/planned/missed adjudication to the LLM — do not pick one winner
    when multiple patterns match (e.g. a milestone can be 'planned' AND marked 'in_progress').
    Empty list means no status signal detected.
    """
    full_text = " ".join(cells)
    matched = [name for name, pattern in STATUS_PATTERNS.items() if pattern.search(full_text)]
    return matched


def _detect_status(cells: list[str]) -> str:
    """Legacy single-winner status for backward-compat summary counts.
    Prefers more specific signals: achieved > missed > in_progress > planned.
    Use status_signals (all signals) for LLM adjudication.
    """
    signals = _gather_status_signals(cells)
    if not signals:
        return "unknown"
    # Precedence: achieved > missed > in_progress > planned
    for preferred in ("achieved", "missed", "in_progress", "planned"):
        if preferred in signals:
            return preferred
    return signals[0]


def parse_milestone_table(text: str) -> list[dict]:
    """Parse milestone tables, mapping columns by header so wide (4-5 col) tables are read
    correctly and status is detected across ALL cells (incl. a trailing Impact column)."""
    milestones = []
    e_i = d_i = det_i = None
    header_seen = False

    for cells in parse_table_rows(text):
        low = [c.strip().strip("*").lower() for c in cells]
        if _is_header_row(low):
            e_i = _col_index(low, EVENT_HEADERS)
            d_i = _col_index(low, DATE_HEADERS)
            det_i = _col_index(low, DETAIL_HEADERS)
            header_seen = True
            continue

        status = _detect_status(cells)

        if header_seen and e_i is not None:
            desc = _cell(cells, e_i)
            date = _cell(cells, d_i)
            detail = _cell(cells, det_i)
        else:
            # No recognised header — fall back to positional: longest cell = event text.
            desc = max((c.strip().strip("*") for c in cells), key=len, default="")
            date = _cell(cells, 0)
            detail = ""

        if not desc:
            continue

        milestones.append({
            "description": desc[:80],
            "date_or_period": date[:30],
            "detail": detail[:80],
            "status": status,
            # All raw status signals found in this row; LLM uses this for adjudication
            "status_signals": _gather_status_signals(cells),
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


# A career-history table is identified by its header (NOT by row keywords, which leaked
# role-salience rows like "Worker | Rất cao" via the substring "work"). These terms
# appear in the history-table header ("Giai đoạn | Vị trí | Công ty …" / "… | Hoạt động")
# but NOT in the role-salience header ("Vai trò | Mức độ nổi bật | Ghi chú").
_CAREER_TABLE_HEADERS = ("vị trí", "công ty", "position", "company", "hoạt động", "career", "chức danh")


def extract_career_milestones(slug: str) -> list[dict]:
    """Extract career-history rows from growth/career-path.md, scoped by table header so
    role-salience / performance-review tables are not mis-read as career milestones."""
    cp_file = PROFILES / slug / "growth" / "career-path.md"
    if not cp_file.exists():
        return []

    text = cp_file.read_text(encoding="utf-8")
    career_milestones = []
    in_career_table = False

    for cells in parse_table_rows(text):
        low = [c.strip().strip("*").lower() for c in cells]
        if _is_header_row(low):
            in_career_table = "giai đoạn" in " ".join(low) and any(
                term in cell for cell in low for term in _CAREER_TABLE_HEADERS)
            continue
        if not in_career_table:
            continue

        desc = _cell(cells, 0)
        if not desc:
            continue
        career_milestones.append({
            "description": desc[:60],
            "period": _cell(cells, 1)[:30],
            "detail": _cell(cells, 2)[:60],
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
    parser.add_argument("--all", dest="all_chars", action="store_true",
                        help="Track all characters (default when no --character given)")
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
