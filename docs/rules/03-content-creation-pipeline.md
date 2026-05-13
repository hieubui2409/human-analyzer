# Content Creation Pipeline Rules

Standard workflow for creating any content in `assets/`.

## Pipeline Stages

```
1. INTAKE → 2. EXPLORE → 3. CLASSIFY → 4. PLAN → 5. WRITE → 6. REVIEW → 7. PUBLISH
```

| Stage    | Skill                           | Output                             | Required?        |
| -------- | ------------------------------- | ---------------------------------- | ---------------- |
| Intake   | `lucas:intake`                  | Work type + routing                | Always           |
| Explore  | `lucas:exploring`               | CONTEXT.md with locked decisions   | For new angles   |
| Classify | `lucas:classify`                | Risk level (tiny/normal/high_risk) | Always           |
| Plan     | `ck:plan` or inline             | Plan file or mental model          | For normal+ risk |
| Write    | `lucas:post-writer` or manual   | Draft in assets/                   | Always           |
| Review   | Self-review or `lucas:crossref` | Validated draft                    | For normal+ risk |
| Publish  | Manual copy-paste               | Posted content                     | User action      |

## Content Types

### Reality Posts

- Based on real events from character timelines
- MUST cross-reference TIMELINE.md for accuracy
- MUST respect privacy boundaries (see `docs/rules/09-confidentiality-protocol.md`)
- Voice must match WRITING-VOICE.md if writing as character

### Fiction Posts

- Inspired by real events but fictionalized
- May composite multiple events or characters
- MUST NOT contradict established profile facts
- MAY use literary devices and metaphor

### Analysis Posts

- Psychological or behavioral analysis
- MUST anchor to clinical references (internally)
- MUST use accessible language (externally)
- Cite theories without naming them per show-don't-tell rule

### Letter Format

- Epistolary style ("Thư gửi...")
- Intimate, direct address
- Strong emotional resonance
- MUST maintain consistent voice throughout

## Output Standards

Every content package MUST include:

1. `post.md` — markdown source (source of truth)
2. `post.txt` — plain text publish-ready version
3. `prompt.txt` — image generation prompts (if visual)
4. `images/` — generated images directory
5. `README.md` — input parameters and clinical intent

**Sync rule:** `post.md` ↔ `post.txt` must be identical in content. If conflict, `post.md` wins.

## Platform Guidelines

| Platform  | Max length    | Hook requirement         | Hashtags       | Special                                      |
| --------- | ------------- | ------------------------ | -------------- | -------------------------------------------- |
| LinkedIn  | ~3000 chars   | First 2 lines visible    | 3-5 max        | Professional tone even for vulnerability     |
| Facebook  | No hard limit | Emotional hook           | Optional       | Storytelling-friendly, can be raw            |
| Instagram | 2200 chars    | First line before "more" | 15-20          | Visual-first, caption supports image         |
| TikTok    | 60s script    | 3-second hook            | 5-10           | Conversational, fast-paced                   |
| YouTube   | Variable      | Intro hook + structured  | In description | Chapters, timestamps                         |
| Twitter/X | 280/thread    | Punchy, quotable         | 2-3            | Thread format for longer content             |
| Blog      | No limit      | Opening scene            | N/A            | Deep narrative, can include clinical backing |

## Quality Checklist (Before Publish)

- [ ] Content matches character voice profile
- [ ] Clinical terms translated to accessible language
- [ ] Platform format constraints met
- [ ] Facts verified against TIMELINE.md
- [ ] Privacy boundaries respected (no restricted names/locations)
- [ ] post.md and post.txt are in sync
- [ ] Image prompts provided if visual content needed
