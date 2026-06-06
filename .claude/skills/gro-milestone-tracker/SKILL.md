---
name: gro:milestone-tracker
description: "GRO framework milestone tracking — gather career milestones from milestones.md and career-path.md to track actual vs planned progression. Triggers: 'milestone tracker', 'track milestones', 'career milestones', 'milestone status'."
argument-hint: "[--character <name>|--all] [--json] [--pending-only]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "gro-framework"
  position: "tracking"
  dependencies: []
---

# gro:milestone-tracker — Career Milestone Tracking (GRO Framework)

Track career milestones and compare actual vs planned progression.

## Default (No Arguments)

`--all` — gather milestone data for all three characters.

## Flags

| Flag                 | Purpose                                 |
| -------------------- | --------------------------------------- |
| `--character <name>` | Track one character only                |
| `--all`              | Track all characters (default)          |
| `--json`             | Output as JSON                          |
| `--pending-only`     | Show only planned/unachieved milestones |

## Data Sources Read (per character)

1. `milestones.md` — all life milestones
2. `growth/career-path.md` — career-specific milestones and trajectory
3. `identity/achievements.md` — verified achievements as completed milestones

## Workflow

### Step 1: Gather Milestone Data

1. Run `scripts/gather-career-milestone-tracking-data.py`
2. Extracts: milestone entries, dates, status (achieved/planned/missed)
3. Cross-references achievements for validation

### Step 2: LLM Analysis (heuristic)

LLM analyzes gathered data for:

- Milestone completion rate
- On-track vs delayed assessment
- Next milestone identification
- Trajectory assessment

### Step 3: Output

```
## Milestone Tracker: {character}

**Total Milestones:** {N}
**Achieved:** {N} | **Planned:** {N} | **Missed:** {N}

### Milestone Timeline
| Date | Milestone | Status | Evidence |
|------|-----------|--------|----------|

### Next Milestones
1. {upcoming milestone} — target: {date}
```

## Scripts

| Script                                             | Purpose                             |
| -------------------------------------------------- | ----------------------------------- |
| `scripts/gather-career-milestone-tracking-data.py` | Extract milestone data from profile |

## Safety

- READ-ONLY — never modifies profile or material files
- Domain boundary: reads `docs/profiles/` only
- LLM does all heuristic judgment; script does deterministic gathering only

## Events

- Emits no events (read-only tracking tool)

## Examples

```bash
/gro:milestone-tracker                              # all characters
/gro:milestone-tracker --character character-c            # Nhân vật C only
/gro:milestone-tracker --all --pending-only         # upcoming milestones
/gro:milestone-tracker --json                       # machine-readable
```

## See Also

- `gro:career-path` — full career trajectory (context for milestones)
- `gro:career-forecast` — project future milestones [FORECAST]
- `psy:arc-tracker` — psychological growth tracking (complementary)
- `docs/rules/15-gro-framework.md` — GRO domain rules
