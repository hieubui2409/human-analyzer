"""Append a single ORC framework event as a JSON line to the persistent event log."""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import SESSION_STATE, EVENT_STREAMS, CASCADE_EVENTS

VALID_EVENT_TYPES = [
    "MAT.integrated",
    "MAT.archived",
    "PSY.refresh",
    "PSY.crisis",
    "PSY.relation-angle-discovered",
    "CRE.recalibrate",
    "CRE.evidence-checked",
    "CRE.angle-discovered",
    "CRE.published",
    "GRO.assessed",
    "GRO.forecast",
    "GRO.mentored",
    "GRO.profiled",
    "ORC.bootstrap",
    "ORC.decision",
    "ORC.classify",
    "ORC.intake",
    "COM.privacy",
    "COM.governance",
    "COM.commit",
]


def resolve_stream(event_type: str):
    """Route an event to its framework stream by prefix; unknown → cascade-events."""
    framework = event_type.split(".", 1)[0].upper()
    return EVENT_STREAMS.get(framework, CASCADE_EVENTS), framework


def main():
    parser = argparse.ArgumentParser(
        description="Append a ORC framework event to the persistent event log"
    )
    parser.add_argument("--event-type", required=True,
                        help=f"Event type. Known: {', '.join(VALID_EVENT_TYPES)}")
    parser.add_argument("--source", required=True,
                        help="Originating skill (e.g. mat:indexer, psy:wave)")
    parser.add_argument("--character", default="",
                        help="Character slug (optional, e.g. character-a)")
    parser.add_argument("--reason", default="",
                        help="Human-readable reason for the event")
    args = parser.parse_args()

    # Warn for unknown event types but allow custom ones
    if args.event_type not in VALID_EVENT_TYPES:
        print(f"WARNING: '{args.event_type}' is not a known event type. Appending anyway.",
              file=sys.stderr)

    # Route to the framework stream by event-type prefix
    log_file, framework = resolve_stream(args.event_type)
    if framework not in EVENT_STREAMS:
        print(f"WARNING: unknown framework prefix '{framework}' — routing to cascade-events.jsonl.",
              file=sys.stderr)

    # Ensure directory exists
    SESSION_STATE.mkdir(parents=True, exist_ok=True)

    event = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "event": args.event_type,
        "source": args.source,
        "character": args.character or None,
        "reason": args.reason or None,
    }
    # Remove None values for compact log
    event = {k: v for k, v in event.items() if v is not None}

    with log_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    print(f"Event logged: {event['event']} from {event['source']}"
          + (f" [{event['character']}]" if "character" in event else "")
          + f" at {event['timestamp']}")
    print(f"Stream: {log_file.name}")


if __name__ == "__main__":
    main()
