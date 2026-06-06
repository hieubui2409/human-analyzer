# orc:agent-memory — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

Imagine you have three specialized domain agents (psychologist, content-strategist, growth-analyst) working on your character profiles. Each learns insights from their work—which character defense mechanisms trigger under stress, which writing hooks land best on LinkedIn, how competencies evolve. Without memory, each session starts from scratch. With memory, they build on what they've learned. This skill manages that shared learning layer.

## 2. Core concepts (the mental model)

**Three agents, one memory per agent.** Each agent has a memory file (`.claude/agent-memory/{agent-name}.md`) containing:
- **Character Insights:** Domain-specific calibrations learned about each character (e.g., "Character B's avoidance intensifies under academic pressure" for the psychologist).
- **Patterns Learned:** Cross-session accumulated patterns (e.g., "LinkedIn vulnerability-hook + resolution structure works").
- **Anti-Patterns:** What didn't work, so agents avoid repeating it.
- **Instinct-Promoted Patterns:** High-confidence learnings promoted from the instinct store by `orc:dream`.

**Why this matters:** Agents can read their memory at the start of work and adjust behavior based on what's worked before. They append findings at the end. Over time, memory grows richer and more reliable.

## 3. Learning path

**First run:** `--show` — see if memory exists and what's in it. Likely empty on first session.

**Second run (if seeding):** `--seed` — initialize from current profiles and high-confidence instincts. This "primes" the memory with what's already known.

**Ongoing:** Agents naturally read/append. You don't invoke this skill constantly—just when you need to inspect or reset memory.

**Periodic consolidation:** If memory feels scattered, `orc:dream` merges overlapping insights and promotes strong patterns into agent memory.

## 4. Use cases (each = a sample conversation)

### Use case: View what the psychologist has learned about Character B

> You: "Show me what the psychologist agent knows about Character B"
>
> Skill: Reads `.claude/agent-memory/psychologist.md`, extracts insights about Character B (e.g., attachment patterns, defense triggers), and displays them with instinct stats. You see calibration that shapes how future PSY work handles her.

### Use case: Seed memory after major profile updates

> You: "The profiles are now complete. Seed all agent memories from them."
>
> Skill: Reads each character's formulation.md (for psychologist), writing-voice.md (for content-strategist), career-path.md (for growth-analyst), plus high-confidence instincts. Populates agent memory with initial character insights and patterns. Next session, agents start informed.

### Use case: Reset memory to clear inconsistencies

> You: "Agent memory has contradictions. Reset and back it up."
>
> Skill: Archives current memory to `.claude/agent-memory/.archive/{date}/`, writes fresh templates, and confirms. Agents now start with blank slate; instinct store survives (separate system).

### Use case: Check instinct-relevant data for the content-strategist

> You: "What instincts are relevant to the content-strategist's work?"
>
> Skill: Filters instincts by agent category (writing, audience), shows those with confidence scores, and highlights promotion candidates (insights ready to promote into agent memory).

## 5. Important caveats

- **Memory is additive, not auto-correcting.** If an agent records something wrong, it stays until manually pruned. The `orc:dream` skill handles cleanup; use `--reset` for hard reset.
- **Instincts are separate.** Agent memory is the curated, domain-specific layer. Instincts are the evolving, scored layer. Both feed learning, but they have different purposes.
- **Agents must decide to use it.** This skill doesn't auto-trigger. Agents need to be designed to read memory before work and append after. It's a tool available to them, not a mandatory gate.
- **Three agents only.** Memory is scoped to the three hardcoded domain agents (psychologist, content-strategist, growth-analyst). Other agents don't have memory files here.
