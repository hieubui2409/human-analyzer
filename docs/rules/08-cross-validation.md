# Cross-Validation Rules

Standards for validating consistency across character profiles and within individual profiles.

## When to Validate

- After Wave 3 of any major profile update
- After integrating new materials that affect multiple characters
- After any cross-character event update (events involving ≥2 characters)
- After PSY.refresh event triggered by MAT integration
- Periodically as maintenance (run `psy:crossref`)

## 4 Consistency Dimensions

Every validation MUST check these dimensions:

| Dimension     | Description                                                  | Example Check                                    |
| ------------- | ------------------------------------------------------------ | ------------------------------------------------ |
| Temporal      | Dates don't conflict, ages match DOB, event order is logical | Nhân vật C can't be 18 in 2024 if born 14/05/2007     |
| Relational    | Character A's view of B matches B's view of A                | If Nhân vật A says "kết nghĩa 09/2025", Nhân vật B must agree |
| Psychological | Defense mechanisms logically stem from documented trauma     | Avoidance must trace to a specific wound         |
| Factual       | Numbers, names, places are identical across all files        | Debt amount "1 tỷ" must be same in all files     |

## Cross-Character Validation

### Relationship Symmetry

For every relationship documented in character A's `relationships/family.md` or `relationships/{character}.md`:

1. Character B's corresponding relationship file MUST have a matching section
2. Key facts MUST match: dates, events, role descriptions
3. Psychological assessments may differ (each character's perspective)

### Shared Timeline Events

Events involving multiple characters MUST appear in ALL participants' `timeline/overview.md`:

- Same date (or both marked `[~approximate]`)
- Same factual description (may differ in perspective/impact)
- Cross-reference comment linking to other character's file

Format:

```markdown
<!-- Cross-ref: docs/profiles/{other}/timeline/overview.md — same event -->
```

### Age/Date Calculation Rules

- Always calculate age from DOB, not from stated age
- Verify: `current_year - birth_year = stated_age` (±1 for birthday not yet passed)
- Date format: `YYYY-MM-DD` or `YYYY-MM` for approximate
- Uncertain dates: `[~approximate]`
- Disputed dates: `[DISPUTED: source A says X, source B says Y]`

## Within-Profile Validation

### File-to-File Consistency

| Check                         | Files involved                                                                        |
| ----------------------------- | ------------------------------------------------------------------------------------- |
| Status tags match             | INDEX.md ↔ all other files                                                            |
| Timeline events referenced    | timeline/overview.md ↔ psychology/core-wounds, darkness/traumas, light/strengths-hope |
| Relationship names consistent | relationships/family.md ↔ identity/core.md                                            |
| Clinical references accurate  | psychology/core-wounds, darkness/traumas ↔ docs/references/                           |
| Milestones subset of timeline | milestones.md ↔ timeline/overview.md                                                  |
| Coping mechanisms documented  | psychology/core-wounds.md ↔ psychology/defense-mechanisms.md                          |
| State phases consistent       | timeline/state-timeline.md ↔ CURRENT-STATE.md                                         |

### Source Priority Compliance

Verify that no P3/P4 source overrides a P1/P2 source on the same fact.
See `04-materials-ingestion.md` for full priority hierarchy.

## Validation Report Format

Reports go to `plans/reports/` with naming: `validation-{date}-{type}.md`

Required sections:

1. **Executive Summary** — scope, files checked, issues found
2. **Inconsistencies Found** — table with file, before, after, root cause
3. **Consistency Matrix** — per-file check across all 4 dimensions
4. **Cross-Reference Validation** — narrative thread consistency
5. **Source Priority Compliance** — P1-P4 adherence
6. **Unresolved Items** — items requiring human review

### Severity Classification

| Severity | Definition                           | Action Required         |
| -------- | ------------------------------------ | ----------------------- |
| CRITICAL | Factual contradiction between files  | Fix immediately         |
| MAJOR    | Missing cross-reference or asymmetry | Fix before next publish |
| MINOR    | Wording variation, non-material diff | Fix when convenient     |
| INFO     | Observation, no action needed        | Log only                |

## Automation

- `psy:crossref` runs automated cross-validation
- `psy:crossref --pair hieu chien` validates specific character pair
- `psy:crossref --full` validates all characters against each other
