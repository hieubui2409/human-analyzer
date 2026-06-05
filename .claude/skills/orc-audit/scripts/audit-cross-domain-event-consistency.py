"""Audit cross-domain event consistency against the canonical routing registry.

The single source of truth for event routing is ``platform_lib/event_routing.py``
(``EVENT_ROUTING`` + ``DOMAIN_PATH_RULES``). Consumers import it rather than
re-declaring event strings, so this audit reads the canonical tables directly and
checks referential-integrity invariants — instead of scraping literal strings out
of consumer scripts that no longer hold them.

Machine registries (imported, never regex-scraped):
  routable     EVENT_ROUTING keys                         (the routable vocabulary)
  valid_types  append-event-to-log VALID_EVENT_TYPES      (everything loggable)
  path_map     DOMAIN_PATH_RULES targets + GRO.profiled   (events raised by file diffs)
  emits        EVENT_ROUTING[*].emits                     (cascade targets)

Hard invariants — a violation is a real wiring break:
  C1  routable ⊆ valid_types   every routable event is loggable
  C2  emits ⊆ routable         every cascade target is itself a routable event
  C3  path_map ⊆ routable      every diff-derived event is routable

Doc-sync advisories — surfaced, not failures (rules/SKILL.md are prose):
  C4  every event mentioned in rules-12 / SKILL.md is a known event (no orphan docs)
  C5  every routable event is documented in rules-12

Doc sources are markdown, so event mentions there are extracted with a
domain-anchored regex; the machine registries are always imported.
"""
import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.event_routing import (
    EVENT_ROUTING,
    DOMAIN_PATH_RULES,
    routable_events,
    emits_for,
)
from platform_lib.paths import ROOT

SKILLS_DIR = ROOT / ".claude" / "skills"
RULES_DIR = ROOT / "docs" / "rules"
CLAUDE_MD = ROOT / "CLAUDE.md"
RULES_FILE = "12-orc-orchestration.md"
FRAMEWORK_PREFIXES = ("com-", "cre-", "gro-", "mat-", "orc-", "psy-")
DOMAINS = ("MAT", "PSY", "CRE", "GRO", "ORC", "COM")

# Domain-anchored so it cannot match stray tokens like ``NOTES.md`` — only the
# six framework prefixes followed by a lowercase event suffix qualify.
EVENT_PATTERN = re.compile(r"\b(?:" + "|".join(DOMAINS) + r")\.[a-z][a-z_\-]*\b")

# Events derived from a path diff but not keyed directly in DOMAIN_PATH_RULES
# (the PSY→GRO refinement on ``/growth/`` paths). Kept explicit so C3 sees it.
_PATH_DERIVED_EXTRA = {"GRO.profiled"}


