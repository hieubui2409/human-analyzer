#!/usr/bin/env python3
"""Check cross-references BETWEEN reference files (ref→ref): linked, mentioned, missing."""
import os
import sys
import re
import argparse
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))

from platform_lib.clinical_terms import build_reference_index
from platform_lib.paths import REFERENCES
from platform_lib.formatters import print_table, eprint

STOPWORDS = {
    "theory", "model", "pattern", "system", "process", "factor", "level",
    "stage", "style", "response", "state", "effect", "disorder", "complex",
    "syndrome", "behavior", "mô hình", "quá trình", "hệ thống", "trạng thái",
    "hành vi", "yếu tố", "phản ứng", "giai đoạn", "stress", "trauma",
    "therapy", "treatment", "clinical", "mental", "health", "psychological",
    "self", "child", "parent", "family", "social", "emotional",
}


def is_meaningful_term(term: str, min_len: int = 6) -> bool:
    """Filter out generic/stopword terms that cause false positive cross-links."""
    if len(term) < min_len:
        return False
    if term.lower() in STOPWORDS:
        return False
    return True


def scan_cross_links(ref_index: dict, min_term_len: int = 6) -> list[dict]:
    """For each ref file, find which other theories it links/mentions/misses."""
    results = []

    for source_name, source_info in ref_index.items():
        fpath = REFERENCES / source_info["file"]
        if not fpath.exists():
            continue
        content = fpath.read_text(encoding="utf-8")

        for target_name, target_info in ref_index.items():
            if target_name == source_name:
                continue
            target_file = target_info["file"]
            has_md_link = bool(re.search(
                r'\[.*?\]\(.*?' + re.escape(target_file) + r'.*?\)', content
            ))
            has_mention = False
            for kt in target_info["key_terms"]:
                if is_meaningful_term(kt, min_term_len) and re.search(r'\b' + re.escape(kt) + r'\b', content, re.IGNORECASE):
                    has_mention = True
                    break

            if has_md_link:
                status = "linked"
            elif has_mention:
                status = "mentioned"
            else:
                source_terms_in_target = False
                target_content = (REFERENCES / target_file).read_text(encoding="utf-8") if (REFERENCES / target_file).exists() else ""
                for kt in source_info["key_terms"]:
                    if is_meaningful_term(kt, min_term_len) and re.search(r'\b' + re.escape(kt) + r'\b', target_content, re.IGNORECASE):
                        source_terms_in_target = True
                        break
                if not source_terms_in_target:
                    continue
                status = "missing"

            results.append({
                "source": source_name,
                "target": target_name,
                "status": status,
            })
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Scan cross-references between reference theory files"
    )
    parser.add_argument(
        "--status", choices=["linked", "mentioned", "missing", "all"],
        default="all", help="Filter by link status (default: all)"
    )
    parser.add_argument(
        "--source", help="Filter by source theory name (substring match)"
    )
    parser.add_argument(
        "--min-term-length", type=int, default=6,
        help="Minimum key term length to reduce false positives (default: 6)"
    )
    parser.add_argument(
        "--check-file-exists", action="store_true",
        help="Annotate 'missing' entries with whether target ref file exists"
    )
    args = parser.parse_args()

    ref_index = build_reference_index(REFERENCES)
    if not ref_index:
        eprint("[ERR] Empty reference index. Check docs/references/INDEX.md")
        sys.exit(1)

    results = scan_cross_links(ref_index, min_term_len=args.min_term_length)

    if args.status != "all":
        results = [r for r in results if r["status"] == args.status]
    if args.source:
        results = [r for r in results if args.source.lower() in r["source"].lower()]

    if args.check_file_exists:
        for r in results:
            if r["status"] == "missing":
                target_file = ref_index.get(r["target"], {}).get("file", "")
                r["has_ref_file"] = (REFERENCES / target_file).exists() if target_file else False
        headers = ["Source Theory", "Target Theory", "Status", "Has File"]
        rows = [[r["source"][:50], r["target"][:50], r["status"],
                 str(r.get("has_ref_file", ""))] for r in results]
    else:
        headers = ["Source Theory", "Target Theory", "Status"]
        rows = [[r["source"][:50], r["target"][:50], r["status"]] for r in results]

    print_table(headers, rows)

    counts = {"linked": 0, "mentioned": 0, "missing": 0}
    missing_with_file = 0
    missing_no_file = 0
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
        if r["status"] == "missing" and args.check_file_exists:
            if r.get("has_ref_file"):
                missing_with_file += 1
            else:
                missing_no_file += 1

    summary = f"[OK] linked={counts['linked']} mentioned={counts['mentioned']} missing={counts['missing']}"
    if args.check_file_exists:
        summary += f" (missing_with_file={missing_with_file} missing_no_file={missing_no_file})"
    eprint(summary)


if __name__ == "__main__":
    main()
