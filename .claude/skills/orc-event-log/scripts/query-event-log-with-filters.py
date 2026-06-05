"""Query the ORC event log with optional filters and render a formatted table."""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import EVENT_STREAMS, resolve_character


def parse_date(date_str: str) -> datetime:
    """Parse YYYY-MM-DD to UTC datetime."""
    return datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)


def _read_stream(path) -> list[dict]:
    if not path.exists():
        return []
    events = []
    with path.open(encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
                ev["_stream"] = path.name
                events.append(ev)
            except json.JSONDecodeError as e:
                print(f"WARNING: skipping malformed line {i} in {path.name}: {e}", file=sys.stderr)
    return events


def load_events(framework: str = "all") -> list[dict]:
    """Read one framework stream, or merge all 6 sorted by timestamp."""
    if framework == "all":
        paths = list(EVENT_STREAMS.values())
    else:
        path = EVENT_STREAMS.get(framework.upper())
        paths = [path] if path else []
    events = []
    for p in paths:
        events.extend(_read_stream(p))
    events.sort(key=lambda e: e.get("timestamp", ""))
    return events


def apply_filters(
    events: list[dict],
    event_type: str | None,
    character: str | None,
    source: str | None,
    since: datetime | None,
    until: datetime | None,
) -> list[dict]:
    result = []
    for ev in events:
        if event_type and ev.get("event") != event_type:
            continue
        if character and ev.get("character") != character:
            continue
        if source and ev.get("source") != source:
            continue
        if since or until:
            try:
                ts = datetime.strptime(ev["timestamp"], "%Y-%m-%dT%H:%M:%SZ").replace(
                    tzinfo=timezone.utc
                )
                if since and ts < since:
                    continue
                if until and ts > until:
                    continue
            except (KeyError, ValueError):
                pass
        result.append(ev)
    return result


def format_timestamp(ts: str) -> str:
    """Shorten ISO timestamp for table display."""
    try:
        dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return ts[:16]


def main():
    parser = argparse.ArgumentParser(description="Query the ORC event log with filters")
    parser.add_argument("--event-type", help="Filter by event type")
    parser.add_argument("--character", help="Filter by character slug")
    parser.add_argument("--source", help="Filter by source skill")
    parser.add_argument("--since", help="Events on or after YYYY-MM-DD")
    parser.add_argument("--until", help="Events on or before YYYY-MM-DD")
    parser.add_argument("--framework", default="all",
                        choices=["all", "psy", "mat", "cre", "gro", "orc", "com"],
                        help="Framework stream to query (default: all, merged sorted)")
    parser.add_argument("--limit", type=int, default=20,
                        help="Max results to show (default: 20)")
    parser.add_argument("--json", dest="json_out", action="store_true", help="Raw JSON output")
    args = parser.parse_args()

    since = parse_date(args.since) if args.since else None
    until = parse_date(args.until) if args.until else None

    all_events = load_events(args.framework)

    if not all_events:
        print(f"No events found for framework='{args.framework}'.")
        print("Use `orc:event-log --append` to log events.")
        return

    # Resolve character alias to canonical slug before filtering (e.g. "hieu" -> "character-a").
    resolved_character = None
    if args.character:
        try:
            resolved_character = resolve_character(args.character)
        except ValueError:
            # Unknown alias — pass through as-is so partial matches still work
            resolved_character = args.character

    filtered = apply_filters(
        all_events,
        event_type=args.event_type,
        character=resolved_character,
        source=args.source,
        since=since,
        until=until,
    )

    # Most recent first
    filtered = list(reversed(filtered))

    if args.json_out:
        print(json.dumps(filtered[: args.limit], indent=2, ensure_ascii=False))
        return

    # Build filter description
    filters_desc = []
    if args.event_type:
        filters_desc.append(f"event-type={args.event_type}")
    if args.character:
        filters_desc.append(f"character={args.character}")
    if args.source:
        filters_desc.append(f"source={args.source}")
    if args.since:
        filters_desc.append(f"since={args.since}")
    if args.until:
        filters_desc.append(f"until={args.until}")

    print(f"\n{'='*70}")
    print("  Event Log Query")
    print(f"{'='*70}")
    print(f"  Filters: {', '.join(filters_desc) or 'none'}")
    print(f"  Total in log: {len(all_events)} | Matched: {len(filtered)} | "
          f"Showing: {min(len(filtered), args.limit)}")
    print()

    if not filtered:
        print("  No events match the given filters.")
        return

    display = filtered[: args.limit]
    print(f"  {'Timestamp':<18s} {'Event':<20s} {'Source':<18s} {'Character':<20s} Reason")
    print(f"  {'-'*18} {'-'*20} {'-'*18} {'-'*20} {'-'*30}")

    for ev in display:
        ts = format_timestamp(ev.get("timestamp", ""))
        event = ev.get("event", "")[:18]
        source = ev.get("source", "")[:16]
        char = ev.get("character", "—")[:18]
        reason = ev.get("reason", "")[:35] or "—"
        print(f"  {ts:<18s} {event:<20s} {source:<18s} {char:<20s} {reason}")

    if len(filtered) > args.limit:
        print(f"\n  ... {len(filtered) - args.limit} more events (use --limit N to see more)")

    # Quick summary by event type
    if len(filtered) > 5:
        from collections import Counter
        by_type = Counter(ev.get("event", "unknown") for ev in filtered)
        print(f"\n  Breakdown by event type:")
        for etype, count in by_type.most_common():
            print(f"    {etype}: {count}")


if __name__ == "__main__":
    main()