def load_valid_event_types() -> set[str]:
    """Import the logger module and read its authoritative VALID_EVENT_TYPES."""
    path = SKILLS_DIR / "orc-event-log" / "scripts" / "append-event-to-log.py"
    if not path.exists():
        return set()
    spec = importlib.util.spec_from_file_location("_orc_append_event_log", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return set(getattr(module, "VALID_EVENT_TYPES", []))


def events_in_markdown(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return set(EVENT_PATTERN.findall(path.read_text(encoding="utf-8")))


# Only the "## Events" / "### Events" section of a SKILL.md is an emit contract —
# events named elsewhere (prose, "known event types" lists, downstream references)
# are not declarations that the skill emits them, so they must not be flagged.
_EVENTS_SECTION = re.compile(r"\n#{2,4}\s+Events\b(.*?)(\n#{2,4}\s+|\Z)", re.S)


def declared_emits_in_skill_mds() -> dict[str, set[str]]:
    results = {}
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        match = _EVENTS_SECTION.search(skill_md.read_text(encoding="utf-8"))
        if not match:
            continue
        events = set(EVENT_PATTERN.findall(match.group(1)))
        if events:
            results[skill_dir.name] = events
    return results


def path_map_events() -> set[str]:
    return {rule["event"] for rule in DOMAIN_PATH_RULES.values()} | _PATH_DERIVED_EXTRA


def emit_targets() -> set[str]:
    targets = set()
    for event in EVENT_ROUTING:
        targets.update(emits_for(event))
    return targets


def validate_skill_count() -> dict:
    """Assert framework skill count matches CLAUDE.md declared count."""
    actual_skills = [
        d.name
        for d in sorted(SKILLS_DIR.iterdir())
        if d.is_dir() and d.name.startswith(FRAMEWORK_PREFIXES) and (d / "SKILL.md").exists()
    ]
    declared_count = None
    if CLAUDE_MD.exists():
        match = re.search(r"(\d+)\s+(?:framework\s+)?skills?\b", CLAUDE_MD.read_text(encoding="utf-8"), re.IGNORECASE)
        if match:
            declared_count = int(match.group(1))
    return {
        "actual_count": len(actual_skills),
        "declared_count": declared_count,
        "actual_skills": actual_skills,
        "match": (len(actual_skills) == declared_count) if declared_count else None,
    }


def run_checks() -> dict:
    routable = set(routable_events())
    valid_types = load_valid_event_types()
    known = routable | valid_types
    path_events = path_map_events()
    emits = emit_targets()
    rules_events = events_in_markdown(RULES_DIR / RULES_FILE)
    declared_emits = declared_emits_in_skill_mds()
    emit_union = set().union(*declared_emits.values()) if declared_emits else set()

    violations = []  # hard wiring breaks (C1-C3) + emit-contract breaches (C4)
    advisories = []  # doc-sync drift (C5) + conceptual-convention notes (C6)

    for ev in sorted(routable - valid_types):
        violations.append({"check": "C1", "event": ev, "detail": "routable but not in VALID_EVENT_TYPES (not loggable)"})
    for ev in sorted(emits - routable):
        violations.append({"check": "C2", "event": ev, "detail": "named in an emits cascade but not a routable event"})
    for ev in sorted(path_events - routable):
        violations.append({"check": "C3", "event": ev, "detail": "path-map target is not a routable event"})
    # A skill's "## Events" table is an emit contract: declaring an event the logger
    # rejects is a real breach (the emit would fail), so this is a hard violation.
    for ev in sorted(emit_union - known):
        violations.append({"check": "C4", "event": ev, "detail": "declared in a SKILL.md ## Events table but not loggable — emit would be rejected"})

    for ev in sorted(routable - rules_events):
        advisories.append({"check": "C5", "event": ev, "detail": "routable event not documented in rules-12"})
    # rules-12 Core Events are explicitly conventions, not code (rules-12 header), so a
    # conceptual event with no wiring is expected — surfaced for typo/staleness review only.
    for ev in sorted(rules_events - known):
        advisories.append({"check": "C6", "event": ev, "detail": "rules-12 conceptual convention, not wired as loggable/routable (informational)"})

    return {
        "routable": sorted(routable),
        "valid_types": sorted(valid_types),
        "path_map_events": sorted(path_events),
        "emit_targets": sorted(emits),
        "violations": violations,
        "advisories": advisories,
    }


def _filter_domain(items: list[dict], domain: str) -> list[dict]:
    if domain == "ALL":
        return items
    return [i for i in items if i["event"].startswith(domain + ".")]


def main():
    parser = argparse.ArgumentParser(description="Audit cross-domain event consistency")
    parser.add_argument("--domain", default="all", help="Filter domain (MAT|PSY|CRE|GRO|ORC|COM|all)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--fix-suggestions", action="store_true", help="Include fix suggestions")
    args = parser.parse_args()
    domain = args.domain.upper()

    skill_count = validate_skill_count()
    checks = run_checks()
    violations = _filter_domain(checks["violations"], domain)
    advisories = _filter_domain(checks["advisories"], domain)

    if args.fix_suggestions:
        for entry in violations + advisories:
            entry["suggestion"] = f"Reconcile '{entry['event']}': {entry['detail']}"

    result = {
        "sources_scanned": 5,
        "skill_count": skill_count,
        "registries": {
            "routable": checks["routable"],
            "valid_types": checks["valid_types"],
            "path_map_events": checks["path_map_events"],
            "emit_targets": checks["emit_targets"],
        },
        "violations": violations,
        "advisories": advisories,
        "summary": {
            "routable_events": len(checks["routable"]),
            "violations": len(violations),
            "advisories": len(advisories),
            "consistent": len(violations) == 0,
        },
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if not violations else 1

    sc = skill_count
    if sc["match"] is True:
        print(f"\n  ✓ Skill count assertion PASS: {sc['actual_count']} framework skills (matches CLAUDE.md)")
    elif sc["match"] is False:
        print(f"\n  ✗ Skill count assertion FAIL: actual={sc['actual_count']}, CLAUDE.md declares={sc['declared_count']}")
    else:
        print(f"\n  ? Skill count: {sc['actual_count']} framework skills found (CLAUDE.md count not parsed)")

    print(f"\n  Routable events: {len(checks['routable'])}  |  Loggable: {len(checks['valid_types'])}")
    print(f"  Hard violations (C1-C4): {len(violations)}")
    if violations:
        for v in violations:
            print(f"    ✗ [{v['check']}] {v['event']}: {v['detail']}")
    else:
        print("    ✓ Referential integrity holds — routable ⊆ loggable, emits/path-map ⊆ routable, declared emits loggable")

    print(f"\n  Doc-sync advisories (C5-C6): {len(advisories)}")
    for a in advisories:
        print(f"    · [{a['check']}] {a['event']}: {a['detail']}")

    return 0 if not violations else 1


if __name__ == "__main__":
    sys.exit(main())
