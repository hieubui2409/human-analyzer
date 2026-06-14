#!/usr/bin/env python3
"""evl:standardize — deterministic gather + finalize wrapper for the psychometric battery.

Thin preset over the generic EVL pipeline: the rubric defaults to psychometric-big-five
(Big Five OCEAN · Dark Triad SD3 · Attachment ECR-R). The LLM judging and post-finalize
narration (attachment quadrant, Dark Triad elevation flag) happen BETWEEN these two calls,
orchestrated by the skill via the Agent tool. No scoring or clinical judgment lives here.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib import evl_pipeline as P  # noqa: E402
from platform_lib.paths import RUBRICS, resolve_character  # noqa: E402

DEFAULT_RUBRIC = "psychometric-big-five"


def _rubric_path(ref: str) -> Path:
    """Resolve a rubric id or explicit path to a YAML file under docs/rubrics/."""
    p = Path(ref)
    if p.exists():
        return p
    return RUBRICS / (ref if ref.endswith(".yaml") else f"{ref}.yaml")


def main():
    ap = argparse.ArgumentParser(
        description=(
            "evl:standardize — gather evidence / finalize scorecard for the psychometric "
            "battery (deterministic; LLM judges and clinical narration run between the two "
            "steps). Rubric defaults to psychometric-big-five."
        )
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("gather", help="emit the evidence bundle for the LLM judges")
    g.add_argument("--character", required=True)
    g.add_argument(
        "--rubric",
        default=DEFAULT_RUBRIC,
        help=f"rubric id or path under docs/rubrics/ (default: {DEFAULT_RUBRIC})",
    )

    f = sub.add_parser("finalize", help="aggregate judge scores + write the scorecard")
    f.add_argument("--character", required=True)
    f.add_argument(
        "--rubric",
        default=DEFAULT_RUBRIC,
        help=f"rubric id or path under docs/rubrics/ (default: {DEFAULT_RUBRIC})",
    )
    f.add_argument(
        "--scores",
        required=True,
        help="path to judge scores JSON (CriterionScore list)",
    )
    f.add_argument("--asof", required=True, help="ISO date stamped on the scorecard")

    args = ap.parse_args()
    char = resolve_character(args.character)
    rubric_path = _rubric_path(args.rubric)

    if args.cmd == "gather":
        print(json.dumps(P.gather_payload(char, rubric_path), ensure_ascii=False, indent=2))
        return

    scores = json.loads(Path(args.scores).read_text(encoding="utf-8"))
    path, result = P.finalize_scorecard(
        char,
        rubric_path,
        scores,
        asof=args.asof,
        updated_by="evl:standardize",
    )
    print(
        json.dumps(
            {
                "scorecard": str(path),
                "overall": result["overall"],
                "verdict": result["verdict"],
                "unverified": result["unverified"],
                "below_min_tier": result["below_min_tier"],
                "coverage": result["verified_coverage"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
