# Confidentiality & Privacy Protocol

Rules for handling sensitive information across profiles, materials, and published content.

## Privacy Tags

### Tag Definitions

| Tag                        | Meaning                                           | Where allowed                  |
| -------------------------- | ------------------------------------------------- | ------------------------------ |
| `[PRIVATE]`                | Internal reference only, never surface in content | Profiles, materials            |
| `[CONFIDENTIAL: {person}]` | Do not reference in public content about {person} | Profiles, materials            |
| `[ANONYMIZE]`              | Use pseudonym or role description in content      | Profiles → content translation |

### Application Rules

- Tags MUST appear inline, adjacent to the sensitive content
- Tags cascade: a `[PRIVATE]` section means ALL facts within are private
- When content has both `[PRIVATE]` and non-private facts, tag each separately

## Content Boundary Rules

### Names

- Characters with public profiles (Nhân vật A, Nhân vật C, Nhân vật B): names may appear in public content
- Third parties marked `[CONFIDENTIAL]`: NEVER use real name in published content
- Use role descriptions instead: "người mentor", "người bạn", "người thân"

### Locations

- Do not reveal specific locations that could identify or endanger characters
- Example: "không lộ quê quán Tỉnh X để bảo vệ Nhân vật B" in certain contexts
- General regions acceptable when relevant to narrative

### Clinical Information

- Raw clinical terms: NEVER in social media content (see `02-clinical-reference-usage.md`)
- Diagnosis labels: NEVER published externally
- Crisis details: NEVER surface in content without explicit consent

### Relationship Details

- Secret relationships marked `[PRIVATE]`: do not allude to in content
- Family conflicts: may be referenced in anonymized/metaphorical form only
- Financial details (debt amounts, income): anonymize or omit in content

## Privacy Levels for Content Creation

Content privacy levels:

| Level          | Definition                                       | Use case                     |
| -------------- | ------------------------------------------------ | ---------------------------- |
| Public/Persona | Public-facing, maintains character's front image | Social media posts           |
| Private/Hidden | Inner voice, shared only in restricted contexts  | Private group posts, letters |

Content creators MUST specify privacy level before drafting. The level determines:

- Which facts can be included
- Whether `[PRIVATE]` tagged information is accessible
- Tone and disclosure depth

## File-Level Rules

| File type      | Privacy handling                                         |
| -------------- | -------------------------------------------------------- |
| Profiles       | May contain all tags, full clinical detail               |
| Materials      | Preserve original, tag sensitive parts                   |
| Assets (posts) | MUST NOT contain `[PRIVATE]` or `[CONFIDENTIAL]` content |
| Plans/Reports  | May reference private info for internal use              |

## Narrative Approach & Privacy

| Approach     | Description                          | Privacy implication                      |
| ------------ | ------------------------------------ | ---------------------------------------- |
| Direct       | Tell the story as it happened        | Higher privacy risk, check tags          |
| Metaphorical | Use allegory/fiction to convey truth | Lower risk, can reference private themes |

## Audit

- Before publishing any content, verify no `[PRIVATE]`/`[CONFIDENTIAL]` content leaked
- `lucas:post-writer` includes sensitivity scan in quality check phase
- `lucas:prompt-leverage` applies sensitivity scan layer
