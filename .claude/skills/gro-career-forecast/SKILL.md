---
name: gro:career-forecast
description: "GRO framework career projection — gather current career data for LLM-powered trajectory forecasting. All output marked [FORECAST — NOT FACTUAL]. Triggers: 'career forecast', 'career projection', 'predict career', 'future career'."
argument-hint: "[--character <name>|--all] [--json] [--horizon <years>]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "gro-framework"
  position: "forecast"
  dependencies: []
---

# gro:career-forecast — Career Trajectory Projection (GRO Framework)

Generate LLM-powered career trajectory projections. All output clearly marked as speculative.

**[FORECAST — NOT FACTUAL]**: All projections are speculative analysis, not verified facts.

## Default (No Arguments)

`--all` — gather forecast data for all three characters.

## Flags

| Flag                 | Purpose                           |
| -------------------- | --------------------------------- |
| `--character <name>` | Forecast one character only       |
| `--all`              | Forecast all characters (default) |
| `--json`             | Output as JSON                    |
| `--horizon <years>`  | Projection horizon (default: 3)   |

## Data Sources Read (per character)

1. `growth/career-path.md` — current career stage and trajectory
2. `growth/competencies.md` — current skill levels
3. `growth/learning-profile.md` — learning patterns
4. `identity/core.md` §Career / §Education — factual career history

## Workflow

### Step 1: Gather Current State

1. Run `scripts/gather-career-forecast-input-data.py`
2. Extracts: current career stage, skill levels, learning style, trajectory direction
3. Compiles forecast input package for LLM

### Step 2: LLM Projection (heuristic)

LLM generates projections based on:

- Career stage progression (Super's model)
- Skill growth trajectory (Dreyfus progression rates)
- Life stage context (age, education status)
- Known risk factors and protective factors

### Step 3: Output

```
## Career Forecast: {character} [FORECAST — NOT FACTUAL]

**Current Stage:** {stage}
**Horizon:** {N} years
**Confidence:** Low (speculative projection)

### Projected Trajectory
| Year | Projected Stage | Key Milestones | Confidence |
|------|----------------|----------------|------------|

### Assumptions
- {assumption 1}

### Risk Scenarios
- {scenario 1}

⚠️ This is a speculative projection, not a verified fact.
```

## Scripts

| Script                                         | Purpose                                  |
| ---------------------------------------------- | ---------------------------------------- |
| `scripts/gather-career-forecast-input-data.py` | Compile current state for LLM projection |

## Safety

- READ-ONLY — never modifies profile or material files
- Domain boundary: reads `docs/profiles/` only
- All output MUST include [FORECAST — NOT FACTUAL] markers
- LLM does all heuristic judgment; script does deterministic gathering only

## Events

- Emits `GRO.forecast` (log only — no downstream cascade)

## Examples

```bash
/gro:career-forecast                              # all characters, 3-year horizon
/gro:career-forecast --character character-a --horizon 5 # Nhân vật A, 5-year projection
/gro:career-forecast --json                       # machine-readable
```

## See Also

- `gro:career-path` — current career data (input for forecast)
- `gro:competency-map` — current skill levels (input for forecast)
- `psy:hypothesis` — PSY-domain behavioral prediction (complementary)
- `docs/rules/15-gro-framework.md` — GRO domain rules
