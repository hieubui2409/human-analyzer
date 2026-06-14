"""Append a single ORC framework event as a JSON line to the persistent event log."""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import TELEMETRY, EVENT_STREAMS, CASCADE_EVENTS
from platform_lib.event_routing import routable_events

# Audit-only events not in the routing table (internal lifecycle / CRE / COM signals).
# Every event a skill's SKILL.md "## Events" table declares it emits must be loggable
# here, or the emit is rejected at runtime — orc:audit C1 enforces routable⊆loggable and
# flags any declared-but-unregistered event.
_AUDIT_EVENT_TYPES = [
    "MAT.archived",
    "MAT.contradiction",  # emitted by mat:indexer on medium+ contradictions (rules-12 logging table)
    "PSY.crisis",
    "PSY.relation-angle-discovered",
    "CRE.evidence-checked",
    "CRE.angle-discovered",
    "CRE.published",
    "CRE.privacy_cleared",  # emitted by cre:privacy-guard on a clean scan (rules-14 §CRE.privacy_cleared)
    "CRE.humanized",  # emitted by cre:humanize after a scan/rewrite (log only)
    "EVL.compared",        # emitted by evl:compare when a cross-character ranking may feed CRE (log only, no cascade)
    "EVL.tracked",         # emitted by evl:track on a significant verdict/coverage change (log only)
    "EVL.rubric_imported", # emitted by evl:rubric-import after a draft rubric is written (log only)
    "ORC.bootstrap",
    "ORC.decision",
    "ORC.classify",
    "ORC.intake",
    "ORC.audited",  # emitted by orc:audit after an audit run (log only)
    "ORC.routed",   # emitted by orc:domain-router after routing events downstream
    "COM.privacy",
    "COM.governance",
    "COM.commit",
]

# Union of routable events (from canonical table) and audit-only events above.
VALID_EVENT_TYPES = sorted(set(_AUDIT_EVENT_TYPES) | set(routable_events()))


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
    TELEMETRY.mkdir(parents=True, exist_ok=True)

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
