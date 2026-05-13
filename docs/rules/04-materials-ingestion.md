# Materials Ingestion Rules

Standards for adding new source materials to `docs/materials/`.

## Source Priority Hierarchy

Always resolve conflicts using source priority hierarchy:

1. **P1 (Direct):** Interviews, personal logs, explicit corrections
2. **P2 (Documentary):** Official records, news, public data
3. **P3 (Conversational):** Chat logs, text messages
4. **P4 (Analytical):** Third-party or AI inferences

Rule: newer > older when same priority level. Unresolvable conflicts → tag `[UNCERTAIN]`.

## Ingestion Process

### Step 1: Receive Material

- User provides transcript, document, screenshot, letter, news article
- Determine source type and priority level (P1-P4)

### Step 2: Store Raw

Save to `docs/materials/{character}/` with descriptive filename:

- Format: `{type}-{topic}-{source}.md`
- Examples: `transcript-duong-conflict.md`, `letter-gioi-thieu-f15.md`, `news-vietseeds-interview.md`
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

1. Check extracted facts against existing TIMELINE.md entries
2. Identify contradictions with current profile content
3. Classify as: new information, confirmation, contradiction, enrichment

### Step 5: Update Profiles

Follow the 3-wave pipeline (`lucas:wave`) for significant updates:

- Wave 1: Source + identity/timeline/relationships
- Wave 2: Deep psychology (SOUL, DARKNESS, LIGHT)
- Wave 3: Cross-validate across all characters

For minor updates (single fact addition):

- Update directly with `[Source: docs/materials/{file}]` tag
- Run `lucas:crossref --pair` for affected characters

## Material Types

| Type             | Expected Content             | Storage Format                       |
| ---------------- | ---------------------------- | ------------------------------------ |
| Transcript       | Conversation with timestamps | Markdown with speaker labels         |
| Letter           | Written correspondence       | Markdown preserving original format  |
| Conversation log | Messenger/chat               | Markdown with timestamps + sender    |
| Clinical note    | Professional assessment      | Markdown with medical terminology    |
| News article     | Published media              | Markdown with source URL + date      |
| Interview        | Q&A format                   | Markdown with Q/A labels             |
| Photo/screenshot | Visual evidence              | Store in materials, describe in text |

## Confidentiality Tags

Some materials contain sensitive information:

- `[CONFIDENTIAL: {person}]` — do not reference in public content
- `[ANONYMIZE]` — use pseudonym or role description in content
- `[PRIVATE]` — internal reference only, never surface

## Validation

- `lucas:materials --new` detects recently added materials
- `lucas:crossref` checks profile consistency after ingestion
- `lucas:ref-audit` ensures clinical terms from materials are properly referenced
