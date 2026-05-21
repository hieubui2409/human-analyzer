---
name: orc:session-state
description: "Track session state across conversations — what profiles were updated, content created, decisions made. View current state, archive history, recover on resume. Use when user says 'session state', 'what did we do', 'session recap', or automatically via hooks on SessionStart/Stop."
argument-hint: "[--show|--archive|--reset]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "workflow"
  position: "utility"
  dependencies: []
---

# Session State Management

Track structured session state for ck-marketing project. Persists across Stop/Resume cycles via JSON state file + markdown archive.

## Default (No Arguments)

`--show` — print current session state summary.

## Flags

| Flag        | Purpose                                       |
| ----------- | --------------------------------------------- |
| `--show`    | Print current state from state.json           |
| `--archive` | Archive current state to timestamped markdown |
| `--reset`   | Reset state to defaults (keep archive)        |

## State File

Location: `.claude/session-state/state.json`

### Core Fields

| Field              | Type     | Description                                                    |
| ------------------ | -------- | -------------------------------------------------------------- |
| `schema_version`   | string   | Always "2.0"                                                   |
| `mode`             | enum     | tiny / normal / high_risk                                      |
| `phase`            | enum     | idle / exploring / planning / creating / reviewing / completed |
| `branch`           | string   | Current git branch                                             |
| `plan_path`        | string   | Active plan directory (relative)                               |
| `profiles_touched` | string[] | Character profiles modified this session                       |
| `content_created`  | string[] | Content assets created this session                            |
| `decisions`        | string[] | Key decisions made this session                                |
| `harness_delta`    | string[] | .claude/ or docs/ files changed                                |
| `last_updated`     | ISO date | Auto-set on write                                              |

### Framework Context Fields

| Field            | Type   | Description                                             |
| ---------------- | ------ | ------------------------------------------------------- |
| `active_domain`  | enum   | Current work domain: MAT / PSY / CRE / GRO / ORC / null |
| `mat_pipeline`   | object | MAT pipeline tracking (see below)                       |
| `psy_updates`    | object | PSY framework update tracking (see below)               |
| `cre_pipeline`   | object | CRE content pipeline tracking (see below)               |
| `pending_events` | array  | Unprocessed event queue from domain triggers            |

#### `mat_pipeline` Object

```json
{
  "active_ingestions": [],
  "last_indexed": null,
  "contradictions_unresolved": 0,
  "files_by_status": {
    "raw": 0,
    "extracted": 0,
    "analyzed": 0,
    "validated": 0,
    "integrated": 0,
    "archived": 0
  }
}
```

#### `psy_updates` Object

```json
{
  "profiles_refreshed": [],
  "pending_refresh": [],
  "last_crossref": null,
  "consistency_score": null
}
```

#### `cre_pipeline` Object

```json
{
  "active_content": [],
  "platform_queue": [],
  "voice_audit_pending": false,
  "privacy_guard_pending": false
}
```

#### `pending_events` Array

Events emitted by domain skills, consumed by ORC orchestration:

```json
[
  {
    "event": "MAT.integrated",
    "source": "mat:indexer",
    "character": "character-b",
    "timestamp": "..."
  },
  {
    "event": "PSY.refresh",
    "source": "psy:crossref",
    "character": "character-b",
    "timestamp": "..."
  }
]
```

Event types: `MAT.integrated`, `MAT.contradiction`, `PSY.refresh`, `PSY.flag`, `CRE.recalibrate`, `CRE.published`, `GRO.assessed`, `GRO.forecast`, `GRO.mentored`, `GRO.profiled`

## Hook Integration

Automated via `.claude/hooks/session-state-json.cjs`:

- **SessionStart (startup/resume):** Read state.json, print recovery summary to stderr
- **Stop:** Detect harness delta via `git diff`, update state.json

## Workflow

### --show

1. Read `.claude/session-state/state.json`
2. Print formatted summary:
   ```
   ## Session State
   Mode: {mode} | Phase: {phase} | Branch: {branch}
   Plan: {plan_path or "none"}
   Profiles: {profiles_touched or "none"}
   Content: {content_created or "none"}
   Decisions: {decisions or "none"}
   Harness delta: {count} files
   Last updated: {last_updated}
   ```

### --archive

1. Read current state.json
2. Write to `.claude/session-state/archive/{YYYYMMDD-HHmm}.md`
3. Reset state.json to defaults

### --reset

1. Write default state.json (preserve branch)
2. Do NOT archive — just reset

## Updating State During Work

Claude should update state.json fields as work progresses:

- After modifying a profile file → append to `profiles_touched`
- After creating content in assets/ → append to `content_created`
- After making a significant decision → append to `decisions`
- After crisis assessment → record crisis event in decisions
- After narrative twist → record twist event in decisions
- After MAT ingestion → update `mat_pipeline.active_ingestions` and `mat_pipeline.files_by_status`
- After PSY profile edit → append to `psy_updates.profiles_refreshed`, check `psy_updates.pending_refresh`
- After CRE content creation → update `cre_pipeline.active_content`
- After domain event → append to `pending_events` for ORC consumption
- Set `active_domain` when entering a domain workflow (MAT/PSY/CRE/GRO)
- After GRO work on `docs/growth/` files → set `active_domain` to `GRO`

Use bash to update:

```bash
python3 -c "
import json
with open('.claude/session-state/state.json') as f: s = json.load(f)
s['profiles_touched'] = list(set(s.get('profiles_touched', []) + ['character-a']))
s['phase'] = 'creating'
s['active_domain'] = 'PSY'
with open('.claude/session-state/state.json', 'w') as f: json.dump(s, f, indent=2)
"
```

## Safety

- Writes ONLY to `.claude/session-state/state.json` — never modifies profiles, content, or references
- Scope: session state tracking and persistence. Does NOT classify tasks, create content, or modify project files.

## Auto-Trigger Suggestions

When archiving a session (`--archive`), if `profiles_touched` or `content_created` are non-empty, suggest:

- `orc:compounding` — extract durable learnings before archiving
- `orc:dream` — if 5+ sessions archived since last dream, suggest memory consolidation

## Domain Transition Protocol

When switching between framework domains (MAT → PSY → CRE):

1. Flush `pending_events` — process any unhandled events before domain switch
2. Update `active_domain` to new domain
3. Check if previous domain left incomplete work (e.g., unresolved contradictions in MAT)
4. Log domain transition in `decisions` array

## See Also

- `/orc:classify` — risk classification writes mode to state.json
- `/orc:compounding` — extract learnings from session work
- `/orc:dream` — periodic consolidation triggered by session-state archive cadence
- `/com:git` — project-aware git operations
- `mat:loader` — MAT pipeline events update mat_pipeline fields
- `mat:indexer` — emits MAT.integrated/MAT.contradiction events
- `docs/rules/12-orc-orchestration.md` — event system that drives pending_events
