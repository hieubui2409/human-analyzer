"""Gather current career state data for LLM-powered career projection."""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import ALL_CHARS, CHAR_DISPLAY, PROFILES, resolve_character
from platform_lib.markdown_parser import extract_sections, parse_dreyfus_skills
from platform_lib.growth_taxonomy import SUPER_STAGES, mentioned_terms


def extract_career_state(slug: str) -> dict:
    """Extract current career state from growth/career-path.md.

    C1-GRO-09b: result["stage"] (single-pick via earliest_term) removed and
    replaced with result["stages_mentioned"] signal list. The LLM adjudicates
    which stage is current — scripts only gather, never judge.
    """
    cp_file = PROFILES / slug / "growth" / "career-path.md"
    result = {"exists": False, "stages_mentioned": [], "sections": {}, "lines": 0}

    if not cp_file.exists():
        return result

    text = cp_file.read_text(encoding="utf-8")
    result["exists"] = True
    result["lines"] = len(text.splitlines())
    result["sections"] = extract_sections(cp_file)
    result["stages_mentioned"] = mentioned_terms(text, SUPER_STAGES)

    return result


def extract_skill_summary(slug: str) -> dict:
    """Extract top skills from growth/competencies.md."""
    comp_file = PROFILES / slug / "growth" / "competencies.md"
    result = {"exists": False, "skill_count": 0, "top_skills": []}

    if not comp_file.exists():
        return result

    text = comp_file.read_text(encoding="utf-8")
    result["exists"] = True

    skills = parse_dreyfus_skills(text)
    result["skill_count"] = len(skills)
    result["top_skills"] = sorted(skills, key=lambda s: s["level"], reverse=True)[:5]
    return result


def extract_learning_style(slug: str) -> dict:
    """Extract learning style from growth/learning-profile.md."""
    lp_file = PROFILES / slug / "growth" / "learning-profile.md"
    result = {"exists": False, "kolb_style": "unknown"}

    if not lp_file.exists():
        return result

    text = lp_file.read_text(encoding="utf-8").lower()
    result["exists"] = True
    for style in ["diverging", "assimilating", "converging", "accommodating"]:
        if style in text:
            result["kolb_style"] = style
            break

    return result


def extract_education_age(slug: str) -> dict:
    """Extract age and education from identity/core.md."""
    id_file = PROFILES / slug / "identity" / "core.md"
    result = {"exists": False, "age_context": "", "education": ""}

    if not id_file.exists():
        return result

    text = id_file.read_text(encoding="utf-8")
    result["exists"] = True

    age_match = re.search(r'(?:tuổi|age)[^\d]*(\d{1,2})', text, re.IGNORECASE)
    if age_match:
        result["age_context"] = f"~{age_match.group(1)} tuổi (2026)"

    sections = extract_sections(id_file)
    for key, content in sections.items():
        if any(kw in key.lower() for kw in ["education", "học vấn", "đại học"]):
            result["education"] = content[:200]
            break

    return result


def gather_character(slug: str) -> dict:
    """Gather forecast input data for one character."""
    career = extract_career_state(slug)
    skills = extract_skill_summary(slug)
    learning = extract_learning_style(slug)
    edu = extract_education_age(slug)

    return {
        "slug": slug,
        "display": CHAR_DISPLAY.get(slug, slug),
        "career_state": career,
        "skill_summary": skills,
        "learning_style": learning,
        "education_age": edu,
        "forecast_ready": all([career["exists"], skills["exists"], learning["exists"]]),
    }


def main():
    parser = argparse.ArgumentParser(description="Gather career forecast input data")
    parser.add_argument("--character", "-c", help="Character slug or alias")
    parser.add_argument("--json", dest="json_out", action="store_true", help="JSON output")
    parser.add_argument("--horizon", type=int, default=3, help="Projection horizon in years")
    args = parser.parse_args()

    chars = [resolve_character(args.character)] if args.character else ALL_CHARS
    results = {slug: gather_character(slug) for slug in chars}

    for slug in results:
        results[slug]["horizon_years"] = args.horizon

    if args.json_out:
        print(json.dumps(results, indent=2, ensure_ascii=False, default=str))
        return

    for slug, data in results.items():
        display = data["display"]
        career = data["career_state"]
        skills = data["skill_summary"]

        print(f"\n{'='*70}")
        print(f"  {display} ({slug}) — Forecast Input [FORECAST — NOT FACTUAL]")
        print(f"{'='*70}")

        stages_str = ", ".join(career["stages_mentioned"]) or "—"
        print(f"\n  Career stages mentioned: {stages_str}")
        print(f"  (LLM adjudicates current stage from the above signal)")
        top_str = ", ".join(s["name"] + f"(L{s['level']})" for s in skills["top_skills"][:3])
        print(f"  Top skills: {top_str}")
        print(f"  Learning style: {data['learning_style']['kolb_style']}")
        print(f"  Age context: {data['education_age'].get('age_context', 'unknown')}")
        print(f"  Forecast ready: {'✓' if data['forecast_ready'] else '✗'}")
        print(f"  Horizon: {args.horizon} years")

    print(f"\n{'='*70}")
    print(f"  Summary: {len(results)} characters gathered")
    print(f"  Next: LLM generates [FORECAST — NOT FACTUAL] career projections")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
