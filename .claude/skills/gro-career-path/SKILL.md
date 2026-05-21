---
name: gro:career-path
description: "GRO framework career trajectory analysis — gather career data from growth/career-path.md, identity/core.md, and materials for LLM analysis of decisions, inflection points, and trajectory. Triggers: 'career path', 'career analysis', 'career trajectory', 'career decisions'."
argument-hint: "[--character <name>|--all] [--json] [--decisions-only]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "gro-framework"
  position: "analysis"
  dependencies: []
---

# gro:career-path — Career Trajectory Analysis (GRO Framework)

Analyze career trajectory, decisions, and inflection points using Super's Life-Career Rainbow + SCCT frameworks.

## Default (No Arguments)

`--all` — gather career data for all three characters.

## Flags

| Flag                 | Purpose                          |
| -------------------- | -------------------------------- |
| `--character <name>` | Analyze one character only       |
| `--all`              | Analyze all characters (default) |
| `--decisions-only`   | Show only career decision data   |
| `--json`             | Output as JSON                   |

## Data Sources Read (per character)

1. `growth/career-path.md` — primary career data (Super's model)
2. `identity/core.md` §Career / §Education — factual career/education history
3. `docs/materials/{char}/` — MAT materials mentioning career keywords
4. `milestones.md` — career-relevant milestones

## Workflow

### Step 1: Gather Career Data

1. Run `scripts/gather-career-data-from-profile-and-materials.py`
2. Extracts: career stages, role history, key decisions, salary data, SCCT factors
3. Cross-references identity/core.md for factual grounding

### Step 2: LLM Analysis (heuristic)

LLM analyzes gathered data for:

- Career stage assessment (Super's Life-Career Rainbow)
- Decision quality analysis (inflection points)
- SCCT self-efficacy evaluation
- Role salience patterns
- Risk factors and growth opportunities

### Step 3: Output

```
## Career Path Analysis: {character}

**Career Stage:** {Super's stage} ({age context})
**SCCT Self-Efficacy:** {level}/10

### Career Timeline
| Period | Role/Status | Key Decision | Impact |
|--------|------------|--------------|--------|

### Decision Analysis
| # | Decision | Type | Evidence Tier | Outcome |
|---|----------|------|---------------|---------|

### Risk Factors
- {risk 1}
- {risk 2}

### Growth Opportunities
- {opportunity 1}
```

## Scripts

| Script                                                     | Purpose                                |
| ---------------------------------------------------------- | -------------------------------------- |
| `scripts/gather-career-data-from-profile-and-materials.py` | Extract career data from profile + MAT |

## Safety

- READ-ONLY — never modifies profile or material files
- Domain boundary: reads `docs/profiles/` and `docs/materials/`
- LLM does all heuristic judgment; script does deterministic gathering only

## Events

- Emits `GRO.assessed` after career analysis completes (downstream: `CRE.recalibrate`)

## Examples

```bash
/gro:career-path                              # all characters
/gro:career-path --character hieu             # Nhân vật A only
/gro:career-path --all --decisions-only       # decision data only
/gro:career-path --json                       # machine-readable
```

## See Also

- `gro:competency-map` — skill assessment (complements career trajectory)
- `gro:career-forecast` — project career trajectory forward [FORECAST]
- `gro:validate` — cross-check career data consistency
- `docs/rules/15-gro-framework.md` — GRO domain rules
