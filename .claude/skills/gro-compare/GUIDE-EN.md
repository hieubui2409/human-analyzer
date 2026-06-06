# gro:compare — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

You have 3 character profiles and want to understand **how they differ and relate.** Are they at the same career stage? Do their learning styles complement or clash? Who mentors whom? This skill side-by-side compares career stage, skill distribution, learning style (Kolb), and mentoring networks across all characters. Useful for understanding dyad dynamics, team composition, or narrative tension.

## 2. Core concepts (the mental model)

**Script-gathers, LLM judges.** The Python script reads all 4 GRO files per character (career-path, competencies, learning-profile, mentoring-map) and extracts comparable dimensions. The LLM then generates insights:

1. **Career stage differential:** Who is in Growth vs Exploration vs Establishment? Age spread?
2. **Skill distribution:** Does one character have all the hard skills, another soft skills? Overlaps?
3. **Learning style compatibility:** Kolb styles (Diverging, Assimilating, Converging, Accommodating) — do they learn the same way or differently?
4. **Mentoring network:** Who are primary mentors? Cross-mentoring? Isolation risk?

**Non-invasive.** Read-only; no events emitted; purely informational.

## 3. Learning path

**First run:** `gro:compare --dimension all` — see all 4 dimensions. Scan for obvious contrasts.

**Next:** `gro:compare --dimension career` — focus on career stage only. Identify who is junior, mid, senior.

**Deepen:** `gro:compare --dimension learning` — Kolb styles. Notice if everyone is Diverging (all brainstormers) or mixed (some practical, some reflective).

**As you grow:** `gro:compare --json` for programmatic feeds; `--dimension mentoring` to understand knowledge-transfer patterns.

## 4. Use cases (each = a sample conversation)

### Use case: Understand dyad complementarity for content

> **You:** "gro:compare --dimension competency --json | jq '.characters | map(.top_skills)'"
>
> **Skill:** Extracts top skills per character. Character A has technical depth, Character B has communication strength, Character C has management experience.
>
> **Use:** You see complementary strengths. In a dyad, they could mentor each other (Character A teaches Character B technical, Character B teaches Character A communication). Useful for mentoring-content angles.

### Use case: Spot learning-style mismatches for collaboration

> **You:** "gro:compare --dimension learning"
>
> **Skill:** Character A = Converging (practical, problem-solving). Character B = Diverging (imaginative, emotional). Character C = Assimilating (logical, theory).
>
> **Use:** If they work together, expect friction: Character A wants to solve now, Character B wants to brainstorm options, Character C wants to understand the pattern. Useful for conflict angles or team-dynamics storytelling.

## 5. Important caveats

- **Surface-level only.** This skill flags differences; deep dyad/triad analysis requires reading the profiles directly.
- **Kolb styles are heuristic.** The learning-profile skill (and this comparison) rely on heuristic LLM judgment; not a validated test.
- **No PSY comparison.** This skill compares GRO dimensions only. For psychological comparison (attachment patterns, defense mechanisms, trauma overlap), use `psy:profile-compare`.
- **Mentoring network is static.** Reflects the current mentoring-map, not hypothetical future mentoring relationships.
