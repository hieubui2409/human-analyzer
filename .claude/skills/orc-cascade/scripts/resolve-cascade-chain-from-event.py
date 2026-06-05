"""Resolve a trigger event into its full cascade chain across domains."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.event_routing import EVENT_ROUTING


def resolve_chain(trigger: str, max_depth: int) -> dict:
    chain = []
    visited = set()
    circular = False
    queue = [(trigger, 0)]

    while queue:
        event, depth = queue.pop(0)
        if depth > max_depth:
            continue
        if event in visited:
            circular = True
            continue
        visited.add(event)

        routing = EVENT_ROUTING.get(event)
        if not routing:
            chain.append({
                "depth": depth, "event": event,
                "domain": event.split(".")[0], "downstream_skills": [],
                "note": "unknown event — no routing defined",
            })
            continue

        chain.append({
            "depth": depth, "event": event,
            "domain": routing["domain"],
            "downstream_skills": [s["skill"] for s in routing["downstream"]],
        })

        for emitted in routing.get("emits", []):
            queue.append((emitted, depth + 1))

    return {
        "trigger": trigger,
        "max_depth": max_depth,
        "chain": chain,
        "circular_detected": circular,
        "total_steps": len(chain),
    }


def main():
    parser = argparse.ArgumentParser(description="Resolve event cascade chain")
    parser.add_argument("--trigger", required=True, help="Starting event")
    parser.add_argument("--max-depth", type=int, default=5, help="Max cascade depth")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    result = resolve_chain(args.trigger, args.max_depth)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    print(f"\n  Cascade: {result['trigger']}")
    print(f"  Steps: {result['total_steps']}")
    if result["circular_detected"]:
        print("  ⚠ Circular reference detected!")
    for step in result["chain"]:
        indent = "  " + "  " * step["depth"]
        skills = ", ".join(step["downstream_skills"]) or "(terminal)"
        print(f"{indent}→ {step['event']} [{step['domain']}] → {skills}")


if __name__ == "__main__":
    main()
