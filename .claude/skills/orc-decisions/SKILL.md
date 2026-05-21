---
name: orc:decisions
description: "Record and retrieve character arc decisions. Captures why X was chosen over Y for storylines, profile interpretations, content angles. Searchable decision log prevents re-litigating settled choices. Use when making character arc choices, resolving conflicting interpretations, or checking past decisions. Triggers: 'decision', 'record decision', 'why did we choose', 'arc decision', 'check decision log'."
argument-hint: "[--record|--search <query>|--list|--review]"
metadata:
  author: hieubt
  version: "1.0.0"
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

Each decision stored as markdown in `plans/decisions/`:

```markdown
# {YYYY-MM-DD} — {Short title}

**Character(s):** {name(s)}
**Category:** {arc|interpretation|content|relationship|clinical}
**Status:** {active|superseded|revisit}

## Decision

{What was decided}

## Alternatives Considered

1. {Option A} — {why rejected}
2. {Option B} — {why rejected}

## Rationale

{Why this choice, with profile references}

## Evidence

- {Profile file}: {relevant quote or section}
- {Reference file}: {theory supporting this}

## Impact

- {What this decision affects going forward}
- {Files that should reflect this decision}

## Revisit Conditions

{When this decision should be reconsidered}
```

## Workflow

### --record

1. `AskUserQuestion` — gather decision details:
   - Q1: What was decided? (free text)
   - Q2: Which character(s)? (Nhân vật A/Nhân vật B/Nhân vật C/cross)
   - Q3: Category? (arc/interpretation/content/relationship/clinical)
   - Q4: What alternatives were considered? (free text)
   - Q5: Why this choice? (free text)
2. Auto-populate evidence by reading relevant profile files
3. Write to `plans/decisions/{YYYYMMDD}-{slug}.md`
4. Update session state: append to `decisions` array
5. Print confirmation with file path

### --search `<query>`

1. `grep -ril "{query}" plans/decisions/` — find matching files
2. For each match, read and extract title + decision + status
3. Print results sorted by date (newest first)

### --list

1. `ls -t plans/decisions/*.md | head -20`
2. For each file, extract title + character + category + status
3. Print as table:
   ```
   | Date       | Character | Category       | Decision                        | Status |
   | 2026-05-13 | Nhân vật B       | interpretation | Avoidance is attachment-based   | active |
   | 2026-05-10 | Nhân vật A-Nhân vật B  | relationship   | Kết nghĩa framing over mentoring | active |
   ```

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

| Script                                   | Purpose                                                            |
| ---------------------------------------- | ------------------------------------------------------------------ |
| `scripts/index-decisions-with-search.py` | Build searchable index of all decision records in plans/decisions/ |

## Safety

- Decisions are append-only — never delete, only supersede
- Old decisions kept for historical context
- Scope: decision records for ck-marketing character work. Does NOT handle implementation.

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
