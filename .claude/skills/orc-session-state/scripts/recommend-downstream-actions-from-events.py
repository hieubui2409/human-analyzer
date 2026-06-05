"""Recommend downstream actions from domain events for orc:session-state."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.event_routing import downstream_for


def recommend_actions(events: list[dict]) -> list[dict]:
    """Given events, recommend downstream skill invocations."""
    recommendations = []
    seen = set()

    for event in events:
        event_type = event.get("event", "")
        actions = downstream_for(event_type)
        trigger_files = event.get("trigger_files", [])

        # Extract character slug from trigger files
        char_slug = ""
        for f in trigger_files:
            parts = f.split("/")
            if len(parts) >= 3 and parts[0] == "docs":
                char_slug = parts[2]
                break

        for action in actions:
            key = f"{action['skill']}:{char_slug}"
            if key in seen:
                continue
            seen.add(key)

            args = action["args"]
            if char_slug and "--character" not in args:
                args = f"--character {char_slug} {args}".strip()

            recommendations.append({
                "skill": action["skill"],
                "args": args,
                "reason": action["reason"],
                "triggered_by": event_type,
                "priority": len(recommendations) + 1,
            })

    return recommendations


def main():
    parser = argparse.ArgumentParser(description="Recommend downstream actions from events")
    parser.add_argument("--events-file", help="JSON file with events (from detect-domain-state-changes)")
    parser.add_argument("--events-json", help="Inline JSON events string")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    events = []
    if args.events_file:
        with open(args.events_file) as f:
            events = json.load(f)
    elif args.events_json:
        events = json.loads(args.events_json)
    else:
        data = sys.stdin.read().strip()
        if data:
            events = json.loads(data)

    if not events:
        print("No events provided. Pipe from detect-domain-state-changes or use --events-file.")
        sys.exit(0)

    recommendations = recommend_actions(events)

    if args.json:
        print(json.dumps(recommendations, indent=2, ensure_ascii=False))
        return

    print(f"\n  Recommendations based on {len(events)} event(s):")
    print(f"\n  {'#':<4s} {'Skill':<20s} {'Args':<30s} {'Triggered By':<18s}")
    print(f"  {'-'*4} {'-'*20} {'-'*30} {'-'*18}")

    for rec in recommendations:
        print(f"  {rec['priority']:<4d} {rec['skill']:<20s} {rec['args']:<30s} {rec['triggered_by']:<18s}")
        print(f"       Reason: {rec['reason']}")


if __name__ == "__main__":
    main()
