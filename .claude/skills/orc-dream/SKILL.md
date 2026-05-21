---
name: mpc:dream
description: "Periodic consolidation of character insights and storytelling patterns. Scans memory, session archives, recent work to merge, update, or create durable learnings. Resolves contradictions, prunes stale memories, strengthens weak ones. Use weekly or when memory feels fragmented. Triggers: 'dream', 'consolidate', 'clean up learnings', 'memory maintenance'."
argument-hint: "[--scan|--merge|--prune|--full]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "workflow"
  position: "maintenance"
  dependencies: ["mpc:compounding"]
---

# Dream — Periodic Learning Consolidation

Consolidate scattered insights into coherent, up-to-date knowledge. Run periodically to keep memory system healthy.

## Default (No Arguments)

`--full` — scan + merge + prune in sequence.

## Flags

| Flag      | Purpose                                           |
| --------- | ------------------------------------------------- |
| `--scan`  | Inventory current memories, report health stats   |
| `--merge` | Find overlapping memories, propose merges         |
| `--prune` | Identify stale/outdated memories, propose removal |
| `--full`  | All three in sequence (default)                   |

## Workflow

### Phase 1: Scan (--scan)

1. Read all files in project memory: `.claude/projects/-home-hieubt-Documents-ck-marketing/memory/`
2. Read `MEMORY.md` index
3. Categorize each memory by metadata type:
   - `user` — user preferences
   - `feedback` — behavioral guidance
   - `project` — ongoing work context
   - `reference` — external pointers
4. Check for `source: mpc:compounding` tagged memories
5. Report:
   ```
   ## Memory Health
   Total: {N} memories
   By type: user({n}), feedback({n}), project({n}), reference({n})
   From compounding: {n}
   Broken links: {list of [[name]] references that don't resolve}
   Last updated: {oldest and newest dates}
   ```

### Phase 2: Merge (--merge)

1. Group memories by topic (character name, content type, workflow)
2. For each group with 2+ memories:
   - Compare content for overlap
   - Identify complementary vs contradictory information
3. Propose merges via `AskUserQuestion`:

   ```
   Found {N} merge candidates:

   1. MERGE: "hoa-attachment-pattern" + "hoa-avoidance-triggers"
      → Combined: "hoa-attachment-avoidance-dynamics"
      Reason: Both describe Nhân vật B's attachment behavior from different angles

   2. CONFLICT: "hieu-writing-voice-linkedin" vs "hieu-writing-voice-general"
      → LinkedIn memory says "professional vulnerability" but general says "raw confessional"
      Action needed: clarify which applies where

   3. UPDATE: "chien-current-status" — mentions "F15 interview" but he's now enrolled
      → Suggest updating to current status
   ```

4. Execute approved merges:
   - Write merged file
   - Delete superseded files
   - Update `MEMORY.md` index

### Phase 3: Prune (--prune)

1. For each memory, check staleness:
   - `project` type older than 30 days → flag for review
   - `reference` type → verify external resource still relevant
   - Memories referencing deleted/moved files → flag
2. Cross-reference with current profile state:
   - Read character INDEX.md files
   - Compare memory claims against current profile content
   - Flag memories that contradict current profiles
3. Propose removals via `AskUserQuestion`:

   ```
   Prune candidates:

   1. STALE: "project-merge-freeze" (2026-03-05) — 2+ months old, likely resolved
   2. OUTDATED: "hoa-grade-11" — profiles now show Grade 12
   3. ORPHAN: "content-tiktok-strategy" — references plan that no longer exists
   ```

4. Execute approved removals

### Phase 4: Strengthen (during --full only)

After merge + prune, identify gaps:

1. For each character, check if memory covers:
   - Core psychological pattern (from psychology/formulation.md)
   - Key relationship dynamics
   - Current arc/status
   - Writing voice notes (Nhân vật A only)
2. If gaps found, suggest creating memories from current profiles
3. Ensure cross-character memories link properly with `[[name]]`

## Memory Quality Rules

- Each memory should have ONE clear insight, not a list of everything
- `description` field must be specific enough to judge relevance without reading body
- `Why` and `How to apply` lines are mandatory for project/feedback types
- Links (`[[name]]`) should connect related insights across characters

## Output

After full run, print summary:

```
## Dream Complete

Scanned: {N} memories
Merged: {M} (from {X} originals)
Pruned: {P}
Created: {C} (gap-fill)
Broken links fixed: {L}

Memory health: {good|needs-attention|fragmented}
Next dream recommended: {date}
```

## Auto-Trigger Conditions

Dream should be suggested (not forced) when:

- `mpc:session-state --archive` detects 5+ sessions since last dream
- `mpc:compounding` has written 5+ new memories since last dream
- Memory scan shows 3+ broken `[[name]]` links

Check last dream date via: `ls -t .claude/projects/-home-hieubt-Documents-ck-marketing/memory/.dream-backup/ | head -1`

## Scripts

| Script                                      | Purpose                                                              |
| ------------------------------------------- | -------------------------------------------------------------------- |
| `scripts/inventory-project-memory-files.py` | Inventory all memory files with metadata for scan/merge/prune phases |

## Safety

- NEVER deletes memories without user confirmation
- NEVER modifies profile files — only memory directory
- Always shows before/after for merges
- Backs up memory state before destructive operations (copy to `memory/.dream-backup/`)
- Scope: memory maintenance for ck-marketing. Does NOT handle content creation, profile editing, or code changes.

## Examples

```bash
/mpc:dream                    # full consolidation
/mpc:dream --scan             # health check only
/mpc:dream --merge            # find + execute merges
/mpc:dream --prune            # find + remove stale
```

## See Also

- `/mpc:compounding` — creates the learnings that dream consolidates
- `/mpc:session-state` — session archives provide consolidation input
- `/mpc:bootstrap` — benefits from clean, consolidated memory
