"""Gather career data from growth/career-path.md, identity/core.md, and materials for LLM analysis."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import ALL_CHARS, CHAR_DISPLAY, MATERIALS, PROFILES, resolve_character
from platform_lib.markdown_parser import extract_sections, extract_frontmatter


CAREER_KEYWORDS = [
    "career", "job", "work", "salary", "lương", "nghề", "công việc",
    "company", "công ty", "position", "chức vụ", "role", "vai trò",
    "promotion", "thăng tiến", "resign", "nghỉ việc", "hire", "tuyển",
    "intern", "thực tập", "freelance", "part-time", "làm thêm",
    "SCCT", "super's", "life-career", "career stage", "trajectory",
    "decision", "quyết định", "inflection", "bước ngoặt",
]


def extract_career_from_profile(slug: str) -> dict:
    """Extract career data from growth/career-path.md."""
    career_file = PROFILES / slug / "growth" / "career-path.md"
    result = {"exists": False, "frontmatter": {}, "sections": {}, "lines": 0, "raw_text": ""}

    if not career_file.exists():
        return result

    text = career_file.read_text(encoding="utf-8")
    result["exists"] = True
    result["lines"] = len(text.splitlines())
    result["raw_text"] = text
    result["frontmatter"] = extract_frontmatter(career_file) or {}
    result["sections"] = extract_sections(career_file)
    return result


def extract_identity_career_section(slug: str) -> dict:
    """Extract career/education sections from identity/core.md."""
    identity_file = PROFILES / slug / "identity" / "core.md"
    result = {"exists": False, "career_section": "", "education_section": ""}

    if not identity_file.exists():
        return result

    result["exists"] = True
    sections = extract_sections(identity_file)

    for key, content in sections.items():
        key_lower = key.lower()
        if any(kw in key_lower for kw in ["career", "nghề nghiệp", "công việc", "work"]):
            result["career_section"] += content + "\n"
        if any(kw in key_lower for kw in ["education", "học vấn", "đại học", "trường"]):
            result["education_section"] += content + "\n"

    return result


def extract_milestones_career(slug: str) -> list[str]:
    """Extract career-relevant milestones."""
    milestones_file = PROFILES / slug / "milestones.md"
    if not milestones_file.exists():
        return []

    text = milestones_file.read_text(encoding="utf-8").lower()
    lines = text.splitlines()
    career_lines = []
    for line in lines:
        if any(kw in line for kw in ["career", "job", "work", "salary", "lương", "nghề",
                                      "công việc", "công ty", "thực tập", "làm thêm",
                                      "scholarship", "học bổng", "university", "đại học"]):
            career_lines.append(line.strip())
    return career_lines


def count_career_materials(slug: str) -> dict:
    """Count materials mentioning career-related keywords."""
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

        if any(kw.lower() in text for kw in CAREER_KEYWORDS):
            count += 1
            files.append(fpath.name)

    return {"count": count, "files": files[:10]}


def gather_character(slug: str) -> dict:
    """Gather all career data for one character."""
    return {
        "slug": slug,
        "display": CHAR_DISPLAY.get(slug, slug),
        "career_profile": extract_career_from_profile(slug),
        "identity_career": extract_identity_career_section(slug),
        "milestones_career": extract_milestones_career(slug),
        "materials_career": count_career_materials(slug),
    }


def main():
    parser = argparse.ArgumentParser(description="Gather career data for GRO analysis")
    parser.add_argument("--character", "-c", help="Character slug or alias")
    parser.add_argument("--json", dest="json_out", action="store_true", help="JSON output")
    parser.add_argument("--decisions-only", action="store_true", help="Show decision data only")
    args = parser.parse_args()

    chars = [resolve_character(args.character)] if args.character else ALL_CHARS
    results = {slug: gather_character(slug) for slug in chars}

    if args.decisions_only:
        for slug in results:
            cp = results[slug]["career_profile"]
            sections = cp.get("sections", {})
            decisions = {k: v for k, v in sections.items()
                         if any(kw in k.lower() for kw in ["decision", "quyết định", "key"])}
            results[slug] = {"slug": slug, "display": results[slug]["display"], "decisions": decisions}

    if args.json_out:
        for slug in results:
            if "career_profile" in results[slug]:
                results[slug]["career_profile"].pop("raw_text", None)
        print(json.dumps(results, indent=2, ensure_ascii=False, default=str))
        return

    for slug, data in results.items():
        display = data["display"]
        cp = data.get("career_profile", {})
        ic = data.get("identity_career", {})
        mc = data.get("materials_career", {})

        print(f"\n{'='*70}")
        print(f"  {display} ({slug}) — Career Data Gathering")
        print(f"{'='*70}")

        if args.decisions_only:
            decisions = data.get("decisions", {})
            if decisions:
                for heading, content in decisions.items():
                    print(f"\n  [{heading}]")
                    for line in content.splitlines()[:10]:
                        if line.strip():
                            print(f"    {line.strip()[:80]}")
            else:
                print(f"  No decision sections found")
            continue

        print(f"\n  [growth/career-path.md]")
        if cp["exists"]:
            print(f"  Lines: {cp['lines']}")
            print(f"  Confidence: {cp['frontmatter'].get('confidence', 'unknown')}")
            print(f"  Sections: {', '.join(cp['sections'].keys())[:80]}")
        else:
            print(f"  MISSING — file does not exist")

        print(f"\n  [identity/core.md — Career/Education]")
        if ic["exists"]:
            career_len = len(ic["career_section"].strip())
            edu_len = len(ic["education_section"].strip())
            print(f"  Career section: {career_len} chars")
            print(f"  Education section: {edu_len} chars")
        else:
            print(f"  MISSING — identity/core.md not found")

        print(f"\n  [Materials — Career Keywords]")
        print(f"  Matching files: {mc['count']}")
        if mc["files"]:
            for f in mc["files"][:5]:
                print(f"    - {f}")

        if data["milestones_career"]:
            print(f"\n  [Milestones — Career-relevant]")
            for m in data["milestones_career"][:5]:
                print(f"    - {m[:80]}")

    print(f"\n{'='*70}")
    print(f"  Summary: {len(results)} characters gathered")
    print(f"  Next: LLM analyzes career trajectory, decisions, inflection points")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
