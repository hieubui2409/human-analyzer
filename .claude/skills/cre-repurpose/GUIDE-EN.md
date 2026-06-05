# cre:repurpose — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

You published a LinkedIn post about Nhân vật A's mentoring journey. It did well. Now you want to reach Twitter (thread format) and Instagram audiences. Instead of rewriting from scratch 3 times, you feed this skill the LinkedIn post → it extracts the core message → adapts to Twitter (280-char segments, quotable), then separately adapts to Instagram (caption format, hashtags, emoji). Each adaptation respects the source's evidence and voice. Difference from `cre:multiplatform`: this works post-publish (1→1), multiplatform is generation-time (1→N native from a concept).

## 2. Core concepts (the mental model)

**Adaptation vs. Generation:**

- `cre:multiplatform`: "Here's an angle. Generate 5 natives from scratch — one per platform."
- `cre:repurpose`: "Here's a published post. Adapt it to another platform."

**Adaptation workflow:**

1. **Read source** content (post.md from file or latest from platform)
2. **Extract core message** — the essence (story, insight, call-to-action)
3. **Adapt**: adjust for target platform's structure, length, tone, hook model (LinkedIn → Twitter is very different)
4. **Validate**: privacy-guard (leak?), voice-audit (voice drift?), evidence preserved
5. **Output**: standard 5-file package to `assets/{target-platform}/`

**Platform adaptation rules** live in `.claude/scripts/platform_lib/platform_constraints.py` (same module as `cre:multiplatform` — DRY, no duplication).

## 3. Learning path

**First run:** Find a published post, adapt it:
```bash
/cre:repurpose --from assets/linkedin/260526-mentorship --to twitter --character hieu
```
Reads LinkedIn post → extracts core message ("mentoring builds trust through consistency") → adapts to Twitter thread format (280-char segments, quotable) → runs gates → outputs to assets/twitter/{slug}/.

**As you grow:** Try `--tone override` to shift tone for target platform (e.g., LinkedIn is professional; TikTok adaptation should be conversational).

**Standard flow:** Write post on primary platform → `cre:post-writer` → publish → repurpose to 2-3 secondary platforms sequentially.

## 4. Use cases (each = a sample conversation)

### Use case: LinkedIn to TikTok

> **You:** "I published a LinkedIn post. Now adapt it for TikTok."
>
> **Skill:** `--from assets/linkedin/260526-mentorship --to tiktok --character hieu` → reads LinkedIn → extracts story → adapts to TikTok script (9:16, <60s, hook within 3s, conversational).
>
> **Skill:** Runs privacy-guard + voice-audit → outputs assets/tiktok/{slug}/.
>
> **You:** Review, maybe tweak, then post to TikTok.

### Use case: Blog to Twitter

> **You:** "I have a long-form blog post. Turn it into a Twitter thread."
>
> **Skill:** `--from assets/blog/260526-growth-journey --to twitter` → extracts key insights → formats as thread (5-8 tweets, each <280 chars, logically sequenced).
>
> **You:** Post thread to Twitter.

### Use case: Batch repurposing

> **You:** "Adapt the LinkedIn post to Facebook, Instagram, and Twitter (3 invocations)."
>
> **Skill:** 
> - `--from assets/linkedin/260526-post --to facebook`
> - `--from assets/linkedin/260526-post --to instagram`
> - `--from assets/linkedin/260526-post --to twitter`
>
> **You:** 3 outputs, each adapted to platform norms.

### Use case: Tone override

> **You:** "LinkedIn post is analytical. For TikTok, make it more vulnerable and conversational."
>
> **Skill:** `--from assets/linkedin/260526-post --to tiktok --tone vulnerable-conversational`
>
> **Skill:** Adapts structure + shifts tone → outputs adapted TikTok script.

## 5. Important caveats

- **Core message preservation:** Adapted content must maintain the source's evidence tier and clinical accuracy. No oversimplification that creates misinformation.
- **One invocation = one output:** Each call generates one target platform. For N platforms, invoke N times (or use `cre:multiplatform` for 1→N generation).
- **Gates can block:** If privacy-guard flags a leak or voice-audit detects drift, adaptation is held. Investigate and fix source.
- **Evidence tier integrity:** If source used T1 evidence, adapted version must not downgrade to T5 speculation.
- **Privacy threshold differs by platform:** Blog is permissive; LinkedIn is strict. Same content may PASS on blog, FAIL on LinkedIn.

## See also

- [`SKILL.md`](./SKILL.md) for technical contract
- `cre:multiplatform` — 1→N native generation (generation-time, not post-publish)
- `cre:post-writer` — single-platform creation
- `cre:evidence-scanner`, `cre:voice-audit`, `cre:privacy-guard` — validation gates
- Rule 03 (content pipeline), Rule 14 (CRE events)
