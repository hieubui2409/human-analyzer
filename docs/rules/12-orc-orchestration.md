---
title: ORC Orchestration — Event-Driven Framework Coordination
version: "1.0"
created: "2026-05-17"
---

# Rule 12: ORC Orchestration — Event-Driven Framework Coordination

## Overview

ORC (Orchestrator) is the meta-framework that routes events between MAT, PSY, CRE, and GRO domains. It does not own content — it owns workflow state and inter-domain signal passing.

## Domain Boundaries

| Domain | Writes to                                        | Reads from                                      |
| ------ | ------------------------------------------------ | ----------------------------------------------- |
| MAT    | `docs/materials/{character}/`                    | Raw source files only                           |
| PSY    | `docs/profiles/{character}/`, `docs/references/` | `docs/materials/` (read-only after MAT)         |
| CRE    | `assets/`                                        | `docs/profiles/` (read-only), `docs/materials/` |
| GRO    | `docs/profiles/{character}/growth/`              | `docs/profiles/`, `docs/materials/` (read-only) |
| ORC    | `.claude/` (skills, session-state, config)       | All domains (orchestration only, no edits)      |

**Hard rule**: No domain writes outside its boundary. Cross-boundary changes are bugs.

## Event System

Events are named `{DOMAIN}.{action}`. They are not code — they are conventions for skill routing decisions.

### Core Events

| Event               | Trigger condition                              | Downstream action                                               |
| ------------------- | ---------------------------------------------- | --------------------------------------------------------------- |
| `MAT.ingested`      | New material added to `docs/materials/`        | MAT pipeline Stage 1 begins                                     |
| `MAT.analyzed`      | Material processing_status → "analyzed"        | Cross-validation against profile                                |
| `MAT.integrated`    | Material processing_status → "integrated"      | → `PSY.refresh` + `CRE.recalibrate`                             |
| `MAT.contradiction` | Contradiction detected (severity: medium+)     | → `PSY.flag` → human review or `PSY.updated`                    |
| `PSY.refresh`       | Profile sections affected by new material      | Re-read affected files, update if needed                        |
| `PSY.flag`          | Unresolved contradiction in profile data       | Log to `VALIDATION-NOTES.md`, alert user                        |
| `PSY.updated`       | Profile file(s) modified                       | → `psy:propagate` cascade + `CRE.recalibrate` if voice-relevant |
| `PSY.crisis`        | Crisis assessment triggered                    | Log to event-log, escalate to user                              |
| `CRE.recalibrate`   | Voice/tone assumptions may be stale            | Reload 3-layer voice architecture                               |
| `CRE.blocked`       | Defense-mechanism gating prevents content type | Route to alternate content type                                 |
| `MAT.archived`      | Material archived via mat:archive              | Log to event-log                                                |
| `GRO.assessed`      | Competency/skill assessment completed          | → `CRE.recalibrate` (competency data informs content angle)     |
| `GRO.forecast`      | Career forecast generated                      | Log only (informational, no cascade)                            |
| `GRO.mentored`      | Mentoring interaction documented               | → `PSY.refresh` (mentoring reveals psychological insights)      |
| `GRO.profiled`      | Learning profile updated                       | → `CRE.recalibrate` (learning profile changes content style)    |
| `COM.rules_updated` | Files under `docs/rules/` changed              | → `com:rules --validate` (verify rule consistency)              |
| `ORC.skill_updated` | Files under `.claude/skills/` changed          | → `orc:bootstrap --quick` (refresh session context)            |
| `ORC.script_updated`| Files under `.claude/scripts/` changed         | → `orc:bootstrap --quick` (refresh session context)            |

### Event Flow Diagram

```
User provides material
        │
        ▼
[MAT.ingested] → Stage 1-4 pipeline
        │
        ▼
[MAT.integrated]
        │
        ├──────────────────────────────────┐
        ▼                                  ▼
[PSY.refresh]                     [CRE.recalibrate]
   Update affected                Reload voice layers
   profile sections               from updated profiles
        │
        ▼
[PSY.updated] (if changes made)
        │
        ▼
[CRE.recalibrate] (if voice-relevant sections changed)
```

## Contradiction → Voice Refresh Loop

When MAT detects a contradiction in source material:

```
MAT.contradiction (severity: medium+)
        │
        ▼
PSY reviews conflict:
  - Is new material higher tier? → newer supersedes
  - Same tier? → coexist as complexity, [DISPUTED] tag
  - Safety-relevant? → escalate to user immediately
        │
        ▼
PSY.updated (profile sections corrected)
        │
        ▼
CRE.recalibrate (if affected sections touch voice/tone/defense)
        │
        ▼
CRE rebuilds 3-layer voice architecture from updated files
```

Low-severity contradictions (minor detail differences) do not trigger the full loop — they are logged in `VALIDATION-NOTES.md` and batched for Wave 3 review.

## Session State Tracking

ORC tracks multi-step workflow state to enable resumption and prevent double-processing.

### Session State File

`.claude/session-state/state.json` — owned exclusively by ORC.

Key fields:

```json
{
  "active_character": "character-a",
  "current_phase": "PSY.refresh",
  "pending_events": ["CRE.recalibrate"],
  "materials_in_flight": [
    "docs/materials/character-a/analyzed/2026-05-17-gemini.md"
  ],
  "last_psy_refresh": "2026-05-17T10:30:00Z",
  "open_contradictions": [],
  "session_mode": "materials-ingestion"
}
```

