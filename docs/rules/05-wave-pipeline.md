# Wave Pipeline Rules

The 3-wave execution protocol for profile generation and major updates.

## When to Use

- Creating a new character profile from scratch
- Major profile updates involving multiple files (≥3 files affected)
- Integrating significant new source materials (crisis events, relationship reveals)

For minor updates (single fact, single file) → skip waves, update directly with `[Source:]` tag.

## The 3 Waves

```
WAVE 1: Foundation → WAVE 2: Deep Dive → WAVE 3: Synthesis & Validation
```

### Wave 1: Foundation (Data Extraction)

Extract objective facts to build/update the character's base.

**Scope:**

- **Identity**: Name, DOB, Origins, Career, Education
- **Timeline**: Chronological events (verify ages align with DOB)
- **Relationships**: Family tree, key connections

**Outputs:** `IDENTITY.md`, `TIMELINE.md`, `RELATIONSHIPS.md`

**Process:**

1. Intake raw sources → classify by priority (P1-P4, see `04-materials-ingestion.md`)
2. Store raw materials in `docs/materials/{character}/`
3. Extract identity facts, timeline events, relationship cards
4. Tag confidential info with `[PRIVATE]` or `[CONFIDENTIAL]`
5. Cross-reference with existing data, mark `[UNCERTAIN]` where unverifiable

### Wave 2: Deep Dive (Psychological Analysis)

Analyze behavioral patterns, trauma, and voice.

**Scope:**

- **Soul & Wound**: Core wounds, emotional triggers, dominant/hidden emotions
- **Duality**: External Mask vs. Internal Reality
- **Coping & Growth**: Healthy/unhealthy coping mechanisms, growth edges
- **Crisis Assessment**: If applicable, document risk level per `06-crisis-protocol.md`

**Outputs:** `SOUL.md`, `DARKNESS.md`, `LIGHT.md`, `CHARACTERISTIC.md`, `MILESTONES.md`

**Mandatory Clinical Referencing (NGUYÊN TẮC TỐI THƯỢNG):**

> Mọi phát hiện tâm lý PHẢI được liên kết với `docs/references/` bằng Markdown link.
> Tuyệt đối không phân tích "suông" (armchair psychology).

See `02-clinical-reference-usage.md` for full citation rules.

### Wave 3: Synthesis & Validation

Cross-reference all generated/updated files.

**4 Consistency Dimensions:**

| Dimension     | What to check                                      |
| ------------- | -------------------------------------------------- |
| Temporal      | No impossible date overlaps, ages match DOB        |
| Relational    | Symmetric references between character profiles    |
| Psychological | Mechanisms logically stem from mapped trauma       |
| Factual       | Numbers, names, places consistent across all files |

**Process:**

1. Validate every updated file against all 4 dimensions
2. Check cross-character references (see `08-cross-validation.md`)
3. Resolve inconsistencies found
4. Compile/update `INDEX.md`
5. Generate validation report in `plans/reports/`

## Wave File Structure (for major updates)

```
plans/{date}-{slug}/
├── plan.md
├── wave1.md
├── wave2.md
└── wave3.md
```

## Success Criteria per Wave

| Wave | Minimum outputs                                                     |
| ---- | ------------------------------------------------------------------- |
| 1    | Raw sources stored, ≥N timeline events, relationship cards updated  |
| 2    | ≥5 triggers, ≥3 coping mechanisms, inner conflict documented        |
| 3    | All 4 dimensions validated, inconsistencies resolved, INDEX updated |

## Automation

- `lucas:wave` skill orchestrates the 3-wave process
- `lucas:crossref` validates cross-character consistency (Wave 3)
- `lucas:ref-audit` ensures clinical references are accurate (Wave 2-3)
