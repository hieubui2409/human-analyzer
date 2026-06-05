"""Route domain events to downstream skills from git diff or explicit event."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import ROOT
from platform_lib.event_routing import (
    downstream_for,
    detect_events,  # canonical shared implementation (applies IGNORE_PATTERNS + dedup)
)


def get_changed_files(ref: str) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", ref],
            capture_output=True, text=True, cwd=str(ROOT)
        )
        return [f for f in result.stdout.strip().splitlines() if f] if result.returncode == 0 else []
    except (OSError, subprocess.SubprocessError):
        return []


def route_events(events: list[dict]) -> list[dict]:
    recommendations = []
    for evt in events:
        actions = downstream_for(evt["event"])
        for action in actions:
            recommendations.append({
                "skill": action["skill"],
                "args": action["args"],
                "reason": action["reason"],
                "triggered_by": evt["event"],
            })
    return recommendations


def route_explicit_event(event_name: str) -> list[dict]:
    actions = downstream_for(event_name)
    return [
        {"skill": a["skill"], "args": a["args"], "reason": a["reason"], "triggered_by": event_name}
        for a in actions
    ]


def main():
    parser = argparse.ArgumentParser(description="Route domain events to downstream skills")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--event", help="Route a specific named event")
    group.add_argument("--from-diff", action="store_true", help="Detect events from git diff")
    parser.add_argument("--ref", default="HEAD~1", help="Git ref to diff against")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--dry-run", action="store_true", help="Show routing without executing")
    args = parser.parse_args()

    if args.event:
        events = [{"event": args.event, "domain": args.event.split(".")[0], "trigger_files": []}]
        recommendations = route_explicit_event(args.event)
    else:
        files = get_changed_files(args.ref)
        events = detect_events(files)
        recommendations = route_events(events)

    result = {
        "mode": "explicit" if args.event else "diff",
        "events_detected": events,
        "recommendations": recommendations,
        "dry_run": args.dry_run,
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    print(f"\n  Mode: {result['mode']}")
    print(f"  Events: {len(events)}")
    print(f"  Recommendations: {len(recommendations)}")
    if args.dry_run:
        print("  [DRY RUN — no execution]")
    for i, rec in enumerate(recommendations, 1):
        print(f"\n  {i}. {rec['skill']} {rec['args']}")
        print(f"     Triggered by: {rec['triggered_by']}")
        print(f"     Reason: {rec['reason']}")


if __name__ == "__main__":
    main()
