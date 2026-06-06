---
name: gro:validate
description: "GRO framework validation — cross-check growth data consistency across career-path, competencies, learning-profile, and mentoring-map. Detect contradictions, missing cross-references, stale data. Triggers: 'gro validate', 'growth validation', 'growth consistency', 'gro check'."
argument-hint: "[--character <name>|--all] [--json] [--fix]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "gro-framework"
  position: "validation"
  dependencies: []
---

# gro:validate — Growth Data Consistency Validation (GRO Framework)

Cross-check growth data consistency across all 4 GRO profile files + identity/core.md.

## Default (No Arguments)

`--all` — validate all three characters.

## Flags

| Flag                 | Purpose                                          |
| -------------------- | ------------------------------------------------ |
| `--character <name>` | Validate one character only                      |
| `--all`              | Validate all characters (default)                |
| `--json`             | Output as JSON                                   |
| `--fix`              | LLM suggests fixes for detected issues           |
| `--stale-days N`     | Days threshold for staleness warning (default 90)|

## Validation Dimensions

The script (`validate-growth-data-consistency.py`) implements these deterministic checks:

### 1. Frontmatter Consistency

- All 4 growth files exist and have required frontmatter fields
- `domain: growth`, `type: data`, correct `character:` slug
- `updated_by: gro:{skill}` format
- `last_updated` not stale (configurable via `--stale-days`, default 90 days)

### 2. Cross-File Consistency (heuristic)

- Career-path.md and competencies.md cross-reference each other (keyword presence check)
- Mentoring-map.md references known relationship files
- Note: fine-grained skill-existence checks (e.g., each career-path skill in competencies)
  are **not implemented** — those require LLM judgment

### 3. GRO ↔ PSY Boundary

- Growth files contain no PSY-domain terms (defense mechanisms, attachment, trauma, etc.)
- Cross-references to PSY files are read-only citations, not duplicated content

### 4. Evidence Grounding

- Presence of evidence markers: [Source:], [UNVERIFIED], [LIMITED DATA], [PRIVATE]
- Note: material reference link validation is **not implemented** — script checks markers only

### 5. Life Stage Adaptation

- Not implemented in the script — LLM judgment required for career-stage appropriateness

## Workflow

### Step 1: Deterministic Checks

1. Run `scripts/validate-growth-data-consistency.py`
2. Checks: frontmatter schema, cross-file references, boundary violations, evidence markers, file existence
3. Returns structured findings (pass/warn/fail per check)

### Step 2: LLM Analysis (with --fix)

LLM reviews findings and suggests specific corrections for failures.

### Step 3: Output

```
## GRO Validation Report

**Date:** {YYYY-MM-DD}

### Summary
| Character | Pass | Warn | Fail | Score |
|-----------|------|------|------|-------|

### {Character} — Findings
| # | Check | Status | Detail |
|---|-------|--------|--------|
| 1 | Frontmatter schema | PASS | All 4 files valid |
| 2 | Cross-file skills | WARN | 2 skills in career-path.md missing from competencies.md |
| 3 | PSY boundary | PASS | No boundary violations |

### Fix Suggestions (--fix only)
1. {suggestion}
```

## Scripts

| Script                                        | Purpose                                    |
| --------------------------------------------- | ------------------------------------------ |
| `scripts/validate-growth-data-consistency.py` | Deterministic cross-file validation checks |

## Safety

- READ-ONLY by default — never modifies files
- With `--fix`: LLM suggests changes, does not apply automatically
- Domain boundary: reads `docs/profiles/` and `docs/materials/`

## Events

- Emits no events (read-only audit tool)

## Examples

```bash
/gro:validate                              # all characters
/gro:validate --character character-a             # Nhân vật A only
/gro:validate --all --json                 # machine-readable
/gro:validate --fix                        # include fix suggestions
/gro:validate --stale-days 180             # warn on files >180 days old
```

## Schema Validation (C7)

Growth-data consistency checks are complementary to the **Draft-7 frontmatter contract**
for `growth/competencies.md` + `growth/career-path.md` (domain=growth). Run the shared
validator for machine-enforceable frontmatter checks (additive — keeps existing consistency
scoring); Dreyfus 1-7 / Super-stage judgment stays heuristic in this skill:

```bash
PY=$HOME/.claude/skills/.venv/bin/python3
$PY .claude/scripts/validate-all-against-schemas.py   # whole corpus, CI exit code
```

`platform_lib/schema_validator.py` is the single Draft-7 engine (shared with `psy:health-check`,
`orc:audit`, KG-06; growth-competency.schema.json + growth-career-path.schema.json).

## See Also

- `psy:crossref` — cross-character PSY validation
- `psy:health-check` — profile completeness scoring
- `mat:indexer` — material coverage validation
- `docs/rules/15-gro-framework.md` — GRO domain rules
- `validate-all-against-schemas.py` — C7 Draft-7 corpus gate (shared engine)
