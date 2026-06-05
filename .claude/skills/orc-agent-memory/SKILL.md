---
name: orc:agent-memory
description: "Persistent memory for CK-domain agents (psychologist, content-strategist, growth-analyst). Stores domain-specific insights, character calibration, patterns learned, and instinct-promoted knowledge. Agents read before work, write after. Use to view, seed, or manage agent memory. Triggers: 'agent memory', 'what has the agent learned', 'agent learnings', 'reset agent memory'."
argument-hint: "[--show|--seed|--reset|--agent <name>|--instinct-feed <name>]"
metadata:
  author: hieubt
  version: "2.0.0"
  category: "workflow"
  position: "utility"
  dependencies: ["orc:compounding"]
---

# Agent Memory — Persistent Learning for CK-Domain Agents

Store and retrieve learnings specific to 3 CK-domain custom agents. Each agent builds domain-specific memory from sessions and instinct promotions.

## Default (No Arguments)

`--show` — display all agent memories with instinct stats.

## Flags

| Flag                     | Purpose                                           |
| ------------------------ | ------------------------------------------------- |
| `--show`                 | Display current agent memories (default)          |
| `--seed`                 | Initialize agent memory from profiles + instincts |
| `--reset`                | Clear agent memory (with confirmation)            |
| `--agent <name>`         | Filter to specific agent                          |
| `--instinct-feed <name>` | Show only instinct-relevant data for an agent     |

## Agent Memory Directory

Location: `.claude/agent-memory/`

```
.claude/agent-memory/
├── psychologist.md       ← PSY: clinical insights, formulation patterns
├── content-strategist.md ← CRE: voice calibration, platform patterns
└── growth-analyst.md     ← GRO: career observations, competency evolution
```

## Agent-to-Category Mapping

Instincts are filtered to agents by category (imported from `instinct_store.AGENT_CATEGORY_MAP`):

| Agent              | Instinct Categories          |
| ------------------ | ---------------------------- |
| psychologist       | psychology, clinical         |
| content-strategist | writing, audience            |
| growth-analyst     | growth                       |
| _(unmapped)_       | process → instinct pool only |

## Memory Schema

Each agent memory file:

```markdown
# {Agent Name} Memory

Last updated: {ISO date}

## Character Insights

### Nhân vật A

- {domain-specific calibration}

### Nhân vật B

- {domain-specific calibration}

### Nhân vật C

- {domain-specific calibration}

## Patterns Learned

- {accumulated patterns from sessions}

## Anti-patterns

- {what didn't work}

## Instinct-Promoted Patterns

- {populated by orc:dream promotion pipeline}
```

**psychologist.md**: Character Insights = clinical observations per character. Patterns = formulation patterns, defense mechanism triggers, attachment dynamics.

**content-strategist.md**: Character Insights = voice calibration per character. Patterns = platform patterns, hook styles, content structures.

**growth-analyst.md**: Character Insights = career trajectory observations. Patterns = competency evolution, mentoring effectiveness.

## Workflow

### --show

1. Read all files in `.claude/agent-memory/`
2. Load instincts via `instinct_store.load_instincts(status="active")`
3. For each agent, filter instincts by `AGENT_CATEGORY_MAP`
4. Print summary per agent:

   ```
   ## Agent Memory Status

   psychologist: {N} character insights, {M} patterns, {P} anti-patterns
     Relevant instincts: 5 (3 psychology, 2 clinical)
     Top: [0.85] "Nhân vật B avoidance intensifies under academic pressure"
   content-strategist: {N} character insights, {M} patterns
     Relevant instincts: 3 (2 writing, 1 audience)
   growth-analyst: {N} character insights, {M} patterns
     Relevant instincts: 2 (2 growth)

   Promotion-ready: 2 instincts eligible for agent memory integration
   ```

### --seed

Initialize agent memory from current profile state + instincts:

1. **psychologist.md**: Read `psychology/formulation.md`, `psychology/defense-mechanisms.md`, `psychology/attachment-style.md` for each character → seed Character Insights
2. **content-strategist.md**: Read `identity/writing-voice.md` (Nhân vật A) + `docs/rules/03-content-creation-pipeline.md` → seed voice calibration and platform patterns
3. **growth-analyst.md**: Read `growth/career-path.md`, `growth/competencies.md` for each character → seed career observations
4. Query instincts by agent category mapping via `instinct_store.get_agent_categories()`
5. Append promoted instincts (conf ≥ 0.80) to "## Instinct-Promoted Patterns"
6. Print: "Seeded {N} character insights, {M} patterns, {P} promoted instincts"

### --reset

1. Confirm via `AskUserQuestion`
2. Archive current memory to `.claude/agent-memory/.archive/{date}/`
3. Write empty memory templates
4. Print confirmation

### --agent `<name>`

Filter all operations to one agent. Valid names: `psychologist`, `content-strategist`, `growth-analyst`.

### --instinct-feed `<name>`

Show only instinct-relevant data for a specific agent:

1. Load instincts filtered by agent's categories
2. Show instinct list sorted by confidence
3. Show promotion candidates for this agent's domain
4. Skip memory file content (instincts only)

## How Agents Use Memory

### Before Work (Agent reads)

Domain agents should read their memory file at start:

```
Read .claude/agent-memory/{agent-name}.md
Apply character insights for {character being analyzed}
Reference patterns learned
Avoid documented anti-patterns
Check instinct-promoted patterns for recent calibration
```

### After Work (Agent appends)

After completing domain work, append learnings:

```
If new character insight discovered → update Character Insights
If new pattern validated → add to Patterns Learned
If something failed → add to Anti-patterns
Update "Last updated" timestamp
```

## Integration with orc:compounding + orc:dream

- `orc:compounding` extracts session learnings → atomic instincts with confidence scores
- `orc:dream --full` Phase 5 evaluates instincts for promotion
- Promoted instincts (conf ≥ 0.80, evidence ≥ 3) are written to agent memory under "## Instinct-Promoted Patterns"
- Agent memory is the persistent, curated layer; instincts are the evolving, scored layer

## Scripts

| Script                                        | Purpose                                                     |
| --------------------------------------------- | ----------------------------------------------------------- |
| `scripts/show-agent-memory-stats-by-agent.py` | Display memory stats (entry counts, last updated) per agent |

## Safety

- Agent memory is additive — never auto-deletes entries
- Reset requires explicit confirmation + archives first
- Memory files are `.claude/`-scoped
- Scope: agent memory management for human-analyzer. Does NOT handle content creation or profile editing.

## Examples

```bash
/orc:agent-memory                                 # show all
/orc:agent-memory --show                          # same
/orc:agent-memory --seed                          # initialize from profiles + instincts
/orc:agent-memory --agent psychologist            # show psychologist only
/orc:agent-memory --instinct-feed growth-analyst  # instinct data for GRO agent
/orc:agent-memory --reset                         # clear with backup
```

## See Also

- `/orc:compounding` — feeds learnings into instinct store → agent memory
- `/orc:dream` — promotes high-confidence instincts to agent memory
- `/cre:prompt-leverage` — agent memory informs prompt strengthening
