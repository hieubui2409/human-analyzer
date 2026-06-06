---
name: gro:learning-profile
description: "GRO framework learning profile analysis — gather learning data from growth/learning-profile.md and materials for LLM mapping using Kolb's Experiential Learning Cycle. Triggers: 'learning profile', 'learning style', 'kolb', 'cognitive style'."
argument-hint: "[--character <name>|--all] [--json]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "gro-framework"
  position: "analysis"
  dependencies: []
---

# gro:learning-profile — Learning Style Mapping (GRO Framework)

Map cognitive style and learning patterns using Kolb's Experiential Learning Cycle.

## Default (No Arguments)

`--all` — gather learning profile data for all three characters.

## Flags

| Flag                 | Purpose                          |
| -------------------- | -------------------------------- |
| `--character <name>` | Profile one character only       |
| `--all`              | Profile all characters (default) |
| `--json`             | Output as JSON                   |

## Data Sources Read (per character)

1. `growth/learning-profile.md` — primary learning style data (Kolb)
2. `identity/core.md` §Education — educational background
3. `psychology/growth-edges.md` — growth patterns (cross-reference only)
4. `docs/materials/{char}/` — MAT materials mentioning learning keywords

## Kolb's Learning Styles

| Style         | Axes    | Description                            |
| ------------- | ------- | -------------------------------------- |
| Diverging     | CE + RO | Imaginative, emotional, brainstorming  |
| Assimilating  | AC + RO | Logical, analytical, theory-building   |
| Converging    | AC + AE | Practical, problem-solving, technical  |
| Accommodating | CE + AE | Hands-on, risk-taking, action-oriented |

## Workflow

### Step 1: Gather Learning Data

1. Run `scripts/gather-learning-data-from-profile-and-materials.py`
2. Extracts: learning style, cycle strengths/gaps, study patterns, evidence
3. Cross-references education data from identity/core.md

### Step 2: LLM Analysis (heuristic)

LLM analyzes gathered data for:

- Kolb style classification with evidence
- Cycle strength/weakness identification
- Learning barrier analysis
- Content style recommendations (how to frame information for this person)

### Step 3: Output

```
## Learning Profile: {character}

**Dominant Style:** {Kolb style} ({axes})
**Cycle Strengths:** {strong phases}
**Cycle Gaps:** {weak phases}

### Learning Patterns
| Pattern | Evidence | Source |
|---------|----------|--------|

### Study Behaviors
- {behavior 1}: {description}

### Content Style Implications
→ Frame content using {approach} for maximum engagement
```

## Scripts

| Script                                                       | Purpose                                  |
| ------------------------------------------------------------ | ---------------------------------------- |
| `scripts/gather-learning-data-from-profile-and-materials.py` | Extract learning data from profile + MAT |

## Safety

- READ-ONLY — never modifies profile or material files
- Domain boundary: reads `docs/profiles/` and `docs/materials/`
- LLM does all heuristic judgment; script does deterministic gathering only

## Events

- Emits `GRO.profiled` after learning profile analysis completes (downstream: `CRE.recalibrate`)

## Examples

```bash
/gro:learning-profile                              # all characters
/gro:learning-profile --character character-c            # Nhân vật C only
/gro:learning-profile --json                       # machine-readable
```

## See Also

- `gro:competency-map` — skill levels (what is learned)
- `gro:career-path` — career context (why learning matters)
- `gro:validate` — cross-check learning data consistency
- `docs/rules/15-gro-framework.md` — GRO domain rules
