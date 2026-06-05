---
name: orc:audit
description: "Audit cross-domain event consistency — verify all declarations match. Triggers: 'event audit', 'consistency check', 'domain audit'."
argument-hint: "[--domain <MAT|PSY|CRE|GRO|all>] [--json] [--fix-suggestions]"
metadata:
  framework: ORC
  domain: orchestration
  type: audit
  version: "1.0"
---

# orc:audit

## Overview

Scans all event declaration sources (SKILL.md tables, rules files, Python scripts) and cross-checks for consistency. Reports missing events, orphan events, routing mismatches, and undeclared emissions.

## Flags

| Flag                | Description                                       |
| ------------------- | ------------------------------------------------- |
| `--domain`          | Filter to specific domain or `all` (default: all) |
| `--json`            | JSON output                                       |
| `--fix-suggestions` | Include suggested edits to resolve mismatches     |

## Main

Reads the canonical routing registry (`platform_lib/event_routing.py`) and the
loggable registry (`append-event-to-log.py`) by **import** — never by scraping
literal strings out of consumer scripts (consumers now import the registry, so
string-scraping yields false mismatches). Markdown sources (rules-12, SKILL.md)
are still regex-scanned because they are prose.

Invariants:

| #  | Invariant                | Meaning                                                   | Severity      |
| -- | ------------------------ | --------------------------------------------------------- | ------------- |
| C1 | routable ⊆ loggable      | every `EVENT_ROUTING` key is in `VALID_EVENT_TYPES`       | violation     |
| C2 | emits ⊆ routable         | every cascade `emits` target is itself routable           | violation     |
| C3 | path-map ⊆ routable      | every `DOMAIN_PATH_RULES` target event is routable        | violation     |
| C4 | declared emits loggable  | every `## Events` table emit is in `VALID_EVENT_TYPES`    | violation     |
| C5 | routable documented      | every routable event appears in rules-12                  | advisory      |
| C6 | conceptual conventions   | rules-12 events not wired (expected per rules-12 header)  | informational |

Exit code is non-zero only when a hard violation (C1-C4) is found.

## Output

```json
{
  "sources_scanned": 5,
  "registries": {"routable": [...], "valid_types": [...], "path_map_events": [...], "emit_targets": [...]},
  "violations": [
    {"check": "C4", "event": "ORC.routed", "detail": "declared in a SKILL.md ## Events table but not loggable — emit would be rejected"}
  ],
  "advisories": [
    {"check": "C6", "event": "MAT.ingested", "detail": "rules-12 conceptual convention, not wired as loggable/routable (informational)"}
  ],
  "summary": {"routable_events": 13, "violations": 0, "advisories": 4, "consistent": true}
}
```

## Scripts

| Script                                    | Purpose                                       |
| ----------------------------------------- | --------------------------------------------- |
| `audit-cross-domain-event-consistency.py` | Cross-check event declarations across sources |

## Events

| Event         | When Emitted                              |
| ------------- | ----------------------------------------- |
| `ORC.audited` | After audit pipeline completes (log only) |

## Domains Supported

MAT, PSY, CRE, GRO, COM, ORC

## Schema Validation (C7)

Event-consistency auditing pairs with the **Draft-7 event contract**
(`event-jsonl.schema.json`) for machine-enforceable per-record structure on the 6 B5
streams. Run the shared validator (additive — keeps existing consistency checks):

```bash
PY=$HOME/.claude/skills/.venv/bin/python3
$PY .claude/scripts/validate-all-against-schemas.py   # validates *.jsonl lines too
```

`platform_lib/schema_validator.py` is the single Draft-7 engine (shared with `psy:health-check`,
`gro:validate`, KG-06). Validates each event line's timestamp/event prefix/fields.

## Safety

- Read-only: scans files, never modifies
- Reports findings for LLM or human to act on
- Deterministic: pattern-based extraction, no heuristics
