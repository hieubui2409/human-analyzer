"""CI entry — validate the whole corpus against Draft-7 schemas (C7).

Iterates profiles + materials + growth + event streams, validates each against its
authoritative schema via platform_lib.schema_validator, prints a summary table, and
exits non-zero on ANY violation (CI gate). READ-ONLY.

NOTE (red-team R-cross): this is a CI/skill check, NOT a PreToolUse hard-block —
GateGuard (A3) already protects edits; a schema bug must never halt all edits.

Usage:
  validate-all-against-schemas.py [--json] [--quiet]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from platform_lib import paths
from platform_lib.schema_validator import validate_paths


def _collect() -> list[Path]:
    files: list[Path] = []
    if paths.PROFILES.exists():
        files += sorted(paths.PROFILES.rglob("*.md"))
    if paths.MATERIALS.exists():
        files += sorted(paths.MATERIALS.rglob("*.md"))
    if paths.SESSION_STATE.exists():
        files += sorted(paths.SESSION_STATE.glob("*.jsonl"))
    return files


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate corpus against Draft-7 schemas (CI).")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--quiet", action="store_true", help="Only print failures + summary")
    args = ap.parse_args()

    results = validate_paths(_collect())
    failures = [r for r in results if r["status"] == "FAIL"]
    passed = sum(1 for r in results if r["status"] == "PASS")
    skipped = sum(1 for r in results if r["status"] == "SKIP")

    if args.json:
        print(json.dumps({"passed": passed, "failed": len(failures), "skipped": skipped,
                          "failures": failures}, indent=2, ensure_ascii=False))
        return 1 if failures else 0

    print(f"\nSchema validation — {passed} PASS, {len(failures)} FAIL, {skipped} SKIP\n")
    for r in failures:
        try:
            rel = str(Path(r["file"]).resolve().relative_to(paths.ROOT))
        except (ValueError, OSError):
            rel = r["file"]
        print(f"  ✗ {rel}  [{r['schema']}]")
        for v in r["violations"][:6]:
            print(f"      {v['field']}: {v['message']}  ({v['rule']})")
    if not failures and not args.quiet:
        print("  ✓ All covered files conform to their schema.")
    print(f"\n{'FAIL' if failures else 'PASS'} — exit {1 if failures else 0}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
