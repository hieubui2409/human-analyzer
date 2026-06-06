# gro:career-path — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

You're building a character profile and want to understand their **career coherence.** Where did they start? What decisions shaped them? Are they on a stable trajectory or at an inflection point? This skill gathers their factual career history, timeline, and key decisions, then analyzes them through two frameworks: **Super's Life-Career Rainbow** (stages: Growth, Exploration, Establishment, Maintenance, Disengagement) and **SCCT** (Social Cognitive Career Theory — self-efficacy, outcome expectations, personal goals). It surfaces decision quality, risk factors, and growth opportunities.

## 2. Core concepts (the mental model)

**Script-gathers, LLM judges.** The Python script extracts career data (role history, dates, salary if available, key decisions). The LLM then applies two judgment lenses:

1. **Super's Life-Career Rainbow:** identifies which stage the character is in now (age, role stability, exploration markers tell the story). Age + role pattern → stage.
2. **SCCT self-efficacy:** evaluates confidence in career choices (did they take on stretch roles? pivot decisively? avoid risk?). Evidence comes from decision patterns and outcomes.

**Script is deterministic; LLM is heuristic.** The script finds data; the LLM judges patterns (e.g., "this person makes bold decisions with moderate confidence" vs "conservative, high-doubt pattern").

## 3. Learning path

**First run:** `gro:career-path --character <name>` — see the career timeline and decision summary. Notice the career stage assessment.

**Next:** `gro:career-path --all` — compare all 3 characters' stages side-by-side. One might be in Establishment, another in Exploration.

**Deepen:** `gro:career-path --decisions-only` — focus only on key career decisions (role changes, education, pivots). See decision rationale, outcome, and what it reveals about decision-making patterns.

**As you grow:** `gro:career-path --json` for programmatic feeds into downstream skills (competency-map, career-forecast).

## 4. Use cases (each = a sample conversation)

### Use case: Understand a character's current career stage

> **You:** "gro:career-path --character character-a"
>
> **Skill:** Gathers Character A's role history (education → first job → current role), dates, and context. LLM assesses: age 28, 5 years in role, recent certifications, no major pivots → Likely in **Establishment stage** (committed to role, building expertise). Risk factors: narrow skill breadth. Growth opportunity: lateral moves in related domains.
>
> **Use:** You now know Character A's career maturity level. Useful for understanding mentoring needs, competency gaps, or story arcs (stable vs turbulent).

### Use case: Analyze decision-making patterns

> **You:** "gro:career-path --character character-c --decisions-only"
>
> **Skill:** Extracts 4–5 major career decisions (e.g., "left startup to join corporate", "pursued certification", "negotiated promotion"). For each, LLM scores evidence quality, outcome (success/neutral/setback), and what it reveals about risk tolerance and confidence.
>
> **Use:** See if a character is risk-averse, opportunistic, deliberate, or scattered. Useful for predicting future behavior or developing character motivation.

## 5. Important caveats

- **Self-efficacy is heuristic.** The LLM infers confidence from decision patterns and outcomes; it's educated guessing, not a validated psych test.
- **No PSY-domain analysis.** Career-path analyzes career decisions and stage, not psychological drivers (attachment, defense, trauma, etc.). If you need "why did they make that choice psychologically?", use PSY domain.
- **Boundary (Rule 15):** Reads from PSY (e.g., growth-edges for context) but never makes PSY judgments or cross-writes into PSY files.
- **Evidence quality matters.** The analysis is as good as the data in growth/career-path.md. Missing dates, vague decisions, or stale data degrade accuracy.
