---
name: psy:health-check
description: "Profile completeness scoring — check all 25 expected profile files per character, score 0-100 per file, aggregate overall health score, and surface gaps. Triggers: 'profile health', 'completeness check', 'what is missing', 'profile gaps', 'health score'."
argument-hint: "[--character <name>|--all] [--json] [--gaps-only]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "psy-framework"
  position: "audit"
  dependencies: []
---

# psy:health-check — Profile Completeness Scoring

Score the completeness of character profiles against the 25-file universal nested structure. Surface missing files and empty sections.

## Default (No Arguments)

`--all` — score all three characters.

## Flags

| Flag                 | Purpose                         |
| -------------------- | ------------------------------- |
| `--character <name>` | Score one character only        |
| `--all`              | Score all characters (default)  |
| `--gaps-only`        | Show only files with score < 80 |
| `--json`             | Output as JSON                  |

## Expected Profile Files (25)

Per `paths.PROFILE_FILES`:

```
INDEX.md, CURRENT-STATE.md, milestones.md
identity/core.md, identity/writing-voice.md, identity/achievements.md, identity/media-coverage.md
psychology/core-wounds.md, psychology/defense-mechanisms.md, psychology/attachment-style.md
psychology/growth-edges.md, psychology/formulation.md, psychology/diagnostics.md
psychology/cultural-formulation.md, psychology/archetype.md
relationships/family.md
timeline/overview.md, timeline/state-timeline.md
darkness/traumas.md
light/strengths-hope.md
evidence/conversations.md
growth/career-path.md, growth/competencies.md, growth/learning-profile.md, growth/mentoring-map.md
```

> Cross-character relationship files (e.g. `relationships/character-b.md`) are scored dynamically via `list_relationship_files()` and added to the per-character count.

## Scoring Rubric (per file)

| Condition                     | Score |
| ----------------------------- | ----- |
| File missing                  | 0     |
| File exists but empty         | 10    |
| File < 50 lines               | 40    |
| File 50-100 lines             | 70    |
| File 100+ lines               | 90    |
| File has expected H2 sections | +10   |
| Max possible                  | 100   |

## Workflow

### Step 1: Check Files

1. Run `scripts/score-profile-completeness.py`
2. For each character: iterate 25 expected file paths
3. For each file: compute score per rubric

### Step 2: Aggregate

- Per-file score
- Category average (identity, psychology, relationships, etc.)
- Overall 0-100

### Step 3: Output

```
## Profile Health Report

**Date:** {YYYY-MM-DD}

### Overall Health

| Character | Score | Files Present | Missing | Grade |
|-----------|-------|---------------|---------|-------|
| Nhân vật A      | 87/100 | 24/25        | 1       | B+    |
| Nhân vật B       | 72/100 | 22/25        | 3       | C+    |
| Nhân vật C     | 65/100 | 20/25        | 5       | C     |

### Nhân vật A — Completeness Matrix

| File                           | Score | Lines | Status     |
|-------------------------------|-------|-------|------------|
| INDEX.md                      | 100   | 145   | Complete   |
| psychology/formulation.md     | 40    | 35    | Thin       |
| identity/media-coverage.md    | 0     | —     | MISSING    |
...

### Gaps Summary

Priority gaps to fill:
1. {character} — {file}: MISSING — {category impact}
2. {character} — {file}: Thin (35 lines) — needs expansion

### Next Step
→ Use `psy:wave` to systematically fill gaps
```

## Scripts

| Script                                  | Purpose                                      |
| --------------------------------------- | -------------------------------------------- |
| `scripts/score-profile-completeness.py` | Check 25 files per character, compute scores |

## Safety

- READ-ONLY — never modifies profile files
- Domain boundary: `docs/profiles/` only

## Examples

```bash
/psy:health-check                              # all characters
/psy:health-check --character hieu             # Nhân vật A only
/psy:health-check --all --gaps-only            # show only weak areas
/psy:health-check --json                       # machine-readable
```

## See Also

- `psy:wave` — 3-wave profiling to fill completeness gaps
- `orc:bootstrap --full` — load full context (uses health to prioritize)
- `psy:crossref` — consistency validation (run after gaps are filled)
