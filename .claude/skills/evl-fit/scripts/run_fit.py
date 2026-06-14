#!/usr/bin/env python3
"""evl:fit — deterministic gather + finalize wrapper for role / casting-fit decisions.

Thin by design: it does the two DETERMINISTIC ends of the scoring flow — `gather`
(emit the per-criterion evidence bundle) and `finalize` (aggregate the collected
judge scores + write the scorecard). The LLM judging, multi-judge convergence, and
safety-veto check happen BETWEEN these two calls, orchestrated by the skill via the
Agent tool. No scoring heuristic lives here.

Default rubric: role-casting-fit (kind: decision, high_stakes: true, min_judges: 2).
Override with --rubric for any other decision rubric.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib import evl_pipeline as P  # noqa: E402
from platform_lib.paths import RUBRICS, resolve_character  # noqa: E402

_DEFAULT_RUBRIC = "role-casting-fit"


def _rubric_path(ref: str) -> Path:
    """Resolve a rubric id or path, mirroring run_score.py's convention."""
    p = Path(ref)
    if p.exists():
        return p
    return RUBRICS / (ref if ref.endswith(".yaml") else f"{ref}.yaml")


def main():
    ap = argparse.ArgumentParser(
        description=(
            "evl:fit — gather evidence / finalize scorecard for role / casting-fit "
            "decisions (deterministic; LLM judges and safety-veto check run between "
            "the two steps)"
        )
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("gather", help="emit the evidence bundle for the LLM judges")
    g.add_argument("--character", required=True)
    g.add_argument(
        "--rubric",
        default=_DEFAULT_RUBRIC,
        help=f"decision rubric id or path under docs/rubrics/ (default: {_DEFAULT_RUBRIC})",
    )

    f = sub.add_parser("finalize", help="aggregate judge scores + write the scorecard")
    f.add_argument("--character", required=True)
    f.add_argument(
        "--rubric",
        default=_DEFAULT_RUBRIC,
        help=f"decision rubric id or path under docs/rubrics/ (default: {_DEFAULT_RUBRIC})",
    )
    f.add_argument(
        "--scores",
        required=True,
        help="path to judge scores JSON (CriterionScore list, post-convergence)",
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
        char, rubric_path, scores, asof=args.asof, updated_by="evl:fit"
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
