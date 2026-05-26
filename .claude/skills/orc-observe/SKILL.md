---
name: orc:observe
description: "Emit a cross-framework observation signal (passive telemetry) to the project observation stream — defense-pattern noticed, source low on CRAAP, voice drift, competency delta, PII match. Distinct from orc:event-log (the domain cascade bus): observations never trip cascades, they accrete a signal trail that orc:compounding mines into instincts. READ-mostly, append-only. Use when a framework skill notices something worth remembering at an end-of-work checkpoint, NOT for routing domain events. Triggers: 'observe', 'emit signal', 'note observation', 'record signal', 'end-of-work checkpoint'."
argument-hint: "--framework psy|mat|cre|gro|orc|com --signal <type> --payload <json> [--source skill] [--json]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "orc-framework"
  position: "observation"
  dependencies: ["orc:event-log"]
---

# orc:observe — Cross-Framework Observation Signals

Project-owned observation layer (ECC § B3). Two writers, one stream
(`.claude/telemetry/observations.jsonl`):

1. **Automatic** — the `observe-framework-signal.cjs` PostToolUse hook emits a *deterministic*
   `*-touched` signal whenever a framework's data is edited (path → framework). Fast, fail-open.
2. **Semantic** — a framework skill CALLS this skill at an end-of-work checkpoint to record a
   *judged* signal (defense-pattern, voice-drift, low-craap) the LLM decided was worth keeping.

The split honours GOLDEN RULE #4: the script appends deterministically; the **LLM decides what is
worth observing**. Observations are passive — they never trigger a cascade (that is `orc:event-log`).

## When to Use

- A framework skill, at its documented end-of-work checkpoint, noticed something worth a durable trail
  (PSY defense-pattern, MAT contradiction, CRE voice-drift, GRO competency-delta, COM PII-match).
- NOT for domain events that must cascade (MAT→PSY→CRE) — those go to `orc:event-log` (`PSY.refresh`, …).
- NOT for routing — that is `orc:domain-router` / `orc:cascade`.

## Usage

```bash
PY=$HOME/.claude/skills/.venv/bin/python3
$PY .claude/skills/orc-observe/scripts/emit-framework-observation-signal.py \
    --framework psy --signal defense-pattern \
    --payload '{"character":"hoa","note":"intellectualization under conflict"}' \
    --source psy:crossref --json
```

Invalid framework or signal → non-zero exit, **no write** (bounded vocabulary, 2 KB payload cap).

## Signal vocabulary (bounded — extend deliberately)

| Framework | Signals |
| --------- | ------- |
| psy | core-wound · defense-pattern · attachment-shift · profile-touched |
| mat | low-craap · contradiction · new-source · material-touched |
| cre | voice-drift · evidence-violation · angle-found · content-touched |
| gro | milestone · phase-transition · competency-delta · growth-touched |
| orc | cascade-interrupt · routing-decision · session-event |
| com | pii-match · governance-flag · commit |

The `*-touched` signals are what the automatic hook emits; the rest are semantic (skill-judged).

## End-of-work checkpoint pattern

A framework skill closing its work should, when it judged something notable, append a one-line call:

> **End-of-work:** if a notable pattern surfaced, `orc:observe --framework {fw} --signal {type} --payload {...}`.

This is cooperative (the skill chooses to call). The automatic hook guarantees a baseline `*-touched`
trail even if a skill forgets the semantic call.

## Anti-patterns

- ❌ Emitting a domain event as an observation (use `orc:event-log` — observations don't cascade).
- ❌ Inventing a signal outside the vocabulary (rejected, non-zero exit) — extend the table deliberately.
- ❌ Oversized payloads (capped at 2 KB) — keep a signal a pointer, not a dump.

## See Also

- `orc:event-log` — the domain cascade bus (the complement to this passive trail).
- `orc:compounding` — mines high-signal observations into durable instincts (A5).
- `observe-framework-signal.cjs` — the automatic PostToolUse companion hook.
