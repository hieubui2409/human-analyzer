---
name: gro:compare
description: "GRO framework cross-character comparison — gather growth data from all characters for side-by-side career, competency, learning, and mentoring comparison. Triggers: 'gro compare', 'compare careers', 'compare growth', 'cross-character comparison'."
argument-hint: "[--dimension <career|competency|learning|mentoring|all>] [--json]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "gro-framework"
  position: "comparison"
  dependencies: []
---

# gro:compare — Cross-Character Growth Comparison (GRO Framework)

Side-by-side comparison of career, competency, learning, and mentoring data across all 3 characters.

## Default (No Arguments)

`--dimension all` — compare all dimensions.

## Flags

| Flag                 | Purpose                                                               |
| -------------------- | --------------------------------------------------------------------- |
| `--dimension <name>` | Compare specific dimension (career/competency/learning/mentoring/all) |
| `--json`             | Output as JSON                                                        |

## Workflow

### Step 1: Gather Comparison Data

1. Run `scripts/gather-cross-character-growth-comparison-data.py`
2. Reads all 4 growth files for each character
3. Extracts comparable dimensions: career stage, skill levels, learning style, network type

### Step 2: LLM Analysis (heuristic)

LLM generates comparison insights:

- Career stage differential (Professional vs Student vs Freshman)
- Skill distribution patterns
- Learning style compatibility
- Mentoring network interconnections

### Step 3: Output

```
## Growth Comparison: All Characters

### Career Stage
| Character | Stage | Age | Key Focus |
|-----------|-------|-----|-----------|

### Competency Comparison
| Skill Area | Nhân vật A | Nhân vật B | Nhân vật C |
|-----------|------|-----|-------|

### Learning Style
| Character | Kolb Style | Strengths | Gaps |
|-----------|-----------|-----------|------|

### Mentoring Network
| Character | Network Type | Primary Mentor | Diversity |
|-----------|-------------|----------------|-----------|
```

## Scripts

| Script                                                     | Purpose                                   |
| ---------------------------------------------------------- | ----------------------------------------- |
| `scripts/gather-cross-character-growth-comparison-data.py` | Collect growth data across all characters |

## Safety

- READ-ONLY — never modifies profile or material files
- Domain boundary: reads `docs/profiles/` only
- LLM does all heuristic judgment; script does deterministic gathering only

## Events

- Emits no events (read-only comparison tool)

## Examples

```bash
/gro:compare                                      # all dimensions
/gro:compare --dimension career                   # career stage only
/gro:compare --dimension competency --json        # skill comparison, JSON
```

## See Also

- `psy:profile-compare` — PSY-domain character comparison (complementary)
- `gro:validate` — consistency validation before comparison
- `docs/rules/15-gro-framework.md` — GRO domain rules
