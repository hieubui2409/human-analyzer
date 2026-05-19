#!/usr/bin/env python3
"""Parse light/strengths-hope.md for protective factors: support network, coping strategies, future goals, resilience.
Categorizes internal vs external factors for LLM risk assessment."""
import os
import sys
import argparse
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.paths import resolve_character, character_dir, CHAR_DISPLAY, ALL_CHARS
from platform_lib.markdown_parser import extract_sections
from platform_lib.formatters import print_json, print_table

# Keywords that suggest internal protective factors
INTERNAL_KEYWORDS = re.compile(
    r"\b(resilience|kiên cường|self[\s-]?efficacy|tự tin|agency|meaning|ý nghĩa|purpose|mục đích"
    r"|hope|hy vọng|faith|niềm tin|identity|bản sắc|strength|điểm mạnh|coping|creativity"
    r"|intrinsic|nội tâm|spirituality|tâm linh)\b",
    re.IGNORECASE,
)

# Keywords that suggest external protective factors
EXTERNAL_KEYWORDS = re.compile(
    r"\b(support|hỗ trợ|friend|bạn|family|gia đình|mentor|thầy|community|cộng đồng"
    r"|network|mạng lưới|relationship|quan hệ|connection|kết nối|resource|nguồn lực"
    r"|therapy|therapist|counselor|tư vấn|peer|đồng nghiệp|club|nhóm|organization|tổ chức)\b",
    re.IGNORECASE,
)

# Keywords for future goals
GOAL_KEYWORDS = re.compile(
    r"\b(goal|mục tiêu|dream|ước mơ|plan|kế hoạch|future|tương lai|aspiration|khát vọng"
    r"|ambition|tham vọng|hope to|muốn|want to|study|học|career|sự nghiệp|graduate|tốt nghiệp)\b",
    re.IGNORECASE,
)


def classify_line(line: str) -> list[str]:
    categories = []
    if INTERNAL_KEYWORDS.search(line):
        categories.append("internal")
    if EXTERNAL_KEYWORDS.search(line):
        categories.append("external")
    if GOAL_KEYWORDS.search(line):
        categories.append("future_goal")
    return categories if categories else ["uncategorized"]


def extract_factors(char_slug: str) -> dict:
    cdir = character_dir(char_slug)
    display = CHAR_DISPLAY.get(char_slug, char_slug)
    light_file = cdir / "light/strengths-hope.md"

    if not light_file.exists():
        return {"character": display, "slug": char_slug, "error": "light/strengths-hope.md not found", "factors": []}

    sections = extract_sections(light_file, level=2)
    factors = []

    # Also scan line by line for bullet points
    lines = light_file.read_text(encoding="utf-8").splitlines()
    current_section = "General"
    for i, line in enumerate(lines):
        h = re.match(r"^#{2,3}\s+(.+)", line)
        if h:
            current_section = h.group(1).strip()
            continue
        stripped = line.strip()
        if stripped.startswith(("-", "*", "•")) and len(stripped) > 5:
            content = re.sub(r"^[-*•]\s*", "", stripped)
            cats = classify_line(content)
            factors.append({
                "section": current_section,
                "line_no": i + 1,
                "content": content[:120],
                "categories": cats,
            })

    # Summarize counts
    internal = [f for f in factors if "internal" in f["categories"]]
    external = [f for f in factors if "external" in f["categories"]]
    goals = [f for f in factors if "future_goal" in f["categories"]]

    return {
        "character": display,
        "slug": char_slug,
        "total_factors": len(factors),
        "internal_count": len(internal),
        "external_count": len(external),
        "future_goals_count": len(goals),
        "factors": factors,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Extract protective factors from light/strengths-hope.md (internal vs external categorization)"
    )
    parser.add_argument("--character", help="Character alias or canonical name")
    parser.add_argument("--all", dest="all_chars", action="store_true", help="Process all characters")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--summary", action="store_true", help="Summary table only, no detail")
    args = parser.parse_args()

    if not args.character and not args.all_chars:
        parser.error("Provide --character <name> or --all")

    targets = ALL_CHARS if args.all_chars else [resolve_character(args.character)]
    results = [extract_factors(slug) for slug in targets]

    if args.json:
        print_json(results)
        return

    for r in results:
        print(f"\n## Protective Factors: {r['character']}")
        if "error" in r:
            print(f"  ERROR: {r['error']}")
            continue
        print(f"  Internal: {r['internal_count']}  |  External: {r['external_count']}  |  Future Goals: {r['future_goals_count']}")
        if args.summary:
            continue
        if not r["factors"]:
            print("  No bullet-point factors found in light/strengths-hope.md")
            continue
        headers = ["L#", "Section", "Categories", "Content (truncated)"]
        rows = [[str(f["line_no"]), f["section"][:25], ",".join(f["categories"]), f["content"][:70]] for f in r["factors"]]
        print_table(headers, rows)

    print("\n**NOTE**: Categorization is keyword-based. LLM should verify and assess protective factor strength.")


if __name__ == "__main__":
    main()
