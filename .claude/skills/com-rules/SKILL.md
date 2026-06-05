---
name: com:rules
description: "Validate changed files against docs/rules/*.md. Routes .md files to the right validation skill based on file type. Use after making changes, before commit, or for rule compliance checks. Triggers: 'check rules', 'validate', 'rule compliance', 'validate changes'."
argument-hint: "[--validate|--list|--check <rule#>] [--scope uncommitted|all|path]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "quality"
  position: "review"
  dependencies: ["orc:classify"]
---

# Project Rules Validation

Validate changed files against `docs/rules/*.md` (16 rules). Thin orchestrator — routes to specialized skills, does not duplicate their logic.

## Default (No Arguments)

Validate uncommitted changes against matching rules.

## Flags

| Flag              | Purpose                                            |
| ----------------- | -------------------------------------------------- |
| `--validate`      | Validate changed files against rules               |
| `--list`          | List all 16 rules with status                      |
| `--check <rule#>` | Validate against specific rule (e.g. `--check 01`) |
| `--scope <scope>` | uncommitted (default), all, or path                |

## Rule → Validation Routing

| Rule # | Rule Name                  | Validation Method                                          |
| ------ | -------------------------- | ---------------------------------------------------------- |
| 01     | profile-structure          | Check file exists per schema; frontmatter fields present   |
| 02     | clinical-reference-usage   | Delegate → `psy:ref-audit`                                 |
| 03     | content-creation-pipeline  | Check assets/ structure, post.txt exists                   |
| 04     | materials-ingestion        | Check MAT frontmatter (evidence_tier, craap_score, status) |
| 05     | wave-pipeline              | Check wave markers in profile frontmatter                  |
| 06     | crisis-protocol            | Flag if darkness/traumas.md changed without review         |
| 07     | narrative-twist-protocol   | Flag if strikethrough markers present                      |
| 08     | cross-validation           | Delegate → `psy:crossref`                                  |
| 09     | confidentiality-protocol   | Delegate → `cre:privacy-guard`                             |
| 10     | reference-library-standard | Check reference file schema (frontmatter fields)           |
| 11     | mat-pipeline               | Check material processing_status field                     |
| 12     | orc-orchestration          | Check event references valid                               |
| 13     | orc-workflow               | N/A (process rule, not file rule)                          |
| 14     | cre-evidence-and-events    | Check evidence tier compliance in assets/                  |
| 15     | gro-framework              | Delegate → `gro:validate` (growth/ data + date alignment)  |
| 16     | knowledge-graph            | Delegate → `orc:graph --validate` (graph schema/integrity) |

## Validation Workflow

### Step 1: Determine changed files

```bash
# Default: uncommitted
git diff --name-only && git diff --name-only --cached

# --scope all: all tracked .md files
git ls-files '*.md'

# --scope <path>: specific directory
git ls-files '<path>/*.md'
```

### Step 2: Classify files → rules

| File path pattern                  | Applicable rules               |
| ---------------------------------- | ------------------------------ |
| `docs/profiles/*/identity/*`       | 01, 09                         |
| `docs/profiles/*/psychology/*`     | 01, 02, 05, 08                 |
| `docs/profiles/*/relationships/*`  | 01, 08                         |
| `docs/profiles/*/timeline/*`       | 01                             |
| `docs/profiles/*/darkness/*`       | 01, 06, 09                     |
| `docs/profiles/*/light/*`          | 01                             |
| `docs/profiles/*/evidence/*`       | 01, 09                         |
| `docs/profiles/*/growth/*`         | 01, 15                         |
| `docs/profiles/*/INDEX.md`         | 01                             |
| `docs/profiles/*/CURRENT-STATE.md` | 01                             |
| `docs/materials/*`                 | 04, 11                         |
| `docs/references/*`                | 02, 10                         |
| `docs/graph/*`                     | 08, 16                         |
| `docs/rules/*`                     | (meta — rule files themselves) |
| `assets/*`                         | 03, 09, 14                     |

### Step 3: Run validations

For each matched rule:

**Inline checks** (rules 01, 03, 04, 05, 06, 07, 10, 11, 12):

- Read file, check frontmatter fields exist per rule spec
- Report missing/invalid fields

**Delegate to skill** (rules 02, 08, 09, 14):

- Rule 02 → `psy:ref-audit --file <path>`
- Rule 08 → `psy:crossref` (if cross-character files changed)
- Rule 09 → `cre:privacy-guard --file <path>`
- Rule 14 → Check evidence tier in content vs source material tier

### Step 4: Report

```
## Rule Compliance Report

| Rule | Status | Files Checked | Issues |
|------|--------|---------------|--------|
| 01   | ✅/❌  | 3             | ...    |
| ...  | ...    | ...           | ...    |

### Issues Found
1. [Rule 01] docs/profiles/hoa/INDEX.md — missing `confidence` in frontmatter
2. [Rule 09] assets/facebook/240518-post/ — real name detected

### Recommendations
- Fix issue #1: add `confidence: medium` to frontmatter
- Fix issue #2: replace name with alias
```

## Safety

- Read-only — reports violations, does NOT auto-fix
- Delegated skills also run in read-only/report mode
- Skip rules 06, 13 for automated validation (process rules, not file rules)

## See Also

- `orc:classify` — pre-task risk assessment (use BEFORE changes)
- `com:rules` — post-change validation (use AFTER changes)
- `psy:crossref`, `psy:ref-audit`, `cre:privacy-guard` — specialized validators
- `com:git` — commit after validation passes
