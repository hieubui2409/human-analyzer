---
name: mpc:compounding
description: "Extract durable learnings after content or profile work. Captures character psychology insights, effective writing patterns, audience resonance signals, and clinical accuracy notes. Feeds findings into memory system. Use after completing content creation, profile updates, or arc development. Triggers: 'compound', 'extract learnings', 'what did we learn', 'capture insights'."
argument-hint: "[--auto|--character <name>|--content|--session]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "workflow"
  position: "post-work"
  dependencies: ["mpc:session-state"]
---

# Compounding — Extract Durable Learnings

After content/profile work, extract insights worth remembering. Write to memory system so future sessions benefit.

## Default (No Arguments)

`--session` — analyze session state + recent diffs to extract learnings.

## Flags

| Flag                 | Purpose                                              |
| -------------------- | ---------------------------------------------------- |
| `--session`          | Extract from current session work (default)          |
| `--auto`             | Auto-extract + write to memory, no confirmation      |
| `--character <name>` | Extract character-specific insights                  |
| `--content`          | Extract content creation patterns from recent assets |

## Learning Categories

### 1. Character Psychology

Insights about character behavior, motivations, defense mechanisms discovered during work.

- New understanding of attachment patterns
- Defense mechanism triggers identified
- Relationship dynamics clarified
- Contradictions resolved between profile files

### 2. Writing Patterns

What worked in content creation:

- Tone/voice choices that landed well
- Storytelling structures that fit a character
- Platform-specific adaptations that worked
- Hook/opening patterns

### 3. Audience Resonance

Signals about what connects with audience (if data available):

- Which angles generate engagement
- Which topics resonate per platform
- Content format preferences

### 4. Clinical Accuracy

Notes on psychological framework usage:

- Which theories from `docs/references/` applied correctly
- Corrections or nuances discovered
- Framework combinations that describe a character well

### 5. Process Learnings

Workflow improvements discovered:

- What skill sequence worked well
- Where bottlenecks appeared
- What context was missing at start

## Workflow

### --session (Default)

1. Read `.claude/session-state/state.json`
2. If `profiles_touched` not empty → analyze profile changes
3. If `content_created` not empty → analyze content patterns
4. If `decisions` not empty → evaluate decision quality
5. `git diff --stat HEAD~5` — identify what changed
6. For each changed file, categorize learning type
7. Generate learning candidates (3-7 per session)
8. Present via `AskUserQuestion`:
   ```
   Review extracted learnings. Select which to save to memory:
   □ [Character] Nhân vật B's avoidance pattern intensifies under academic pressure (psychology/formulation.md)
   □ [Writing] LinkedIn posts work better with vulnerability hook + resolution structure
   □ [Clinical] Attachment theory + parentification explains Nhân vật A-Nhân vật B dynamic better than pure rescue narrative
   □ [Process] Reading relationships/family.md before writing cross-character content prevents consistency errors
   ```
9. Write selected learnings to memory files

### --auto

Same as `--session` but skip confirmation. Write all candidates to memory.

### --character `<name>`

1. Resolve character name (same as mpc-bootstrap)
2. Read character's profile files (psychology/formulation.md, psychology/defense-mechanisms.md, relationships/family.md, cross-character files via `list_relationship_files()`)
3. `git log --oneline -20 -- docs/profiles/{resolved}/` — recent changes
4. `git diff HEAD~10 -- docs/profiles/{resolved}/` — what changed
5. Extract character-specific insights:
   - New psychological patterns identified
   - Relationship dynamics updates
   - Timeline additions and their implications
6. Present + write to memory

### --content

1. `git log --oneline -10 -- assets/` — recent content
2. For each new asset directory:
   - Read `post.txt` or main content file
   - Analyze structure, tone, hooks, CTA
   - Compare against `identity/writing-voice.md` if Nhân vật A's content
3. Extract content patterns
4. Present + write to memory

## Memory Output Format

Write to project memory at `.claude/projects/-home-hieubt-Documents-ck-marketing/memory/`:

```markdown
---
name: {category}-{slug}
description: {one-line summary}
metadata:
  type: project
  source: mpc:compounding
  session: {date}
---

{learning content}

**Why:** {context for why this matters}
**How to apply:** {when to use this learning}
```

## Merge Rules

Before writing a new memory:

1. Check existing memories for overlap
2. If related memory exists → update it (append, don't duplicate)
3. If contradicts existing memory → flag for user decision
4. Link related memories with `[[name]]` references
5. After writing new learnings, check if `mpc:dream` should run (if 5+ new memories since last dream consolidation)

## Scripts

| Script                                               | Purpose                                                                    |
| ---------------------------------------------------- | -------------------------------------------------------------------------- |
| `scripts/summarize-session-changes-from-git-diff.py` | Parse git diff to extract changed files and categorize learning candidates |

## Safety

- READ-ONLY for profile/content files — only writes to memory directory
- Never modifies profile files, content assets, or plans
- Always confirms before writing to memory (unless --auto)
- Scope: learning extraction for ck-marketing. Does NOT handle implementation, content creation, or code changes.

## Examples

```bash
/mpc:compounding                          # extract from current session
/mpc:compounding --auto                   # auto-extract, no confirm
/mpc:compounding --character hòa          # Nhân vật B-specific insights
/mpc:compounding --content                # content pattern extraction
```

## Dream Trigger

After writing ≥5 new memories in a single session, suggest running `mpc:dream --merge` to consolidate overlapping insights before they accumulate.

## See Also

- `/mpc:session-state` — provides session context for extraction
- `/mpc:dream` — periodic consolidation of accumulated learnings (trigger when memory count grows)
- `/mpc:bootstrap` — loads context that compounding enriches
