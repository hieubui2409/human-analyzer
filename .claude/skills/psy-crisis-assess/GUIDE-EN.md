# psy:crisis-assess — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

A character has experienced severe trauma. You need to understand: Is this crisis-level risk? What protective factors keep them safe? You have interview transcripts, family context, and timeline. This skill scans for crisis keywords, analyzes them against DSM-5 and ICD-11 clinical frameworks, and outputs structured risk documentation so you know how to write about — or avoid writing about — their mental state.

## 2. Core concepts (the mental model)

- **Two-pass scan**: The script first searches for explicit crisis keywords (24 patterns: "tự tử," "suicide," "chết," etc.). Then it scans for behavioral clusters — patterns that map to crisis-adjacent theories even if the word "crisis" never appears.
- **Never cached**: Unlike other psy skills, crisis verdicts cannot be cached. If you re-read the profile, the skill re-judges. This is a safety gate: a stale cached "LOW" risk on a profile that now hints at self-harm would be dangerous.
- **Risk levels matter**: HIGH risk requires safety documentation; MODERATE requires monitoring; LOW is managed through content boundaries (Rule 09).

## 3. Learning path

**First run:** `psy:crisis-assess --character hieu --quick` — get a fast risk snapshot.

**Deep run:** `psy:crisis-assess --character hieu --full` — full DSM-5 + ICD-11 checklist for detail.

**Update:** After adding new materials, `psy:crisis-assess --character hieu --update` — append new findings to existing documentation.

## 4. Use cases (each = a sample conversation)

### Use case: Quick risk check (you just added trauma materials)

> You: "I integrated interview transcripts mentioning Nhân vật C's abandonment at age 11. Is this HIGH-risk territory?"
> Skill: `psy:crisis-assess --character chien --quick`
> → Keywords: "bỏ rơi" (abandoned) hits. Behavioral: orphaning. Risk Level: MODERATE. Protective factors: mentor, education. Output: appends to darkness/traumas.md.

### Use case: Full clinical assessment (significant profile update)

> You: "Nhân vật B's story has evolved. Gambling addiction, family abandonment, drinking. Full assessment?"
> Skill: `psy:crisis-assess --character hoa --full`
> → DSM-5 MDD: 7/9 criteria. ICD-11 C-PTSD: partial. SI: passive. Outputs: updates darkness/traumas.md, light/strengths-hope.md, INDEX.md status.

### Use case: Crisis content boundary (draft references crisis)

> You: "I wrote a post about Nhân vật A's sacrificial role, but it hints at burnout risk. Should I publish?"
> Skill: `cre:privacy-guard` (calls `psy:crisis-assess` internally) or you pre-check `psy:crisis-assess --character hieu --full` → if HIGH risk, `cre:privacy-guard` flags content.

## 5. Important caveats

- **Not diagnosis**: This documents narrative patterns, not real psychiatric diagnosis. All clinical terms are applied for character analysis accuracy.
- **Deep mode default**: `--quick` skips behavioral-cluster scan. Only use when speed matters (deployment time crunch). Default deep mode is safer.
- **Must document protective factors**: If you find crisis indicators, MANDATORY: identify ≥3 protective factors (internal + external). A character at HIGH risk with zero documented protections is either incomplete data or a genuine safety concern.
- **Aftermath required**: After HIGH-risk assessment, update `orc:session-state` so the session can recover if needed.
