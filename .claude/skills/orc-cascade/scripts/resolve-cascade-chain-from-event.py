"""Resolve a trigger event into its full cascade chain across domains."""
import argparse
import json
import sys

EVENT_ROUTING = {
    "MAT.integrated": {
        "domain": "MAT",
        "downstream": [
            {"skill": "psy:ref-audit", "args": "--discover"},
            {"skill": "psy:crossref", "args": ""},
        ],
        "emits": ["PSY.refresh"],
    },
    "MAT.archived": {
        "domain": "MAT",
        "downstream": [],
        "emits": [],
    },
    "PSY.refresh": {
        "domain": "PSY",
        "downstream": [
            {"skill": "psy:propagate", "args": ""},
            {"skill": "cre:voice-audit", "args": ""},
        ],
        "emits": ["CRE.recalibrate"],
    },
    "PSY.crisis": {
        "domain": "PSY",
        "downstream": [
            {"skill": "psy:crisis-assess", "args": ""},
        ],
        "emits": [],
    },
    "CRE.recalibrate": {
        "domain": "CRE",
        "downstream": [
            {"skill": "cre:privacy-guard", "args": ""},
        ],
        "emits": [],
    },
    "GRO.assessed": {
        "domain": "GRO",
        "downstream": [
            {"skill": "cre:post-writer", "args": "--recalibrate"},
        ],
        "emits": ["CRE.recalibrate"],
    },
    "GRO.forecast": {
        "domain": "GRO",
        "downstream": [],
        "emits": [],
    },
    "GRO.mentored": {
        "domain": "GRO",
        "downstream": [
            {"skill": "psy:crossref", "args": "--validate"},
        ],
        "emits": ["PSY.refresh"],
    },
    "GRO.profiled": {
        "domain": "GRO",
        "downstream": [
            {"skill": "cre:post-writer", "args": "--recalibrate"},
        ],
        "emits": ["CRE.recalibrate"],
    },
    "COM.rules_updated": {
        "domain": "COM",
        "downstream": [
            {"skill": "com:rules", "args": "--validate"},
        ],
        "emits": [],
    },
    "ORC.skill_updated": {
        "domain": "ORC",
        "downstream": [
            {"skill": "orc:bootstrap", "args": "--quick"},
        ],
        "emits": [],
    },
    "ORC.script_updated": {
        "domain": "ORC",
        "downstream": [
            {"skill": "orc:bootstrap", "args": "--quick"},
        ],
        "emits": [],
    },
}


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
