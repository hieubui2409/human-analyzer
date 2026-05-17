#!/usr/bin/env python3
"""Scan assets/*/post.md files and compute per-post writing statistics."""
import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.paths import ASSETS
from platform_lib.formatters import print_table


def compute_stats(text: str) -> dict:
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    words = text.split()
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
    exclamations = len(re.findall(r'!', text))
    questions = len(re.findall(r'\?', text))
    avg_sent_len = round(len(words) / max(len(sentences), 1), 1)
    return {
        "words": len(words),
        "sentences": len(sentences),
        "avg_sent_len": avg_sent_len,
        "paragraphs": len(paragraphs),
        "exclamations": exclamations,
        "questions": questions,
    }


def scan_platform(platform_dir: Path) -> list[dict]:
    results = []
    for slug_dir in sorted(platform_dir.iterdir()):
        if not slug_dir.is_dir():
            continue
        for fname in ["post.md", "post.txt"]:
            post_file = slug_dir / fname
            if post_file.exists():
                text = post_file.read_text(encoding="utf-8")
                stats = compute_stats(text)
                first_line = next((l.strip() for l in text.splitlines() if l.strip()), "")[:60]
                results.append({
                    "platform": platform_dir.name,
                    "slug": slug_dir.name,
                    "file": fname,
                    "title_proxy": first_line,
                    **stats,
                })
                break
    return results


def main():
    parser = argparse.ArgumentParser(description="Scan published post stats across asset platforms")
    parser.add_argument("--platform", default=None, help="Platform name or 'all'")
    parser.add_argument("--all", action="store_true", help="Scan all platforms")
    args = parser.parse_args()

    if not ASSETS.exists():
        print(f"Assets dir not found: {ASSETS}")
        sys.exit(1)

    platforms = []
    if args.all or args.platform == "all" or not args.platform:
        platforms = [d for d in ASSETS.iterdir() if d.is_dir()]
    else:
        p = ASSETS / args.platform
        if not p.exists():
            print(f"Platform not found: {p}")
            sys.exit(1)
        platforms = [p]

    all_stats = []
    for pdir in sorted(platforms):
        all_stats.extend(scan_platform(pdir))

    if not all_stats:
        print("No post files found.")
        return

    headers = ["Platform", "Slug", "Words", "Sents", "AvgLen", "Paras", "!", "?", "Title (proxy)"]
    rows = [
        [
            r["platform"], r["slug"], str(r["words"]), str(r["sentences"]),
            str(r["avg_sent_len"]), str(r["paragraphs"]),
            str(r["exclamations"]), str(r["questions"]),
            r["title_proxy"],
        ]
        for r in all_stats
    ]
    print(f"\n## Published Content Stats ({len(all_stats)} posts)\n")
    print_table(headers, rows)


if __name__ == "__main__":
    main()
