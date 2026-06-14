#!/usr/bin/env python3
"""evl:compare — deterministic cross-character ranking on one rubric.

Thin by design: args → platform_lib calls → print. Zero heuristics, zero LLM
judging. Scores must already exist (produced by evl:score). A character without
a scorecard is listed as missing — loud, never dropped, never imputed as zero.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib import evl_compare  # noqa: E402
from platform_lib.paths import ALL_CHARS, resolve_character  # noqa: E402


def _resolve_characters(raw: str) -> list[str]:
    """Parse a comma-separated character list and resolve each alias to its canonical slug."""
    resolved = []
    errors = []
    for token in raw.split(","):
        token = token.strip()
        if not token:
            continue
        try:
            resolved.append(resolve_character(token))
        except ValueError as exc:
            errors.append(str(exc))
    if errors:
        sys.exit("evl:compare — unknown character(s):\n" + "\n".join(errors))
    return resolved


def main() -> None:
    ap = argparse.ArgumentParser(
        description=(
            "evl:compare — rank characters on one rubric using existing scorecards. "
            "Fully deterministic; no LLM judgment. Run evl:score first to produce scorecards."
        )
    )
    ap.add_argument(
        "--rubric-id",
        required=True,
        help="Rubric id matching scorecard filenames under docs/profiles/{char}/eval/",
    )
    ap.add_argument(
        "--characters",
        default=None,
        help="Comma-separated character names/aliases (default: all characters in roster)",
    )
    ap.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Emit machine-readable JSON instead of the rendered markdown table",
    )
    args = ap.parse_args()

    characters = _resolve_characters(args.characters) if args.characters else list(ALL_CHARS)

    result = evl_compare.compare(args.rubric_id, characters)

    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(evl_compare.render_comparison(result))


if __name__ == "__main__":
    main()
