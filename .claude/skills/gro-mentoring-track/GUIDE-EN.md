# gro:mentoring-track — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

You want to understand **how a character is supported in their growth.** Who are their mentors? What do mentors provide? Are there gaps (e.g., career sponsorship but no role models)? This skill analyzes mentoring relationships using **Kram's Developmental Networks framework**, which distinguishes two types of support: **Career functions** (sponsorship, coaching, exposure) and **Psychosocial functions** (friendship, acceptance, role model). Useful for understanding resilience, support systems, isolation risk, or mentoring-content angles.

## 2. Core concepts (the mental model)

**Script-gathers, LLM judges.** The Python script extracts mentoring data (mentor names, relationships, frequency, roles, functions provided). The LLM then assesses:

1. **Career functions:** Does this character have a sponsor (advocate in senior positions)? A coach (skill-building)? Exposure (opportunities)?
2. **Psychosocial functions:** Do they have acceptance (unconditional support)? A role model (inspiring figure)? Friendship (peer support)?
3. **Network diversity:** Are mentors from different backgrounds, industries, demographics? Or all similar?
4. **Dependency risk:** Is there over-reliance on one mentor? Isolation if that mentor leaves?

**Kram's insight:** Well-developed professionals usually need mentors from diverse sources, not one all-purpose mentor.

## 3. Learning path

**First run:** `gro:mentoring-track --character <name>` — see mentoring relationships and Kram function assessment. Notice which functions are strong/weak.

**Next:** `gro:mentoring-track --all` — compare mentoring networks across all 3 characters. Who has the strongest support? Most isolated?

**Deepen:** Cross-reference with `gro:career-path` — does career trajectory match mentoring support? (e.g., someone in Establishment stage should have diverse mentors; someone in Exploration might rely on one coach).

**As you grow:** Combine with `gro:compare --dimension mentoring` to see mentoring cross-connections (e.g., "Character A mentors Character B in technical skills; Character B mentors Character A in communication").

## 4. Use cases (each = a sample conversation)

### Use case: Assess mentoring support for career advancement

> **You:** "gro:mentoring-track --character character-a"
>
> **Skill:** Extracts Character A's mentoring relationships. Finds: Primary mentor provides coaching (skill-building) and friendship (emotional support). Secondary mentor is in senior role (sponsorship potential). No role model or peer supporters (gap).
>
> **Use:** Character A has good coaching but lacks visible role models and peer network. Career progression might stall without exposure and advocacy. Useful for storytelling (mentoring-gap as obstacle) or growth angle (building peer support).

### Use case: Spot mentoring interconnections for dyad content

> **You:** "gro:mentoring-track --all"
>
> **Skill:** Finds that Character A mentors Character B (coaching), Character B mentors Character C (acceptance/friendship), Character C advises Character A (sponsorship). Forms a triangle.
>
> **Use:** They form a mentoring ecosystem where each provides different functions to others. Useful for group dynamics, mutual-support narratives, or systemic resilience content.

## 5. Important caveats

- **Kram framework is heuristic.** The LLM infers which functions each mentor provides; this is educated interpretation, not validated data.
- **Network diversity is self-reported.** Assessment relies on mentoring-map data; if the data is sparse or vague, diversity scoring is unreliable.
- **No psychosocial depth.** This skill assesses whether psychosocial support exists (role model, friendship), not quality or authenticity. For relationship psychology, use PSY domain.
- **Mentoring is dynamic.** The output reflects current mentoring-map; real mentoring relationships evolve. Outdated data = outdated analysis.
- **Boundary (Rule 15):** This skill reads family context from identity/core.md but does not make attachment or trauma assessments — those are PSY domain.
