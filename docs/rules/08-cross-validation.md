# Cross-Validation Rules

Standards for validating consistency across character profiles and within individual profiles.

## When to Validate

- After Wave 3 of any major profile update
- After integrating new materials that affect multiple characters
- After any cross-character event update (events involving ≥2 characters)
- After PSY.refresh event triggered by MAT integration
- Periodically as maintenance (run `psy:crossref`)

## 10 Consistency Dimensions

Every validation MUST check these dimensions. Dimensions 1-4 have automated script support; dimensions 5-10 require LLM judgment.

### Core Dimensions (Automated)

| #   | Dimension     | Description                                                  | Example Check                                    |
| --- | ------------- | ------------------------------------------------------------ | ------------------------------------------------ |
| 1   | Temporal      | Dates don't conflict, ages match DOB, event order is logical | Nhân vật C can't be 18 in 2024 if born 14/05/2007     |
| 2   | Relational    | Character A's view of B matches B's view of A                | If Nhân vật A says "kết nghĩa 09/2025", Nhân vật B must agree |
| 3   | Psychological | Defense mechanisms logically stem from documented trauma     | Avoidance must trace to a specific wound         |
| 4   | Factual       | Numbers, names, places are identical across all files        | Debt amount "1 tỷ" must be same in all files     |

### Extended Dimensions (LLM Judgment)

| #   | Dimension     | Description                                                      | Example Check                                              |
| --- | ------------- | ---------------------------------------------------------------- | ---------------------------------------------------------- |
| 5   | Evidential    | Profile claims backed by material evidence ≥T3                   | "Avoidant attachment" claim must trace to T2+ material     |
| 6   | Developmental | Growth trajectory plausible given timeline + milestones          | Recovery claim in 2025 must follow documented intervention |
| 7   | Cultural      | Cultural context consistent across characters from same milieu   | Vietnamese family dynamics consistent for Tỉnh X       |
| 8   | Systemic      | Family system dynamics balance (parentification ↔ role reversal) | If Nhân vật A is parentified, sibling roles must reflect this    |
| 9   | Narrative     | Story arcs across characters form coherent threads               | Mentor-mentee arc must progress logically across timelines |
| 10  | Linguistic    | Voice consistency when characters describe shared events         | Same event described in compatible (not identical) tone    |

### When to Validate Extended Dimensions

- **Evidential (5)**: After `MAT.integrated` — new material may support or contradict claims
- **Developmental (6)**: After profile updates to `growth-edges.md` or `milestones.md`
- **Cultural (7)**: When adding new character or updating `cultural-formulation.md`
- **Systemic (8)**: After any `relationships/family.md` update
- **Narrative (9)**: After `psy:arc-tracker` detects trajectory shift
- **Linguistic (10)**: Before `cre:post-writer` when content references shared events

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
3. **Consistency Matrix** — per-file check across all 10 dimensions
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
