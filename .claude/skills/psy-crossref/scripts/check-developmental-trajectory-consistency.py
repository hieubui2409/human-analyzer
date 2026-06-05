"""Dimension 6: Gather developmental trajectory signals from timeline and growth files.

GATHER-ONLY (Golden Rule): this script emits deterministic signals — dated growth/regression
occurrences, intervention events, phase transitions. It does NOT emit clinical plausibility
verdicts (unsupported_growth, unexplained_regression, abrupt_phase_transition).
LLM adjudication is required to assess whether transitions are clinically plausible.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import ALL_CHARS, CHAR_DISPLAY, PROFILES, resolve_character
from platform_lib.markdown_parser import extract_frontmatter, extract_sections

DATE_PATTERN = re.compile(r"(\d{4})[-/](\d{1,2})(?:[-/](\d{1,2}))?")
GROWTH_KEYWORDS = ["recovery", "improvement", "progress", "healing", "resolved", "stable",
                   "hồi phục", "tiến bộ", "ổn định", "cải thiện", "vượt qua"]
REGRESSION_KEYWORDS = ["relapse", "crisis", "deterioration", "worsening", "regression",
                       "tái phát", "khủng hoảng", "xấu đi", "suy thoái"]
INTERVENTION_KEYWORDS = ["therapy", "counseling", "medication", "support", "mentoring",
                         "treatment", "intervention", "tư vấn", "điều trị", "hỗ trợ"]


def extract_dates_from_text(text: str) -> list[str]:
    """Extract YYYY-MM or YYYY-MM-DD dates from text."""
    dates = []
    for m in DATE_PATTERN.finditer(text):
        year, month = m.group(1), m.group(2)
        day = m.group(3)
        if day:
            dates.append(f"{year}-{month.zfill(2)}-{day.zfill(2)}")
        else:
            dates.append(f"{year}-{month.zfill(2)}")
    return dates


def find_keyword_contexts(text: str, keywords: list[str], label: str) -> list[dict]:
    """Find lines containing keywords and their associated dates."""
    results = []
    lines = text.split("\n")
    for i, line in enumerate(lines):
        lower = line.lower()
        matched = [kw for kw in keywords if kw in lower]
        if matched:
            nearby_text = "\n".join(lines[max(0, i-2):i+3])
            dates = extract_dates_from_text(nearby_text)
            results.append({
                "line_num": i + 1,
                "type": label,
                "keywords": matched,
                "dates": dates,
                "excerpt": line.strip()[:100],
            })
    return results


def gather_character(slug: str) -> dict:
    """Gather developmental trajectory signals for a character."""
    profile_dir = PROFILES / slug

    growth_file = profile_dir / "psychology" / "growth-edges.md"
    timeline_file = profile_dir / "timeline" / "overview.md"
    state_file = profile_dir / "timeline" / "state-timeline.md"
    milestones_file = profile_dir / "milestones.md"

    growth_text = growth_file.read_text(encoding="utf-8") if growth_file.exists() else ""
    timeline_text = timeline_file.read_text(encoding="utf-8") if timeline_file.exists() else ""
    state_text = state_file.read_text(encoding="utf-8") if state_file.exists() else ""
    milestones_text = milestones_file.read_text(encoding="utf-8") if milestones_file.exists() else ""

    combined_timeline = timeline_text + "\n" + state_text + "\n" + milestones_text

    growth_occurrences = find_keyword_contexts(growth_text, GROWTH_KEYWORDS, "growth")
    regression_occurrences = find_keyword_contexts(growth_text, REGRESSION_KEYWORDS, "regression")
    intervention_occurrences = find_keyword_contexts(combined_timeline, INTERVENTION_KEYWORDS, "intervention")

    # Detect phase transitions (deterministic pattern match only — no plausibility verdict)
    phase_transitions = []
    if state_file.exists():
        phases = re.findall(r"(?:phase|giai đoạn)\s*\d+[^:]*:\s*([^\n]+)", state_text, re.IGNORECASE)
        for i in range(1, len(phases)):
            prev_phase = phases[i-1].lower()
            curr_phase = phases[i].lower()
            prev_is_crisis = any(kw in prev_phase for kw in REGRESSION_KEYWORDS)
            curr_is_growth = any(kw in curr_phase for kw in GROWTH_KEYWORDS)
            nearby = state_text[state_text.lower().find(phases[i].lower()):
                                state_text.lower().find(phases[i].lower()) + 500]
            has_trigger = any(kw in nearby.lower() for kw in INTERVENTION_KEYWORDS)
            phase_transitions.append({
                "from_phase": phases[i-1][:60],
                "to_phase": phases[i][:60],
                "crisis_to_growth": prev_is_crisis and curr_is_growth,
                "trigger_documented": has_trigger,
                "needs_llm_adjudication": True,
            })

    return {
        "growth_occurrences": growth_occurrences,
        "regression_occurrences": regression_occurrences,
        "intervention_occurrences": intervention_occurrences,
        "phase_transitions": phase_transitions,
        "needs_llm_adjudication": True,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Gather developmental trajectory signals (Dim 6) — LLM adjudicates plausibility"
    )
    parser.add_argument("--character", "-c", help="Character slug or alias")
    parser.add_argument("--json", dest="json_out", action="store_true")
    args = parser.parse_args()

    chars = [resolve_character(args.character)] if args.character else ALL_CHARS

    all_signals: dict[str, dict] = {}
    for slug in chars:
        all_signals[slug] = gather_character(slug)

    if args.json_out:
        print(json.dumps(all_signals, indent=2, ensure_ascii=False, default=str))
        return

    print(f"\n{'='*70}")
    print("  Dimension 6: Developmental Trajectory Signals (GATHER-ONLY)")
    print("  NOTE: Clinical plausibility assessment requires LLM adjudication.")
    print(f"{'='*70}")

    for slug, signals in all_signals.items():
        display = CHAR_DISPLAY.get(slug, slug)
        print(f"\n  {display} ({slug})")
        g = signals["growth_occurrences"]
        r = signals["regression_occurrences"]
        iv = signals["intervention_occurrences"]
        pt = signals["phase_transitions"]
        print(f"    Growth occurrences: {len(g)} | Regression: {len(r)} | "
              f"Interventions: {len(iv)} | Phase transitions: {len(pt)}")

        if g:
            print(f"\n    Growth occurrences:")
            for item in g:
                dates_str = ", ".join(item["dates"]) if item["dates"] else "undated"
                print(f"      L{item['line_num']} [{dates_str}] {item['excerpt'][:70]}")

        if r:
            print(f"\n    Regression occurrences:")
            for item in r:
                dates_str = ", ".join(item["dates"]) if item["dates"] else "undated"
                print(f"      L{item['line_num']} [{dates_str}] {item['excerpt'][:70]}")

        if pt:
            print(f"\n    Phase transitions (crisis→growth / trigger present):")
            for t in pt:
                flag = "C→G" if t["crisis_to_growth"] else "   "
                trigger = "trigger:YES" if t["trigger_documented"] else "trigger:NO "
                print(f"      [{flag}] [{trigger}] '{t['from_phase'][:35]}' → '{t['to_phase'][:35]}'")

    print(f"\n  All signals require LLM adjudication before plausibility verdict.")


if __name__ == "__main__":
    main()
