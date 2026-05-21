---
name: orc:domain-router
description: "Route domain events to downstream skills based on git diff or explicit event. Triggers: 'route events', 'domain routing', 'event routing', 'what should run next'."
argument-hint: "[--event <EVENT>|--from-diff [--ref <REF>]] [--json] [--dry-run]"
metadata:
  framework: ORC
  domain: orchestration
  type: routing
  version: "1.0"
---

# orc:domain-router

## Overview

Unified event routing interface that detects domain changes from git diff or explicit events, then recommends downstream skill invocations. Wraps `detect-domain-state-changes-from-git-diff.py` + `recommend-downstream-actions-from-events.py` into a single pipeline.

## Flags

| Flag          | Description                                        |
| ------------- | -------------------------------------------------- |
| `--event`     | Route a specific named event (e.g. MAT.integrated) |
| `--from-diff` | Detect changed files via git diff                  |
| `--ref`       | Git ref to diff against (default: HEAD~1)          |
| `--json`      | JSON output                                        |
| `--dry-run`   | Show routing without executing                     |

## Main

1. Accept input: explicit `--event` or `--from-diff`
2. If `--from-diff`: detect domain changes from git diff → generate events
3. For each event: look up downstream actions from EVENT_ROUTING
4. Output ordered list of recommended skill invocations with args

## Output

```json
{
  "events_detected": [...],
  "recommendations": [
    {"skill": "psy:crossref", "args": "--validate", "reason": "...", "triggered_by": "PSY.refresh"}
  ]
}
```

## Scripts

| Script                              | Purpose                                  |
| ----------------------------------- | ---------------------------------------- |
| `route-domain-events-from-state.py` | Detect + route events in single pipeline |

## Events

| Event        | When Emitted                                |
| ------------ | ------------------------------------------- |
| `ORC.routed` | After routing pipeline completes (log only) |

## Domains Supported

MAT, PSY, CRE, GRO, COM, ORC

## Safety

- `--dry-run` mode prevents any actual skill execution
- Read-only: this skill only recommends, never executes downstream skills
- Deterministic: routing rules are hardcoded, not heuristic

## Examples

```bash
# Route from recent git changes
orc:domain-router --from-diff --json

# Route a specific event
orc:domain-router --event GRO.assessed --json

# Dry run with custom ref
orc:domain-router --from-diff --ref main --dry-run
```
