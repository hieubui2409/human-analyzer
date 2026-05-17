#!/usr/bin/env python3
"""Scan DARKNESS.md + SOUL.md for crisis-related keywords AND behavioral patterns.
Default: deep mode (keywords + behavioral clusters). Use --quick for keywords only.
Gathering only — LLM classifies risk level from output."""
import os
import sys
import argparse
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.paths import resolve_character, character_dir, CHAR_DISPLAY, ALL_CHARS
from platform_lib.formatters import print_json, print_table, eprint
from platform_lib.behavioral_clusters import (
    scan_file_for_behavioral_clusters,
    CRISIS_ADJACENT_SLUGS,
)

CRISIS_KEYWORDS = [
    # English
    r"\bsuicid(al|e|ality|ation)?\b",
    r"\bself[\s-]?harm(ing)?\b",
    r"\bself[\s-]?injur(y|ing|ious)?\b",
    r"\bwant(s)?\s+to\s+die\b",
    r"\bmuốn\s+chết\b",
    r"\bmuốn\s+biến\s+mất\b",
    r"\btự\s+tử\b",
    r"\btự\s+hại\b",
    r"\bcắt\s+tay\b",
    r"\boverdose\b",
    r"\battempt(ed)?\b",
    r"\bcrisis\b",
    r"\b(active|passive)\s+SI\b",
    r"\bsuicidal\s+ideation\b",
    r"\bideation\b",
    r"\bnonsuicidal\b",
    r"\bNSSI\b",
    r"\bhopelessness\b",
    r"\bworthlessness\b",
    r"\bbetter\s+off\s+(dead|without\s+me)\b",
    r"\bno\s+reason\s+to\s+(live|stay)\b",
    r"\bchết\b",
    r"\bkết\s+thúc\s+tất\s+cả\b",
    r"\bthôi\s+sống\b",
]

TARGET_FILES = ["DARKNESS.md", "SOUL.md"]

COMPILED = [(kw, re.compile(kw, re.IGNORECASE)) for kw in CRISIS_KEYWORDS]


def scan_file(filepath) -> list[dict]:
    """Return list of {keyword, line_no, line_text, before, after}."""
    if not filepath.exists():
        return []
    lines = filepath.read_text(encoding="utf-8").splitlines()
    results = []
    for i, line_text in enumerate(lines):
        for kw, pat in COMPILED:
            if pat.search(line_text):
                before = lines[i - 1].strip() if i > 0 else ""
                after = lines[i + 1].strip() if i < len(lines) - 1 else ""
                results.append({
                    "file": filepath.name,
                    "line_no": i + 1,
                    "keyword_pattern": kw,
                    "line_text": line_text.strip(),
                    "before": before,
                    "after": after,
                })
                break  # one hit per line is enough
    return results


def scan_behavioral(filepath, slugs=None) -> list[dict]:
    """Scan file for behavioral cluster patterns (crisis-adjacent theories)."""
    if not filepath.exists():
        return []
    target_slugs = slugs or CRISIS_ADJACENT_SLUGS
    raw = scan_file_for_behavioral_clusters(filepath, target_slugs)
    return [{
        "file": filepath.name,
        "line_no": h["line"],
        "keyword_pattern": f"[behavioral] {h['cluster_slug']}",
        "line_text": h["context"],
        "before": "",
        "after": "",
        "source": "behavioral",
    } for h in raw]


def scan_character(char_slug: str, quick: bool = False) -> dict:
    cdir = character_dir(char_slug)
    display = CHAR_DISPLAY.get(char_slug, char_slug)
    keyword_hits = []
    behavioral_hits = []
    for fname in TARGET_FILES:
        fpath = cdir / fname
        keyword_hits.extend(scan_file(fpath))
        if not quick:
            behavioral_hits.extend(scan_behavioral(fpath))
    all_hits = keyword_hits + behavioral_hits
    return {
        "character": display,
        "slug": char_slug,
        "total_hits": len(all_hits),
        "keyword_hits": len(keyword_hits),
        "behavioral_hits": len(behavioral_hits),
        "hits": all_hits,
        "mode": "quick" if quick else "deep",
    }


def main():
    parser = argparse.ArgumentParser(
        description="Scan DARKNESS.md + SOUL.md for crisis keywords + behavioral clusters (gathering for LLM risk classification)"
    )
    parser.add_argument("--character", help="Character alias (hieu, hoa, chien) or 'all'")
    parser.add_argument("--all", dest="all_chars", action="store_true", help="Scan all characters")
    parser.add_argument("--quick", action="store_true", help="Keywords only (skip behavioral cluster scan)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if not args.character and not args.all_chars:
        parser.error("Provide --character <name> or --all")

    targets = ALL_CHARS if args.all_chars else [resolve_character(args.character)]

    results = [scan_character(slug, quick=args.quick) for slug in targets]

    if args.json:
        print_json(results)
        return

    for r in results:
        mode_label = "Quick (keywords only)" if r["mode"] == "quick" else "Deep (keywords + behavioral clusters)"
        print(f"\n## Crisis Scan: {r['character']} [{mode_label}]")
        print(f"Total hits: {r['total_hits']} (keyword: {r['keyword_hits']}, behavioral: {r['behavioral_hits']})")
        if not r["hits"]:
            print("  ⚠ No explicit or behavioral patterns found.")
            print("  → LLM MUST independently re-read DARKNESS.md + SOUL.md for implicit crisis indicators.")
            continue
        headers = ["File", "Line", "Source", "Pattern", "Text (truncated)"]
        rows = []
        for h in r["hits"]:
            source = h.get("source", "keyword")
            rows.append([
                h["file"],
                str(h["line_no"]),
                source,
                h["keyword_pattern"][:35],
                h["line_text"][:70],
            ])
        print_table(headers, rows)
        print()
        for h in r["hits"]:
            source = h.get("source", "keyword")
            print(f"  Line {h['line_no']} [{h['file']}] ({source}):")
            if h.get("before"):
                print(f"    before : {h['before'][:100]}")
            print(f"    HIT    : {h['line_text'][:100]}")
            if h.get("after"):
                print(f"    after  : {h['after'][:100]}")
            print()

    total = sum(r["total_hits"] for r in results)
    total_kw = sum(r["keyword_hits"] for r in results)
    total_bh = sum(r["behavioral_hits"] for r in results)
    print(f"\n**NOTE**: {total} total hit(s) (keyword: {total_kw}, behavioral: {total_bh}). LLM should assess clinical risk level from context above.")


if __name__ == "__main__":
    main()
