#!/usr/bin/env python3
"""Extract growth/stagnation/regression indicators from profile files for arc analysis."""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.paths import resolve_character, character_dir, CHAR_DISPLAY
from platform_lib.markdown_parser import extract_sections, extract_milestones
from platform_lib.formatters import print_json

ADAPTIVE_COPING = [
    r"journaling", r"meditation", r"exercise", r"therapy", r"support\s+network",
    r"self[-\s]reflection", r"boundary", r"help[-\s]seeking", r"vulnerability",
    r"gratitude", r"meaning[-\s]making", r"post[-\s]traumatic\s+growth",
]
MALADAPTIVE_COPING = [
    r"avoidance", r"isolation", r"overwork", r"overachiev", r"numbing",
    r"rumination", r"self[-\s]blame", r"hypervigilance", r"suppression",
    r"intellectualiz", r"compartmentaliz", r"denial", r"fawn",
]
CRISIS_KEYWORDS = [
    r"breakdown", r"crisis", r"suicid", r"self[-\s]harm", r"collapse",
    r"rock\s+bottom", r"hospitali", r"meltdown", r"panic\s+attack",
]
PROTECTIVE_KEYWORDS = [
    r"mentor", r"community", r"purpose", r"achievement", r"scholarship",
    r"recognition", r"support", r"love", r"hope", r"progress", r"growth",
]


def count_pattern_matches(text: str, patterns: list[str]) -> list[str]:
    found = []
    for pat in patterns:
        if re.search(pat, text, re.IGNORECASE):
            found.append(pat.replace(r"[-\s]", "-").replace(r"\s+", " "))
    return found


def main():
    parser = argparse.ArgumentParser(description="Extract growth indicators from profile")
    parser.add_argument("--character", required=True, help="Character name or alias")
    args = parser.parse_args()

    slug = resolve_character(args.character)
    cdir = character_dir(args.character)
    display = CHAR_DISPLAY.get(slug, slug)

    result = {"character": display}

    # psychology/formulation.md coping mechanisms
    soul_path = cdir / "psychology" / "formulation.md"
    if soul_path.exists():
        soul_text = soul_path.read_text(encoding="utf-8")
        result["coping_adaptive"] = count_pattern_matches(soul_text, ADAPTIVE_COPING)
        result["coping_maladaptive"] = count_pattern_matches(soul_text, MALADAPTIVE_COPING)
    else:
        result["coping_adaptive"] = []
        result["coping_maladaptive"] = []

    # darkness/traumas.md crisis frequency
    dark_path = cdir / "darkness" / "traumas.md"
    if dark_path.exists():
        dark_text = dark_path.read_text(encoding="utf-8")
        result["crisis_keywords_found"] = count_pattern_matches(dark_text, CRISIS_KEYWORDS)
        result["crisis_event_count"] = len(result["crisis_keywords_found"])
    else:
        result["crisis_keywords_found"] = []
        result["crisis_event_count"] = 0

    # light/strengths-hope.md protective factors
    light_path = cdir / "light" / "strengths-hope.md"
    if light_path.exists():
        light_text = light_path.read_text(encoding="utf-8")
        result["protective_factors"] = count_pattern_matches(light_text, PROTECTIVE_KEYWORDS)
        result["protective_factor_strength"] = len(result["protective_factors"])
    else:
        result["protective_factors"] = []
        result["protective_factor_strength"] = 0

    # milestones.md achievement count
    milestones_path = cdir / "milestones.md"
    milestones = extract_milestones(milestones_path)
    achieved = [m for m in milestones if m.get("status") == "ACHIEVED"]
    result["milestone_count"] = len(milestones)
    result["milestones_achieved"] = len(achieved)

    result["adaptive_count"] = len(result["coping_adaptive"])
    result["maladaptive_count"] = len(result["coping_maladaptive"])

    print_json(result)


if __name__ == "__main__":
    main()
