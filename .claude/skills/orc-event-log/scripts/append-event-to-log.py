"""Append a single MPC framework event as a JSON line to the persistent event log."""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import SESSION_STATE

LOG_FILE = SESSION_STATE / "event-log.jsonl"

VALID_EVENT_TYPES = [
    "MAT.integrated",
    "MAT.archived",
    "PSY.refresh",
    "PSY.crisis",
    "CRE.recalibrate",
    "MPC.bootstrap",
    "MPC.decision",
    "MPC.classify",
    "MPC.intake",
]


def main():
    parser = argparse.ArgumentParser(
        description="Append a MPC framework event to the persistent event log"
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

    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    print(f"Event logged: {event['event']} from {event['source']}"
          + (f" [{event['character']}]" if "character" in event else "")
          + f" at {event['timestamp']}")
    print(f"Log file: {LOG_FILE}")


if __name__ == "__main__":
    main()
