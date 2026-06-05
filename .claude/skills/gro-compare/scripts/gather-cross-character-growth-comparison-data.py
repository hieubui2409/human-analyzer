"""Gather growth data from all characters for cross-character comparison."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import ALL_CHARS, CHAR_DISPLAY, PROFILES
from platform_lib.markdown_parser import extract_frontmatter, parse_dreyfus_skills
from platform_lib.growth_taxonomy import (
    SUPER_STAGES, KOLB_STYLES, KRAM_NETWORK_TYPES, mentioned_terms,
)


DIMENSIONS = ["career", "competency", "learning", "mentoring"]

DIMENSION_TO_FILE = {
    "career": "growth/career-path.md",
    "competency": "growth/competencies.md",
    "learning": "growth/learning-profile.md",
    "mentoring": "growth/mentoring-map.md",
}


def gather_dimension(slug: str, dimension: str) -> dict:
    """Gather data for one dimension of one character.

    C1-GRO-09b: single-pick detect_* functions removed. Only `*_mentioned` lists
    are emitted (deterministic gather). `needs_llm_adjudication: true` signals the
    LLM that stage/style/network classification requires heuristic judgment.
    """
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
        result["stages_mentioned"] = mentioned_terms(text, SUPER_STAGES)
        result["needs_llm_adjudication"] = True
    elif dimension == "competency":
        skills = parse_dreyfus_skills(text)
        result["skill_count"] = len(skills)
        result["avg_level"] = round(sum(s["level"] for s in skills) / len(skills), 1) if skills else 0
        result["top_skills"] = sorted(skills, key=lambda s: s["level"], reverse=True)[:3]
    elif dimension == "learning":
        result["styles_mentioned"] = mentioned_terms(text, KOLB_STYLES)
        result["needs_llm_adjudication"] = True
    elif dimension == "mentoring":
        result["network_types_mentioned"] = mentioned_terms(text, KRAM_NETWORK_TYPES)
        result["needs_llm_adjudication"] = True

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
            print(f"{'Stages Mentioned':<28s} {'Lines':<7s} {'Confidence'}")
        elif dim == "competency":
            print(f"{'Skills':<8s} {'Avg Lvl':<9s} {'Top Skill':<20s} {'Confidence'}")
        elif dim == "learning":
            print(f"{'Styles Mentioned':<22s} {'Lines':<7s} {'Confidence'}")
        elif dim == "mentoring":
            print(f"{'Network Types Mentioned':<24s} {'Lines':<7s} {'Confidence'}")

        print(f"  {'-'*12} {'-'*50}")

        for slug in ALL_CHARS:
            data = results[slug]["dimensions"][dim]
            display = results[slug]["display"]

            if not data["exists"]:
                print(f"  {display:<12s} MISSING")
                continue

            if dim == "career":
                stages = ", ".join(data["stages_mentioned"]) or "—"
                print(f"  {display:<12s} {stages:<28s} {data['lines']:<7d} {data['confidence']}")
            elif dim == "competency":
                top = data["top_skills"][0]["name"] if data.get("top_skills") else "—"
                print(f"  {display:<12s} {data['skill_count']:<8d} {data['avg_level']:<9.1f} {top:<20s} {data['confidence']}")
            elif dim == "learning":
                styles = ", ".join(data["styles_mentioned"]) or "—"
                print(f"  {display:<12s} {styles:<22s} {data['lines']:<7d} {data['confidence']}")
            elif dim == "mentoring":
                nets = ", ".join(data["network_types_mentioned"]) or "—"
                print(f"  {display:<12s} {nets:<24s} {data['lines']:<7d} {data['confidence']}")

    print(f"\n{'='*70}")
    print(f"  needs_llm_adjudication=true on career/learning/mentoring dims —")
    print(f"  LLM classifies stage/style/network from *_mentioned signal lists.")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
