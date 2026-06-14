#!/usr/bin/env python3
"""evl:validate — deterministic rubric + scorecard structural checker.

Thin by design: args → platform_lib calls → print. No heuristics here. Two modes:
RUBRIC (--rubric <id|path> | --all) validates shape + cross-field invariants via
evl_schema.validate_rubric; SCORECARD (--scorecard <json> --rubric <id|path> [--strict])
runs evl_structural.run_structural and prints a per-checker verdict table. Exits non-zero
on FAIL; UNMAPPED is loud but non-fatal unless --strict.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib import evl_schema  # noqa: E402
from platform_lib import evl_structural  # noqa: E402
from platform_lib.paths import RUBRICS  # noqa: E402


def _rubric_path(ref: str) -> Path:
    """Resolve a rubric id or explicit path to a Path object."""
    p = Path(ref)
    if p.exists():
        return p
    return RUBRICS / (ref if ref.endswith(".yaml") else f"{ref}.yaml")


def _validate_one_rubric(path: Path) -> tuple[bool, list[str]]:
    """Load and validate a single rubric file. Returns (valid, errors)."""
    try:
        rubric = evl_schema.load_rubric(path)
    except Exception as exc:  # noqa: BLE001 — surface parse errors as errors
        return False, [str(exc)]
    errors = evl_schema.validate_rubric(rubric)
    return (len(errors) == 0), errors


def run_rubric_mode(args) -> int:
    """Validate one or all rubrics. Returns exit code."""
    if args.all:
        paths = evl_schema.list_rubrics()
        if not paths:
            print("No rubrics found in docs/rubrics/", file=sys.stderr)
            return 1
    else:
        paths = [_rubric_path(args.rubric)]

    results = []
    for path in paths:
        rubric_id = path.stem
        valid, errors = _validate_one_rubric(path)
        results.append({"id": rubric_id, "valid": valid, "errors": errors})

    overall_pass = all(r["valid"] for r in results)

    if args.json:
        print(json.dumps({
            "mode": "rubric",
            "verdict": "PASS" if overall_pass else "FAIL",
            "rubrics": results,
        }, ensure_ascii=False, indent=2))
        return 0 if overall_pass else 1

    # Human-readable output
    for r in results:
        tag = "PASS" if r["valid"] else "FAIL"
        print(f"[{tag}] {r['id']}")
        for err in r["errors"]:
            print(f"       - {err}")

    print()
    if overall_pass:
        print(f"PASS — {len(results)} rubric(s) valid")
    else:
        failed = sum(1 for r in results if not r["valid"])
        print(f"FAIL — {failed}/{len(results)} rubric(s) invalid")

    return 0 if overall_pass else 1


# Column widths for the verdict table
_COL_CHECK = 34
_COL_STATUS = 8


def _print_table(rows: list[dict]) -> None:
    header = f"{'Check':<{_COL_CHECK}}  {'Status':<{_COL_STATUS}}  Detail"
    print(header)
    print("-" * len(header))
    for row in rows:
        print(f"{row['check']:<{_COL_CHECK}}  {row['status']:<{_COL_STATUS}}  {row['detail']}")


def run_scorecard_mode(args) -> int:
    """Validate a scorecard against its rubric. Returns exit code."""
    scorecard_path = Path(args.scorecard)
    if not scorecard_path.exists():
        print(f"error: scorecard not found: {scorecard_path}", file=sys.stderr)
        return 2

    try:
        scorecard = json.loads(scorecard_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"error: scorecard is not valid JSON: {exc}", file=sys.stderr)
        return 2

    rubric_path = _rubric_path(args.rubric)
    if not rubric_path.exists():
        print(f"error: rubric not found: {rubric_path}", file=sys.stderr)
        return 2

    try:
        rubric = evl_schema.load_rubric(rubric_path)
    except Exception as exc:  # noqa: BLE001
        print(f"error: could not load rubric: {exc}", file=sys.stderr)
        return 2

    verdict, rows = evl_structural.run_structural(
        scorecard, rubric, strict=args.strict
    )
    overall_pass = verdict == "PASS"

    if args.json:
        print(json.dumps({
            "mode": "scorecard",
            "scorecard": str(scorecard_path),
            "rubric": rubric_path.stem,
            "strict": args.strict,
            "verdict": verdict,
            "checks": rows,
        }, ensure_ascii=False, indent=2))
        return 0 if overall_pass else 1

    # Human-readable output
    print(f"Scorecard : {scorecard_path}")
    print(f"Rubric    : {rubric_path.stem}")
    if args.strict:
        print("Mode      : strict (UNMAPPED → FAIL)")
    print()
    _print_table(rows)
    print()
    print(f"{'PASS' if overall_pass else 'FAIL'} — {verdict}")

    return 0 if overall_pass else 1


def main() -> None:
    ap = argparse.ArgumentParser(
        description=(
            "evl:validate — structural checker for EVL rubrics and scorecards. "
            "RUBRIC mode: --rubric <id|path> or --all. "
            "SCORECARD mode: --scorecard <json> --rubric <id|path> [--strict]."
        )
    )

    # RUBRIC mode flags
    rubric_group = ap.add_mutually_exclusive_group()
    rubric_group.add_argument(
        "--rubric", metavar="ID_OR_PATH",
        help="rubric id or path under docs/rubrics/ (RUBRIC mode or SCORECARD context)",
    )
    rubric_group.add_argument(
        "--all", action="store_true",
        help="validate all docs/rubrics/*.yaml (RUBRIC mode)",
    )

    # SCORECARD mode flag
    ap.add_argument(
        "--scorecard", metavar="JSON_PATH",
        help="scorecard JSON path (enables SCORECARD mode; requires --rubric)",
    )
    ap.add_argument(
        "--strict", action="store_true",
        help="treat UNMAPPED criteria as FAIL (default: loud but non-fatal)",
    )
    ap.add_argument(
        "--json", action="store_true",
        help="machine-readable JSON output",
    )

    args = ap.parse_args()

    if args.scorecard is not None:  # SCORECARD mode
        if not args.rubric:
            ap.error("--scorecard requires --rubric")
        sys.exit(run_scorecard_mode(args))

    # RUBRIC mode: default to --all when no flag given
    if not args.rubric and not args.all:
        args.all = True

    sys.exit(run_rubric_mode(args))


if __name__ == "__main__":
    main()
