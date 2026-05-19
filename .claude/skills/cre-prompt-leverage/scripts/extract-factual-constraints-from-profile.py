#!/usr/bin/env python3
"""Extract hard factual constraints from profile files for prompt strengthening."""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.paths import resolve_character, character_dir, CHAR_DISPLAY
from platform_lib.markdown_parser import extract_sections, extract_timeline_events
from platform_lib.formatters import print_json

DOB_PATTERN = re.compile(r'(?:sinh|born|DOB|ngày sinh)[^\d]*(\d{2}/\d{2}/\d{4})', re.IGNORECASE)
AGE_PATTERN = re.compile(r'(\d{1,2})\s*tuổi|age[:\s]+(\d{1,2})', re.IGNORECASE)
LOCATION_PATTERN = re.compile(
    r'(?:tại|ở|location|địa chỉ|quê)[:\s]+([^\n,\.]{3,40})', re.IGNORECASE
)
OCCUPATION_PATTERN = re.compile(
    r'(?:nghề nghiệp|occupation|job|chức vụ|vị trí|engineer|developer|student)[:\s]*([^\n]{3,60})',
    re.IGNORECASE
)


def extract_identity_facts(cdir) -> dict:
    facts = {}
    id_path = cdir / "identity/core.md"
    if not id_path.exists():
        return facts
    text = id_path.read_text(encoding='utf-8')

    m = DOB_PATTERN.search(text)
    if m:
        facts["dob"] = m.group(1)

    m = AGE_PATTERN.search(text)
    if m:
        facts["age"] = m.group(1) or m.group(2)

    locs = LOCATION_PATTERN.findall(text)
    if locs:
        facts["location"] = locs[0].strip()

    occs = OCCUPATION_PATTERN.findall(text)
    if occs:
        facts["occupation"] = occs[0].strip()[:80]

    # Extract key facts section if present
    sections = extract_sections(id_path, level=2)
    for heading, content in sections.items():
        if any(k in heading.lower() for k in ['thông tin', 'basic', 'key fact', 'tóm tắt']):
            bullets = []
            for line in content.splitlines():
                m2 = re.match(r'\s*[-*]\s+(.+)', line)
                if m2:
                    bullets.append(m2.group(1).strip()[:100])
            if bullets:
                facts["key_identity_facts"] = bullets[:8]
            break

    return facts


def extract_relationship_status(cdir) -> dict:
    rel_path = cdir / "relationships/family.md"
    if not rel_path.exists():
        return {}
    text = rel_path.read_text(encoding='utf-8')
    sections = extract_sections(rel_path, level=2)
    summary = {}
    for heading, content in sections.items():
        if any(k in heading.lower() for k in ['status', 'tình trạng', 'summary', 'tóm tắt', 'current']):
            bullets = [re.match(r'\s*[-*]\s+(.+)', l) for l in content.splitlines()]
            summary[heading] = [b.group(1).strip()[:100] for b in bullets if b][:5]
    return summary


def extract_recent_timeline(cdir) -> list[dict]:
    tl_path = cdir / "timeline/overview.md"
    events = extract_timeline_events(tl_path)
    # Return last 5 events as "current state"
    return events[-5:] if events else []


def main():
    parser = argparse.ArgumentParser(description="Extract factual constraints for prompt strengthening")
    parser.add_argument("--character", required=True, help="Character name or alias")
    args = parser.parse_args()

    slug = resolve_character(args.character)
    cdir = character_dir(args.character)
    display = CHAR_DISPLAY.get(slug, slug)

    result = {
        "character": display,
        "identity": extract_identity_facts(cdir),
        "relationship_status": extract_relationship_status(cdir),
        "recent_timeline": extract_recent_timeline(cdir),
    }
    print_json(result)


if __name__ == "__main__":
    main()
