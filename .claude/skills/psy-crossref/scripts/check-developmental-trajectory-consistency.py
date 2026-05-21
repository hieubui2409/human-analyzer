"""Dimension 6: Check developmental trajectory plausibility against timeline."""
import argparse
import json
import re
import sys
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


def check_character(slug: str) -> list[dict]:
    """Check developmental trajectory for a character."""
    profile_dir = PROFILES / slug
    findings = []

    growth_file = profile_dir / "psychology" / "growth-edges.md"
    timeline_file = profile_dir / "timeline" / "overview.md"
    state_file = profile_dir / "timeline" / "state-timeline.md"
    milestones_file = profile_dir / "milestones.md"

    growth_text = growth_file.read_text(encoding="utf-8") if growth_file.exists() else ""
    timeline_text = timeline_file.read_text(encoding="utf-8") if timeline_file.exists() else ""
    state_text = state_file.read_text(encoding="utf-8") if state_file.exists() else ""
    milestones_text = milestones_file.read_text(encoding="utf-8") if milestones_file.exists() else ""

    combined_timeline = timeline_text + "\n" + state_text + "\n" + milestones_text

    growth_claims = find_keyword_contexts(growth_text, GROWTH_KEYWORDS, "growth")
    regression_claims = find_keyword_contexts(growth_text, REGRESSION_KEYWORDS, "regression")

    timeline_interventions = find_keyword_contexts(combined_timeline, INTERVENTION_KEYWORDS, "intervention")
    intervention_dates = set()
    for item in timeline_interventions:
        intervention_dates.update(item["dates"])

    for claim in growth_claims:
        if not claim["dates"]:
            findings.append({
                "severity": "MINOR",
                "type": "undated_growth",
                "message": f"Growth claim without date: {claim['excerpt']}",
                "file": "psychology/growth-edges.md",
                "line": claim["line_num"],
            })
            continue

        claim_date = claim["dates"][0]
        has_prior_intervention = False
        for int_date in intervention_dates:
            if int_date < claim_date:
                has_prior_intervention = True
                break

        if not has_prior_intervention and intervention_dates:
            findings.append({
                "severity": "MAJOR",
                "type": "unsupported_growth",
                "message": f"Growth claim at {claim_date} without prior intervention documented in timeline",
                "file": "psychology/growth-edges.md",
                "line": claim["line_num"],
                "excerpt": claim["excerpt"],
            })

    for claim in regression_claims:
        if claim["dates"]:
            reg_date = claim["dates"][0]
            timeline_dates = extract_dates_from_text(combined_timeline)
            nearby_events = [d for d in timeline_dates
                            if abs(int(d[:4]) - int(reg_date[:4])) <= 1]
            if not nearby_events:
                findings.append({
                    "severity": "MAJOR",
                    "type": "unexplained_regression",
                    "message": f"Regression at {reg_date} without proximate timeline event",
                    "file": "psychology/growth-edges.md",
                    "line": claim["line_num"],
                    "excerpt": claim["excerpt"],
                })

    if state_file.exists():
        phases = re.findall(r"(?:phase|giai đoạn)\s*\d+[^:]*:\s*([^\n]+)", state_text, re.IGNORECASE)
        for i in range(1, len(phases)):
            prev_phase = phases[i-1].lower()
            curr_phase = phases[i].lower()
            prev_is_crisis = any(kw in prev_phase for kw in REGRESSION_KEYWORDS)
            curr_is_growth = any(kw in curr_phase for kw in GROWTH_KEYWORDS)
            if prev_is_crisis and curr_is_growth:
                nearby = state_text[state_text.lower().find(phases[i].lower()):
                                    state_text.lower().find(phases[i].lower()) + 500]
                has_trigger = any(kw in nearby.lower() for kw in INTERVENTION_KEYWORDS)
                if not has_trigger:
                    findings.append({
                        "severity": "MINOR",
                        "type": "abrupt_phase_transition",
                        "message": f"Phase transition from crisis to growth without documented trigger: '{phases[i-1][:40]}' → '{phases[i][:40]}'",
                        "file": "timeline/state-timeline.md",
                    })

    return findings


def main():
    parser = argparse.ArgumentParser(description="Check developmental trajectory consistency (Dim 6)")
    parser.add_argument("--character", "-c", help="Character slug or alias")
    parser.add_argument("--json", dest="json_out", action="store_true")
    args = parser.parse_args()

    chars = [resolve_character(args.character)] if args.character else ALL_CHARS

    all_findings: dict[str, list[dict]] = {}
    for slug in chars:
        all_findings[slug] = check_character(slug)

    if args.json_out:
        print(json.dumps(all_findings, indent=2, ensure_ascii=False, default=str))
        return

    print(f"\n{'='*70}")
    print("  Dimension 6: Developmental Trajectory Consistency")
    print(f"{'='*70}")

    total_issues = 0
    for slug, findings in all_findings.items():
        display = CHAR_DISPLAY.get(slug, slug)
        print(f"\n  {display} ({slug})")
        if not findings:
            print("    Developmental trajectory is consistent.")
            continue
        majors = [f for f in findings if f["severity"] == "MAJOR"]
        minors = [f for f in findings if f["severity"] == "MINOR"]
        print(f"    MAJOR: {len(majors)} | MINOR: {len(minors)}")
        print(f"\n    {'Severity':<8s} {'Type':<25s} Message")
        print(f"    {'-'*8} {'-'*25} {'-'*50}")
        for f in findings:
            print(f"    {f['severity']:<8s} {f['type']:<25s} {f['message'][:70]}")
        total_issues += len(findings)

    print(f"\n  TOTAL ISSUES: {total_issues}")
    sys.exit(1 if total_issues > 0 else 0)


if __name__ == "__main__":
    main()
