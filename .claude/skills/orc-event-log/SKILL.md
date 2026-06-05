---
name: orc:event-log
description: "Persistent event logging and audit trail — append framework events (MAT.integrated, PSY.refresh, CRE.recalibrate, etc.) to a JSONL log and query with filters. Provides audit trail for all cross-domain ORC events. Triggers: 'log event', 'event history', 'audit trail', 'show events', 'event log'."
argument-hint: "[--append --event-type <type> --source <skill> --character <name> --reason <text>] | [--query [--event-type <type>] [--character <name>] [--since YYYY-MM-DD] [--source <skill>]]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "orc-orchestration"
  position: "infrastructure"
  dependencies: []
---

# orc:event-log — Persistent Event Logging

Append framework events to **6 framework-partitioned JSONL streams** under `.claude/session-state/` and query the history with filters. Events route by event-type prefix.

## Framework Streams (B2 partition)

| Prefix  | Stream file              | Framework |
| ------- | ------------------------ | --------- |
| `PSY.*` | `character-events.jsonl` | PSY       |
| `MAT.*` | `material-events.jsonl`  | MAT       |
| `CRE.*` | `content-events.jsonl`   | CRE       |
| `GRO.*` | `growth-signals.jsonl`   | GRO       |
| `ORC.*` | `cascade-events.jsonl`   | ORC       |
| `COM.*` | `governance-audit.jsonl` | COM       |

Unknown prefixes fall back to `cascade-events.jsonl` with a WARNING. Query merges all streams by default, or targets one via `--framework`.

## Default (No Arguments)

`--query` — show recent events (last 20).

## Modes

### Append Mode

```bash
/orc:event-log --append --event-type MAT.integrated --source mat:indexer --character hieu --reason "New transcript processed"
```

### Query Mode

```bash
/orc:event-log --query --event-type PSY.refresh --since 2026-01-01
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

| Flag                  | Purpose                                                      |
| --------------------- | ------------------------------------------------------------ |
| `--query`             | Switch to query mode (default)                               |
| `--framework <fw>`    | Stream to query: all (default), psy, mat, cre, gro, orc, com |
| `--event-type <type>` | Filter by event type                                         |
| `--character <name>`  | Filter by character                                          |
| `--source <skill>`    | Filter by source skill                                       |
| `--since YYYY-MM-DD`  | Events after this date                                       |
| `--until YYYY-MM-DD`  | Events before this date                                      |
| `--limit N`           | Max results (default: 20)                                    |
| `--json`              | Raw JSON output                                              |

## Event Types

| Event Type        | Trigger                                                |
| ----------------- | ------------------------------------------------------ |
| `MAT.integrated`  | Material passes Stage 3-4 in mat:indexer               |
| `PSY.refresh`     | Profile section updated via psy: skill                 |
| `CRE.recalibrate` | Content recalibrated after PSY change                  |
| `GRO.assessed`    | Competency assessment completed via gro:competency-map |
| `GRO.forecast`    | Career forecast generated via gro:career-forecast      |
| `GRO.mentored`    | Mentoring session recorded via gro:mentoring-track     |
| `GRO.profiled`    | Learning profile updated via gro:learning-profile      |
| `ORC.bootstrap`   | Session bootstrapped via orc:bootstrap                 |
| `ORC.decision`    | Decision recorded via orc:decisions                    |
| `PSY.crisis`      | Crisis assessment triggered                            |
| `MAT.archived`    | Material archived via mat:archive                      |
| `COM.privacy`     | Privacy/PII violation detected via cre:privacy-guard   |
| `COM.governance`  | Governance/confidentiality audit result                |
| `COM.commit`      | Commit scan result via com:git                         |

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

1. Run `scripts/query-event-log-with-filters.py` with filters
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
| `scripts/query-event-log-with-filters.py`     | Filter and display events from JSONL |

## Safety

- `--query` is READ-ONLY
- `--append` only writes to the framework stream files under `.claude/session-state/`
- Never modifies profile or material files
- Domain boundary: `.claude/session-state/` only

## Examples

```bash
/orc:event-log                                                    # recent events
/orc:event-log --query --event-type MAT.integrated                # all integrations
/orc:event-log --query --character hieu --since 2026-05-01        # Nhân vật A events this month
/orc:event-log --append --event-type PSY.refresh --source psy:wave --character hoa --reason "Wave 1 complete"
```

## See Also

- `orc:session-state` — runtime session tracking (in-memory)
- `orc:decisions` — decision records (separate from event log)
- `orc:bootstrap` — loads context (logs ORC.bootstrap event)
