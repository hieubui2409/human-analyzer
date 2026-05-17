#!/usr/bin/env python3
"""Parse WRITING-VOICE.md into structured JSON voice dimensions."""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.paths import resolve_character, character_dir, CHAR_DISPLAY
from platform_lib.markdown_parser import extract_sections
from platform_lib.formatters import print_json

VOICE_SECTION_MAP = {
    "tone": ["tone", "giọng", "tông"],
    "vocabulary": ["vocabulary", "từ vựng", "word", "ngôn ngữ"],
    "structure": ["structure", "cấu trúc", "format", "bố cục"],
    "thematic": ["theme", "chủ đề", "thematic", "topic"],
}


def classify_section(heading: str) -> str:
    h = heading.lower()
    for dim, keywords in VOICE_SECTION_MAP.items():
        if any(k in h for k in keywords):
            return dim
    return "other"


def extract_bullet_points(text: str) -> list[str]:
    bullets = []
    for line in text.splitlines():
        m = re.match(r"^\s*[-*•]\s+(.+)", line)
        if m:
            bullets.append(m.group(1).strip())
    return bullets


def main():
    parser = argparse.ArgumentParser(description="Extract structured voice profile from WRITING-VOICE.md")
    parser.add_argument("--character", default="hieu", help="Character name (default: hieu)")
    args = parser.parse_args()

    slug = resolve_character(args.character)
    cdir = character_dir(args.character)
    display = CHAR_DISPLAY.get(slug, slug)

    voice_path = cdir / "WRITING-VOICE.md"
    if not voice_path.exists():
        print_json({"error": f"WRITING-VOICE.md not found for {display} at {voice_path}"})
        sys.exit(1)

    sections_h2 = extract_sections(voice_path, level=2)
    sections_h3 = extract_sections(voice_path, level=3)

    profile = {
        "character": display,
        "source": str(voice_path),
        "tone_markers": [],
        "vocabulary_patterns": [],
        "structural_patterns": [],
        "thematic_constants": [],
        "other": [],
        "raw_sections": {},
    }

    all_sections = {**sections_h2, **sections_h3}
    for heading, content in all_sections.items():
        dim = classify_section(heading)
        bullets = extract_bullet_points(content)
        key_map = {
            "tone": "tone_markers",
            "vocabulary": "vocabulary_patterns",
            "structure": "structural_patterns",
            "thematic": "thematic_constants",
            "other": "other",
        }
        profile[key_map[dim]].extend(bullets)
        profile["raw_sections"][heading] = content[:300].strip()

    # Deduplicate
    for k in ["tone_markers", "vocabulary_patterns", "structural_patterns", "thematic_constants", "other"]:
        profile[k] = list(dict.fromkeys(profile[k]))

    print_json(profile)


if __name__ == "__main__":
    main()
