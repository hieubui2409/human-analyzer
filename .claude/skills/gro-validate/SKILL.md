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

| Flag                 | Purpose                                |
| -------------------- | -------------------------------------- |
| `--character <name>` | Validate one character only            |
| `--all`              | Validate all characters (default)      |
| `--json`             | Output as JSON                         |
| `--fix`              | LLM suggests fixes for detected issues |

## Validation Dimensions

### 1. Frontmatter Consistency

- All 4 growth files have required frontmatter fields
- `domain: growth`, `type: data`, correct `character:` slug
- `updated_by: gro:{skill}` format
- `last_updated` not stale (>90 days warning)

### 2. Cross-File Consistency

- Career stage in career-path.md matches competency context in competencies.md
- Mentoring relationships in mentoring-map.md align with relationships/ files
- Learning style in learning-profile.md consistent with competency acquisition evidence
- Skills mentioned in career-path.md exist in competencies.md

### 3. GRO ↔ PSY Boundary

- Growth files contain factual data only (no psychological interpretations)
- Cross-references to PSY files are read-only citations, not duplicated content
- No `defense mechanism`, `attachment`, `trauma` claims in GRO files

### 4. Evidence Grounding

- Claims marked with evidence tier or [UNVERIFIED]
- [LIMITED DATA] markers present where data is thin
- Material references point to existing files

### 5. Life Stage Adaptation

- Career-path.md content appropriate for character's career stage
- Student characters don't have professional skill matrices
- Professional characters have full career trajectories

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
/gro:validate --character hieu             # Nhân vật A only
/gro:validate --all --json                 # machine-readable
/gro:validate --fix                        # include fix suggestions
```

## See Also

- `psy:crossref` — cross-character PSY validation
- `psy:health-check` — profile completeness scoring
- `mat:indexer` — material coverage validation
- `docs/rules/15-gro-framework.md` — GRO domain rules
