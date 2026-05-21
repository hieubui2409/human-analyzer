"""Audit cross-domain event consistency across all declaration sources."""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import ROOT

SKILLS_DIR = ROOT / ".claude" / "skills"
RULES_DIR = ROOT / "docs" / "rules"

SOURCE_SCRIPTS = {
    "valid_types": SKILLS_DIR / "orc-event-log" / "scripts" / "append-event-to-log.py",
    "event_routing": SKILLS_DIR / "orc-session-state" / "scripts" / "recommend-downstream-actions-from-events.py",
    "path_map": SKILLS_DIR / "orc-session-state" / "scripts" / "detect-domain-state-changes-from-git-diff.py",
    "domain_router": SKILLS_DIR / "orc-domain-router" / "scripts" / "route-domain-events-from-state.py",
}

EVENT_PATTERN = re.compile(r'["\']([A-Z]{2,4}\.\w+)["\']')
RULES_FILE = "12-orc-orchestration.md"


def extract_events_from_python(filepath: Path) -> list[str]:
    if not filepath.exists():
        return []
    text = filepath.read_text(encoding="utf-8")
    return sorted(set(EVENT_PATTERN.findall(text)))


def extract_events_from_skill_mds() -> dict[str, list[str]]:
    results = {}
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        text = skill_md.read_text(encoding="utf-8")
        events = EVENT_PATTERN.findall(text)
        if events:
            results[skill_dir.name] = sorted(set(events))
    return results


def extract_events_from_rules() -> list[str]:
    rules_file = RULES_DIR / RULES_FILE
    if not rules_file.exists():
        return []
    text = rules_file.read_text(encoding="utf-8")
    return sorted(set(EVENT_PATTERN.findall(text)))


def build_event_index(
    skill_events: dict[str, list[str]],
    rules_events: list[str],
    script_events: dict[str, list[str]],
) -> dict[str, dict]:
    all_events = set()
    for evts in skill_events.values():
        all_events.update(evts)
    all_events.update(rules_events)
    for evts in script_events.values():
        all_events.update(evts)

    index = {}
    for event in sorted(all_events):
        present_in = []
        missing_from = []

        in_skills = any(event in evts for evts in skill_events.values())
        if in_skills:
            present_in.append("skill_md")
        else:
            missing_from.append("skill_md")

        if event in rules_events:
            present_in.append("rules")
        else:
            missing_from.append("rules")

        for source_name, evts in script_events.items():
            if event in evts:
                present_in.append(source_name)
            else:
                missing_from.append(source_name)

        index[event] = {"present_in": present_in, "missing_from": missing_from}
    return index


def filter_by_domain(index: dict, domain: str) -> dict:
    if domain == "all":
        return index
    prefix = domain + "."
    return {k: v for k, v in index.items() if k.startswith(prefix)}


def main():
    parser = argparse.ArgumentParser(description="Audit cross-domain event consistency")
    parser.add_argument("--domain", default="all", help="Filter domain (MAT|PSY|CRE|GRO|ORC|COM|all)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--fix-suggestions", action="store_true", help="Include fix suggestions")
    args = parser.parse_args()

    skill_events = extract_events_from_skill_mds()
    rules_events = extract_events_from_rules()
    script_events = {}
    for name, path in SOURCE_SCRIPTS.items():
        script_events[name] = extract_events_from_python(path)

    index = build_event_index(skill_events, rules_events, script_events)
    index = filter_by_domain(index, args.domain.upper() if args.domain != "all" else "all")

    mismatches = []
    consistent = []
    for event, info in index.items():
        if info["missing_from"]:
            entry = {"event": event, "present_in": info["present_in"], "missing_from": info["missing_from"]}
            if args.fix_suggestions:
                entry["suggestion"] = f"Add '{event}' to: {', '.join(info['missing_from'])}"
            mismatches.append(entry)
        else:
            consistent.append(event)

    domains_found = {}
    for event in index:
        domain = event.split(".")[0]
        domains_found.setdefault(domain, []).append(event)

    result = {
        "sources_scanned": 2 + len(SOURCE_SCRIPTS),
        "events_by_domain": domains_found,
        "mismatches": mismatches,
        "consistent": consistent,
        "summary": {
            "total_events": len(index),
            "consistent": len(consistent),
            "mismatched": len(mismatches),
        },
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    print(f"\n  Sources scanned: {result['sources_scanned']}")
    print(f"  Total events: {result['summary']['total_events']}")
    print(f"  Consistent: {result['summary']['consistent']}")
    print(f"  Mismatched: {result['summary']['mismatched']}")
    if mismatches:
        print("\n  Mismatches:")
        for m in mismatches:
            print(f"    {m['event']}: missing from {', '.join(m['missing_from'])}")


if __name__ == "__main__":
    main()
