"""Recommend downstream actions from domain events for orc:session-state."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

EVENT_ROUTING = {
    "MAT.integrated": [
        {"skill": "psy:ref-audit", "args": "--discover", "reason": "New material may reveal blind spots in references"},
        {"skill": "psy:crossref", "args": "", "reason": "Cross-validate profiles against new material"},
        {"skill": "mat:indexer", "args": "--contradictions", "reason": "Check for contradictions with existing profiles"},
    ],
    "PSY.refresh": [
        {"skill": "psy:propagate", "args": "", "reason": "Detect cross-character cascade needs from profile change"},
        {"skill": "cre:voice-audit", "args": "", "reason": "Profile change may affect content voice"},
        {"skill": "cre:post-writer", "args": "--recalibrate", "reason": "Recalibrate content creation context"},
        {"skill": "psy:crossref", "args": "--validate", "reason": "Verify cross-character consistency"},
    ],
    "PSY.updated": [
        {"skill": "psy:propagate", "args": "", "reason": "Cascade profile changes to related characters"},
        {"skill": "psy:crossref", "args": "--extended", "reason": "Re-validate all 10 dimensions after update"},
        {"skill": "cre:voice-audit", "args": "", "reason": "Check if voice data needs recalibration"},
        {"skill": "orc:event-log", "args": "--append --event-type PSY.updated", "reason": "Log profile update to audit trail"},
    ],
    "CRE.recalibrate": [
        {"skill": "cre:privacy-guard", "args": "", "reason": "New content needs privacy scan"},
        {"skill": "cre:voice-audit", "args": "", "reason": "Verify voice consistency in new content"},
    ],
    "COM.rules_updated": [
        {"skill": "com:rules", "args": "--validate", "reason": "Verify rule consistency after update"},
    ],
    "ORC.skill_updated": [
        {"skill": "orc:bootstrap", "args": "--quick", "reason": "Refresh session context with updated skills"},
    ],
    "ORC.script_updated": [
        {"skill": "orc:bootstrap", "args": "--quick", "reason": "Refresh session context with updated scripts"},
    ],
    "GRO.assessed": [
        {"skill": "cre:post-writer", "args": "--recalibrate", "reason": "Competency data changed — recalibrate content context"},
    ],
    "GRO.forecast": [],
    "GRO.mentored": [
        {"skill": "psy:crossref", "args": "--validate", "reason": "Mentoring may reveal cross-character psychological insights"},
    ],
    "GRO.profiled": [
        {"skill": "cre:post-writer", "args": "--recalibrate", "reason": "Learning profile changed — recalibrate content context"},
    ],
}


def recommend_actions(events: list[dict]) -> list[dict]:
    """Given events, recommend downstream skill invocations."""
    recommendations = []
    seen = set()

    for event in events:
        event_type = event.get("event", "")
        actions = EVENT_ROUTING.get(event_type, [])
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
