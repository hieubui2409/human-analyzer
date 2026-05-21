---
name: cre:voice-audit
description: "Audit published content for voice/tone consistency against character identity/writing-voice.md profiles. Detects tone drift, vocabulary mismatches, and persona breaks across posts. Use after batch content creation, periodic quality checks, or when voice feels 'off'. Triggers: 'voice check', 'tone audit', 'voice consistency', 'writing style check', 'persona drift', 'tone drift'."
argument-hint: "[--character <name>|--platform <platform>|--file <path>|--report]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "validation"
  position: "post-publish"
  dependencies: ["orc:bootstrap"]
---

# Voice Consistency Audit

Scan published content (assets/) for tone/voice drift against character identity/writing-voice.md profiles.

## When to Use

- After creating multiple posts — verify consistent voice
- Periodic quality check across platforms
- When content "feels off" compared to character's established voice
- Before repurposing — ensure source maintains voice integrity

## Flags

| Flag                    | Purpose                                       |
| ----------------------- | --------------------------------------------- |
| `--character <name>`    | Audit posts written as/about this character   |
| `--platform <platform>` | Audit specific platform only (facebook, etc.) |
| `--file <path>`         | Audit single post file                        |
| `--report`              | Generate formal report to plans/reports/      |

## Workflow

### Step 1: Load Voice Profile

1. Read character's `identity/writing-voice.md` (currently: Nhân vật A only has this file)
2. Additionally read `psychology/archetype.md` for archetypal voice patterns (Nhân vật A: Wounded Healer; Nhân vật B: Lost Child/Trickster; Nhân vật C: Orphan/Seeker)
3. Extract voice dimensions:
   - **Tone markers**: formal/informal, emotional range, humor style
   - **Vocabulary patterns**: signature phrases, avoided words
   - **Structural patterns**: sentence length, paragraph style, hook patterns
   - **Thematic constants**: recurring themes, metaphor families
   - **Archetypal voice**: how the character's archetype influences expression

### Step 2: Scan Published Content

1. List `assets/{platform}/*/post.md` and `post.txt` files
2. For each post, analyze:
   - Tone alignment with identity/writing-voice.md dimensions
   - Vocabulary consistency (signature phrases present? foreign words?)
   - Structural patterns match
   - Thematic alignment

### Step 3: Detect Drift

Flag these drift types:

| Drift Type                   | Detection                                                          | Severity |
| ---------------------------- | ------------------------------------------------------------------ | -------- |
| **Tone break**               | Post uses formal tone when voice is conversational (or vice versa) | HIGH     |
| **Vocabulary mismatch**      | Uses words/phrases character would never use                       | MEDIUM   |
| **Persona break**            | Content contradicts character's established perspective            | HIGH     |
| **Platform over-adaptation** | Repurposed content lost original voice entirely                    | MEDIUM   |
| **Clinical leak**            | Raw clinical terms in character-voiced content                     | HIGH     |

### Step 4: Generate Report

```markdown
## Voice Audit Report

**Date:** {YYYY-MM-DD}
**Character:** {name}
**Posts scanned:** {N}
**Platform(s):** {list}

### Voice Profile Summary (from identity/writing-voice.md)

- Tone: {summary}
- Signature elements: {list}

### Findings

| Post | Platform | Date | Drift type | Severity | Detail |
| ---- | -------- | ---- | ---------- | -------- | ------ |

### Consistency Score

{N}% of posts align with established voice profile

### Recommendations

1. {Specific corrections}
```

## PSY Framework Integration

Voice audit can now leverage PSY profile data for richer validation:

- `psychology/defense-mechanisms.md` — content should reflect character's active defenses (e.g., Nhân vật A's intellectualization in analytical posts)
- `psychology/cultural-formulation.md` — voice should respect cultural expression norms
- `psychology/formulation.md` — perpetuating factors may influence how character "sounds" in content
- `docs/graph/{dyad}.md` — cross-character content should reflect documented communication patterns

## Scope Limitation

Currently only **Nhân vật A** has a `identity/writing-voice.md` file. For Nhân vật B and Nhân vật C:

- No formal voice profile exists → voice audit uses archetype + defense mechanism patterns as proxy
- If content is written _about_ them (by Nhân vật A's voice), audit against Nhân vật A's `identity/writing-voice.md`
- If content is written _as_ them (first-person), use `psychology/archetype.md` + `identity/core.md` personality traits as baseline
- Future: create `identity/writing-voice.md` for Nhân vật B/Nhân vật C as enough content samples accumulate

## Safety

- READ-ONLY — does not modify any content files
- Writes only to stdout or plans/reports/ (with --report)
- Scope: voice/tone consistency validation. Does NOT create or edit content, modify profiles, or manage references.

## See Also

cre:post-writer, cre:repurpose, psy:crossref
