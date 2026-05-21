"""Gather mentoring data from growth/mentoring-map.md, relationships/ files, and materials."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import (
    ALL_CHARS, CHAR_DISPLAY, MATERIALS, PROFILES, resolve_character, list_relationship_files,
)
from platform_lib.markdown_parser import extract_sections, extract_frontmatter


MENTORING_KEYWORDS = [
    "mentor", "mentee", "kram", "developmental network",
    "career function", "psychosocial", "sponsorship", "coaching",
    "role model", "counseling", "friendship", "protection",
    "hướng dẫn", "người hướng dẫn", "anh em kết nghĩa",
]


def extract_mentoring_from_profile(slug: str) -> dict:
    """Extract mentoring data from growth/mentoring-map.md."""
    mm_file = PROFILES / slug / "growth" / "mentoring-map.md"
    result = {"exists": False, "frontmatter": {}, "sections": {}, "lines": 0}

    if not mm_file.exists():
        return result

    text = mm_file.read_text(encoding="utf-8")
    result["exists"] = True
    result["lines"] = len(text.splitlines())
    result["frontmatter"] = extract_frontmatter(mm_file) or {}
    result["sections"] = extract_sections(mm_file)

    text_lower = text.lower()
    for typology in ["receptive", "traditional", "entrepreneurial", "opportunistic"]:
        if typology in text_lower:
            result["network_typology"] = typology
            break

    return result


def extract_relationship_files(slug: str) -> list[dict]:
    """Gather cross-relationship file summaries."""
    rel_files = list_relationship_files(slug)
    summaries = []
    for fpath in rel_files:
        text = fpath.read_text(encoding="utf-8")
        lines = len(text.splitlines())
        fm = extract_frontmatter(fpath) or {}
        has_mentoring = any(kw in text.lower() for kw in MENTORING_KEYWORDS)
        summaries.append({
            "file": fpath.name,
            "lines": lines,
            "relationship_type": fm.get("relationship", "unknown"),
            "has_mentoring_content": has_mentoring,
        })
    return summaries


def count_mentoring_materials(slug: str) -> dict:
    """Count materials mentioning mentoring-related keywords."""
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
        if any(kw.lower() in text for kw in MENTORING_KEYWORDS):
            count += 1
            files.append(fpath.name)

    return {"count": count, "files": files[:10]}


def gather_character(slug: str) -> dict:
    """Gather all mentoring data for one character."""
    mm = extract_mentoring_from_profile(slug)
    return {
        "slug": slug,
        "display": CHAR_DISPLAY.get(slug, slug),
        "mentoring_profile": mm,
        "relationship_files": extract_relationship_files(slug),
        "materials_mentoring": count_mentoring_materials(slug),
        "network_typology": mm.get("network_typology", "not detected"),
    }


def main():
    parser = argparse.ArgumentParser(description="Gather mentoring data for GRO analysis")
    parser.add_argument("--character", "-c", help="Character slug or alias")
    parser.add_argument("--json", dest="json_out", action="store_true", help="JSON output")
    args = parser.parse_args()

    chars = [resolve_character(args.character)] if args.character else ALL_CHARS
    results = {slug: gather_character(slug) for slug in chars}

    if args.json_out:
        print(json.dumps(results, indent=2, ensure_ascii=False, default=str))
        return

    for slug, data in results.items():
        display = data["display"]
        mm = data["mentoring_profile"]

        print(f"\n{'='*70}")
        print(f"  {display} ({slug}) — Mentoring Data Gathering")
        print(f"{'='*70}")

        print(f"\n  [growth/mentoring-map.md]")
        if mm["exists"]:
            print(f"  Lines: {mm['lines']}")
            print(f"  Network typology: {data['network_typology']}")
            print(f"  Confidence: {mm['frontmatter'].get('confidence', 'unknown')}")
            print(f"  Sections: {', '.join(mm['sections'].keys())[:80]}")
        else:
            print(f"  MISSING — file does not exist")

        rel = data["relationship_files"]
        print(f"\n  [Relationship Files]")
        if rel:
            for r in rel:
                mentor_icon = "✓" if r["has_mentoring_content"] else "—"
                print(f"    {mentor_icon} {r['file']} ({r['lines']} lines, {r['relationship_type']})")
        else:
            print(f"    No cross-relationship files found")

        mc = data["materials_mentoring"]
        print(f"\n  [Materials — Mentoring Keywords]")
        print(f"  Matching files: {mc['count']}")
        if mc["files"]:
            for f in mc["files"][:5]:
                print(f"    - {f}")

    print(f"\n{'='*70}")
    print(f"  Summary: {len(results)} characters gathered")
    print(f"  Next: LLM analyzes mentoring dynamics, Kram functions, network risks")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
