# cre:exploring — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

You have a vague idea: "I want to write something about Nhân vật A's mentoring." This skill asks you 7 focused questions — one per turn — that lock down every decision you need *before* you start writing. By the end, you have a CONTEXT.md that tells `cre:post-writer` exactly who, what, where, how, and why. No surprises mid-draft.

## 2. Core concepts (the mental model)

**Sequential decision-locking:**

Each question builds on the last. You can't pick a "tone" before picking a "platform" (TikTok tone ≠ LinkedIn tone). The skill guides you through a dependency chain:

1. **Character** (who?)
2. **Content type** (post / article / profile update / arc?)
3. **Angle** (suggested from profile data matching your character choice)
4. **Platform** (LinkedIn / TikTok / Blog etc. — informs tone choices)
5. **Tone** (raw / reflective / analytical / inspirational — platform-aware)
6. **Clinical framing** (if psychological content, ground in theory?)
7. **Constraints** (real names to avoid, sensitive topics, timeline accuracy needs)

**Output:** CONTEXT.md with all decisions locked. Feeds `cre:post-writer --from-context` (skip interactive, go straight to writing).

## 3. Learning path

**First run:**
```bash
/cre:exploring My mentorship journey with Nhân vật C
```
Start with a topic. The skill asks Q1 (character) — answer Nhân vật A. Q2 (type) — answer "LinkedIn post". Q3 (angle) — pick from profile-derived suggestions. And so on. At the end, you have a CONTEXT.md.

**As you grow:** Try `--resume` to pick up from your last exploration (same file). If you want to re-answer Q3 but keep Q1-Q2, the skill keeps your prior answers and asks "Q3 again?"

**Standard flow:** Explore → lock decisions → `cre:post-writer --from-context` → write immediately.

## 4. Use cases (each = a sample conversation)

### Use case: Content from scratch

> **You:** `/cre:exploring`
>
> **Skill:** Q1: Which character? → You: Nhân vật B. Q2: Content type? → You: Facebook post. Q3: Angle? (suggests 3 from profile). → You: "Nhân vật B's resilience in hardship". Q4-Q7: platform → tone → clinical → constraints.
>
> **Skill:** Writes CONTEXT.md, confirms decisions, ready for `cre:post-writer --from-context`.

### Use case: Refine a discovered angle

> **You:** `cre:angle-discovery --character hieu --top 1` returned one angle.
>
> **Skill:** `cre:exploring --from-context` (hypothetically if angle was output as CONTEXT). Or copy the angle title → `/cre:exploring {angle title}`.
>
> **Skill:** Asks Q2+ (Q1 inferred). You refine platform, tone, clinical frame. Updated CONTEXT.md.

### Use case: Resume interrupted exploration

> **You:** Started exploring, answered Q1-Q3, didn't finish.
>
> **Skill:** `/cre:exploring --resume` → reads last CONTEXT.md → "You answered Q1-Q3. Q4?" (resumes from where you left off).

### Use case: Cross-character relationship content

> **You:** `/cre:exploring relationship dynamic between Nhân vật A and Nhân vật C`
>
> **Skill:** Q1: Select "Cross-character" → Q2: Select "Relationship arc development" → Q3: Suggests angles from `docs/graph/{dyad}.md` → Q4-Q7.

## 5. Important caveats

- **One question per turn:** Don't answer all at once. The skill waits for your answer before moving on.
- **Locked decisions:** Once you answer Q5 (tone), you can't go back to Q2 without `--reset`. `--resume` picks up where you left off.
- **Profile-derived angles:** Q3 suggestions come from actual profile data (timeline events, growth-edges, relationships). Not random.
- **No content writing:** This skill outputs CONTEXT.md. Actual content is written by `cre:post-writer`.
- **Constraints are optional:** If Q7 (constraints) you answer "none", that's OK. But think about real names, sensitive topics.

## See also

- [`SKILL.md`](./SKILL.md) for technical contract
- `cre:post-writer --from-context` — consumes the CONTEXT.md
- `cre:prompt-leverage` — strengthens the context before writing
- `cre:angle-discovery` — autonomous angle mining (feeds exploration)
- Rule 03 (content pipeline), Rule 09 (confidentiality)
