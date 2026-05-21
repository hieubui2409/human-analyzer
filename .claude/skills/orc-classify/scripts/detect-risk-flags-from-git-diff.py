#!/usr/bin/env python3
"""Extract risk signals from git diff file list for LLM-based risk classification.

This script GATHERS risk flags only. It does NOT decide the risk mode.
The LLM reads these signals and makes the tiny/normal/high_risk decision.
"""
import os
import sys
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.paths import ALL_CHARS, CHAR_DISPLAY
from platform_lib.formatters import print_json, severity_badge

# Risk flag definitions
FLAGS = [
    {
        "id": "multi_char_touch",
        "desc": "Multiple character profiles touched in one diff",
        "severity": "HIGH",
        "check": "multi_char",
    },
    {
        "id": "soul_timeline_same_char",
        "desc": "formulation.md + timeline/overview.md modified for same character",
        "severity": "HIGH",
        "check": "soul_timeline",
    },
    {
        "id": "profiles_and_references",
        "desc": "Profile files AND docs/references/ both touched",
        "severity": "MEDIUM",
        "check": "profiles_refs",
    },
    {
        "id": "real_name_in_assets",
        "desc": "assets/ files touched (possible real-name exposure)",
        "severity": "MEDIUM",
        "check": "assets_touch",
    },
    {
        "id": "darkness_soul_combo",
        "desc": "darkness/traumas.md + psychology/formulation.md modified together",
        "severity": "HIGH",
        "check": "darkness_soul",
    },
    {
        "id": "rules_modified",
        "desc": "docs/rules/ files modified",
        "severity": "MEDIUM",
        "check": "rules_touch",
    },
]



def parse_files(diff_files: list[str]) -> dict:
    """Parse file list into structured categories."""
    chars_touched = set()
    file_map = {c: {"files": [], "soul": False, "timeline": False, "darkness": False} for c in ALL_CHARS}
    has_references = False
    has_assets = False
    has_rules = False

    for f in diff_files:
        f = f.strip()
        if not f:
            continue
        for char in ALL_CHARS:
            if f"profiles/{char}/" in f or f"materials/{char}/" in f:
                chars_touched.add(char)
                file_map[char]["files"].append(f)
                if "formulation.md" in f or "core-wounds.md" in f:
                    file_map[char]["soul"] = True
                if "overview.md" in f and "timeline/" in f:
                    file_map[char]["timeline"] = True
                if "traumas.md" in f:
                    file_map[char]["darkness"] = True
        if "docs/references/" in f:
            has_references = True
        if f.startswith("assets/"):
            has_assets = True
        if "docs/rules/" in f:
            has_rules = True

    return {
        "chars_touched": list(chars_touched),
        "file_map": file_map,
        "has_references": has_references,
        "has_assets": has_assets,
        "has_rules": has_rules,
        "has_profiles": len(chars_touched) > 0,
    }


def detect_flags(ctx: dict) -> list[dict]:
    triggered = []
    checks = {
        "multi_char": len(ctx["chars_touched"]) > 1,
        "soul_timeline": any(
            ctx["file_map"][c]["soul"] and ctx["file_map"][c]["timeline"]
            for c in ctx["chars_touched"]
        ),
        "profiles_refs": ctx["has_profiles"] and ctx["has_references"],
        "assets_touch": ctx["has_assets"],
        "darkness_soul": any(
            ctx["file_map"][c]["darkness"] and ctx["file_map"][c]["soul"]
            for c in ctx["chars_touched"]
        ),
        "rules_touch": ctx["has_rules"],
    }
    for flag in FLAGS:
        if checks.get(flag["check"], False):
            triggered.append(flag)
    return triggered


def main():
    parser = argparse.ArgumentParser(
        description="Extract risk signals from git diff (gathering only, no classification)")
    parser.add_argument("--diff-files", nargs="*", help="List of changed file paths")
    args = parser.parse_args()

    if args.diff_files:
        files = args.diff_files
    else:
        files = [l.strip() for l in sys.stdin.read().splitlines() if l.strip()]

    if not files:
        print("No files provided. Pass via --diff-files or stdin (git diff --name-only | python3 ...)")
        sys.exit(1)

    ctx = parse_files(files)
    flags = detect_flags(ctx)

    high_count = sum(1 for f in flags if f["severity"] == "HIGH")
    medium_count = sum(1 for f in flags if f["severity"] == "MEDIUM")

    print_json({
        "flags": flags,
        "summary": {
            "total_flags": len(flags),
            "high_severity": high_count,
            "medium_severity": medium_count,
        },
        "chars_touched": ctx["chars_touched"],
        "file_count": len(files),
        "has_references": ctx["has_references"],
        "has_assets": ctx["has_assets"],
        "has_rules": ctx["has_rules"],
    })


if __name__ == "__main__":
    main()
