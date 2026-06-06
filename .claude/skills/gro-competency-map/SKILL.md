---
name: gro:competency-map
description: "GRO framework competency inventory — gather skill data from growth/competencies.md, identity/core.md, and materials for LLM assessment using Dreyfus 7-level model. Triggers: 'competency map', 'skill assessment', 'skill inventory', 'dreyfus'."
argument-hint: "[--character <name>|--all] [--json] [--gaps-only]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "gro-framework"
  position: "analysis"
  dependencies: []
---

# gro:competency-map — Skill Inventory & Assessment (GRO Framework)

Inventory and assess skills using Dreyfus 7-level model + SFIA hybrid framework.

## Default (No Arguments)

`--all` — gather competency data for all three characters.

## Flags

| Flag                 | Purpose                                               |
| -------------------- | ----------------------------------------------------- |
| `--character <name>` | Assess one character only                             |
| `--all`              | Assess all characters (default)                       |
| `--gaps-only`        | Show only skills rated Novice-Advanced Beginner (1-2) |
| `--json`             | Output as JSON                                        |

## Data Sources Read (per character)

1. `growth/competencies.md` — primary skill inventory (Dreyfus levels)
2. `identity/core.md` §Education / §Career — education and career context
3. `identity/achievements.md` — awards/certifications as skill evidence
4. `docs/materials/{char}/` — MAT materials mentioning skill keywords

## Dreyfus 7-Level Scale

| Level | Name              | Description                        |
| ----- | ----------------- | ---------------------------------- |
| 1     | Novice            | Rule-following, no context         |
| 2     | Advanced Beginner | Situational awareness emerging     |
| 3     | Competent         | Goal-oriented, deliberate planning |
| 4     | Proficient        | Holistic recognition, intuition    |
| 5     | Expert            | Absorbed, effortless, innovative   |
| 6     | Master            | Redefines domain conventions       |
| 7     | Practical Wisdom  | Transcendent, universal principles |

## Workflow

### Step 1: Gather Competency Data

1. Run `scripts/gather-competency-data-from-profile-and-materials.py`
2. Extracts: skill names, Dreyfus levels, evidence, categories (technical/soft/domain)
3. Cross-references achievements for validation

### Step 2: LLM Analysis (heuristic)

LLM analyzes gathered data for:

- Skill distribution assessment
- Strengths vs gaps identification
- Career-stage appropriateness
- Development priority recommendations

### Step 3: Output

```
## Competency Map: {character}

**Total Skills Assessed:** {N}
**Average Level:** {avg}/7

### Skill Matrix
| Category | Skill | Dreyfus Level | Evidence | Confidence |
|----------|-------|---------------|----------|------------|

### Strengths (Level 4+)
- {skill}: Level {N} — {evidence}

### Gaps (Level 1-2)
- {skill}: Level {N} — {recommendation}
```

## Scripts

| Script                                                         | Purpose                               |
| -------------------------------------------------------------- | ------------------------------------- |
| `scripts/gather-competency-data-from-profile-and-materials.py` | Extract skill data from profile + MAT |

## Safety

- READ-ONLY — never modifies profile or material files
- Domain boundary: reads `docs/profiles/` and `docs/materials/`
- LLM does all heuristic judgment; script does deterministic gathering only

## Events

- Emits `GRO.assessed` after competency assessment completes

## Examples

```bash
/gro:competency-map                              # all characters
/gro:competency-map --character character-b              # Nhân vật B only
/gro:competency-map --all --gaps-only            # weak skills only
/gro:competency-map --json                       # machine-readable
```

## See Also

- `gro:career-path` — career trajectory (provides context for skill levels)
- `gro:learning-profile` — learning style (how skills are acquired)
- `gro:validate` — cross-check competency data consistency
- `docs/rules/15-gro-framework.md` — GRO domain rules
