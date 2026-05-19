#!/usr/bin/env python3
"""Scan docs/materials/ for potential duplicate files by comparing file sizes and first 500 chars.
Output: potential duplicate pairs with file paths and similarity indicators."""
import os
import sys
import argparse
import hashlib
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.paths import MATERIALS
from platform_lib.formatters import print_json, print_table


def file_fingerprint(path: Path) -> dict:
    """Compute size + head hash + full hash for a file."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    size = len(text)
    head = text[:500]
    head_hash = hashlib.md5(head.encode("utf-8")).hexdigest()
    full_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
    return {
        "path": str(path),
        "relative": str(path.relative_to(MATERIALS)),
        "size": size,
        "head_hash": head_hash,
        "full_hash": full_hash,
        "head_preview": head[:120].replace("\n", " ").strip(),
    }


def find_duplicates(char_filter: str = None) -> list[dict]:
    """Find duplicate files under docs/materials/."""
    if not MATERIALS.exists():
        return []

    files = []
    if char_filter:
        search_root = MATERIALS / char_filter
    else:
        search_root = MATERIALS

    for f in sorted(search_root.rglob("*")):
        if f.is_file() and not f.name.startswith("."):
            fp = file_fingerprint(f)
            if fp:
                files.append(fp)

    # Group by full_hash first (exact duplicates)
    exact_groups: dict[str, list] = {}
    for fp in files:
        exact_groups.setdefault(fp["full_hash"], []).append(fp)

    # Group by head_hash (near-duplicates — same start, possibly different tails)
    near_groups: dict[str, list] = {}
    for fp in files:
        near_groups.setdefault(fp["head_hash"], []).append(fp)

    pairs = []

    for hash_val, group in exact_groups.items():
        if len(group) > 1:
            for i in range(len(group)):
                for j in range(i + 1, len(group)):
                    pairs.append({
                        "type": "EXACT_DUPLICATE",
                        "file_a": group[i]["relative"],
                        "file_b": group[j]["relative"],
                        "size_a": group[i]["size"],
                        "size_b": group[j]["size"],
                        "hash": hash_val[:12],
                        "preview": group[i]["head_preview"][:80],
                    })

    for hash_val, group in near_groups.items():
        if len(group) > 1:
            # Only report as near-duplicate if not already exact duplicate
            exact_hashes = {fp["full_hash"] for fp in group}
            if len(exact_hashes) > 1:  # Different full hashes = near-duplicate only
                for i in range(len(group)):
                    for j in range(i + 1, len(group)):
                        if group[i]["full_hash"] != group[j]["full_hash"]:
                            pairs.append({
                                "type": "NEAR_DUPLICATE",
                                "file_a": group[i]["relative"],
                                "file_b": group[j]["relative"],
                                "size_a": group[i]["size"],
                                "size_b": group[j]["size"],
                                "hash": hash_val[:12],
                                "preview": group[i]["head_preview"][:80],
                            })

    return pairs


def main():
    parser = argparse.ArgumentParser(
        description="Detect duplicate material files under docs/materials/ by size and content"
    )
    parser.add_argument("--character", help="Limit to one character's materials dir (e.g. character-a)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--exact-only", action="store_true", help="Only show exact duplicates (full hash match)")
    args = parser.parse_args()

    pairs = find_duplicates(char_filter=args.character)

    if args.exact_only:
        pairs = [p for p in pairs if p["type"] == "EXACT_DUPLICATE"]

    if args.json:
        print_json(pairs)
        return

    print(f"\n## Duplicate Material Detection\n")
    print(f"Scanned: {MATERIALS}")
    if args.character:
        print(f"Filtered to: {args.character}")
    print()

    if not pairs:
        print("No duplicate pairs found.")
        return

    print(f"**{len(pairs)} potential duplicate pair(s):**\n")
    headers = ["Type", "File A", "File B", "Size A", "Size B"]
    rows = [
        [p["type"], p["file_a"][:45], p["file_b"][:45], str(p["size_a"]), str(p["size_b"])]
        for p in pairs
    ]
    print_table(headers, rows)

    print()
    for p in pairs:
        print(f"  [{p['type']}] {p['file_a']} ↔ {p['file_b']}")
        print(f"    Preview: {p['preview']}")
        print()


if __name__ == "__main__":
    main()
