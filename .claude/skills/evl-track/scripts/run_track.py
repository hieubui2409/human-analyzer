#!/usr/bin/env python3
"""evl:track — deterministic score-over-time diff.

Thin by design: args → platform_lib calls → print. No heuristics, no causal
inference. The LLM reading the output decides why a score moved.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import resolve_character  # noqa: E402
from platform_lib.evl_tracker import (  # noqa: E402
    load_current,
    load_history,
    diff_scorecards,
    attribute_changes,
)

_SINCE_DEFAULT = "1970-01-01T00:00:00Z"


def _fmt_delta(val) -> str:
    if val is None:
        return "n/a (gap)"
    sign = "+" if val > 0 else ""
    return f"{sign}{val:.3f}"


def _print_markdown(char: str, rubric_id: str, curr: dict, prev: dict,
                    diff: dict, events: list, since: str) -> None:
    print(f"# evl:track — {char} / {rubric_id}\n")

    # Scorecard timestamps
    prev_asof = prev.get("asof", "unknown")
    curr_asof = curr.get("asof", "unknown")
    print(f"**Previous snapshot:** {prev_asof}")
    print(f"**Current scorecard:** {curr_asof}\n")

    # Overall
    print("## Overall")
    print(f"| Metric | Previous | Current | Delta |")
    print(f"|--------|----------|---------|-------|")
    print(f"| Score | {prev.get('overall', 'n/a')} | {curr.get('overall', 'n/a')} "
          f"| {_fmt_delta(diff['overall_delta'])} |")
    print(f"| Coverage | {prev.get('verified_coverage', 'n/a')} "
          f"| {curr.get('verified_coverage', 'n/a')} "
          f"| {_fmt_delta(diff['coverage_delta'])} |")

    vc = diff.get("verdict_change")
    if vc:
        print(f"| Verdict | {vc[0]} | {vc[1]} | changed |")
    else:
        print(f"| Verdict | {prev.get('verdict', 'n/a')} | {curr.get('verdict', 'n/a')} | — |")
    print()

    # Domain deltas
    domains = diff.get("domains", [])
    if domains:
        print("## Domain Deltas")
        print("| Domain | Previous | Current | Delta |")
        print("|--------|----------|---------|-------|")
        for d in domains:
            print(f"| {d['id']} | {d['prev'] if d['prev'] is not None else 'n/a'} "
                  f"| {d['curr'] if d['curr'] is not None else 'n/a'} "
                  f"| {_fmt_delta(d['delta'])} |")
        print()

    # Profile-change events in the window
    since_label = since if since != _SINCE_DEFAULT else "all time"
    print(f"## Profile-Change Events (since {since_label})")
    if events:
        for ev in events:
            ts = ev.get("timestamp", "?")
            # Live event records use `event` + `reason`; tolerate older field names.
            etype = ev.get("event", ev.get("event_type", ev.get("type", "?")))
            detail = ev.get("reason", ev.get("detail", ev.get("description", "")))
            print(f"- `{ts}` **{etype}**" + (f" — {detail}" if detail else ""))
    else:
        print("_No recorded profile-change events in this window._")
    print()
    print("> Causal attribution is the LLM's job: the events above are deterministically "
          "joined by timestamp, not asserted as causes.")


def main() -> None:
    ap = argparse.ArgumentParser(
        description="evl:track — diff current scorecard against latest history snapshot "
                    "(deterministic; LLM narrates causation from the output)")
    ap.add_argument("--character", required=True,
                    help="character name or slug (resolved via paths.resolve_character)")
    ap.add_argument("--rubric-id", required=True,
                    help="rubric id matching the scorecard filename stem")
    ap.add_argument("--since", default=_SINCE_DEFAULT,
                    help="ISO-Z timestamp — restrict event join to this date or later "
                         "(default: all history)")
    ap.add_argument("--json", dest="as_json", action="store_true",
                    help="emit machine-readable JSON instead of markdown")
    args = ap.parse_args()

    char = resolve_character(args.character)
    rubric_id = args.rubric_id
    since = args.since

    curr = load_current(char, rubric_id)
    if curr is None:
        print(f"No current scorecard found for {char!r} / {rubric_id!r}. "
              f"Run evl:score first.", file=sys.stderr)
        sys.exit(1)

    history = load_history(char, rubric_id)
    if not history:
        print(f"No history snapshots found for {char!r} / {rubric_id!r}. "
              f"Cannot diff a first run — run evl:score again after updating evidence, "
              f"then track.", file=sys.stderr)
        sys.exit(0)

    prev = history[-1]  # latest prior snapshot (chronological order from load_history)
    diff = diff_scorecards(prev, curr)
    events = attribute_changes(char, since)

    if args.as_json:
        print(json.dumps({
            "character": char,
            "rubric_id": rubric_id,
            "prev_asof": prev.get("asof"),
            "curr_asof": curr.get("asof"),
            "diff": diff,
            "events_since": since,
            "events": events,
        }, ensure_ascii=False, indent=2))
        return

    _print_markdown(char, rubric_id, curr, prev, diff, events, since)


if __name__ == "__main__":
    main()
