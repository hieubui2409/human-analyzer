#!/usr/bin/env python3
"""Validate reference files against mandatory schema from docs/rules/10-reference-library-standard."""
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.paths import REFERENCES
from platform_lib.markdown_parser import extract_sections, extract_frontmatter
from platform_lib.formatters import print_table, eprint

REQUIRED_SECTIONS = [
    "Định nghĩa", "Biểu hiện", "Ứng dụng", "Tài liệu tham khảo"
]
REQUIRED_FRONTMATTER = ["category", "tags"]


def validate_ref(filepath: Path) -> dict:
    content = filepath.read_text(encoding="utf-8", errors="replace")
    fm = extract_frontmatter(filepath)
    sections = extract_sections(filepath)
    section_names = [h.lower() for h in sections.keys()]
    missing_sections = [s for s in REQUIRED_SECTIONS if not any(s.lower() in sn for sn in section_names)]
    missing_fm = [f for f in REQUIRED_FRONTMATTER if f not in fm]
    return {
        "file": filepath.name,
        "has_frontmatter": bool(fm),
        "missing_frontmatter": missing_fm,
        "section_count": len(sections),
        "missing_sections": missing_sections,
        "line_count": len(content.split("\n")),
        "valid": len(missing_sections) == 0 and len(missing_fm) == 0,
    }


def main():
    if not REFERENCES.exists():
        eprint("[ERR] docs/references/ not found")
        sys.exit(1)
    results = []
    for f in sorted(REFERENCES.glob("*.md")):
        if f.name == "INDEX.md":
            continue
        results.append(validate_ref(f))
    valid = sum(1 for r in results if r["valid"])
    eprint(f"[OK] {len(results)} refs: {valid} valid, {len(results)-valid} issues")
    rows = [[r["file"][:35], "Y" if r["valid"] else "N", str(r["section_count"]),
             ", ".join(r["missing_sections"][:2]) or "-",
             ", ".join(r["missing_frontmatter"]) or "-"]
            for r in results if not r["valid"]]
    if rows:
        print_table(["File", "Valid?", "Sections", "Missing Sections", "Missing FM"], rows)
    else:
        print("All reference files pass schema validation.")


if __name__ == "__main__":
    main()
