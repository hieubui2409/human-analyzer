# Content Creation Pipeline Rules

Standard workflow for creating any content in `assets/`. Governed by the CRE (Creative) framework domain.

## CRE Framework Integration

Content creation operates within the ORC framework:

- **MAT → CRE**: New integrated materials trigger `CRE.recalibrate` (voice/tone refresh)
- **PSY → CRE**: Psychological state changes from `state-timeline.md` constrain content routing
- **CRE domain boundary**: CRE ONLY writes to `assets/`. Profile updates go through PSY framework.

## 3-Layer Voice Architecture

Every piece of content MUST be built from three layers loaded in order:

1. **Core personality** — `identity/core.md` (stable traits, values, fundamental voice)
2. **Tone adaptation** — `identity/writing-voice.md` (platform-specific tone, register shifts)
3. **Behavioral patterns** — `psychology/defense-mechanisms.md` (what character cannot express, defense gating)

If any layer file is missing → STOP and request PSY framework to generate it first.

## Defense-Mechanism Gating

Before generating vulnerability or emotionally-raw content, check `psychology/defense-mechanisms.md`:

- If active defense = **denial** → do NOT generate content that requires character to acknowledge the denied truth
- If active defense = **intellectualization** → vulnerability content must be framed through analysis/insight, not raw emotion
- If active defense = **dissociation** → avoid first-person emotional immersion framing
- Defense state is context-dependent; consult `timeline/state-timeline.md` for current phase

## Clinical-to-Accessible Translation

Three-step translation process for any psychological insight:

1. **Core truth** — identify the clinical mechanism (internal documentation only)
2. **Metaphor reframe** — find the universal human experience that maps to it
3. **Growth contextualization** — frame through character's arc, not pathology

Example (internal → external):

- Core truth: Parentification + anxious attachment → hypervigilance about abandonment
- Metaphor reframe: "Khi còn nhỏ, phải học cách đọc tâm trạng người lớn trước khi được phép là đứa trẻ"
- Growth contextualization: "Giờ mới dần học được rằng: cảm xúc của mình cũng quan trọng không kém"

## Pipeline Stages

```
1. INTAKE → 2. EXPLORE → 3. CLASSIFY → 4. PLAN → 5. WRITE → 6. REVIEW → 7. PUBLISH
```

| Stage    | Skill                         | Output                             | Required?        |
| -------- | ----------------------------- | ---------------------------------- | ---------------- |
| Intake   | `orc:intake`                  | Work type + routing                | Always           |
| Explore  | `cre:explore`                 | CONTEXT.md with locked decisions   | For new angles   |
| Classify | `orc:classify`                | Risk level (tiny/normal/high_risk) | Always           |
| Plan     | `ck:plan` or inline           | Plan file or mental model          | For normal+ risk |
| Write    | `cre:post-writer` or manual   | Draft in assets/                   | Always           |
| Review   | Self-review or `psy:crossref` | Validated draft                    | For normal+ risk |
| Publish  | Manual copy-paste             | Posted content                     | User action      |

## Phase-Appropriate Content

Content routing MUST respect psychological state phase from `timeline/state-timeline.md`:

| Phase              | Allowed content types                      | Blocked content types             |
| ------------------ | ------------------------------------------ | --------------------------------- |
| Crisis / Acute     | Retrospective reflection, hope signals     | Raw vulnerability, confrontation  |
| Stabilizing        | Growth narratives, mentorship, learning    | Triggering themes without resolve |
| Integration        | Full arc stories, analysis, transformation | None                              |
| Maintenance/Stable | All types                                  | None                              |

Always verify character's current phase before drafting.

## Content Types

### Reality Posts

- Based on real events from character timelines
- MUST cross-reference `timeline/overview.md` for accuracy
- MUST respect privacy boundaries (see `docs/rules/09-confidentiality-protocol.md`)
- Voice must match `identity/writing-voice.md` if writing as character

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

## 3-Gate Quality Check (Before Publish)

Gate 1 — Consistency (>75% threshold):

- [ ] Content matches `identity/writing-voice.md` voice profile
- [ ] Defense-mechanism gating validated (no blocked content types surfaced)
- [ ] Phase-appropriate for current `timeline/state-timeline.md` state
- [ ] Facts verified against `timeline/overview.md`

Gate 2 — Privacy scan:

- [ ] Clinical terms translated to accessible language
- [ ] Privacy boundaries respected (no restricted names/locations)
- [ ] No `[PRIVATE]` / `[CONFIDENTIAL]` content leaked

Gate 3 — Engagement forecast (>30% threshold):

- [ ] Platform format constraints met
- [ ] Hook strength validated for target platform
- [ ] post.md and post.txt are in sync
- [ ] Image prompts provided if visual content needed
