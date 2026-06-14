#!/usr/bin/env python3
"""evl:compatibility — deterministic gather + finalize wrapper for dyad rubrics.

Thin by design: it does the two DETERMINISTIC ends of the dyad scoring flow —
`gather` (emit the pooled per-criterion evidence bundle from BOTH characters) and
`finalize` (aggregate the collected judge scores + write the dyad scorecard). The
LLM judging happens BETWEEN these two calls, orchestrated by the skill via the
Agent tool. No scoring heuristic lives here.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib import evl_pipeline as P  # noqa: E402
from platform_lib.paths import RUBRICS, resolve_character  # noqa: E402

_DEFAULT_RUBRIC = "relationship-compatibility"


def _rubric_path(ref: str) -> Path:
    p = Path(ref)
    if p.exists():
        return p
    return RUBRICS / (ref if ref.endswith(".yaml") else f"{ref}.yaml")


def main():
    ap = argparse.ArgumentParser(
        description=(
            "evl:compatibility — gather dyad evidence / finalize dyad scorecard "
            "(deterministic; LLM judges run between the two steps)"
        )
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("gather", help="emit the pooled evidence bundle for the LLM judges")
    g.add_argument("--character-a", required=True, dest="character_a",
                   help="first character in the pair")
    g.add_argument("--character-b", required=True, dest="character_b",
                   help="second character in the pair")
    g.add_argument("--rubric", default=_DEFAULT_RUBRIC,
                   help=f"dyad rubric id or path under docs/rubrics/ (default: {_DEFAULT_RUBRIC})")

    f = sub.add_parser("finalize", help="aggregate judge scores + write the dyad scorecard")
    f.add_argument("--character-a", required=True, dest="character_a")
    f.add_argument("--character-b", required=True, dest="character_b")
    f.add_argument("--rubric", default=_DEFAULT_RUBRIC,
                   help=f"dyad rubric id or path under docs/rubrics/ (default: {_DEFAULT_RUBRIC})")
    f.add_argument("--scores", required=True,
                   help="path to judge scores JSON (CriterionScore list)")
    f.add_argument("--asof", required=True,
                   help="ISO date stamped on the scorecard (YYYY-MM-DD)")

    args = ap.parse_args()

    char_a = resolve_character(args.character_a)
    char_b = resolve_character(args.character_b)
    rubric_path = _rubric_path(args.rubric)

    if args.cmd == "gather":
        payload = P.gather_dyad_payload((char_a, char_b), rubric_path)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    scores = json.loads(Path(args.scores).read_text(encoding="utf-8"))
    path, result = P.finalize_dyad_scorecard(
        (char_a, char_b),
        rubric_path,
        scores,
        asof=args.asof,
        updated_by="evl:compatibility",
    )
    print(json.dumps({
        "scorecard": str(path),
        "pair": [char_a, char_b],
        "overall": result["overall"],
        "verdict": result["verdict"],
        "unverified": result["unverified"],
        "below_min_tier": result["below_min_tier"],
        "coverage": result["verified_coverage"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
