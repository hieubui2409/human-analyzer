"""Gather competency data from growth/competencies.md, identity/core.md, and materials for LLM assessment."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import ALL_CHARS, CHAR_DISPLAY, MATERIALS, PROFILES, resolve_character
from platform_lib.markdown_parser import extract_sections, extract_frontmatter, parse_dreyfus_skills


DREYFUS_LEVELS = {
    1: "Novice",
    2: "Advanced Beginner",
    3: "Competent",
    4: "Proficient",
    5: "Expert",
    6: "Master",
    7: "Practical Wisdom",
}

SKILL_KEYWORDS = [
    "skill", "kỹ năng", "competency", "ability", "năng lực",
    "dreyfus", "SFIA", "proficient", "expert", "novice",
    "technical", "soft skill", "leadership", "communication",
    "programming", "lập trình", "python", "java", "react",
]


def extract_competencies_from_profile(slug: str) -> dict:
    """Extract competency data from growth/competencies.md."""
    comp_file = PROFILES / slug / "growth" / "competencies.md"
    result = {"exists": False, "frontmatter": {}, "sections": {}, "lines": 0,
              "skills_found": [], "raw_text": ""}

    if not comp_file.exists():
        return result

    text = comp_file.read_text(encoding="utf-8")
    result["exists"] = True
    result["lines"] = len(text.splitlines())
    result["raw_text"] = text
    result["frontmatter"] = extract_frontmatter(comp_file) or {}
    result["sections"] = extract_sections(comp_file)

    for skill in parse_dreyfus_skills(text):
        result["skills_found"].append({
            "name": skill["name"],
            "level": skill["level"],
            "level_name": DREYFUS_LEVELS.get(skill["level"], "Unknown"),
        })

    return result


def extract_achievements_skills(slug: str) -> list[str]:
    """Extract skill-relevant achievements."""
    ach_file = PROFILES / slug / "identity" / "achievements.md"
    if not ach_file.exists():
        return []

    text = ach_file.read_text(encoding="utf-8")
    lines = text.splitlines()
    relevant = []
    for line in lines:
        line_lower = line.lower()
        if any(kw in line_lower for kw in ["award", "giải", "scholarship", "học bổng",
                                            "certificate", "chứng chỉ", "competition",
                                            "cuộc thi", "rank", "hạng", "top"]):
            relevant.append(line.strip())
    return relevant[:10]


def count_skill_materials(slug: str) -> dict:
    """Count materials mentioning skill-related keywords."""
    mdir = MATERIALS / slug
    if not mdir.exists():
        return {"count": 0, "files": []}

    count = 0
    files = []
    for fpath in sorted(mdir.rglob("*.md")):
        if fpath.is_dir():
            continue
        try:
            text = fpath.read_text(encoding="utf-8").lower()
        except (OSError, UnicodeDecodeError):
            continue
        if any(kw.lower() in text for kw in SKILL_KEYWORDS):
            count += 1
            files.append(fpath.name)

    return {"count": count, "files": files[:10]}


def gather_character(slug: str) -> dict:
    """Gather all competency data for one character."""
    comp = extract_competencies_from_profile(slug)
    return {
        "slug": slug,
        "display": CHAR_DISPLAY.get(slug, slug),
        "competency_profile": comp,
        "achievements_skills": extract_achievements_skills(slug),
        "materials_skills": count_skill_materials(slug),
        "skill_count": len(comp["skills_found"]),
        "avg_level": (round(sum(s["level"] for s in comp["skills_found"]) / len(comp["skills_found"]), 1)
                      if comp["skills_found"] else 0),
    }


def main():
    parser = argparse.ArgumentParser(description="Gather competency data for GRO assessment")
    parser.add_argument("--character", "-c", help="Character slug or alias")
    parser.add_argument("--json", dest="json_out", action="store_true", help="JSON output")
    parser.add_argument("--gaps-only", action="store_true", help="Show only skills rated 1-2")
    args = parser.parse_args()

    chars = [resolve_character(args.character)] if args.character else ALL_CHARS
    results = {slug: gather_character(slug) for slug in chars}

    if args.json_out:
        for slug in results:
            results[slug]["competency_profile"].pop("raw_text", None)
        print(json.dumps(results, indent=2, ensure_ascii=False, default=str))
        return

    for slug, data in results.items():
        display = data["display"]
        comp = data["competency_profile"]

        print(f"\n{'='*70}")
        print(f"  {display} ({slug}) — Competency Data Gathering")
        print(f"{'='*70}")

        print(f"\n  [growth/competencies.md]")
        if comp["exists"]:
            print(f"  Lines: {comp['lines']}")
            print(f"  Skills parsed: {data['skill_count']}")
            print(f"  Avg Dreyfus level: {data['avg_level']}/7")
            print(f"  Confidence: {comp['frontmatter'].get('confidence', 'unknown')}")

            skills = comp["skills_found"]
            if args.gaps_only:
                skills = [s for s in skills if s["level"] <= 2]

            if skills:
                print(f"\n  {'Skill':<30s} {'Level':<6s} {'Name'}")
                print(f"  {'-'*30} {'-'*6} {'-'*20}")
                for s in skills:
                    print(f"  {s['name']:<30s} {s['level']:<6d} {s['level_name']}")
        else:
            print(f"  MISSING — file does not exist")

        if data["achievements_skills"]:
            print(f"\n  [Achievements — Skill-relevant]")
            for a in data["achievements_skills"][:5]:
                print(f"    - {a[:80]}")

        mc = data["materials_skills"]
        print(f"\n  [Materials — Skill Keywords]")
        print(f"  Matching files: {mc['count']}")

    print(f"\n{'='*70}")
    print(f"  Summary: {len(results)} characters gathered")
    print(f"  Next: LLM assesses skill distribution, strengths, gaps")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
