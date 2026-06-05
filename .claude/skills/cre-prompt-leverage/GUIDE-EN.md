# cre:prompt-leverage — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

You have a rough brief: "Write a LinkedIn post about Nhân vật A's mentoring journey." That's vague. This skill transforms it into a detailed execution prompt: extract Nhân vật A's voice patterns ("analytical, dense imagery, intellectualization defense"), clinical theory to reference (attachment theory, growth mindset), LinkedIn constraints (3000 chars, hook first, no hashtag spam), specific profile facts (DOB, current status, key relationships), and sensitivity flags (no real family names, verify timeline). Result: a prompt so specific that `cre:post-writer` knows exactly what to do.

## 2. Core concepts (the mental model)

**Five strengthening layers applied sequentially:**

1. **Voice Lock:** Extract linguistic patterns from `identity/writing-voice.md` + `psychology/defense-mechanisms.md`. Tone, vocabulary, recurring metaphors, anti-patterns (what character never says).

2. **Clinical Accuracy:** Identify relevant theories from brief. Read `docs/references/{theory}.md`. Extract key terms, common misapplications, accessibility notes. Guard against clinical jargon leak.

3. **Platform Formatting:** Map platform constraints (LinkedIn: 3000 chars, text-first, hook in 2 lines; TikTok: 9:16, <60s, conversational). Add to prompt.

4. **Profile Cross-Reference:** List files to read (identity/core.md, relationships/, timeline/). Add factual constraints (DOB, current status, key events, evidence tier policy).

5. **Sensitivity Scan:** Identify trauma references, real names, clinical terms. Add handling guidelines and constraints.

**Output:** Strengthened prompt + pre-read checklist + quality checklist for validation.

## 3. Learning path

**First run (standalone):**
```bash
/cre:prompt-leverage "Write a LinkedIn post about Nhân vật A's growth in assertiveness"
```
Output: strengthened prompt with all 5 layers + "Pre-read: identity/core.md, psychology/growth-edges.md, identity/writing-voice.md" + "Verify: assertiveness_unlock is T1 evidence (session notes)?"

**As you grow:** Try `--from-context` to read a CONTEXT.md from exploration. All 5 layers applied based on locked decisions.

**Standard flow:** Explore → lock decisions (CONTEXT.md) → prompt-leverage (strengthen) → post-writer (write).

## 4. Use cases (each = a sample conversation)

### Use case: Standalone strengthening

> **You:** `/cre:prompt-leverage Write a blog post about Nhân vật B's relationship with gambling`
>
> **Skill:** Applies 5 layers → outputs: "Original: Write a blog post... | Strengthened: [full prompt with Nhân vật B's voice, cultural formulation theory, blog constraints, family relationship facts, sensitivity on gambling trauma]"
>
> **You:** Copy strengthened prompt → feed to `cre:post-writer`.

### Use case: From exploration

> **You:** Explored, locked CONTEXT.md. Now: `/cre:prompt-leverage --from-context`
>
> **Skill:** Extracts decisions from CONTEXT.md → applies 5 layers → outputs strengthened prompt.
>
> **You:** Verify pre-read list, then `cre:post-writer --from-context`.

### Use case: Batch preparation

> **You:** 10 content briefs queued. Strengthen all, then write.
>
> **Skill:** Loop: `/cre:prompt-leverage {brief}` → strengthened prompts saved to `plans/prompts/`.
>
> **You:** Review all 10, then parallel: 10× `cre:post-writer` with strengthened prompts.

### Use case: Platform override

> **You:** `/cre:prompt-leverage {brief} --platform tiktok`
>
> **Skill:** Emphasizes TikTok constraints (9:16, <60s, hook within 3s, conversational).
>
> **You:** Better TikTok-specific prompt output.

## 5. Important caveats

- **Layers are additive:** Each layer adds constraints; more constraints = better clarity for LLM, but not always "better" content (risk of over-specification).
- **Pre-read list is advisory:** Files to read before writing. Author should skim or read fully per time budget.
- **Clinical terms are guarded:** Layer 2 warns about clinical jargon; author decides when clinical reference is OK.
- **Not auto-validation:** Strengthened prompt is more complete, not certified correct. Post-writer still validates.
- **Context.md integration:** If CONTEXT.md decisions are vague, strengthened prompt reflects that. Explore thoroughly for best results.

## See also

- [`SKILL.md`](./SKILL.md) for technical contract
- `cre:exploring` — produces CONTEXT.md
- `cre:post-writer` — uses this internally (Layer 2) for prompt strengthening
- Rule 03 (content pipeline), Rule 02 (clinical reference)
