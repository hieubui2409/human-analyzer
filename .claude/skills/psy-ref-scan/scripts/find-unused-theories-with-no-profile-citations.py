#!/usr/bin/env python3
"""Find clinical theories in docs/references/ with zero citations across all character profiles, with suggested applications."""
import os
import sys
import argparse
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.paths import REFERENCES, ALL_CHARS, CHAR_DISPLAY, character_dir, CLINICAL_PROFILE_FILES
from platform_lib.clinical_terms import build_reference_index
from platform_lib.formatters import print_table, print_json

# Suggested characters per theory category based on project knowledge
CATEGORY_CHAR_HINTS = {
    "Rối Loạn & Sang Chấn": ["character-a", "character-b"],
    "Cơ Chế Bảo Vệ": ["character-a", "character-c"],
    "Gắn Bó & Quan Hệ": ["character-b", "character-a"],
    "Bản Sắc & Phát Triển": ["character-c", "character-b"],
    "Nhận Thức & Hành Vi": ["character-a", "character-c"],
    "Hệ Thống Gia Đình": ["character-b", "character-c"],
    "Hiện Sinh & Ý Nghĩa": ["character-a"],
    "Phục Hồi & Tăng Trưởng": ["character-a", "character-c"],
}


def is_cited_anywhere(theory_name: str, key_terms: list[str]) -> bool:
    """Return True if theory or any key term appears in ANY clinical profile file."""
    needle_theory = theory_name.lower()
    needles_terms = [t.lower() for t in key_terms if len(t) > 3]

    for char in ALL_CHARS:
        for fname in CLINICAL_PROFILE_FILES:
            fpath = character_dir(char) / fname
            if not fpath.exists():
                continue
            try:
                text = fpath.read_text(encoding="utf-8", errors="replace").lower()
            except Exception:
                continue
            if needle_theory in text:
                return True
            for term in needles_terms:
                if term in text:
                    return True
    return False


def suggest_characters(category: str) -> str:
    """Return suggested character names for a theory category."""
    hints = CATEGORY_CHAR_HINTS.get(category, ALL_CHARS)
    return ", ".join(CHAR_DISPLAY.get(c, c) for c in hints)


def main():
    parser = argparse.ArgumentParser(
        description="Find unused clinical theories with zero profile citations"
    )
    parser.add_argument("--category", help="Filter by theory category (partial match)")
    parser.add_argument("--suggest", action="store_true",
                        help="Show suggested profile applications")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    ref_index = build_reference_index(REFERENCES)
    if not ref_index:
        print("No reference index found. Check docs/references/INDEX.md")
        sys.exit(1)

    unused = []
    for theory_name, ref_data in sorted(ref_index.items()):
        if args.category and args.category.lower() not in ref_data.get("category", "").lower():
            continue
        key_terms = ref_data.get("key_terms", [])
        if not is_cited_anywhere(theory_name, key_terms):
            entry = {
                "theory": theory_name,
                "category": ref_data.get("category", ""),
                "file": ref_data.get("file", ""),
                "key_terms": key_terms[:3],
            }
            if args.suggest:
                entry["suggested_for"] = suggest_characters(ref_data.get("category", ""))
            unused.append(entry)

    total = len(ref_index)
    used_count = total - len(unused)

    if args.json:
        print_json({
            "total_theories": total,
            "used": used_count,
            "unused": len(unused),
            "unused_theories": unused,
        })
        return

    print(f"\n## Unused Clinical Theories\n")
    print(f"**Total theories:** {total}  |  **Used:** {used_count}  |  **Unused:** {len(unused)}\n")

    if not unused:
        print("All theories are cited in at least one profile.")
        return

    if args.suggest:
        headers = ["Theory", "Category", "Key Terms", "Suggest For"]
        rows = [[u["theory"][:40], u["category"][:25],
                 ", ".join(u["key_terms"])[:30],
                 u.get("suggested_for", "")]
                for u in unused]
        print_table(headers, rows)
    else:
        headers = ["Theory", "Category", "Key Terms"]
        rows = [[u["theory"][:45], u["category"][:25],
                 ", ".join(u["key_terms"])[:35]]
                for u in unused]
        print_table(headers, rows)

    print(f"\n_Run with --suggest to see recommended profile applications._")
    print(f"_Run with --category <name> to filter by category._")


if __name__ == "__main__":
    main()
