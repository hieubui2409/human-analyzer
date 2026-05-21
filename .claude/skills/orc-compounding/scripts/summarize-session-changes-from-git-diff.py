#!/usr/bin/env python3
"""Summarize what changed this session: categorize files, net line changes, characters affected."""
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.paths import ROOT, ALL_CHARS, CHAR_DISPLAY
from platform_lib.formatters import print_json

FILE_CATEGORIES = {
    "profiles": re.compile(r"docs/profiles/"),
    "materials": re.compile(r"docs/materials/"),
    "references": re.compile(r"docs/references/"),
    "assets": re.compile(r"^assets/"),
    "plans": re.compile(r"^plans/"),
    "skills": re.compile(r"\.claude/skills/"),
    "config": re.compile(r"\.claude/(?!skills)"),
    "rules": re.compile(r"docs/rules/"),
}


def run_git(args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["git"] + args, capture_output=True, text=True,
            cwd=str(ROOT), timeout=15
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""


def categorize_file(path: str) -> str:
    for cat, pattern in FILE_CATEGORIES.items():
        if pattern.search(path):
            return cat
    return "other"


def detect_character(path: str) -> str | None:
    for slug in ALL_CHARS:
        if slug in path:
            return CHAR_DISPLAY.get(slug, slug)
    return None


def main():
    # Get diff stat for unstaged + staged changes
    diff_stat = run_git(["diff", "--stat", "HEAD"])
    if not diff_stat:
        diff_stat = run_git(["diff", "--stat"])

    # Get list of changed files
    changed_files_raw = run_git(["diff", "--name-only", "HEAD"])
    if not changed_files_raw:
        changed_files_raw = run_git(["diff", "--name-only"])

    # Also get staged
    staged_raw = run_git(["diff", "--cached", "--name-only"])
    untracked_raw = run_git(["ls-files", "--others", "--exclude-standard"])

    all_files = set()
    for raw in [changed_files_raw, staged_raw, untracked_raw]:
        if raw:
            all_files.update(raw.splitlines())

    categorized: dict[str, list[str]] = {cat: [] for cat in FILE_CATEGORIES}
    categorized["other"] = []
    characters_affected = set()

    for f in sorted(all_files):
        cat = categorize_file(f)
        categorized[cat].append(f)
        char = detect_character(f)
        if char:
            characters_affected.add(char)

    # Net line changes from diff stat summary
    net_lines = {"added": 0, "deleted": 0}
    for line in diff_stat.splitlines():
        m = re.search(r'(\d+) insertion', line)
        if m:
            net_lines["added"] += int(m.group(1))
        m = re.search(r'(\d+) deletion', line)
        if m:
            net_lines["deleted"] += int(m.group(1))

    result = {
        "total_files_changed": len(all_files),
        "characters_affected": sorted(characters_affected),
        "net_lines": net_lines,
        "files_by_category": {k: v for k, v in categorized.items() if v},
        "diff_summary": diff_stat[:800] if diff_stat else "(no diff found — may already be committed)",
    }
    print_json(result)


if __name__ == "__main__":
    main()
