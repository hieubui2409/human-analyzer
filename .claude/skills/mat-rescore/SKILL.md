---
name: mat:rescore
description: "MAT framework CRAAP re-scoring — identify materials with missing, incomplete, or stale CRAAP scores and flag them for re-evaluation. Triggers: 'rescore materials', 're-evaluate CRAAP', 'update evidence tiers', 'craap check', 'fix scores'."
argument-hint: "[--character <name>] [--missing-only] [--raw-only] [--json]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "mat-framework"
  position: "pipeline-maintenance"
  dependencies: []
---

# mat:rescore — CRAAP Re-scoring Identifier (MAT Framework)

Identify materials with missing, incomplete, or outdated CRAAP scores across `docs/materials/`.

## MAT Pipeline Position

```
Stage 1 → Stage 2 (CRAAP scoring) → Stage 3 → ...
                    ↑
              mat:rescore (audit)
```

mat:rescore audits Stage 2 quality — finds materials that need CRAAP re-evaluation.

## Default (No Arguments)

Scan all characters and report materials needing rescore.

## Flags

| Flag                 | Purpose                                     |
| -------------------- | ------------------------------------------- |
| `--character <name>` | Limit to one character                      |
| `--missing-only`     | Only show files with no craap_score at all  |
| `--raw-only`         | Only show files with processing_status: raw |
| `--json`             | Output as JSON                              |

## Rescore Triggers

A material needs rescoring if ANY of the following is true:

| Condition                       | Reason                         |
| ------------------------------- | ------------------------------ |
| No `craap_score` in frontmatter | Never scored                   |
| Any score field is null/missing | Partial scoring                |
| `total` doesn't match sum       | Calculation error              |
| `processing_status` is "raw"    | Never processed past ingestion |
| No frontmatter at all           | Missing MAT compliance         |

## Workflow

### Step 1: Scan

1. Run `scripts/identify-materials-needing-rescore.py`
2. For each `.md` file in `docs/materials/{character}/`
3. Parse YAML frontmatter
4. Evaluate against rescore triggers

### Step 2: Output

```
## Rescore Audit Report

**Date:** {YYYY-MM-DD}
**Scope:** {characters}

### Materials Needing Rescore

| File | Character | Reason | Current Status | Current Score |
|------|-----------|--------|----------------|---------------|
| transcript-xx.md | hieu | missing craap_score | raw | — |
| letter-xx.md | hoa | partial fields (authority=null) | extracted | 12/25 |
...

**Total:** N materials need rescore

### Summary by Character

| Character | Total | Needs Rescore | % Clean |
|-----------|-------|---------------|---------|

### Next Step
→ For each flagged file, run `mat:loader --ingest <file>` to re-run Stage 2
```

## Scripts

| Script                                          | Purpose                               |
| ----------------------------------------------- | ------------------------------------- |
| `scripts/identify-materials-needing-rescore.py` | Scan + flag materials with CRAAP gaps |

## Safety

- READ-ONLY — never modifies files
- Domain boundary: `docs/materials/` only

## Examples

```bash
/mat:rescore                             # audit all characters
/mat:rescore --character hieu            # Nhân vật A only
/mat:rescore --missing-only              # only files with no CRAAP at all
/mat:rescore --raw-only                  # only raw-status files
/mat:rescore --json                      # machine-readable output
```

## See Also

- `mat:loader --ingest` — re-run Stage 1-2 for flagged files
- `mat:loader --status` — pipeline status overview
- `.claude/schemas/material-schema.yaml` — CRAAP schema
