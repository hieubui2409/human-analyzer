# orc:compounding — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

Every session teaches you something. Which character defense mechanisms trigger under stress? Which writing hooks land best on LinkedIn? What mentoring approach works for which character? Without capturing those learnings, you repeat the same trial-and-error each session. Compounding locks in what you've learned, so future sessions inherit that knowledge.

## 2. Core concepts (the mental model)

**Learning categories:** Psychology (character insights), Writing (what hooks work), Audience (engagement patterns), Clinical (theory application), Growth (competency evolution), Process (workflow efficiency).

**From scattered notes to durable memory:** Git diffs show what changed. Session state shows what was touched. Compounding extracts learning from those signals and writes it to project memory and the instinct store.

**Reinforcement over time:** If you observe the same pattern twice, compounding reinforces it, raising confidence. Eventually, patterns promoted to agent memory (for domain agents to use).

## 3. Learning path

**First run:** `orc:compounding --session` — after completing work, extract learnings interactively. Pick which to save.

**Auto mode:** `orc:compounding --auto` — extract all candidates, write automatically. Use when you're confident in the extraction.

**Character focus:** `orc:compounding --character hiếu` — extract learnings about one character only.

**Content patterns:** `orc:compounding --content` — focus on writing/engagement patterns from recent posts.

## 4. Use cases (each = a sample conversation)

### Use case: Extract psychology insights after profile update

> You: "I just updated Nhân vật B's formulation. Extract learnings about her."
>
> Skill: Reads formulation.md, defense-mechanisms.md, relationships/family.md. Finds: "Nhân vật B's avoidance intensifies under academic pressure" (psychology). Offers to save to memory. You confirm. Memory updated for next session.

### Use case: Capture writing patterns after content creation

> You: "I wrote three LinkedIn posts this session. What patterns worked?"
>
> Skill: Reads posts, compares against writing-voice.md. Extracts: "Vulnerability hook + resolution structure gets engagement" (writing pattern). Also notes: "Nhân vật A voice best when personal + actionable" (audience pattern). You review and save.

### Use case: Auto-extract at session end

> You: "Session wrap-up. Compound everything automatically."
>
> Skill: Runs --auto, extracts all candidate learnings from git diffs + session state, writes to memory without asking. Summary printed showing what was captured.

## 5. Important caveats

- **Extraction is heuristic.** Compounding suggests learnings based on what changed, but it can't judge significance. Review suggestions before saving.
- **Memory is additive.** If you extract the same pattern twice, it gets reinforced (confidence rises). But contradictions aren't auto-resolved; manual review needed.
- **Instincts decay over time.** High-confidence instincts stay strong, low-confidence ones decay. `orc:dream` handles lifecycle.
- **Context matters.** A pattern that worked once may not work again if context changed. Learnings are observations, not laws.
