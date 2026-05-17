#!/usr/bin/env python3
"""Scan character profile files for raw clinical terms + behavioral clusters.
Default: clinical terms only. Use --deep to add behavioral cluster scan.
"""
import os
import sys
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))

from platform_lib.clinical_terms import scan_file_for_clinical_terms
from platform_lib.behavioral_clusters import scan_file_for_behavioral_clusters
from platform_lib.paths import (
    PROFILES, CLINICAL_PROFILE_FILES, ALL_CHARS,
    resolve_character, character_dir, CHAR_DISPLAY,
)
from platform_lib.formatters import print_table, eprint


def scan_character(slug: str, deep: bool = False) -> dict:
    char_path = PROFILES / slug
    clinical_rows = []
    behavioral_rows = []
    for fname in CLINICAL_PROFILE_FILES:
        fpath = char_path / fname
        if not fpath.exists():
            continue
        hits = scan_file_for_clinical_terms(fpath)
        for h in hits:
            ctx = h["context"].replace("|", "\\|")
            clinical_rows.append([
                CHAR_DISPLAY.get(slug, slug),
                fname,
                str(h["line"]),
                "clinical",
                h["term"],
                ctx[:70],
            ])
        if deep:
            bh_hits = scan_file_for_behavioral_clusters(fpath)
            for bh in bh_hits:
                ctx = bh["context"].replace("|", "\\|")
                behavioral_rows.append([
                    CHAR_DISPLAY.get(slug, slug),
                    fname,
                    str(bh["line"]),
                    "behavioral",
                    bh["cluster_slug"],
                    ctx[:70],
                ])
    return {
        "slug": slug,
        "display": CHAR_DISPLAY.get(slug, slug),
        "clinical_rows": clinical_rows,
        "behavioral_rows": behavioral_rows,
    }


def main():
    parser = argparse.ArgumentParser(description="Scan profile files for clinical terms + behavioral clusters")
    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument("--character", "-c", help="Character name/alias (hieu, hoa, chien)")
    grp.add_argument("--all", "-a", action="store_true", help="Scan all characters")
    parser.add_argument("--deep", action="store_true", help="Add behavioral cluster scan alongside clinical terms")
    args = parser.parse_args()

    chars = ALL_CHARS if args.all else [resolve_character(args.character)]

    all_rows = []
    total_clinical = 0
    total_behavioral = 0
    for slug in chars:
        result = scan_character(slug, deep=args.deep)
        all_rows.extend(result["clinical_rows"])
        all_rows.extend(result["behavioral_rows"])
        total_clinical += len(result["clinical_rows"])
        total_behavioral += len(result["behavioral_rows"])

    mode = "deep (clinical + behavioral)" if args.deep else "clinical only"
    headers = ["Character", "File", "Line", "Source", "Term", "Context"]
    print_table(headers, all_rows)

    if args.deep:
        eprint(f"[OK] {len(all_rows)} hits (clinical: {total_clinical}, behavioral: {total_behavioral}) across {len(chars)} character(s) [{mode}]")
        if len(all_rows) == 0:
            eprint("[WARN] 0 hits — LLM should independently re-read profiles for implicit clinical concepts")
    else:
        eprint(f"[OK] {total_clinical} clinical term hits across {len(chars)} character(s) [{mode}]")


if __name__ == "__main__":
    main()
