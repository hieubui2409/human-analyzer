---
name: orc:decisions
description: "Record and retrieve character arc decisions. Captures why X was chosen over Y for storylines, profile interpretations, content angles. Searchable decision log prevents re-litigating settled choices. Use when making character arc choices, resolving conflicting interpretations, or checking past decisions. Triggers: 'decision', 'record decision', 'why did we choose', 'arc decision', 'check decision log'."
argument-hint: "[--record|--search <query>|--list|--review]"
metadata:
  author: hieubt
  version: "1.1.0"
  category: "workflow"
  position: "during-work"
  dependencies: []
---

# Decisions — Character Arc Decision Records

Record WHY choices were made for character arcs, profile interpretations, and content angles. Prevents re-litigating settled decisions.

## Default (No Arguments)

`--list` — show recent decisions.

## Flags

| Flag               | Purpose                                   |
| ------------------ | ----------------------------------------- |
| `--record`         | Record a new decision (interactive)       |
| `--search <query>` | Search decisions by keyword               |
| `--list`           | List recent decisions (last 20)           |
| `--review`         | Review decisions for a specific character |

## Decision Record Format

Each decision stored as a separate markdown file in `.claude/decisions/`. New records written by `--record` get a monotonic `DEC-n` id allocated atomically (see Scripts). Legacy hand-authored records without a `DEC-n` id coexist and are listed as-is.

```markdown
---
id: DEC-1
status: active
date: YYYY-MM-DD
character: {slug}
supersedes: DEC-n   # optional — id of the prior ruling this replaces
---

## DEC-1 — {Short title}

{Rationale — WHY this choice, with profile references}
```

## Workflow

### --record

1. `AskUserQuestion` — gather decision details:
   - Q1: What was decided? (free text)
   - Q2: Which character(s)? (Nhân vật A/Nhân vật B/Nhân vật C/cross)
   - Q3: Category? (arc/interpretation/content/relationship/clinical)
   - Q4: What alternatives were considered? (free text)
   - Q5: Why this choice? (free text)
   - Q6: Does this supersede a prior decision? (DEC-n or blank)
2. Call `record-decision-with-alloc.py --title "..." --rationale "..." [--supersedes DEC-n]`
   - Script atomically allocates the next DEC-n id inside an exclusive file lock
     (concurrent agents cannot grab the same id — critical for team-mode safety)
   - If `--supersedes DEC-n` is set, the prior record's `status:` is flipped to
     `superseded` in the same lock, so the register never has zero-active + phantom-retired
3. Print confirmation with id and file path

### --search `<query>`

1. `grep -ril "{query}" .claude/decisions/` — find matching files
2. For each match, read and extract title + decision + status
3. Print results sorted by date (newest first)

### --list

1. Run `index-decisions-with-search.py --list`
2. Table columns: Date | ID | Title | Character | Status | Lineage
   - Lineage column shows `supersedes DEC-n` or `superseded_by DEC-n` where relevant
3. Legacy council-*.md records listed with id=legacy

### --review

1. `AskUserQuestion` — which character?
2. Filter decisions by character
3. Check for conflicts between active decisions
4. Check if any decisions reference outdated profile content
5. Report:

   ```
   ## Decision Review: {character}

   Active decisions: {N}
   Superseded: {M}
   Needs revisit: {list with reasons}
   Potential conflicts: {list}
   ```

## Categories

| Category         | When to use                                    |
| ---------------- | ---------------------------------------------- |
| `arc`            | Character storyline direction                  |
| `interpretation` | How to read a character's psychology/behavior  |
| `content`        | Content angle or approach choice               |
| `relationship`   | How to portray relationship dynamics           |
| `clinical`       | Which clinical framework applies to a behavior |
| `growth`         | Career path direction choices (GRO domain)     |
| `forecast`       | Forecast confidence threshold decisions        |

## Scripts

| Script                                   | Purpose                                                              |
| ---------------------------------------- | -------------------------------------------------------------------- |
| `scripts/index-decisions-with-search.py` | Build searchable index of all decision records in .claude/decisions/ |
| `scripts/record-decision-with-alloc.py`  | Atomic alloc-id + append backend (called by --record workflow)       |

## Safety

- Decisions are append-only — never delete, only supersede
- Old decisions kept for historical context
- The `--record` backend uses an exclusive file lock so concurrent agents in team-mode
  cannot allocate the same DEC-n id (closes the TOCTOU alloc-then-write race)
- `.claude/decisions/` is excluded from the framework release pack (character-tagged data)
- Scope: decision records for human-analyzer character work. Does NOT handle implementation.

## Examples

```bash
/orc:decisions                                        # list recent
/orc:decisions --record                               # new decision
/orc:decisions --search "attachment"                   # find related
/orc:decisions --review                               # audit decisions
```

## See Also

- `/cre:exploring` — exploration often produces decisions to record
- `/orc:compounding` — learnings may reference or challenge past decisions
- `/orc:classify` — high_risk work should check decision log first
