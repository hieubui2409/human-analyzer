# orc:event-log — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

As domains fire events (PSY.refresh, CRE.recalibrate), they get logged. Event-log is the audit trail: "who triggered what, when?" You can query: "all PSY events in the last 3 days," "all events from psy:crossref," "all events for Nhân vật B." It's a searchable history of domain activity.

## 2. Core concepts (the mental model)

**6 framework streams.** Each domain (MAT, PSY, CRE, GRO, ORC, COM) has its own JSONL file. Events route by prefix (PSY.* → character-events.jsonl, etc.).

**Append-only.** Once logged, events never change. Always searchable history.

**Queries are filters.** Combine event-type + character + date + skill to find specific activity.

## 3. Learning path

**First query:** `orc:event-log --query` — recent events (last 20).

**Filter by event:** `orc:event-log --query --event-type PSY.refresh` — only PSY refreshes.

**Filter by character:** `orc:event-log --query --character character-b` — all events for Nhân vật B.

**Filter by date:** `orc:event-log --query --since 2026-06-01` — events from June onward.

**Append an event:** Skills call `--append --event-type MAT.integrated --source mat:indexer --character hieu --reason "New material processed"`.

## 4. Use cases (each = a sample conversation)

### Use case: Query recent PSY events

> You: "What PSY work happened this week?"
>
> Skill: Queries character-events.jsonl for `event-type=PSY.refresh`, `--since=7 days ago`. Shows: PSY.refresh on 2026-06-04 (psy:crossref, Nhân vật B), PSY.refresh on 2026-06-02 (psy:wave, Nhân vật A). You see PSY activity.

### Use case: Trace all events for one character

> You: "Show all events for Nhân vật C."
>
> Skill: Queries across all 6 streams for `character=character-c`. Returns: MAT.integrated, PSY.refresh, GRO.assessed events in order. You see full activity chain for that character.

### Use case: Log a domain event

> Skill (mat:indexer) completes: `orc:event-log --append --event-type MAT.integrated --source mat:indexer --character character-a --reason "Transcript validated, integration gate passed"`. Event logged to material-events.jsonl with ISO timestamp.

## 5. Important caveats

- **Events are facts, not interpretation.** Log says "MAT.integrated," not "material was good" or "ready for use."
- **Event logs grow indefinitely.** No auto-cleanup; archives should periodically back up old logs.
- **Queries are case-sensitive.** `--event-type PSY.refresh` ≠ `PSY.REFRESH`.
- **Timestamps are ISO 8601.** Sorting and filtering assume UTC.
