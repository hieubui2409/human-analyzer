#!/usr/bin/env python3
"""Check if wave gate requirements are met for a character."""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.paths import resolve_character, character_dir, CHAR_DISPLAY
from platform_lib.markdown_parser import extract_sections, extract_tags
from platform_lib.formatters import print_json

WAVE1_REQUIRED_SECTIONS = {
    "IDENTITY.md": ["Thông tin cơ bản", "Học vấn", "Nghề nghiệp"],
    "TIMELINE.md": [],  # just needs to be non-empty
}
WAVE1_CONFIDENTIAL_FILES = ["IDENTITY.md", "RELATIONSHIPS.md"]

WAVE2_REQUIRED_SECTIONS = {
    "SOUL.md": [],
    "DARKNESS.md": [],
    "LIGHT.md": [],
}
WAVE2_CLINICAL_REFS_FILES = ["SOUL.md", "DARKNESS.md", "CHARACTERISTIC.md"]


def check_wave1(char_dir_path):
    issues = []
    for fname, sections in WAVE1_REQUIRED_SECTIONS.items():
        fpath = char_dir_path / fname
        if not fpath.exists():
            issues.append(f"MISSING: {fname}")
            continue
        text = fpath.read_text(encoding="utf-8")
        if len(text.strip()) < 100:
            issues.append(f"TOO_SPARSE: {fname} (<100 chars)")
        for sec in sections:
            extracted = extract_sections(fpath, level=2)
            if sec not in extracted and not any(sec.lower() in k.lower() for k in extracted):
                issues.append(f"MISSING_SECTION: {fname} → {sec}")

    # Check confidential tags applied
    for fname in WAVE1_CONFIDENTIAL_FILES:
        fpath = char_dir_path / fname
        if not fpath.exists():
            continue
        text = fpath.read_text(encoding="utf-8")
        tags = extract_tags(text)
        if not tags:
            issues.append(f"NO_CONFIDENTIAL_TAGS: {fname}")

    return issues


def check_wave2(char_dir_path):
    issues = []
    for fname in WAVE2_REQUIRED_SECTIONS:
        fpath = char_dir_path / fname
        if not fpath.exists():
            issues.append(f"MISSING: {fname}")
            continue
        text = fpath.read_text(encoding="utf-8").strip()
        if len(text) < 200:
            issues.append(f"TOO_SPARSE: {fname} (<200 chars)")

    # Check clinical refs linked (look for [[ref]] or (ref) links)
    import re
    ref_pattern = re.compile(r"\[\[.+?\]\]|\[.+?\]\(docs/references/")
    for fname in WAVE2_CLINICAL_REFS_FILES:
        fpath = char_dir_path / fname
        if not fpath.exists():
            continue
        text = fpath.read_text(encoding="utf-8")
        if not ref_pattern.search(text):
            issues.append(f"NO_CLINICAL_REF_LINKS: {fname}")

    return issues


def check_wave3(char_dir_path):
    issues = []
    # Wave 3 gate: wave 2 complete + cross-validation done
    required = ["SOUL.md", "DARKNESS.md", "LIGHT.md", "MILESTONES.md", "CHARACTERISTIC.md"]
    for fname in required:
        fpath = char_dir_path / fname
        if not fpath.exists():
            issues.append(f"MISSING: {fname}")
            continue
        if len(fpath.read_text(encoding="utf-8").strip()) < 300:
            issues.append(f"INSUFFICIENT: {fname}")
    return issues


def main():
    parser = argparse.ArgumentParser(description="Check wave gate requirements")
    parser.add_argument("--character", required=True, help="Character name or alias")
    parser.add_argument("--wave", required=True, choices=["1", "2", "3"], help="Wave number to check gate for")
    args = parser.parse_args()

    slug = resolve_character(args.character)
    cdir = character_dir(args.character)
    display = CHAR_DISPLAY.get(slug, slug)

    if args.wave == "1":
        issues = check_wave1(cdir)
        gate_label = "Wave 1→2"
    elif args.wave == "2":
        issues = check_wave2(cdir)
        gate_label = "Wave 2→3"
    else:
        issues = check_wave3(cdir)
        gate_label = "Wave 3 Completion"

    passed = len(issues) == 0
    result = {
        "character": display,
        "gate": gate_label,
        "passed": passed,
        "issue_count": len(issues),
        "issues": issues,
    }
    print_json(result)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
