#!/usr/bin/env python3
"""Extract hard factual constraints from profile files for prompt strengthening."""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.paths import resolve_character, character_dir, CHAR_DISPLAY, list_relationship_files
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


TABLE_ROW = re.compile(r'\|\s*\*?\*?(.+?)\*?\*?\s*\|\s*(.+?)\s*\|')

def _extract_table_field(text: str, keys: list[str]) -> str | None:
    for line in text.splitlines():
        m = TABLE_ROW.match(line.strip())
        if m:
            label = m.group(1).strip().strip("*").lower()
            if any(k in label for k in keys):
                return m.group(2).strip()
    return None


def extract_identity_facts(cdir) -> dict:
    facts = {}
    id_path = cdir / "identity/core.md"
    if not id_path.exists():
        return facts
    text = id_path.read_text(encoding='utf-8')

    dob = _extract_table_field(text, ["ngày sinh", "dob", "born"])
    if dob:
        facts["dob"] = dob
    elif (m := DOB_PATTERN.search(text)):
        facts["dob"] = m.group(1)

    age = _extract_table_field(text, ["tuổi", "age"])
    if age:
        facts["age"] = re.sub(r'[^\d]', '', age)[:3]
    elif (m := AGE_PATTERN.search(text)):
        facts["age"] = m.group(1) or m.group(2)

    loc = _extract_table_field(text, ["quê", "nơi ở", "location", "địa chỉ"])
    if loc:
        facts["location"] = loc[:60]
    elif (locs := LOCATION_PATTERN.findall(text)):
        facts["location"] = locs[0].strip()

    occ = _extract_table_field(text, ["nghề", "vị trí", "chức vụ", "occupation", "job"])
    if occ and "|" not in occ:
        facts["occupation"] = occ[:80]
    else:
        career_pat = re.compile(r'\|\s*[\d/\-]+present\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|')
        student_pat = re.compile(r'\|\s*\d{4}-\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|')
        cm = career_pat.search(text)
        if cm:
            facts["occupation"] = f"{cm.group(1).strip()} @ {cm.group(2).strip()}"[:80]
        elif (sm := student_pat.search(text)):
            facts["occupation"] = f"{sm.group(2).strip()} @ {sm.group(1).strip()}"[:80]
        elif re.search(r'học sinh|sinh viên|student', text, re.IGNORECASE):
            facts["occupation"] = "Học sinh/Sinh viên"

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
    rel_files = [cdir / "relationships/family.md"]
    slug = cdir.name
    rel_files.extend(list_relationship_files(slug))
    summary = {}
    keywords = ['status', 'tình trạng', 'summary', 'tóm tắt', 'current', 'mối quan hệ', 'vai trò']
    for rel_path in rel_files:
        if not rel_path.exists():
            continue
        for level in (2, 3):
            sections = extract_sections(rel_path, level=level)
            for heading, content in sections.items():
                if any(k in heading.lower() for k in keywords):
                    items = []
                    for line in content.splitlines():
                        bm = re.match(r'\s*[-*]\s+(.+)', line)
                        if bm:
                            items.append(bm.group(1).strip()[:100])
                        tm = TABLE_ROW.match(line.strip())
                        if tm and not line.strip().startswith("| ---"):
                            items.append(f"{tm.group(1).strip()}: {tm.group(2).strip()}"[:100])
                    if items:
                        label = f"{heading} ({rel_path.stem})" if level == 3 else heading
                        summary[label] = items[:5]
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
