---
name: mpc:event-log
description: "Persistent event logging and audit trail — append framework events (MAT.integrated, PSY.refresh, CRE.recalibrate, etc.) to a JSONL log and query with filters. Provides audit trail for all cross-domain MPC events. Triggers: 'log event', 'event history', 'audit trail', 'show events', 'event log'."
argument-hint: "[--append --event-type <type> --source <skill> --character <name> --reason <text>] | [--query [--event-type <type>] [--character <name>] [--since YYYY-MM-DD] [--source <skill>]]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "mpc-orchestration"
  position: "infrastructure"
  dependencies: []
---

# mpc:event-log — Persistent Event Logging

Append MPC framework events to `.claude/session-state/event-log.jsonl` and query the history with filters.

## Default (No Arguments)

`--query` — show recent events (last 20).

## Modes

### Append Mode

```bash
/mpc:event-log --append --event-type MAT.integrated --source mat:indexer --character hieu --reason "New transcript processed"
```

### Query Mode

```bash
/mpc:event-log --query --event-type PSY.refresh --since 2026-01-01
```

## Flags

### Append flags

| Flag                  | Purpose                                        |
| --------------------- | ---------------------------------------------- |
| `--append`            | Switch to append mode                          |
| `--event-type <type>` | Event type (MAT.integrated, PSY.refresh, etc.) |
| `--source <skill>`    | Originating skill (e.g. mat:indexer)           |
| `--character <name>`  | Character slug (optional)                      |
| `--reason <text>`     | Human-readable reason                          |

### Query flags

| Flag                  | Purpose                        |
| --------------------- | ------------------------------ |
| `--query`             | Switch to query mode (default) |
| `--event-type <type>` | Filter by event type           |
| `--character <name>`  | Filter by character            |
| `--source <skill>`    | Filter by source skill         |
| `--since YYYY-MM-DD`  | Events after this date         |
| `--until YYYY-MM-DD`  | Events before this date        |
| `--limit N`           | Max results (default: 20)      |
| `--json`              | Raw JSON output                |

## Event Types

| Event Type        | Trigger                                  |
| ----------------- | ---------------------------------------- |
| `MAT.integrated`  | Material passes Stage 3-4 in mat:indexer |
| `PSY.refresh`     | Profile section updated via psy: skill   |
| `CRE.recalibrate` | Content recalibrated after PSY change    |
| `MPC.bootstrap`   | Session bootstrapped via mpc:bootstrap   |
| `MPC.decision`    | Decision recorded via mpc:decisions      |
| `PSY.crisis`      | Crisis assessment triggered              |
| `MAT.archived`    | Material archived via mat:archive        |

## Event Log Format

Each event is one JSON line in `.claude/session-state/event-log.jsonl`:

```json
{
  "timestamp": "2026-05-18T14:30:00Z",
  "event": "MAT.integrated",
  "source": "mat:indexer",
  "character": "character-a",
  "reason": "Transcript validated, integration gate passed"
}
```

## Workflow

### Append

1. Run `scripts/append-event-to-log.py` with event fields
2. Create `.claude/session-state/event-log.jsonl` if not exists
3. Append JSON line with ISO timestamp

### Query

1. Run `scripts/query-event-log.py` with filters
2. Read JSONL, apply filters (AND logic)
3. Sort by timestamp descending
4. Render formatted table

### Query Output

```
## Event Log Query

**Filters:** event-type=PSY.refresh, since=2026-01-01
**Matches:** 7 events

| Timestamp           | Event        | Source       | Character | Reason                   |
|---------------------|--------------|--------------|-----------|--------------------------|
| 2026-05-18 14:30    | PSY.refresh  | psy:wave     | hieu      | Wave 2 deep dive done    |
| 2026-05-10 09:15    | PSY.refresh  | psy:crossref | hoa       | Timeline sync applied    |
...
```

## Scripts

| Script                           | Purpose                              |
| -------------------------------- | ------------------------------------ |
| `scripts/append-event-to-log.py` | Append one event to JSONL log        |
| `scripts/query-event-log.py`     | Filter and display events from JSONL |

## Safety

- `--query` is READ-ONLY
- `--append` only writes to `.claude/session-state/event-log.jsonl`
- Never modifies profile or material files
- Domain boundary: `.claude/session-state/` only

## Examples

```bash
/mpc:event-log                                                    # recent events
/mpc:event-log --query --event-type MAT.integrated                # all integrations
/mpc:event-log --query --character hieu --since 2026-05-01        # Nhân vật A events this month
/mpc:event-log --append --event-type PSY.refresh --source psy:wave --character hoa --reason "Wave 1 complete"
```

## See Also

- `mpc:session-state` — runtime session tracking (in-memory)
- `mpc:decisions` — decision records (separate from event log)
- `mpc:bootstrap` — loads context (logs MPC.bootstrap event)
