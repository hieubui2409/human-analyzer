---
name: gro:mentoring-track
description: "GRO framework mentoring relationship documentation — gather mentoring data from growth/mentoring-map.md, relationships/ files, and materials for LLM insight extraction using Kram's model. Triggers: 'mentoring track', 'mentor analysis', 'mentoring relationship', 'kram'."
argument-hint: "[--character <name>|--all] [--json]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "gro-framework"
  position: "analysis"
  dependencies: []
---

# gro:mentoring-track — Mentoring Relationship Documentation (GRO Framework)

Document and analyze mentoring relationships using Kram's Developmental Networks framework.

## Default (No Arguments)

`--all` — gather mentoring data for all three characters.

## Flags

| Flag                 | Purpose                          |
| -------------------- | -------------------------------- |
| `--character <name>` | Analyze one character only       |
| `--all`              | Analyze all characters (default) |
| `--json`             | Output as JSON                   |

## Data Sources Read (per character)

1. `growth/mentoring-map.md` — primary mentoring data (Kram's model)
2. `relationships/*.md` — cross-relationship files for relationship context
3. `docs/materials/{char}/` — MAT materials mentioning mentoring keywords
4. `identity/core.md` §Family — family mentoring context

## Workflow

### Step 1: Gather Mentoring Data

1. Run `scripts/gather-mentoring-data-from-profile-and-relationships.py`
2. Extracts: mentoring relationships, Kram career/psychosocial functions, network typology
3. Cross-references relationship files for consistency

### Step 2: LLM Analysis (heuristic)

LLM analyzes gathered data for:

- Kram function completeness assessment
- Network diversity/strength evaluation
- Dependency risk identification
- Mentoring dynamic evolution tracking

### Step 3: Output

```
## Mentoring Analysis: {character}

**Network Type:** {Kram typology}
**Primary Mentor:** {name} — {role}

### Mentoring Relationships
| Mentor/Mentee | Career Functions | Psychosocial Functions | Status |
|---------------|-----------------|----------------------|--------|

### Network Assessment
- Diversity: {low/medium/high}
- Strength: {low/medium/high}

### Insights
- {insight 1}
```

## Scripts

| Script                                                            | Purpose                                             |
| ----------------------------------------------------------------- | --------------------------------------------------- |
| `scripts/gather-mentoring-data-from-profile-and-relationships.py` | Extract mentoring data from profile + relationships |

## Safety

- READ-ONLY — never modifies profile or material files
- Domain boundary: reads `docs/profiles/` and `docs/materials/`
- LLM does all heuristic judgment; script does deterministic gathering only

## Events

- Emits `GRO.mentored` after mentoring analysis completes (downstream: `PSY.refresh`)

## Examples

```bash
/gro:mentoring-track                              # all characters
/gro:mentoring-track --character character-b              # Nhân vật B only
/gro:mentoring-track --json                       # machine-readable
```

## See Also

- `gro:career-path` — career trajectory (mentoring supports career development)
- `gro:validate` — cross-check mentoring data consistency
- `psy:crossref` — cross-character relationship validation
- `docs/rules/15-gro-framework.md` — GRO domain rules
