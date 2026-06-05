#!/usr/bin/env python3
"""Build a structured LLM prompt for behavioral deep-scan of character profile files.

DETERMINISTIC gathering only — no LLM call made here.
The returned prompt is consumed by the orchestrating Claude (main agent) to find
IMPLICIT behavioral patterns (behavior present but theory term not used).

Usage:
    build-behavioral-deep-scan-prompt.py --character hieu
    build-behavioral-deep-scan-prompt.py --character hoa --file psychology/formulation.md
    build-behavioral-deep-scan-prompt.py --character chien --slugs savior-complex,hypervigilance
    build-behavioral-deep-scan-prompt.py --character hieu --json
"""
import json
import os
import sys
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))

from platform_lib.behavioral_clusters import extract_sections_for_llm_review, build_llm_prompt_for_deep_scan
from platform_lib.paths import (
    PROFILES,
    CLINICAL_PROFILE_FILES,
    resolve_character,
    CHAR_DISPLAY,
)
from platform_lib.formatters import eprint


def collect_target_files(slug: str, file_arg: str | None) -> list:
    """Return list of (Path, relative_name) for files to scan."""
    char_path = PROFILES / slug
    if file_arg:
        # Single file specified by caller (relative to profile root)
        fpath = char_path / file_arg
        if not fpath.exists():
            eprint(f"[ERROR] File not found: {fpath}")
            sys.exit(1)
        return [(fpath, file_arg)]
    # Default: all clinical profile files that exist
    targets = []
    for fname in CLINICAL_PROFILE_FILES:
        fpath = char_path / fname
        if fpath.exists():
            targets.append((fpath, fname))
    return targets


def parse_slugs(slugs_arg: str | None) -> list | None:
    """Parse comma-separated slugs string into list, or None for all."""
    if not slugs_arg:
        return None
    return [s.strip() for s in slugs_arg.split(",") if s.strip()]


def main():
    parser = argparse.ArgumentParser(
        description="Build LLM prompt for behavioral deep-scan of character profiles."
    )
    parser.add_argument(
        "--character", "-c",
        required=True,
        help="Character slug or alias (hieu, hoa, chien, or full slug)",
    )
    parser.add_argument(
        "--file", "-f",
        default=None,
        help="Single profile file to scan (relative to profile root, e.g. psychology/formulation.md). "
             "Default: scan all clinical profile files.",
    )
    parser.add_argument(
        "--slugs", "-s",
        default=None,
        help="Comma-separated list of theory slugs to include (default: all). "
             "E.g. savior-complex,hypervigilance,complex-ptsd",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON {character, files, prompt} instead of plain prompt text.",
    )
    args = parser.parse_args()

    slug = resolve_character(args.character)
    display = CHAR_DISPLAY.get(slug, slug)
    target_slugs = parse_slugs(args.slugs)
    targets = collect_target_files(slug, args.file)

    if not targets:
        eprint(f"[WARN] No profile files found for {display} ({slug}) — profile may not be built yet.")
        sys.exit(0)

    # Aggregate sections from all target files
    all_sections = []
    scanned_files = []
    for fpath, fname in targets:
        sections = extract_sections_for_llm_review(fpath)
        if sections:
            all_sections.extend(sections)
            scanned_files.append(fname)

    if not all_sections:
        eprint(f"[WARN] No readable sections found in {len(targets)} file(s) for {display}.")
        sys.exit(0)

    prompt = build_llm_prompt_for_deep_scan(all_sections, slugs=target_slugs)

    if args.json:
        output = {
            "character": slug,
            "files": scanned_files,
            "prompt": prompt,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(prompt)

    eprint(
        f"[OK] Behavioral deep-scan prompt built for {display} "
        f"({len(scanned_files)} file(s), {len(all_sections)} sections). "
        "Pass this prompt to the LLM (main agent) for implicit behavioral matching."
    )


if __name__ == "__main__":
    main()
