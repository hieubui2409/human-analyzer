#!/usr/bin/env python3
"""Map each clinical theory from docs/references/INDEX.md to character profiles by term matching with scored relevance."""
import os
import sys
import re
import argparse
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.paths import REFERENCES, ALL_CHARS, CHAR_DISPLAY, character_dir, CLINICAL_PROFILE_FILES
from platform_lib.clinical_terms import build_reference_index
from platform_lib.formatters import print_table, print_json

STAR = {"3": "★★★", "2": "★★☆", "1": "★☆☆", "0": "☆☆☆"}


def score_theory_in_file(theory_name: str, key_terms: list[str], filepath: Path) -> int:
    """Score how much a theory appears in a file. Direct mention=3, term match=2, partial=1."""
    if not filepath.exists():
        return 0
    text = filepath.read_text(encoding="utf-8", errors="replace").lower()
    score = 0
    # Direct theory name mention
    if theory_name.lower() in text:
        score += 3
    # Key term matches
    for term in key_terms:
        if len(term) > 3 and term.lower() in text:
            score += 2
            break  # cap at 2 per file for term match
    # Partial / filename stem match
    stem = re.sub(r"[-_]", " ", Path(theory_name).stem).lower()
    for word in stem.split():
        if len(word) > 4 and word in text:
            score += 1
            break
    return min(score, 5)


def build_theory_profile_map(ref_index: dict) -> list[dict]:
    results = []
    for theory_name, ref_data in sorted(ref_index.items()):
        key_terms = ref_data.get("key_terms", [])
        char_scores = {}
        for char in ALL_CHARS:
            total = 0
            for fname in CLINICAL_PROFILE_FILES:
                fpath = character_dir(char) / fname
                total += score_theory_in_file(theory_name, key_terms, fpath)
            char_scores[char] = min(total, 5)

        results.append({
            "theory": theory_name,
            "category": ref_data.get("category", ""),
            "file": ref_data.get("file", ""),
            "scores": char_scores,
            "max_score": max(char_scores.values()) if char_scores else 0,
        })
    # Sort by max_score desc
    results.sort(key=lambda x: x["max_score"], reverse=True)
    return results


def stars(score: int) -> str:
    if score >= 4:
        return "★★★"
    if score >= 2:
        return "★★☆"
    if score >= 1:
        return "★☆☆"
    return "☆☆☆"


def main():
    parser = argparse.ArgumentParser(description="Map clinical theories to character profiles with relevance scores")
    parser.add_argument("--min-score", type=int, default=1, help="Minimum score to include (default: 1)")
    parser.add_argument("--character", help="Show scores for specific character only")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    ref_index = build_reference_index(REFERENCES)
    if not ref_index:
        print("No reference index found. Check docs/references/INDEX.md")
        sys.exit(1)

    mapping = build_theory_profile_map(ref_index)
    mapping = [m for m in mapping if m["max_score"] >= args.min_score]

    if args.json:
        print_json(mapping)
        return

    print(f"\n## Theory → Profile Mapping ({len(mapping)} theories, min_score={args.min_score})\n")

    if args.character:
        from platform_lib.paths import resolve_character
        slug = resolve_character(args.character)
        headers = ["Theory", "Category", CHAR_DISPLAY[slug], "Score"]
        rows = [[m["theory"][:45], m["category"][:20],
                 stars(m["scores"].get(slug, 0)), str(m["scores"].get(slug, 0))]
                for m in mapping if m["scores"].get(slug, 0) >= args.min_score]
        print_table(headers, rows)
    else:
        headers = ["Theory", "Category"] + [CHAR_DISPLAY[c] for c in ALL_CHARS]
        rows = [[m["theory"][:40], m["category"][:18]] +
                [stars(m["scores"].get(c, 0)) for c in ALL_CHARS]
                for m in mapping]
        print_table(headers, rows)

    print(f"\n_Legend: ★★★ = strong (4-5pts) | ★★☆ = moderate (2-3pts) | ★☆☆ = weak (1pt)_")


if __name__ == "__main__":
    main()
