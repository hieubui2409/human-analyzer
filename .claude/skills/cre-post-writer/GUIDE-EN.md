# cre:post-writer — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

You want to write a post about Character A's mentoring journey on LinkedIn. You could start with a blank screen, but that's slow and risky. This skill asks "Who? What? Platform? Tone?" → loads Character A's voice profile → strengthens your prompt with platform constraints, clinical guardrails, and profile facts → generates a draft → automatically checks it for evidence tier support, voice consistency, and privacy leaks → outputs a production-ready 5-file package. You review, maybe tweak, then manually post.

## 2. Core concepts (the mental model)

**7-phase pipeline:**

1. **Stale voice gate:** Check if profile is fresh enough to write. If materials newer than last PSY refresh → voice data is stale; block or warn.
2. **Context loading:** Load character lite profile (5s), extract voice, formulation, defense patterns.
3. **Prompt strengthening:** Apply 5 layers — voice lock, clinical accuracy, platform formatting, profile cross-reference, sensitivity scan.
4. **Draft generation:** LLM writes native to platform + content type (reality/fiction/analysis/letter).
5. **Mandatory gates:** Run evidence-scanner (T1-T2 only?), voice-audit (tone match?), privacy-guard (leak?). FAIL blocks.
6. **Profile alignment check:** Factual, psychological, relationship consistency vs. profiles. Fix contradictions.
7. **Quality checklist:** Platform constraints met? Sensitivity respected? Image prompts safe?

**Output:** `assets/{platform}/{YYMMDD}-{slug}/` with post.md, post.txt, prompt.txt, image-prompts.txt, README.md.

## 3. Learning path

**First run (interactive):**
```bash
/cre:post-writer
# Q1: Character? → Character A
# Q2: Platform? → LinkedIn
# Q3: Type? → Reality
# Q4: Topic? → Mentoring Character C through uncertainty
# Q5: Specific angle? → How consistency builds trust
```
Skill generates draft → runs gates → outputs to assets/linkedin/{date}-{slug}/ → you review post.txt, maybe tweak, then manually post.

**As you grow:** Use `cre:exploring` first → lock decisions → `cre:post-writer --from-context`. Faster workflow, all decisions documented in CONTEXT.md.

**Standard flow:** Explore (7 Q&A) → strengthen prompt (5 layers auto) → generate → gate → output.

## 4. Use cases (each = a sample conversation)

### Use case: Interactive mode

> **You:** `/cre:post-writer`
>
> **Skill:** Asks Q1-Q5, loads context, generates draft, runs gates, outputs to assets/.
>
> **You:** Review post.txt, manually copy-paste to LinkedIn.

### Use case: From CONTEXT.md

> **You:** Explored, locked decisions in CONTEXT.md. Now: `/cre:post-writer --from-context`
>
> **Skill:** Skips Q1-Q5 (reads CONTEXT.md), goes straight to generation.
>
> **You:** Faster, decisions already documented.

### Use case: Quick mode (skip profile load)

> **You:** `/cre:post-writer Letter to Character C --character character-a --platform blog --type letter --quick`
>
> **Skill:** Doesn't reload lite profile (uses session context), faster.
>
> **You:** Good when you've already loaded context in same session.

### Use case: Batch with exploration

> **You:** Multiple posts planned. Explore once, write multiple times.
>
> **Skill:** 
> - `/cre:exploring` (Q1-Q7, lock CONTEXT.md)
> - `/cre:post-writer --from-context` (writes post 1)
> - `/cre:exploring --reset` (explore new topic, new CONTEXT.md)
> - `/cre:post-writer --from-context` (writes post 2)
>
> **You:** Batch workflow, all decisions documented.

## 5. Important caveats

- **Stale voice gate mandatory:** If materials integrated > PSY last refresh, voice is out-of-sync with profile. Run `cre:voice-audit --character <name>` to check drift severity.
- **Gates can fail:** Evidence FAIL (T4-T5 claim) or privacy FAIL (leak detected) blocks output. Fix and re-run; don't force through.
- **CONTEXT.md is optional:** Interactive mode works standalone. But exploration first = better decisions (documented in CONTEXT.md).
- **Post.txt is copy-paste ready:** post.md is markdown; post.txt is plain text for direct platform paste. Use post.txt.
- **Image prompts are advisory:** Image generation is out-of-scope; script outputs prompts for external tool (e.g., Midjourney, Replicate).

## See also

- [`SKILL.md`](./SKILL.md) for technical contract
- `cre:exploring` — structured exploration (produces CONTEXT.md)
- `cre:prompt-leverage` — called internally (5 strengthening layers)
- `cre:evidence-scanner`, `cre:voice-audit`, `cre:privacy-guard` — mandatory gates
- `cre:multiplatform` — 1→N generation (uses post-writer internally per platform)
- Rule 03 (content pipeline), Rule 09 (confidentiality), Rule 14 (CRE evidence)