### State Transitions

```
idle → mat-ingestion → psy-refresh → cre-recalibrate → idle
           │
           └── contradiction detected → psy-flag → human-review → resolve → psy-refresh
```

ORC must clear `pending_events` before marking session complete.

## Skill Routing

### Skill Prefix Map

| Prefix  | Domain | Skills                                                                                                                            | Count |
| ------- | ------ | --------------------------------------------------------------------------------------------------------------------------------- | ----- |
| `psy-*` | PSY    | bootstrap, crossref, ref-audit, ref-scan, ref-create, arc-tracker, hypothesis, wave, crisis-assess                                | 9     |
| `mat-*` | MAT    | loader, indexer                                                                                                                   | 2     |
| `cre-*` | CRE    | post-writer, explore, repurpose                                                                                                   | 3     |
| `gro-*` | GRO    | career-path, competency-map, learning-profile, validate, mentoring-track, career-forecast, compare, milestone-tracker             | 8     |
| `orc-*` | ORC    | bootstrap, session-state, classify, intake, compounding, dream, decisions, agent-memory, event-log, domain-router, cascade, audit | 12    |

### Skill Activation Rules

- `orc:intake` runs first on every new task — classifies work type before any domain skill activates
- `orc:classify` risk-gates all content creation — must run before `cre:post-writer`
- `mat:*` skills MUST complete before `psy:*` skills consume their output
- `psy:*` profile-modifying skills MUST complete before `cre:*` voice-dependent skills

## Multi-Step Workflow Guards

1. **No concurrent domain writes** — if PSY is updating a profile, CRE must wait for `PSY.updated` before recalibrating
2. **Event idempotency** — same event fired twice must not double-process (check session state before acting)
3. **Contradiction escalation ceiling** — if contradiction is safety-relevant (crisis/suicidal ideation), STOP all automation and surface to user
4. **Stale voice guard** — if `last_psy_refresh` is older than the last material integration, force `CRE.recalibrate` before any content creation

## Persistent Event Logging

All core events SHOULD be appended to the persistent audit log at `.claude/session-state/event-log.jsonl` via `orc:event-log --append`.

### Log Format

Each event is one JSON line:

```json
{
  "timestamp": "2026-05-18T14:30:00Z",
  "event": "MAT.integrated",
  "source": "mat:indexer",
  "character": "character-a",
  "reason": "Transcript validated, integration gate passed"
}
```

### When to Log

| Event               | Logging skill           | Automatic? |
| ------------------- | ----------------------- | ---------- |
| `MAT.ingested`      | mat:loader              | Yes        |
| `MAT.integrated`    | mat:indexer             | Yes        |
| `MAT.contradiction` | mat:indexer             | Yes        |
| `PSY.refresh`       | psy:wave / psy:crossref | Yes        |
| `PSY.updated`       | psy:wave                | Yes        |
| `PSY.crisis`        | psy:crisis-assess       | Yes        |
| `CRE.recalibrate`   | cre:post-writer         | Yes        |
| `ORC.bootstrap`     | orc:bootstrap           | Yes        |
| `ORC.decision`      | orc:decisions           | Yes        |
| `MAT.archived`      | mat:archive             | Yes        |

### Querying

```bash
# Recent events
/orc:event-log --query

# Filter by type and date
/orc:event-log --query --event-type PSY.refresh --since 2026-05-01

# Filter by character
/orc:event-log --query --character hieu
```

### Scripts

- `orc-event-log/scripts/append-event-to-log.py` — append one event
- `orc-event-log/scripts/query-event-log-with-filters.py` — filter and display

## Automatic Project Hooks (project-owned, no ck dependency)

Two project-authored hooks (git-tracked `settings.json` entries → project scripts) run
automatically; neither `require`s ck-config-utils (CAP-1). Both fail-open — an error never
blocks the tool/compaction.

| Hook | Event | Does | Manual entry |
| ---- | ----- | ---- | ------------ |
| `observe-framework-signal.cjs` | PostToolUse (Edit\|Write) | Maps the edited path → framework, appends a deterministic `{fw}-touched` signal to `observations.jsonl` (B3). | `orc:observe` (semantic signals) |
| `write-framework-delta-compact-digest.cjs` | PreCompact | Snapshots a bounded per-framework delta to `compact-digest.json`; `orc:bootstrap` re-injects on resume (C5). | `orc:session-state --compact-digest` |

**Observation stream vs event bus:** observations (`observations.jsonl`) are passive telemetry —
they never trip a cascade. Domain events (the framework streams) drive the cascade. `orc:observe`
records LLM-judged signals; the hook guarantees a deterministic baseline trail. Enable flags live in
`framework-config.json` (`hooks.observeFrameworkSignal`, `hooks.compactDigest`; default on).

## Failure Modes

| Failure                               | Recovery                                             |
| ------------------------------------- | ---------------------------------------------------- |
| MAT pipeline stalls at "analyzed"     | Re-run Stage 4 validation; check contradiction flags |
| PSY refresh produces no changes       | Normal — log "no-op refresh", clear pending event    |
| CRE blocked by defense-mechanism gate | Route to alternate content type; log blocked attempt |
| Session state desync                  | Re-read all domain files; rebuild state from scratch |
| Contradiction resolution timeout      | Tag `[PENDING HUMAN REVIEW]`; proceed with caution   |
