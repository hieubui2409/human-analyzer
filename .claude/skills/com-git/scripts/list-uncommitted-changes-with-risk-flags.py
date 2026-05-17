#!/usr/bin/env python3
"""List uncommitted changes and flag risky files (credentials, private data, large files)."""
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.paths import ROOT
from platform_lib.formatters import print_table, print_json, eprint

RISKY_PATTERNS = [".env", "credentials", "secret", "password", "token", "api_key", "private"]
LARGE_THRESHOLD = 500_000


def get_changes() -> list[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain", "-u"], capture_output=True, text=True, cwd=ROOT)
    return [l.strip() for l in result.stdout.strip().split("\n") if l.strip()]


def analyze(changes: list[str]) -> list[dict]:
    results = []
    for line in changes:
        status = line[:2].strip()
        filepath = line[3:].strip()
        flags = []
        fp_lower = filepath.lower()
        for p in RISKY_PATTERNS:
            if p in fp_lower:
                flags.append(f"RISKY:{p}")
        full = ROOT / filepath
        if full.exists() and full.stat().st_size > LARGE_THRESHOLD:
            flags.append(f"LARGE:{full.stat().st_size // 1000}KB")
        results.append({"status": status, "file": filepath, "flags": flags})
    return results


def main():
    changes = get_changes()
    if not changes:
        print("No uncommitted changes.")
        return
    results = analyze(changes)
    risky = sum(1 for r in results if r["flags"])
    eprint(f"[OK] {len(results)} changes, {risky} flagged")
    rows = [[r["status"], r["file"][:60], ", ".join(r["flags"]) or "-"] for r in results]
    print_table(["Status", "File", "Flags"], rows)


if __name__ == "__main__":
    main()
