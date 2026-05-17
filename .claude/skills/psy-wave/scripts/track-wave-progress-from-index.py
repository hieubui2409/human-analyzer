#!/usr/bin/env python3
"""Read wave progress from each character's INDEX.md and output a status table."""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.paths import ALL_CHARS, CHAR_DISPLAY, character_dir
from platform_lib.formatters import print_table

WAVE_PATTERN = re.compile(r"\[Wave\s*(\d)\s*:\s*([A-Z_]+)\]", re.IGNORECASE)


def parse_wave_status(char_slug: str) -> dict:
    index_path = character_dir(char_slug) / "INDEX.md"
    status = {"Wave 1": "UNKNOWN", "Wave 2": "UNKNOWN", "Wave 3": "UNKNOWN"}
    if not index_path.exists():
        return status
    text = index_path.read_text(encoding="utf-8")
    for m in WAVE_PATTERN.finditer(text):
        wave_num = m.group(1)
        wave_status = m.group(2).upper()
        key = f"Wave {wave_num}"
        if key in status:
            status[key] = wave_status
    return status


STATUS_ICONS = {
    "COMPLETE": "DONE",
    "IN_PROGRESS": "WIP",
    "NOT_STARTED": "---",
    "UNKNOWN": "?",
}


def main():
    headers = ["Character", "Wave 1", "Wave 2", "Wave 3"]
    rows = []
    for slug in ALL_CHARS:
        display = CHAR_DISPLAY.get(slug, slug)
        status = parse_wave_status(slug)
        rows.append([
            display,
            STATUS_ICONS.get(status["Wave 1"], status["Wave 1"]),
            STATUS_ICONS.get(status["Wave 2"], status["Wave 2"]),
            STATUS_ICONS.get(status["Wave 3"], status["Wave 3"]),
        ])
    print("## Wave Progress\n")
    print_table(headers, rows)


if __name__ == "__main__":
    main()
