"""Gather growth data from all characters for cross-character comparison."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import ALL_CHARS, CHAR_DISPLAY, PROFILES
from platform_lib.markdown_parser import extract_frontmatter, parse_dreyfus_skills
from platform_lib.growth_taxonomy import (
    SUPER_STAGES, KOLB_STYLES, KRAM_NETWORK_TYPES, earliest_term, mentioned_terms,
)


DIMENSIONS = ["career", "competency", "learning", "mentoring"]

DIMENSION_TO_FILE = {
    "career": "growth/career-path.md",
    "competency": "growth/competencies.md",
    "learning": "growth/learning-profile.md",
    "mentoring": "growth/mentoring-map.md",
}


def detect_career_stage(text: str) -> str:
    return earliest_term(text, SUPER_STAGES)


def detect_kolb_style(text: str) -> str:
    return earliest_term(text, KOLB_STYLES)


def detect_network_type(text: str) -> str:
    return earliest_term(text, KRAM_NETWORK_TYPES)


def gather_dimension(slug: str, dimension: str) -> dict:
    """Gather data for one dimension of one character."""
    rel_path = DIMENSION_TO_FILE[dimension]
    fpath = PROFILES / slug / rel_path
    result = {"exists": False, "lines": 0}

    if not fpath.exists():
        return result

    text = fpath.read_text(encoding="utf-8")
    result["exists"] = True
    result["lines"] = len(text.splitlines())
    fm = extract_frontmatter(fpath) or {}
    result["confidence"] = fm.get("confidence", "unknown")

    if dimension == "career":
        result["stage"] = detect_career_stage(text)
        result["stages_mentioned"] = mentioned_terms(text, SUPER_STAGES)
    elif dimension == "competency":
        skills = parse_dreyfus_skills(text)
        result["skill_count"] = len(skills)
        result["avg_level"] = round(sum(s["level"] for s in skills) / len(skills), 1) if skills else 0
        result["top_skills"] = sorted(skills, key=lambda s: s["level"], reverse=True)[:3]
    elif dimension == "learning":
        result["kolb_style"] = detect_kolb_style(text)
        result["styles_mentioned"] = mentioned_terms(text, KOLB_STYLES)
    elif dimension == "mentoring":
        result["network_type"] = detect_network_type(text)
        result["network_types_mentioned"] = mentioned_terms(text, KRAM_NETWORK_TYPES)

    return result


def gather_all(dimensions: list[str]) -> dict:
    """Gather comparison data across all characters."""
    comparison = {}
    for slug in ALL_CHARS:
        comparison[slug] = {
            "display": CHAR_DISPLAY.get(slug, slug),
            "dimensions": {},
        }
        for dim in dimensions:
            comparison[slug]["dimensions"][dim] = gather_dimension(slug, dim)
    return comparison


def main():
    parser = argparse.ArgumentParser(description="Gather cross-character growth comparison data")
    parser.add_argument("--dimension", "-d", default="all",
                        choices=["career", "competency", "learning", "mentoring", "all"],
                        help="Dimension to compare")
    parser.add_argument("--json", dest="json_out", action="store_true", help="JSON output")
    args = parser.parse_args()

    dims = DIMENSIONS if args.dimension == "all" else [args.dimension]
    results = gather_all(dims)

    if args.json_out:
        print(json.dumps(results, indent=2, ensure_ascii=False, default=str))
        return

    print(f"\n{'='*70}")
    print(f"  Cross-Character Growth Comparison")
    print(f"{'='*70}")

    for dim in dims:
        print(f"\n  [{dim.upper()}]")
        print(f"  {'Character':<12s} ", end="")

        if dim == "career":
            print(f"{'Stage':<18s} {'Lines':<7s} {'Confidence'}")
        elif dim == "competency":
            print(f"{'Skills':<8s} {'Avg Lvl':<9s} {'Top Skill':<20s} {'Confidence'}")
        elif dim == "learning":
            print(f"{'Kolb Style':<16s} {'Lines':<7s} {'Confidence'}")
        elif dim == "mentoring":
            print(f"{'Network Type':<16s} {'Lines':<7s} {'Confidence'}")

        print(f"  {'-'*12} {'-'*50}")

        for slug in ALL_CHARS:
            data = results[slug]["dimensions"][dim]
            display = results[slug]["display"]

            if not data["exists"]:
                print(f"  {display:<12s} MISSING")
                continue

            if dim == "career":
                print(f"  {display:<12s} {data['stage']:<18s} {data['lines']:<7d} {data['confidence']}")
            elif dim == "competency":
                top = data["top_skills"][0]["name"] if data.get("top_skills") else "—"
                print(f"  {display:<12s} {data['skill_count']:<8d} {data['avg_level']:<9.1f} {top:<20s} {data['confidence']}")
            elif dim == "learning":
                print(f"  {display:<12s} {data['kolb_style']:<16s} {data['lines']:<7d} {data['confidence']}")
            elif dim == "mentoring":
                print(f"  {display:<12s} {data.get('network_type', '—'):<16s} {data['lines']:<7d} {data['confidence']}")

    print(f"\n{'='*70}")
    print(f"  Next: LLM compares trajectories, identifies patterns, cross-character insights")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
