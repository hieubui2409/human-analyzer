"""Gather learning data from growth/learning-profile.md and materials for LLM analysis."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import ALL_CHARS, CHAR_DISPLAY, MATERIALS, PROFILES, resolve_character
from platform_lib.markdown_parser import extract_sections, extract_frontmatter


KOLB_STYLES = {
    "diverging": "CE + RO — Imaginative, emotional, brainstorming",
    "assimilating": "AC + RO — Logical, analytical, theory-building",
    "converging": "AC + AE — Practical, problem-solving, technical",
    "accommodating": "CE + AE — Hands-on, risk-taking, action-oriented",
}

LEARNING_KEYWORDS = [
    "learn", "học", "study", "nghiên cứu", "tự học",
    "kolb", "learning style", "phong cách học",
    "concrete experience", "reflective observation",
    "abstract conceptualization", "active experimentation",
    "CE", "RO", "AC", "AE",
    "cognitive", "nhận thức", "problem-solving",
]


def extract_learning_from_profile(slug: str) -> dict:
    """Extract learning data from growth/learning-profile.md."""
    lp_file = PROFILES / slug / "growth" / "learning-profile.md"
    result = {"exists": False, "frontmatter": {}, "sections": {}, "lines": 0,
              "detected_style": None, "raw_text": ""}

    if not lp_file.exists():
        return result

    text = lp_file.read_text(encoding="utf-8")
    result["exists"] = True
    result["lines"] = len(text.splitlines())
    result["raw_text"] = text
    result["frontmatter"] = extract_frontmatter(lp_file) or {}
    result["sections"] = extract_sections(lp_file)

    text_lower = text.lower()
    for style in KOLB_STYLES:
        if style in text_lower:
            result["detected_style"] = style
            break

    return result


def extract_education_context(slug: str) -> dict:
    """Extract education data from identity/core.md."""
    identity_file = PROFILES / slug / "identity" / "core.md"
    result = {"exists": False, "education_section": ""}

    if not identity_file.exists():
        return result

    result["exists"] = True
    sections = extract_sections(identity_file)

    for key, content in sections.items():
        key_lower = key.lower()
        if any(kw in key_lower for kw in ["education", "học vấn", "đại học", "trường", "học tập"]):
            result["education_section"] += content + "\n"

    return result


def extract_growth_edges_learning(slug: str) -> list[str]:
    """Extract learning-relevant growth edges from psychology/growth-edges.md."""
    ge_file = PROFILES / slug / "psychology" / "growth-edges.md"
    if not ge_file.exists():
        return []

    text = ge_file.read_text(encoding="utf-8")
    lines = text.splitlines()
    relevant = []
    for line in lines:
        line_lower = line.lower()
        if any(kw in line_lower for kw in ["learn", "học", "cognitive", "nhận thức",
                                            "study", "academic", "metacognition"]):
            relevant.append(line.strip())
    return relevant[:10]


def count_learning_materials(slug: str) -> dict:
    """Count materials mentioning learning-related keywords."""
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
        if any(kw.lower() in text for kw in LEARNING_KEYWORDS):
            count += 1
            files.append(fpath.name)

    return {"count": count, "files": files[:10]}


def gather_character(slug: str) -> dict:
    """Gather all learning data for one character."""
    lp = extract_learning_from_profile(slug)
    return {
        "slug": slug,
        "display": CHAR_DISPLAY.get(slug, slug),
        "learning_profile": lp,
        "education_context": extract_education_context(slug),
        "growth_edges_learning": extract_growth_edges_learning(slug),
        "materials_learning": count_learning_materials(slug),
        "kolb_style": lp["detected_style"],
    }


def main():
    parser = argparse.ArgumentParser(description="Gather learning data for GRO analysis")
    parser.add_argument("--character", "-c", help="Character slug or alias")
    parser.add_argument("--json", dest="json_out", action="store_true", help="JSON output")
    args = parser.parse_args()

    chars = [resolve_character(args.character)] if args.character else ALL_CHARS
    results = {slug: gather_character(slug) for slug in chars}

    if args.json_out:
        for slug in results:
            results[slug]["learning_profile"].pop("raw_text", None)
        print(json.dumps(results, indent=2, ensure_ascii=False, default=str))
        return

    for slug, data in results.items():
        display = data["display"]
        lp = data["learning_profile"]
        ec = data["education_context"]

        print(f"\n{'='*70}")
        print(f"  {display} ({slug}) — Learning Data Gathering")
        print(f"{'='*70}")

        print(f"\n  [growth/learning-profile.md]")
        if lp["exists"]:
            print(f"  Lines: {lp['lines']}")
            print(f"  Detected Kolb style: {data['kolb_style'] or 'not detected'}")
            if data["kolb_style"]:
                print(f"  Description: {KOLB_STYLES.get(data['kolb_style'], '')}")
            print(f"  Confidence: {lp['frontmatter'].get('confidence', 'unknown')}")
            print(f"  Sections: {', '.join(lp['sections'].keys())[:80]}")
        else:
            print(f"  MISSING — file does not exist")

        print(f"\n  [identity/core.md — Education]")
        if ec["exists"]:
            edu_len = len(ec["education_section"].strip())
            print(f"  Education section: {edu_len} chars")
        else:
            print(f"  MISSING — identity/core.md not found")

        if data["growth_edges_learning"]:
            print(f"\n  [Growth Edges — Learning-relevant]")
            for g in data["growth_edges_learning"][:5]:
                print(f"    - {g[:80]}")

        mc = data["materials_learning"]
        print(f"\n  [Materials — Learning Keywords]")
        print(f"  Matching files: {mc['count']}")

    print(f"\n{'='*70}")
    print(f"  Summary: {len(results)} characters gathered")
    print(f"  Next: LLM maps cognitive style, learning patterns, content implications")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
