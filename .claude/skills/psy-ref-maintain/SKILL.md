---
name: psy:ref-maintain
description: "Reference library health audit — scan docs/references/ for unused theories, count citations across all profiles, flag zero-citation orphans, and surface coverage gaps. Triggers: 'clean references', 'unused theories', 'reference maintenance', 'orphan theories', 'reference audit'."
argument-hint: "[--orphans-only] [--gaps-only] [--json]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "psy-framework"
  position: "maintenance"
  dependencies: []
---

# psy:ref-maintain — Reference Library Health Audit

Audit the clinical reference library in `docs/references/`. Find orphaned theories (zero citations), coverage gaps, and cross-link health across all profiles.

## Default (No Arguments)

Full health audit of all 62 theories.

## Flags

| Flag             | Purpose                                        |
| ---------------- | ---------------------------------------------- |
| `--orphans-only` | Show only theories with zero profile citations |
| `--gaps-only`    | Show only profiles missing key theory coverage |
| `--json`         | Output as JSON                                 |

## What Gets Audited

### 1. Citation Count

For each theory file in `docs/references/`:

- Count how many times the theory name appears in `docs/profiles/` files
- Flag zero-citation orphans (no profile references this theory)

### 2. Index Consistency

- Is the theory listed in `docs/references/INDEX.md`?
- Does the index entry link to the file?

### 3. Schema Compliance

Each reference file should have: theory name, category, core concepts, clinical application, profile implications, references/sources.

### 4. Profile Coverage Gaps

Check if all 3 characters have at least one reference in key categories:

- Defense mechanisms theory
- Attachment theory
- Trauma theory
- Big Five / personality assessment

## Workflow

### Step 1: Scan

1. Run `scripts/audit-reference-library-health.py`
2. List all `.md` files in `docs/references/` (excluding INDEX.md)
3. For each file: extract theory name, count citations across profiles

### Step 2: Classify

| Status        | Condition                    |
| ------------- | ---------------------------- |
| ACTIVE        | 3+ citations across profiles |
| USED          | 1-2 citations                |
| ORPHAN        | 0 citations — not referenced |
| NOT_INDEXED   | Missing from INDEX.md        |
| SCHEMA_BREACH | Missing required sections    |

### Step 3: Output

```
## Reference Library Health Report

**Date:** {YYYY-MM-DD}
**Total theories:** {N}
**Active:** {N} | **Used:** {N} | **Orphans:** {N}

### Orphaned Theories (zero citations)

| Theory File | Category | Status |
|-------------|----------|--------|
| cognitive-distortions.md | CBT | ORPHAN |
...

### Index Gaps

| Theory | File Exists | In INDEX.md |
|--------|-------------|-------------|
| X      | ✓           | ✗           |

### Schema Issues

| Theory | Missing Sections |
|--------|-----------------|

### Profile Coverage Gaps

| Character | Missing Category | Suggested Theory |
|-----------|-----------------|------------------|

### Recommended Actions

1. Archive orphaned theories: {list}
2. Add to INDEX.md: {list}
3. For {character}: add {category} reference — suggest {theory}

### Summary

| Health Metric | Score |
|---------------|-------|
| Citation coverage | {N}% |
| Index completeness | {N}% |
| Schema compliance | {N}% |
| **Overall** | **{N}%** |
```

## Scripts

| Script                                      | Purpose                                         |
| ------------------------------------------- | ----------------------------------------------- |
| `scripts/audit-reference-library-health.py` | Scan references, count citations, report health |

## Safety

- READ-ONLY — never modifies reference or profile files
- Only writes report to plans/reports/ if --report flag used

## Examples

```bash
/psy:ref-maintain                          # full audit
/psy:ref-maintain --orphans-only           # show unused theories
/psy:ref-maintain --gaps-only              # show missing coverage
/psy:ref-maintain --json                   # machine-readable
```

## See Also

- `psy:ref-audit` — accuracy check (profiles → references)
- `psy:ref-scan` — coverage mapping (references → profiles)
- `psy:ref-create` — add new reference to library
- `docs/references/INDEX.md` — master theory index
