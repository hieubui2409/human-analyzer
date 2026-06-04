"""Analyze evidence coverage gaps per profile section for mat:indexer --coverage."""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import ALL_CHARS, CHAR_DISPLAY, MATERIALS, PROFILES, PROFILE_FILES, list_relationship_files, resolve_character
from platform_lib.materials_classifier import extract_frontmatter, SOURCE_TO_TIER


SECTION_KEYWORDS = {
    "INDEX.md": ["index", "overview", "summary"],
    "CURRENT-STATE.md": ["current", "state", "snapshot", "hiện tại"],
    "milestones.md": ["milestone", "achievement", "mốc"],
    "identity/core.md": ["identity", "career", "education", "family", "core", "nghề nghiệp"],
    "identity/writing-voice.md": ["writing", "voice", "tone", "style", "giọng văn"],
    "identity/achievements.md": ["achievement", "award", "scholarship", "học bổng", "giải thưởng"],
    "identity/media-coverage.md": ["media", "press", "news", "báo chí"],
    "psychology/core-wounds.md": ["wound", "trauma", "pain", "tổn thương", "core wound"],
    "psychology/defense-mechanisms.md": ["defense", "mechanism", "coping", "phòng vệ"],
    "psychology/attachment-style.md": ["attachment", "relationship", "gắn bó"],
    "psychology/growth-edges.md": ["growth", "edge", "development", "phát triển"],
    "psychology/formulation.md": ["formulation", "5P", "presenting", "predisposing"],
    "psychology/diagnostics.md": ["diagnostic", "big five", "ICD", "personality"],
    "psychology/cultural-formulation.md": ["cultural", "văn hóa", "context"],
    "psychology/archetype.md": ["archetype", "jungian", "pia melody"],
    "relationships/family.md": ["family", "relationship", "gia đình", "mối quan hệ"],
    "timeline/overview.md": ["timeline", "chronolog", "thời gian"],
    "timeline/state-timeline.md": ["state", "phase", "severity", "ICD-11"],
    "darkness/traumas.md": ["trauma", "darkness", "pain", "bóng tối"],
    "light/strengths-hope.md": ["strength", "hope", "resilience", "ánh sáng"],
    "evidence/conversations.md": ["conversation", "evidence", "quote", "bằng chứng"],
    "growth/career-path.md": ["career path", "trajectory", "salary", "SCCT", "super's", "life-career"],
    "growth/competencies.md": ["competency", "skill level", "dreyfus", "SFIA", "kỹ năng"],
    "growth/learning-profile.md": ["learning", "kolb", "study", "tự học", "learning style"],
    "growth/mentoring-map.md": ["mentor", "mentoring", "kram", "developmental network", "mentee"],
}


def count_material_references(slug: str, section: str) -> dict:
    """Count materials that reference a profile section via keyword matching."""
    mdir = MATERIALS / slug
    if not mdir.exists():
        return {"count": 0, "tiers": [], "materials": []}

    keywords = SECTION_KEYWORDS.get(section, [section.split("/")[-1].replace(".md", "").split("-")])
    if isinstance(keywords[0], list):
        keywords = keywords[0]

    count = 0
    tiers = []
    material_names = []

    for fpath in sorted(mdir.rglob("*.md")):
        if fpath.is_dir():
            continue
        try:
            text = fpath.read_text(encoding="utf-8").lower()
        except (OSError, UnicodeDecodeError):
            continue

        matched = any(kw.lower() in text for kw in keywords)
        if matched:
            count += 1
            fm = extract_frontmatter(fpath) or {}
            tier = SOURCE_TO_TIER.get(fm.get("source_category", ""), 5)
            tiers.append(tier)
            material_names.append(fpath.name)

    return {"count": count, "tiers": sorted(set(tiers)), "materials": material_names}


CROSS_REL_KEYWORDS = ["sworn", "kết nghĩa", "mentor", "mentee", "indirect", "relationship"]


def analyze_character(slug: str) -> list[dict]:
    """Analyze coverage for all profile sections (base + cross-relationship)."""
    sections = list(PROFILE_FILES)
    for rf in list_relationship_files(slug):
        rel_section = f"relationships/{rf.name}"
        sections.append(rel_section)
        if rel_section not in SECTION_KEYWORDS:
            SECTION_KEYWORDS[rel_section] = CROSS_REL_KEYWORDS + [rf.stem.replace("-", " ")]
    results = []
    for section in sections:
        refs = count_material_references(slug, section)
        if refs["count"] == 0:
            gap_status = "empty"
        elif refs["count"] <= 2:
            gap_status = "sparse"
        else:
            gap_status = "covered"

        results.append({
            "section": section,
            "material_count": refs["count"],
            "tiers_present": [f"T{t}" for t in refs["tiers"]],
            "gap_status": gap_status,
            "materials": refs["materials"][:5],
        })
    return results


def main():
    parser = argparse.ArgumentParser(description="Analyze evidence coverage gaps per profile section")
    parser.add_argument("--character", "-c", help="Single character slug")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    chars = [resolve_character(args.character)] if args.character else ALL_CHARS
    report = {}
    for slug in chars:
        report[slug] = analyze_character(slug)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return

    for slug, results in report.items():
        display = CHAR_DISPLAY.get(slug, slug)
        covered = sum(1 for r in results if r["gap_status"] == "covered")
        sparse = sum(1 for r in results if r["gap_status"] == "sparse")
        empty = sum(1 for r in results if r["gap_status"] == "empty")

        print(f"\n{'='*70}")
        print(f"  {display} ({slug}) — {covered} covered | {sparse} sparse | {empty} empty")
        print(f"{'='*70}")
        print(f"  {'Section':<40s} {'Mats':<5s} {'Tiers':<12s} {'Status':<8s}")
        print(f"  {'-'*40} {'-'*5} {'-'*12} {'-'*8}")

        for r in results:
            icon = {"covered": "✓", "sparse": "~", "empty": "✗"}[r["gap_status"]]
            tiers_str = ",".join(r["tiers_present"]) if r["tiers_present"] else "—"
            print(f"  {icon} {r['section']:<38s} {r['material_count']:<5d} {tiers_str:<12s} {r['gap_status']:<8s}")


if __name__ == "__main__":
    main()
