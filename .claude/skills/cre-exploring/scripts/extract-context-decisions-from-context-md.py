#!/usr/bin/env python3
"""Parse a CONTEXT.md file and extract locked decisions into structured JSON."""
import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.markdown_parser import extract_sections
from platform_lib.formatters import print_json

DECISION_MARKERS = re.compile(
    r'(LOCKED|DECIDED|DECISION|CONFIRMED|✅|🔒)',
    re.IGNORECASE
)
QUESTION_HEADER = re.compile(r'^(?:Q\d+|Question\s*\d*)[:\.]?\s*(.+)', re.IGNORECASE)


def extract_decisions(filepath: Path) -> list[dict]:
    if not filepath.exists():
        return []

    text = filepath.read_text(encoding='utf-8')
    decisions = []

    # Try to parse Q&A structure first (Q1/Q2... blocks)
    sections = extract_sections(filepath, level=2)
    for heading, content in sections.items():
        m = QUESTION_HEADER.match(heading.strip())
        question = m.group(1).strip() if m else heading.strip()
        decision_lines = []
        for line in content.splitlines():
            if DECISION_MARKERS.search(line):
                clean = re.sub(r'[✅🔒]', '', line).strip()
                clean = re.sub(r'\*+', '', clean).strip()
                if len(clean) > 5:
                    decision_lines.append(clean)
        if decision_lines:
            decisions.append({
                "question": question,
                "decisions": decision_lines,
            })

    # Fallback: scan line-by-line for LOCKED: patterns
    if not decisions:
        for line in text.splitlines():
            if DECISION_MARKERS.search(line):
                clean = re.sub(r'[✅🔒]', '', line).strip()
                if len(clean) > 5:
                    decisions.append({"question": "unknown", "decisions": [clean]})

    return decisions


def main():
    parser = argparse.ArgumentParser(description="Extract locked decisions from CONTEXT.md")
    parser.add_argument("--file", required=True, help="Path to CONTEXT.md file")
    args = parser.parse_args()

    fpath = Path(args.file)
    decisions = extract_decisions(fpath)
    result = {
        "source": str(fpath),
        "decision_count": sum(len(d["decisions"]) for d in decisions),
        "questions_with_decisions": len(decisions),
        "decisions": decisions,
    }
    if not decisions:
        result["note"] = "No locked decisions found. Check for LOCKED/DECIDED/✅/🔒 markers."
    print_json(result)


if __name__ == "__main__":
    main()
