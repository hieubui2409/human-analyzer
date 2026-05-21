#!/usr/bin/env python3
"""Inventory the project memory directory: count by type, detect broken links, list by date."""
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.formatters import print_table, print_json

MEMORY_DIR = Path.home() / ".claude" / "projects" / "-home-hieubt-Documents-ck-marketing" / "memory"

MEMORY_TYPE_PATTERNS = {
    "user": re.compile(r"user|profile|hiếu|hieu", re.IGNORECASE),
    "feedback": re.compile(r"feedback|lesson|learned|calibrat", re.IGNORECASE),
    "project": re.compile(r"project|session|state|wave|arc", re.IGNORECASE),
    "reference": re.compile(r"reference|clinical|theory|ref-", re.IGNORECASE),
}

LINK_PATTERN = re.compile(r'\[\[([^\]]+)\]\]')


def classify_memory_type(filename: str, content: str) -> str:
    for mtype, pattern in MEMORY_TYPE_PATTERNS.items():
        if pattern.search(filename) or pattern.search(content[:200]):
            return mtype
    return "other"


def find_broken_links(filepath: Path, content: str) -> list[str]:
    broken = []
    for m in LINK_PATTERN.finditer(content):
        ref_name = m.group(1).strip()
        # Check if it's a file reference
        if "/" in ref_name or ref_name.endswith(".md"):
            ref_path = filepath.parent / ref_name
            if not ref_path.exists():
                broken.append(ref_name)
    return broken


def main():
    if not MEMORY_DIR.exists():
        print_json({
            "memory_dir": str(MEMORY_DIR),
            "exists": False,
            "note": "Memory directory not found. May use different path.",
        })
        sys.exit(0)

    files = sorted(MEMORY_DIR.iterdir(), key=lambda f: f.stat().st_mtime, reverse=True)
    md_files = [f for f in files if f.suffix == ".md"]

    counts_by_type: dict[str, int] = {}
    all_broken: list[dict] = []
    rows = []

    for f in md_files:
        content = f.read_text(encoding="utf-8", errors="replace")
        mtype = classify_memory_type(f.name, content)
        counts_by_type[mtype] = counts_by_type.get(mtype, 0) + 1
        broken = find_broken_links(f, content)
        for b in broken:
            all_broken.append({"file": f.name, "broken_link": b})
        size = f.stat().st_size
        mtime = f.stat().st_mtime
        import datetime
        date_str = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
        rows.append([f.name, mtype, date_str, f"{size}b", str(len(broken))])

    print(f"## Memory Inventory — {MEMORY_DIR}\n")
    print(f"Total files: {len(md_files)}\n")
    print("### By Type")
    for t, c in sorted(counts_by_type.items()):
        print(f"- {t}: {c}")
    print()
    print("### Files (newest first)")
    print_table(["File", "Type", "Date", "Size", "Broken Links"], rows)

    if all_broken:
        print(f"\n### Broken Links ({len(all_broken)} found)")
        print_table(["File", "Broken Link"], [[b["file"], b["broken_link"]] for b in all_broken])
    else:
        print("\n_No broken [[links]] found._")


if __name__ == "__main__":
    main()
