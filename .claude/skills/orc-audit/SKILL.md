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

1. Scan all `SKILL.md` files for `## Events` tables → extract declared events
2. Read `12-orc-orchestration.md` → extract registered core events
3. Read `append-event-to-log.py` → extract VALID_EVENT_TYPES
4. Read `recommend-downstream-actions-from-events.py` → extract EVENT_ROUTING keys
5. Read `detect-domain-state-changes-from-git-diff.py` → extract PATH_TO_EVENT_MAP values
6. Cross-check: every event should appear in all relevant sources
7. Report mismatches per domain

## Output

```json
{
  "sources_scanned": 5,
  "events_found": {"MAT": [...], "PSY": [...], "CRE": [...], "GRO": [...]},
  "mismatches": [
    {"event": "GRO.forecast", "present_in": ["valid_types", "event_routing"], "missing_from": ["skill_md"]}
  ],
  "summary": {"total_events": 13, "consistent": 11, "mismatched": 2}
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
