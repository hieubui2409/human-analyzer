---
name: mat:archive
description: "MAT framework material archival — filter and archive processed materials by character, date, tier, or status. Marks processing_status as 'archived' for matched files. Triggers: 'archive material', 'remove evidence', 'clean up materials', 'archive old sources'."
argument-hint: "[--character <name>] [--before-date YYYY-MM-DD] [--tier T1-T5] [--status <status>] [--dry-run]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "mat-framework"
  position: "pipeline-maintenance"
  dependencies: []
---

# mat:archive — Material Archival (MAT Framework)

Filter and archive processed source materials in `docs/materials/` by applying `processing_status: archived` to matched files.

## MAT Pipeline Position

```
Stage 1 → Stage 2 → Stage 3 → Stage 4 → [Archive] ← mat:archive
```

mat:archive is a maintenance operation — runs outside the main pipeline on already-processed materials.

## Default (No Arguments)

`--dry-run` mode on all materials — show what would be archived without modifying files.

## Flags

| Flag                       | Purpose                                              |
| -------------------------- | ---------------------------------------------------- |
| `--character <name>`       | Limit scope to one character                         |
| `--before-date YYYY-MM-DD` | Match files with captured_date before this date      |
| `--tier <T1-T5>`           | Match files with this evidence tier                  |
| `--status <status>`        | Match files with this processing_status              |
| `--dry-run`                | Preview matches without modifying (default behavior) |

## Workflow

### Step 1: Scan

1. Run `scripts/archive-materials-by-filter.py` with given filters
2. Scan `docs/materials/{character}/` for `.md` files with YAML frontmatter
3. Apply all provided filters (AND logic)

### Step 2: Report Preview

Output a table of matched files before any write:

```
## Archive Preview (--dry-run)

| File                          | Character | Tier | Status    | Date Created |
|-------------------------------|-----------|------|-----------|--------------|
| transcript-2024-01-xx.md      | hieu      | T3   | validated | 2024-01-10   |
...

Total: N files would be archived
```

### Step 3: Archive (if not --dry-run)

For each matched file:

1. Read YAML frontmatter
2. Set `processing_status: archived`
3. Update `last_updated` to today's date
4. Write back to file

### Output

```
## Archive Report

**Filters applied:** character=hieu, before-date=2025-01-01, tier=T3
**Files archived:** N
**Files skipped:** M (already archived)

| File | Tier | Previous Status | Action |
|------|------|-----------------|--------|
...
```

## Scripts

| Script                                   | Purpose                                         |
| ---------------------------------------- | ----------------------------------------------- |
| `scripts/archive-materials-by-filter.py` | Scan + filter + archive with frontmatter update |

## Safety

- READ-ONLY by default (--dry-run behavior without explicit action flag)
- WRITE: only updates `processing_status` and `last_updated` in frontmatter
- Never deletes files — only marks as archived
- Domain boundary: `docs/materials/` only
- Never modifies profile files or reference files

## Examples

```bash
/mat:archive                                          # dry-run, show all archivable
/mat:archive --character hieu --dry-run               # preview Nhân vật A's materials
/mat:archive --before-date 2024-12-31 --status validated  # archive old validated
/mat:archive --tier T5 --status raw                   # archive low-tier raw files
```

## See Also

- `mat:loader` — Stage 1-2: ingestion and classification
- `mat:indexer` — Stage 3-4: contradiction detection
- `mat:rescore` — re-evaluate CRAAP scores before archiving
