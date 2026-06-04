"""
Canonical ORC event-routing vocabulary — single source of truth.

Consumers:
  orc-domain-router   -> downstream_for(event)  (list of {skill,args,reason})
  orc-session-state   -> downstream_for(event)
  orc-cascade         -> EVENT_ROUTING[event]    (full {domain,downstream,emits})
  orc-event-log       -> routable_events()       (all known event names)

Shape of EVENT_ROUTING:
  event -> {
      domain: str,                              # framework prefix
      downstream: [{skill, args, reason}],      # skills to recommend
      emits: [event, ...],                      # events this event cascades into
  }

Derivation:
  - downstream = superset of orc-session-state union orc-domain-router
    (session-state was already the superset; its richer reasons are preserved)
  - emits = from orc-cascade + GRO.profiled inferred to match GRO.assessed pattern
  - domain = framework prefix of the event key
"""

# ---------------------------------------------------------------------------
# Canonical routing table
# ---------------------------------------------------------------------------

EVENT_ROUTING: dict[str, dict] = {
    "MAT.integrated": {
        "domain": "MAT",
        "downstream": [
            {
                "skill": "psy:ref-audit",
                "args": "--discover",
                "reason": "New material may reveal blind spots in references",
            },
            {
                "skill": "psy:crossref",
                "args": "",
                "reason": "Cross-validate profiles against new material",
            },
            {
                "skill": "mat:indexer",
                "args": "--contradictions",
                "reason": "Check for contradictions with existing profiles",
            },
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
            {
                "skill": "psy:propagate",
                "args": "",
                "reason": "Detect cross-character cascade needs from profile change",
            },
            {
                "skill": "cre:voice-audit",
                "args": "",
                "reason": "Profile change may affect content voice",
            },
            {
                "skill": "cre:post-writer",
                "args": "--recalibrate",
                "reason": "Recalibrate content creation context",
            },
            {
                "skill": "psy:crossref",
                "args": "--validate",
                "reason": "Verify cross-character consistency",
            },
        ],
        "emits": ["CRE.recalibrate"],
    },
    "PSY.crisis": {
        "domain": "PSY",
        "downstream": [
            {
                "skill": "psy:crisis-assess",
                "args": "",
                "reason": "Assess crisis risk level and trigger protocol",
            },
        ],
        "emits": [],
    },
    "PSY.updated": {
        "domain": "PSY",
        "downstream": [
            {
                "skill": "psy:propagate",
                "args": "",
                "reason": "Cascade profile changes to related characters",
            },
            {
                "skill": "psy:crossref",
                "args": "--extended",
                "reason": "Re-validate all 10 dimensions after update",
            },
            {
                "skill": "cre:voice-audit",
                "args": "",
                "reason": "Check if voice data needs recalibration",
            },
            {
                "skill": "orc:event-log",
                "args": "--append --event-type PSY.updated",
                "reason": "Log profile update to audit trail",
            },
        ],
        "emits": [],
    },
    "CRE.recalibrate": {
        "domain": "CRE",
        "downstream": [
            {
                "skill": "cre:privacy-guard",
                "args": "",
                "reason": "New content needs privacy scan",
            },
            {
                "skill": "cre:voice-audit",
                "args": "",
                "reason": "Verify voice consistency in new content",
            },
        ],
        "emits": [],
    },
    "GRO.assessed": {
        "domain": "GRO",
        "downstream": [
            {
                "skill": "cre:post-writer",
                "args": "--recalibrate",
                "reason": "Competency data changed — recalibrate content context",
            },
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
            {
                "skill": "psy:crossref",
                "args": "--validate",
                "reason": "Mentoring may reveal cross-character psychological insights",
            },
        ],
        "emits": ["PSY.refresh"],
    },
    "GRO.profiled": {
        "domain": "GRO",
        "downstream": [
            {
                "skill": "cre:post-writer",
                "args": "--recalibrate",
                "reason": "Learning profile changed — recalibrate content context",
            },
        ],
        "emits": ["CRE.recalibrate"],
    },
    "COM.rules_updated": {
        "domain": "COM",
        "downstream": [
            {
                "skill": "com:rules",
                "args": "--validate",
                "reason": "Verify rule consistency after update",
            },
        ],
        "emits": [],
    },
    "ORC.skill_updated": {
        "domain": "ORC",
        "downstream": [
            {
                "skill": "orc:bootstrap",
                "args": "--quick",
                "reason": "Refresh session context with updated skills",
            },
        ],
        "emits": [],
    },
    "ORC.script_updated": {
        "domain": "ORC",
        "downstream": [
            {
                "skill": "orc:bootstrap",
                "args": "--quick",
                "reason": "Refresh session context with updated scripts",
            },
        ],
        "emits": [],
    },
}

# ---------------------------------------------------------------------------
# Domain path -> event mapping (used by orc-domain-router for diff detection;
# lives here so all routing knowledge is co-located).
# ---------------------------------------------------------------------------

DOMAIN_PATH_RULES: dict[str, dict] = {
    "docs/materials/": {"event": "MAT.integrated", "domain": "MAT"},
    "docs/profiles/": {"event": "PSY.refresh", "domain": "PSY"},
    "docs/references/": {"event": "PSY.refresh", "domain": "PSY"},
    "docs/graph/": {"event": "PSY.refresh", "domain": "PSY"},
    "assets/": {"event": "CRE.recalibrate", "domain": "CRE"},
    "docs/rules/": {"event": "COM.rules_updated", "domain": "COM"},
    ".claude/skills/": {"event": "ORC.skill_updated", "domain": "ORC"},
    ".claude/scripts/": {"event": "ORC.script_updated", "domain": "ORC"},
}

# Files under docs/profiles/ containing this path segment are rerouted to GRO.profiled.
GRO_PATH_MARKER: str = "/growth/"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def downstream_for(event: str) -> list[dict]:
    """Return the list of downstream skill actions for an event (may be empty)."""
    entry = EVENT_ROUTING.get(event)
    if entry is None:
        return []
    return list(entry["downstream"])


def emits_for(event: str) -> list[str]:
    """Return the list of events emitted downstream by this event (cascade chain)."""
    entry = EVENT_ROUTING.get(event)
    if entry is None:
        return []
    return list(entry["emits"])


def routable_events() -> list[str]:
    """Return sorted list of all known routable event names."""
    return sorted(EVENT_ROUTING.keys())
