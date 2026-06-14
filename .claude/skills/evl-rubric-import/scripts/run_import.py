#!/usr/bin/env python3
"""evl:rubric-import — deterministic parse + scaffold + optional write.

Thin by design: reads external framework text (file or stdin), calls the
platform_lib import pipeline, and prints the draft YAML + gap list to stdout.
With --write it also materialises the draft under docs/rubrics/imported/.

No mapping heuristics live here. No network calls live here. The semantic
mapping (external criteria → canonical anchors/weights) is an input-isolated
LLM sub-agent's responsibility, orchestrated by the skill between a dry-run
call and a --write call.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

import yaml  # noqa: E402 — available after sys.path patch

from platform_lib import evl_import  # noqa: E402


def _read_input(args: argparse.Namespace) -> str:
    """Return external framework text from --input file or --stdin."""
    if args.input:
        path = Path(args.input)
        if not path.exists():
            print(f"ERROR: input file not found: {path}", file=sys.stderr)
            sys.exit(1)
        return path.read_text(encoding="utf-8")
    # --stdin
    return sys.stdin.read()


def main() -> None:
    ap = argparse.ArgumentParser(
        description=(
            "evl:rubric-import — parse an external evaluation framework into a "
            "canonical rubric draft (structure only; no invented weights or anchors)."
        )
    )

    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--input", metavar="PATH", help="path to external framework file")
    src.add_argument("--stdin", action="store_true", help="read framework text from stdin")

    ap.add_argument(
        "--fmt",
        default="md",
        choices=["md", "json", "yaml", "freeform"],
        help="input format (default: md)",
    )
    ap.add_argument("--id", dest="rubric_id", metavar="SLUG", help="rubric id slug for the draft")
    ap.add_argument("--title", metavar="STR", help="override rubric title")
    ap.add_argument(
        "--kind",
        default="decision",
        choices=["decision", "psychometric", "clinical", "dyad"],
        help="rubric kind (default: decision)",
    )
    ap.add_argument("--source", metavar="STR", help="provenance string (URL, citation, author)")
    ap.add_argument(
        "--write",
        action="store_true",
        help="write the draft YAML to docs/rubrics/imported/ and print path",
    )

    args = ap.parse_args()

    text = _read_input(args)

    meta: dict = {"kind": args.kind}
    if args.rubric_id:
        meta["id"] = args.rubric_id
    if args.title:
        meta["title"] = args.title
    if args.source:
        meta["source"] = args.source

    rubric, gaps = evl_import.import_rubric(text, meta, fmt=args.fmt)

    # Emit the draft YAML so the skill (or user) can inspect it before writing.
    print("# --- draft rubric (structure only; gaps must be filled before scoring) ---")
    print(yaml.safe_dump(rubric, sort_keys=False, allow_unicode=True), end="")

    if gaps:
        print("# --- import gaps (fill these before running evl:validate) ---")
        for gap in gaps:
            print(f"#   - {gap}")
    else:
        print("# --- no import gaps detected ---")

    if args.write:
        draft_id = args.rubric_id or rubric.get("id") or "imported-rubric"
        path = evl_import.write_draft(rubric, draft_id)
        print(f"\nDRAFT WRITTEN: {path}")
        if gaps:
            print(f"WARNING: {len(gaps)} gap(s) remain — rubric will fail evl:validate until filled.")


if __name__ == "__main__":
    main()
