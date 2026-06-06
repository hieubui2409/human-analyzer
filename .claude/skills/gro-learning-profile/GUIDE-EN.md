# gro:learning-profile — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

You want to understand **how a character learns best.** Do they brainstorm (Diverging), analyze (Assimilating), solve problems (Converging), or jump in and do (Accommodating)? This skill profiles learning style using **Kolb's Experiential Learning Cycle** — a framework that maps how people prefer to gather information (Concrete Experience vs Abstract Conceptualization) and process it (Reflective Observation vs Active Experimentation). Useful for understanding character development patterns, content personalization, or team dynamics.

## 2. Core concepts (the mental model)

**Script-gathers, LLM judges.** The Python script extracts learning data (study methods, educational background, knowledge-acquisition patterns from growth/learning-profile.md and materials). The LLM then assigns a dominant Kolb style:

1. **Diverging (CE + RO):** imaginative, emotional, brainstormers; prefer reflection, group discussion
2. **Assimilating (AC + RO):** logical, analytical, theory-builders; prefer lectures, reading, models
3. **Converging (AC + AE):** practical, problem-solvers, technical focus; prefer experimentation, hands-on
4. **Accommodating (CE + AE):** hands-on, risk-takers, doers; prefer real-world projects, trying first

**Most people are mixed.** The LLM identifies dominant + secondary styles, then notes cycle gaps (e.g., "strong in Concrete Experience but weak in Reflective Observation").

## 3. Learning path

**First run:** `gro:learning-profile --character <name>` — see dominant Kolb style and cycle strengths/gaps. Scan "Content Style Implications" for personalization hints.

**Next:** `gro:learning-profile --all` — compare learning styles across all 3 characters. Who learns the same way? Who diverges?

**Deepen:** Cross-reference with `gro:competency-map --gaps-only` — if someone has a skill gap, does their learning style explain it? (e.g., Converging learner might struggle with theory-heavy skills).

**As you grow:** Use Kolb style to frame CRE content for each character (Diverging characters → open-ended prompts; Assimilating → research-backed explanations; Converging → step-by-step problem-solving; Accommodating → real-world scenarios).

## 4. Use cases (each = a sample conversation)

### Use case: Personalize content for a character's learning style

> **You:** "gro:learning-profile --character character-b"
>
> **Skill:** Finds Character B is Diverging (imaginative, reflective). Loves brainstorming, dislikes rigid procedures. Cycle gap: weak in Active Experimentation (doesn't jump to action easily).
>
> **Use:** Frame content for Character B as open-ended exploration (not prescriptive steps). Use emotional hooks, diverse perspectives. Avoid "just do it" language. Useful for CRE personalization or mentoring approach.

### Use case: Spot learning-style mismatch for conflict

> **You:** "gro:learning-profile --all"
>
> **Skill:** Character A = Converging (practical, problem-solving). Character B = Diverging (imaginative, reflective). Character C = Assimilating (analytical).
>
> **Use:** If they collaborate on learning (e.g., onboarding), expect friction: Character A wants to solve fast, Character B wants to explore options, Character C wants to understand the system. Useful for conflict storytelling or team-dynamics content.

## 5. Important caveats

- **Kolb is preference, not ability.** A Diverging learner can do hands-on work; they just prefer not to. Useful for understanding comfort zones, not limitations.
- **Kolb classification is heuristic.** The LLM infers style from learning data; not a validated test. Consider it a working hypothesis, not fact.
- **Cycle gaps may reflect context, not style.** If someone shows weak Active Experimentation, it might be learning-style gap OR lack of opportunity (job didn't allow hands-on). LLM tries to distinguish but may miss context.
- **No PSY-domain inference.** Learning style is cognitive preference; it does NOT explain psychological barriers (anxiety, trauma, attachment). Use PSY domain for that.
