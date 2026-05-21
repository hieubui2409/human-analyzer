---
name: orc:cascade
description: "Orchestrate multi-step event cascades across domains. Triggers: 'cascade', 'event chain', 'multi-domain'."
argument-hint: "[--trigger <EVENT>] [--max-depth <N>] [--json]"
metadata:
  framework: ORC
  domain: orchestration
  type: cascade
  version: "1.0"
---

# orc:cascade

## Overview

Resolves a trigger event into its full cascade chain across all domains (MAT, PSY, CRE, GRO). Detects circular references and enforces max-depth to prevent infinite cascades.

## Flags

| Flag          | Description                          |
| ------------- | ------------------------------------ |
| `--trigger`   | Starting event (e.g. MAT.integrated) |
| `--max-depth` | Maximum cascade depth (default: 5)   |
| `--json`      | JSON output                          |

## Main

1. Accept trigger event via `--trigger`
2. Load EVENT_ROUTING table (inline, matching orc-domain-router)
3. Recursively resolve: event → downstream skills → their emitted events → ...
4. Track visited events to detect circular references
5. Enforce `--max-depth` to cap recursion
6. Output ordered cascade tree with depth levels

## Output

```json
{
  "trigger": "MAT.integrated",
  "max_depth": 5,
  "chain": [
    {
      "depth": 0,
      "event": "MAT.integrated",
      "domain": "MAT",
      "downstream_skills": ["psy:ref-audit", "psy:crossref"]
    },
    {
      "depth": 1,
      "event": "PSY.refresh",
      "domain": "PSY",
      "downstream_skills": ["psy:propagate", "cre:voice-audit"]
    },
    {
      "depth": 2,
      "event": "CRE.recalibrate",
      "domain": "CRE",
      "downstream_skills": ["cre:privacy-guard"]
    }
  ],
  "circular_detected": false,
  "total_steps": 3
}
```

## Scripts

| Script                                | Purpose                               |
| ------------------------------------- | ------------------------------------- |
| `resolve-cascade-chain-from-event.py` | Resolve full cascade chain from event |

## Events

No events emitted — orchestration utility only.

## Domains Supported

MAT, PSY, CRE, GRO, COM, ORC

## Safety

- `--max-depth` prevents infinite recursion (default 5)
- Circular reference detection with explicit reporting
- Read-only: never executes downstream skills
- Deterministic: routing rules are hardcoded
