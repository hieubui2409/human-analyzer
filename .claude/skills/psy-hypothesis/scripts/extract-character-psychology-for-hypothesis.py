#!/usr/bin/env python3
"""Extract psychological profile elements needed for hypothesis generation."""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.paths import resolve_character, character_dir, CHAR_DISPLAY
from platform_lib.markdown_parser import extract_sections
from platform_lib.clinical_terms import scan_file_for_clinical_terms
from platform_lib.formatters import print_json

TRIGGER_KEYWORDS = [
    r'trigger', r'provok', r'activat', r'kích hoạt', r'phản ứng với',
    r'nhạy cảm với', r'bị ảnh hưởng',
]
ATTACHMENT_KEYWORDS = [
    r'attachment', r'gắn bó', r'secure', r'anxious', r'avoidant',
    r'disorganized', r'bám víu', r'né tránh',
]
DEFENSE_KEYWORDS = [
    r'defense', r'cơ chế phòng vệ', r'rationali', r'intellectuali',
    r'projection', r'denial', r'splitting', r'compartment', r'sublimation',
]


def extract_keyword_lines(text: str, patterns: list[str]) -> list[str]:
    hits = []
    compiled = [re.compile(p, re.IGNORECASE) for p in patterns]
    for line in text.splitlines():
        if any(c.search(line) for c in compiled):
            stripped = line.strip()
            if len(stripped) > 10:
                hits.append(stripped[:150])
    return list(dict.fromkeys(hits))[:15]


def main():
    parser = argparse.ArgumentParser(description="Extract psychological elements for hypothesis generation")
    parser.add_argument("--character", required=True, help="Character name or alias")
    args = parser.parse_args()

    slug = resolve_character(args.character)
    cdir = character_dir(args.character)
    display = CHAR_DISPLAY.get(slug, slug)

    result = {"character": display}

    # Triggers from DARKNESS.md
    dark_path = cdir / "DARKNESS.md"
    if dark_path.exists():
        dark_text = dark_path.read_text(encoding='utf-8')
        result["triggers"] = extract_keyword_lines(dark_text, TRIGGER_KEYWORDS)
        result["crisis_patterns"] = [
            t['context'] for t in scan_file_for_clinical_terms(dark_path)
            if any(k in t['term'].lower() for k in ['crisis', 'breakdown', 'suicid', 'harm'])
        ][:8]
    else:
        result["triggers"] = []
        result["crisis_patterns"] = []

    # Coping mechanisms from SOUL.md
    soul_path = cdir / "SOUL.md"
    if soul_path.exists():
        soul_text = soul_path.read_text(encoding='utf-8')
        soul_terms = scan_file_for_clinical_terms(soul_path)
        result["defense_mechanisms"] = list({t['term'] for t in soul_terms
                                             if any(re.search(p, t['term'], re.IGNORECASE) for p in DEFENSE_KEYWORDS)})[:8]
        result["coping_lines"] = extract_keyword_lines(soul_text, [r'coping', r'đối phó', r'ứng phó', r'cope'])
    else:
        result["defense_mechanisms"] = []
        result["coping_lines"] = []

    # Attachment from RELATIONSHIPS.md + CHARACTERISTIC.md
    attachment_lines = []
    for fname in ["RELATIONSHIPS.md", "CHARACTERISTIC.md"]:
        fpath = cdir / fname
        if fpath.exists():
            text = fpath.read_text(encoding='utf-8')
            attachment_lines.extend(extract_keyword_lines(text, ATTACHMENT_KEYWORDS))
    result["attachment_signals"] = list(dict.fromkeys(attachment_lines))[:10]

    print_json(result)


if __name__ == "__main__":
    main()
