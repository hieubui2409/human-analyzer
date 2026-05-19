---
name: psy:timeline-sync
description: "Timeline date validation and consistency check — extracts dates from timeline files across characters, cross-compares shared events, and reports mismatches with suggested fixes. Triggers: 'sync timelines', 'timeline consistency', 'date mismatch', 'check dates', 'timeline audit'."
argument-hint: "[--character <name>] [--all] [--json]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "psy-framework"
  position: "validation"
  dependencies: []
---

# psy:timeline-sync — Timeline Date Validation

Extract and cross-compare dates from character timeline files. Detect shared-event mismatches and suggest fixes.

## Default (No Arguments)

`--all` — check all characters.

## Flags

| Flag                 | Purpose                              |
| -------------------- | ------------------------------------ |
| `--character <name>` | Check single character timeline      |
| `--all`              | Cross-check all characters (default) |
| `--json`             | Output as JSON                       |

## Timeline Files Checked

For each character:

- `docs/profiles/{character}/timeline/overview.md`
- `docs/profiles/{character}/timeline/state-timeline.md`
- `docs/profiles/{character}/milestones.md`

## Shared Events (Known Cross-Character)

| Event                      | Characters Involved | Expected Date  |
| -------------------------- | ------------------- | -------------- |
| Kết nghĩa (sworn brothers) | Nhân vật A + Nhân vật B          | September 2025 |
| Scholarship X F15 interview    | Nhân vật A + Nhân vật C        | 2024-2025      |
| Gambling crisis            | Nhân vật A + Nhân vật B          | Oct 2025       |
| First meeting Nhân vật A-Nhân vật B     | Nhân vật A + Nhân vật B          | July 2025      |

## Workflow

### Step 1: Extract Dates

1. Run `scripts/check-and-suggest-timeline-fixes.py`
2. For each character: parse timeline files, extract (event, date) pairs
3. Identify events mentioning other characters by name

### Step 2: Cross-Compare

For each shared event:

1. Find matching entries across profiles
2. Compare dates (exact or approximate month match)
3. Classify: match / mismatch / missing

### Step 3: Output

```
## Timeline Sync Report

**Date:** {YYYY-MM-DD}
**Characters:** Nhân vật A, Nhân vật B, Nhân vật C

### Shared Event Analysis

| Event                  | Nhân vật A says | Nhân vật B says  | Nhân vật C says | Status    |
|------------------------|-----------|-----------|------------|-----------|
| Kết nghĩa              | Sep 2025  | Sep 2025  | N/A        | ✓ MATCH   |
| Gambling crisis        | Oct 2025  | Sep 2025  | N/A        | ✗ MISMATCH|
...

### Mismatches Found

#### MISMATCH: Gambling Crisis Date
- **Nhân vật A** `timeline/overview.md:L42` → "Oct 2025"
- **Nhân vật B** `timeline/overview.md:L18` → "Sep 2025"
- **Suggested fix:** Verify against materials in docs/materials/ and align to correct date
- **Priority:** HIGH

### Per-Character Solo Issues

| Character | File | Issue | Line |
|-----------|------|-------|------|

### Summary

| Status | Count |
|--------|-------|
| MATCH  | N     |
| MISMATCH | M   |
| MISSING | K    |
```

## Scripts

| Script                                        | Purpose                                         |
| --------------------------------------------- | ----------------------------------------------- |
| `scripts/check-and-suggest-timeline-fixes.py` | Extract dates, cross-compare, report mismatches |

## Safety

- READ-ONLY — never modifies profile files
- Domain boundary: `docs/profiles/` (timeline files only)

## Examples

```bash
/psy:timeline-sync                              # check all characters
/psy:timeline-sync --character hieu             # Nhân vật A's timeline only
/psy:timeline-sync --all                        # explicit all mode
/psy:timeline-sync --json                       # machine-readable
```

## See Also

- `psy:crossref` — full cross-character validation (superset of timeline check)
- `psy:propagate` — cascade changes after fixing timeline
- `psy:health-check` — profile completeness (includes timeline files)
