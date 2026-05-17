#!/usr/bin/env python3
"""Extract unanswered questions from CONTEXT.md exploration files."""
import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.formatters import print_table, eprint

QUESTION_PATTERN = re.compile(r'^\s*[-*]\s*\??\s*(.+\?)\s*$', re.MULTILINE)
ANSWERED_MARKERS = ["→", "=>", "answer:", "trả lời:", "resolved", "done"]


def extract_questions(filepath: Path) -> list[dict]:
    content = filepath.read_text(encoding="utf-8", errors="replace")
    results = []
    for m in QUESTION_PATTERN.finditer(content):
        q = m.group(1).strip()
        line_no = content[:m.start()].count("\n") + 1
        answered = any(marker in content[m.end():m.end()+200].lower() for marker in ANSWERED_MARKERS)
        results.append({"question": q[:80], "line": line_no, "answered": answered})
    return results


def main():
    parser = argparse.ArgumentParser(description="Extract unanswered questions from CONTEXT.md")
    parser.add_argument("--file", required=True, help="Path to CONTEXT.md")
    parser.add_argument("--unanswered-only", action="store_true")
    args = parser.parse_args()

    fp = Path(args.file)
    if not fp.exists():
        eprint(f"[ERR] File not found: {fp}")
        sys.exit(1)

    questions = extract_questions(fp)
    if args.unanswered_only:
        questions = [q for q in questions if not q["answered"]]

    eprint(f"[OK] {len(questions)} questions found")
    rows = [[str(q["line"]), "Y" if q["answered"] else "N", q["question"]] for q in questions]
    print_table(["Line", "Answered?", "Question"], rows)


if __name__ == "__main__":
    main()
