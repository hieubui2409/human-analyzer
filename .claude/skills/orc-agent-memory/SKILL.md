---
name: orc:agent-memory
description: "Persistent memory for content-creator and copywriter agents. Stores writing style learnings, successful patterns, platform-specific insights, and character voice calibration. Agents read before writing, write after completing work. Use to view, manage, or seed agent memory. Triggers: 'agent memory', 'what has the agent learned', 'agent learnings', 'reset agent memory'."
argument-hint: "[--show|--seed|--reset|--agent <name>]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "workflow"
  position: "utility"
  dependencies: ["orc:compounding"]
---

# Agent Memory — Persistent Learning for Content Agents

Store and retrieve learnings specific to content-producing agents. Each agent builds a memory of what works.

## Default (No Arguments)

`--show` — display all agent memories.

## Flags

| Flag             | Purpose                                  |
| ---------------- | ---------------------------------------- |
| `--show`         | Display current agent memories (default) |
| `--seed`         | Initialize agent memory from profiles    |
| `--reset`        | Clear agent memory (with confirmation)   |
| `--agent <name>` | Filter to specific agent                 |

## Agent Memory Directory

Location: `.claude/agent-memory/`

```
.claude/agent-memory/
├── content-creator.md    — content-creator agent learnings
├── copywriter.md         — copywriter agent learnings
├── social-media.md       — social-media-manager agent learnings
└── _shared.md            — cross-agent learnings
```

## Memory Schema

Each agent memory file:

```markdown
# {Agent Name} Memory

Last updated: {ISO date}

## Character Voice Calibration

### Nhân vật A

- Tone: {calibrated description}
- Vocabulary: {patterns}
- Effective hooks: {list}
- Anti-patterns: {what to avoid}

### Nhân vật B

- Tone: {calibrated description}
- ...

### Nhân vật C

- Tone: {calibrated description}
- ...

## Platform Patterns

### LinkedIn

- Optimal length: {range}
- Hook style: {what works}
- Structure: {pattern}

### Facebook

- ...

## Successful Templates

1. {Template name}: {structure description}
   - Used for: {context}
   - Example: {reference to asset}

## Failures / Anti-patterns

1. {What didn't work}: {why}

## Clinical Framing Notes

- {Theory}: {how to reference accessibly}
```

## Workflow

### --show

1. Read all files in `.claude/agent-memory/`
2. Print summary per agent:

   ```
   ## Agent Memory Status

   content-creator: {N} voice entries, {M} templates, {P} anti-patterns
   copywriter: {N} voice entries, {M} templates, {P} anti-patterns
   social-media: {N} voice entries, {M} templates, {P} anti-patterns
   _shared: {N} cross-agent learnings

   Last updated: {date}
   ```

### --seed

Initialize agent memory from current profile state:

1. Read `WRITING-VOICE.md` (Nhân vật A) → seed voice calibration
2. Read `CHARACTERISTIC.md` for all 3 characters → seed voice patterns
3. Read `docs/rules/03-content-creation-pipeline.md` + `docs/rules/09-confidentiality-protocol.md` → seed platform constraints
4. Scan `assets/` for recent content → extract templates
5. Write initial memory files
6. Print: "Seeded {N} voice entries, {M} platform rules, {P} templates"

### --reset

1. Confirm via `AskUserQuestion`
2. Archive current memory to `.claude/agent-memory/.archive/{date}/`
3. Write empty memory templates
4. Print confirmation

### --agent `<name>`

Filter all operations to one agent. Valid names: `content-creator`, `copywriter`, `social-media`.

## How Agents Use Memory

### Before Writing (Agent reads)

Content-producing agents should read their memory file at start:

```
Read .claude/agent-memory/{agent-name}.md
Apply voice calibration for {character}
Apply platform patterns for {platform}
Reference successful templates
Avoid documented anti-patterns
```

### After Writing (Agent appends)

After completing content work, append learnings:

```
If new voice insight discovered → update Character Voice Calibration
If new template pattern worked → add to Successful Templates
If something failed → add to Failures / Anti-patterns
Update "Last updated" timestamp
```

## Integration with orc:compounding

`orc:compounding` extracts session-level learnings.
`orc:agent-memory` stores agent-specific operational patterns.

Flow: Work completes → `orc:compounding` extracts insights → relevant insights pushed to agent memory files.

## Scripts

| Script                                        | Purpose                                                     |
| --------------------------------------------- | ----------------------------------------------------------- |
| `scripts/show-agent-memory-stats-by-agent.py` | Display memory stats (entry counts, last updated) per agent |

## Safety

- Agent memory is additive — never auto-deletes entries
- Reset requires explicit confirmation + archives first
- Memory files are .claude/-scoped, not in git by default
- Scope: agent memory management for ck-marketing. Does NOT handle content creation or profile editing.

## Examples

```bash
/orc:agent-memory                           # show all
/orc:agent-memory --show                    # same
/orc:agent-memory --seed                    # initialize from profiles
/orc:agent-memory --agent copywriter        # show copywriter only
/orc:agent-memory --reset                   # clear with backup
```

## See Also

- `/orc:compounding` — feeds learnings into agent memory
- `/orc:dream` — consolidates agent memory during maintenance
- `/cre:prompt-leverage` — agent memory informs prompt strengthening
