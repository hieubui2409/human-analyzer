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

1. Read character's `identity/writing-voice.md`. Extract `## Voice Profile (Structured)` section for quantitative validation.
2. Additionally read `psychology/archetype.md` for archetypal voice patterns (Nhân vật A: Wounded Healer; Nhân vật B: Lost Child/Trickster; Nhân vật C: Orphan/Seeker)
3. Use structured dimensions as primary audit criteria:
   - **Rhythm**: sentence length, cadence, paragraph density
   - **Compression**: viết tắt patterns, terseness level
   - **Emotional Register**: default tone, range, intensity ceiling
   - **Imagery Bank**: primary domains, frequency
   - **Hard Bans**: words/phrases character NEVER uses
   - **Defense Gates**: how defenses manifest in writing
   - **Growth Modifiers**: how current arc shifts voice from baseline

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

## Voice Profile Coverage

All 3 characters have `identity/writing-voice.md` with `## Voice Profile (Structured)` section:

- **Nhân vật A**: richest content — analytical/controlled tone, dense imagery, intellectualization defense gate
- **Nhân vật B**: Messenger-based voice — high compression (viết tắt), guarded default, wide emotional range
- **Nhân vật C**: dual-voice (public mask vs private) — warm default, future-oriented displacement

## Safety

- READ-ONLY — does not modify any content files
- Writes only to stdout or plans/reports/ (with --report)
- Scope: voice/tone consistency validation. Does NOT create or edit content, modify profiles, or manage references.

## See Also

cre:post-writer, cre:repurpose, psy:crossref
