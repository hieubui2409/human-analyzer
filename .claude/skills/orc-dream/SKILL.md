---
name: orc:dream
description: "Periodic consolidation of character insights and storytelling patterns. Scans memory, session archives, recent work to merge, update, or create durable learnings. Resolves contradictions, prunes stale memories, strengthens weak ones. Use weekly or when memory feels fragmented. Triggers: 'dream', 'consolidate', 'clean up learnings', 'memory maintenance'."
argument-hint: "[--scan|--merge|--prune|--full]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "workflow"
  position: "maintenance"
  dependencies: ["orc:compounding"]
---

# Dream — Periodic Learning Consolidation

Consolidate scattered insights into coherent, up-to-date knowledge. Run periodically to keep memory system healthy.

## Default (No Arguments)

`--full` — scan + merge + prune in sequence.

## Flags

| Flag          | Purpose                                              |
| ------------- | ---------------------------------------------------- |
| `--scan`      | Inventory current memories, report health stats      |
| `--merge`     | Find overlapping memories, propose merges            |
| `--prune`     | Identify stale/outdated memories, propose removal    |
| `--full`      | All phases in sequence including instincts (default) |
| `--instincts` | Run instinct lifecycle only (skip memory phases)     |

## Workflow

### Phase 1: Scan (--scan)

1. Read all files in project memory: `.claude/projects/{encoded-project-root}/memory/`
2. Read `MEMORY.md` index
3. Categorize each memory by metadata type:
   - `user` — user preferences
   - `feedback` — behavioral guidance
   - `project` — ongoing work context
   - `reference` — external pointers
4. Check for `source: orc:compounding` tagged memories
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

   1. MERGE: "character-b-attachment-pattern" + "character-b-avoidance-triggers"
      → Combined: "character-b-attachment-avoidance-dynamics"
      Reason: Both describe Nhân vật B's attachment behavior from different angles

   2. CONFLICT: "character-a-writing-voice-linkedin" vs "character-a-writing-voice-general"
      → LinkedIn memory says "professional vulnerability" but general says "raw confessional"
      Action needed: clarify which applies where

   3. UPDATE: "character-c-current-status" — mentions "F15 interview" but he's now enrolled
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
   2. OUTDATED: "character-b-grade-11" — profiles now show Grade 12
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

### Phase 5: Instinct Lifecycle (--full only)

After Phase 4, run instinct maintenance. Import from `platform_lib.instinct_store`.

**5a. Apply Decay:**

- Call `apply_decay(lambda_=0.05)` on all active, non-pinned instincts
- Report: `Decay applied: {N} instincts updated, avg confidence {old} → {new}`

**5b. Archive Stale:**

- Call `archive_stale(conf_threshold=0.4, days_threshold=30)`
- Pinned instincts (process category) are exempt — skip archive regardless of confidence
- Report: `Archived: {N} stale instincts (conf < 0.4, 30+ days unreinforced, {P} pinned skipped)`
- Each archived instinct shown: `[ARCHIVED] {text} (conf: {conf}, last: {date})`

**5c. Cluster Active Instincts:**

- Load active instincts with `confidence ≥ 0.5`
- If sklearn available: TF-IDF + DBSCAN clustering (eps=0.3, min_samples=2)
- If sklearn unavailable: group by `category` field (fallback), warn via stderr
- Skip clustering entirely if < 10 active instincts — use direct listing instead
- Report clusters:
  ```
  Cluster 1 (psychology, 4 instincts):
    - [0.82] Nhân vật B's avoidance intensifies under academic pressure
    - [0.78] Nhân vật B avoids emotional topics when stressed
    - [0.71] Nhân vật B's attachment pattern: anxious-avoidant mix
    - [0.65] Nhân vật B deflects with humor under confrontation
    Core pattern: "Nhân vật B avoidance behavior under stress"
  ```

**5d. Promotion Candidates:**

- Call `get_promotion_candidates(conf_min=0.80, evidence_min=3)`
- Cap at 10 candidates per dream; show top by confidence
- For each candidate, suggest promotion target:
  - `psychology` → update character's `psychology/*.md` or `agent-memory/psychologist.md`
  - `clinical` → update `agent-memory/psychologist.md` clinical insights
  - `writing` → update `agent-memory/content-strategist.md` voice calibration
  - `audience` → update `agent-memory/content-strategist.md` platform patterns
  - `growth` → update `agent-memory/growth-analyst.md` career observations
  - `process` → create/update workflow memory (no agent mapping — instinct pool only)

**5e. Present Recommendations:**

- Use `AskUserQuestion` with promotion candidates:
  ```
  Instinct promotion candidates:
  □ PROMOTE [psychology 0.85, 4x] "Nhân vật B avoidance under stress" → update psychology/defense-mechanisms.md
  □ PROMOTE [writing 0.82, 3x] "Vulnerability hook + resolution" → update agent-memory/content-strategist.md
  □ HOLD [clinical 0.79, 2x] "Attachment + parentification" → needs 1 more reinforcement
  □ ARCHIVE [process 0.35, 1x] "Read family.md first" → stale, 45 days
  ```
- Execute approved promotions (LLM writes the actual update)

### --instincts

Run instinct lifecycle only (Phase 5), skip memory phases (1-4).

## GRO Consolidation Patterns

During --full consolidation, also check GRO-domain memories:

- **Career trajectory consistency:** verify career path memories align across characters (e.g., Nhân vật A's seniority arc vs Nhân vật C's student-to-professional arc)
- **Competency growth trend correlation:** check if competency observations from separate sessions form a coherent growth curve
- Flag contradictions between `gro:competency-map` outputs and psychology/growth-edges.md content

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

Instincts: {total} active, {decayed} decayed, {archived} archived, {promoted} promoted
Clusters: {N} found ({M} instincts clustered, {K} singletons)

Memory health: {good|needs-attention|fragmented}
Next dream recommended: {date}
```

## Auto-Trigger Conditions

Dream should be suggested (not forced) when:

- `orc:session-state --archive` detects 5+ sessions since last dream
- `orc:compounding` has written 5+ new memories since last dream
- Memory scan shows 3+ broken `[[name]]` links
- Active instinct count > 20 (`instinct_store.load_instincts(status="active")`)

Check last dream date via: `ls -t .claude/projects/{encoded-project-root}/memory/.dream-backup/ | head -1`

## Scripts

| Script                                      | Purpose                                                              |
| ------------------------------------------- | -------------------------------------------------------------------- |
| `scripts/inventory-project-memory-files.py` | Inventory all memory files with metadata for scan/merge/prune phases |

## Safety

- NEVER deletes memories without user confirmation
- NEVER modifies profile files — only memory directory
- Always shows before/after for merges
- Backs up memory state before destructive operations (copy to `memory/.dream-backup/`)
- Scope: memory maintenance for human-analyzer. Does NOT handle content creation, profile editing, or code changes.

## Examples

```bash
/orc:dream                    # full consolidation
/orc:dream --scan             # health check only
/orc:dream --merge            # find + execute merges
/orc:dream --prune            # find + remove stale
```

## See Also

- `/orc:compounding` — creates the learnings that dream consolidates
- `/orc:session-state` — session archives provide consolidation input
- `/orc:bootstrap` — benefits from clean, consolidated memory
