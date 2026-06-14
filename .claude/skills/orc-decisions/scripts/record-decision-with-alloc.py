#!/usr/bin/env python3
"""record-decision-with-alloc — thin CLI wrapper for the orc:decisions write path.

Allocates the next monotonic DEC-n id and appends a new decision record inside a
single exclusive lock so concurrent agents cannot collide on ids. This is the
backend called by the orc:decisions --record skill; the interactive UX (AskUserQuestion
flow gathering title/rationale/character/etc.) lives in the SKILL.md workflow and
is NOT replaced by this script.

CLI:
    record-decision-with-alloc.py --title "..." --rationale "..."
        [--character CHAR] [--affects TEXT] [--supersedes DEC-n] [--date YYYY-MM-DD]
        [--decisions-dir PATH]  # default: DECISIONS from paths.py

Output (stdout): JSON  {"id": "DEC-n", "file": "...", "written": true}
On error:              JSON  {"error": "...", "written": false}
"""
import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "scripts"))
from platform_lib.paths import DECISIONS
from platform_lib import decision_store as ds


def main() -> int:
    ap = argparse.ArgumentParser(description="Atomically alloc-id + append a decision record.")
    ap.add_argument("--title", required=True, help="Short title for the decision")
    ap.add_argument("--rationale", required=True, help="WHY this decision was made (multiline ok)")
    ap.add_argument("--character", default="", help="Character slug(s) this decision affects")
    ap.add_argument("--affects", default="", help="Free-text artifact/area this decision affects")
    ap.add_argument("--supersedes", default="", help="DEC-n id being retired by this decision")
    ap.add_argument("--date", default="", help="ISO date YYYY-MM-DD (default: today)")
    ap.add_argument(
        "--decisions-dir",
        default=str(DECISIONS),
        help=f"Path to decisions directory (default: {DECISIONS})",
    )
    args = ap.parse_args()

    decisions_dir = Path(args.decisions_dir)
    try:
        with ds.register_lock(decisions_dir):
            dec_id = ds.alloc_id(decisions_dir)
            out_path = ds.append_decision(
                decisions_dir,
                dec_id,
                args.title,
                args.rationale,
                character=args.character,
                affects=args.affects,
                supersedes=args.supersedes,
                date=args.date or None,
            )
        print(json.dumps({
            "id": dec_id,
            "file": out_path.name,
            "written": True,
        }, ensure_ascii=False))
        return 0
    except ds.DecisionError as exc:
        print(json.dumps({"error": str(exc), "written": False}, ensure_ascii=False))
        return 0
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"error": str(exc), "written": False}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
