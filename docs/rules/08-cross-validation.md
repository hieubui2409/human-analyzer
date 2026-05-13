# Cross-Validation Rules

Standards for validating consistency across character profiles and within individual profiles.

## When to Validate

- After Wave 3 of any major profile update
- After integrating new materials that affect multiple characters
- After any cross-character event update (events involving ≥2 characters)
- Periodically as maintenance (run `lucas:crossref`)

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

For every relationship documented in character A's `RELATIONSHIPS.md`:

1. Character B's `RELATIONSHIPS.md` MUST have a corresponding section
2. Key facts MUST match: dates, events, role descriptions
3. Psychological assessments may differ (each character's perspective)

### Shared Timeline Events

Events involving multiple characters MUST appear in ALL participants' `TIMELINE.md`:

- Same date (or both marked `[~approximate]`)
- Same factual description (may differ in perspective/impact)
- Cross-reference comment linking to other character's file

Format:

```markdown
<!-- Cross-ref: docs/profiles/{other}/TIMELINE.md — same event -->
```

### Age/Date Calculation Rules

- Always calculate age from DOB, not from stated age
- Verify: `current_year - birth_year = stated_age` (±1 for birthday not yet passed)
- Date format: `YYYY-MM-DD` or `YYYY-MM` for approximate
- Uncertain dates: `[~approximate]`
- Disputed dates: `[DISPUTED: source A says X, source B says Y]`

## Within-Profile Validation

### File-to-File Consistency

| Check                         | Files involved                    |
| ----------------------------- | --------------------------------- |
| Status tags match             | INDEX ↔ all other files           |
| Timeline events referenced    | TIMELINE ↔ SOUL, DARKNESS, LIGHT  |
| Relationship names consistent | RELATIONSHIPS ↔ IDENTITY          |
| Clinical references accurate  | SOUL, DARKNESS ↔ docs/references/ |
| Milestones subset of timeline | MILESTONES ↔ TIMELINE             |
| Coping mechanisms documented  | SOUL ↔ CHARACTERISTIC             |

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

- `lucas:crossref` runs automated cross-validation
- `lucas:crossref --pair hieu chien` validates specific character pair
- `lucas:crossref --full` validates all characters against each other
