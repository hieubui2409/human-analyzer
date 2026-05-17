# Materials Ingestion Rules

Standards for adding new source materials to `docs/materials/`.

Full pipeline specification: `docs/rules/11-mat-pipeline.md`
Material schema: `docs/references/material-schema.yaml`

## MAT Framework Overview

Materials ingestion is governed by the MAT (Materials) framework. This rule covers quick-reference ingestion standards; the full 5-stage pipeline (Ingestion → OCR → Extraction → Validation → Integration) is defined in rule 11.

**Domain boundary**: MAT ONLY writes to `docs/materials/`. Profile updates triggered by MAT go through the PSY framework.

## Evidence Tiers

Replaces old P1-P4 priority system. Maps to `material-schema.yaml` `evidence_tier` field:

| Tier | Category   | Confidence | Weight | Examples                                       |
| ---- | ---------- | ---------- | ------ | ---------------------------------------------- |
| 1    | Primary    | High       | 1.0    | Direct testimony, interviews, personal letters |
| 2    | Secondary  | High       | 0.9    | Professional assessments, clinical evaluations |
| 3    | Tertiary   | Medium     | 0.7    | News articles, social media, messenger logs    |
| 4    | Contextual | Med-Low    | 0.5    | Third-party accounts, family testimony         |
| 5    | Auxiliary  | Low        | 0.3    | Inference from metadata, timestamps            |

Rule: higher tier > lower tier when conflict arises. Newer > older within the same tier. Unresolvable conflicts → tag `[UNCERTAIN]`.

## Processing States Lifecycle

Materials move through states in one direction only:

```
raw → extracted → analyzed → validated → integrated → archived
```

- `raw` — received, stored in `docs/materials/{character}/raw/`
- `extracted` — OCR/transcription complete, stored in `docs/materials/{character}/analyzed/`
- `analyzed` — LLM extraction done, YAML frontmatter populated
- `validated` — CRAAP test passed, cross-references checked
- `integrated` — merged into profiles, triggers `PSY.refresh` event
- `archived` — superseded or fully merged, stored in `docs/materials/{character}/archive/`

## CRAAP Test

Every material MUST pass this 5-dimension reliability test before profile integration:

1. **Currency** — When was the material created/captured? Older ≠ less valuable (historical context matters)
2. **Relevance** — Direct connection to which profile sections?
3. **Authority** — Creator's credentials and proximity to subject
4. **Accuracy** — Can claims be cross-referenced? Internal consistency?
5. **Purpose** — Clinical note vs. social media post vs. personal reflection

## Ingestion Process (Quick Reference)

### Step 1: Receive Material

- User provides transcript, document, screenshot, letter, news article
- Determine source type and evidence tier (1-5)
- Assign to `docs/materials/{character}/raw/`

### Step 2: Store Raw

Save to `docs/materials/{character}/raw/` with descriptive filename:

- Format: `{type}-{topic}-{source}.md`
- Examples: `transcript-duong-conflict.md`, `letter-gioi-thieu-f15.md`, `news-vietseeds-interview.md`
- Populate YAML frontmatter from `material-schema.yaml`
- Preserve original text — do NOT sanitize or edit raw materials

### Step 3: Extract Key Facts

For each material, identify:

- **Dates** — with confidence level (exact, approximate, uncertain)
- **People** — names, relationships, roles
- **Events** — what happened, sequence, consequences
- **Psychological signals** — behaviors, patterns, clinical indicators
- **Quotes** — direct quotes worth preserving verbatim

### Step 4: Cross-Reference

Before updating profiles:

1. Check extracted facts against existing `timeline/overview.md` entries
2. Identify contradictions with current profile content
3. Classify as: new information, confirmation, contradiction, enrichment
4. Run CRAAP test; document result in material frontmatter

### Step 5: Update Profiles

Follow the 3-wave pipeline (`psy:wave`) for significant updates:

- Wave 1: Source + identity/timeline/relationships
- Wave 2: Deep psychology (psychology/core-wounds, darkness/traumas, light/strengths-hope)
- Wave 3: Cross-validate across all characters

For minor updates (single fact addition):

- Update directly with `[Source: docs/materials/{file}]` tag
- Run `psy:crossref --pair` for affected characters
- Update material `processing_status` → `integrated`

## Material Types

| Type             | Typical Tier | Expected Content             | Storage Format                       |
| ---------------- | ------------ | ---------------------------- | ------------------------------------ |
| Transcript       | 3            | Conversation with timestamps | Markdown with speaker labels         |
| Letter           | 1            | Written correspondence       | Markdown preserving original format  |
| Conversation log | 3            | Messenger/chat               | Markdown with timestamps + sender    |
| Clinical note    | 2            | Professional assessment      | Markdown with medical terminology    |
| News article     | 3            | Published media              | Markdown with source URL + date      |
| Interview        | 1-2          | Q&A format                   | Markdown with Q/A labels             |
| Photo/screenshot | 3-4          | Visual evidence              | Store in materials, describe in text |

## Confidentiality Tags

Some materials contain sensitive information:

- `[CONFIDENTIAL: {person}]` — do not reference in public content
- `[ANONYMIZE]` — use pseudonym or role description in content
- `[PRIVATE]` — internal reference only, never surface

## Validation

- `mat:indexer` detects recently added materials, flags contradictions
- `mat:loader` prepares materials for analysis pipeline
- `psy:crossref` checks profile consistency after ingestion
- `psy:ref-audit` ensures clinical terms from materials are properly referenced
