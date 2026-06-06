# gro:competency-map — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

You're asking: **What can this character actually do, and how well?** This skill inventories all skills from growth/competencies.md and rates each on the **Dreyfus 7-level scale** (Novice → Advanced Beginner → Competent → Proficient → Expert → Master → Practical Wisdom). It surfaces strengths (Level 4+), gaps (Level 1–2), and opportunities. Useful for understanding character capability, mentoring needs, or story plausibility.

## 2. Core concepts (the mental model)

**Script-gathers, LLM judges.** The Python script extracts skill names, Dreyfus levels (from competencies.md), and evidence (achievements, materials, career history). The LLM then assesses:

1. **Dreyfus level credibility:** Is Level 5 (Expert) evidence-backed? Or over-claimed?
2. **Skill distribution:** Does the character have deep expertise in one domain, shallow in many, or balanced?
3. **Growth trajectory:** Are gaps recent (fixable) or chronic (structural)?

**Evidence matters.** A skill rated Level 3 (Competent) with no evidence markers is flagged; one with achievement citations is credible.

## 3. Learning path

**First run:** `gro:competency-map --character <name>` — see all skills and their Dreyfus levels. Scan the strengths (4+) and gaps (1–2) sections.

**Next:** `gro:competency-map --gaps-only` — focus on weak areas. What would a character need to learn to advance?

**Deepen:** `gro:competency-map --character <name> --json` — programmatic access for downstream analysis (learning-profile, career-forecast).

**As you grow:** Compare across characters (`gro:compare --dimension competency`) to spot complementary strengths.

## 4. Use cases (each = a sample conversation)

### Use case: Assess readiness for a career move

> **You:** "gro:competency-map --character character-a"
>
> **Skill:** Extracts all of Character A's skills. Finds: Technical domain at Level 4–5 (Expert). Project management at Level 2 (Advanced Beginner). Communication at Level 3 (Competent).
>
> **Use:** Character A is ready to lead a technical project but would struggle managing cross-functional teams. Useful for narrative tension (ambitious promotion, growth edge) or mentoring angle (needs communication coaching).

### Use case: Identify growth opportunities for content

> **You:** "gro:competency-map --all --gaps-only"
>
> **Skill:** Returns Level 1–2 skills across all 3 characters. All three are weak in Data Analysis. Character B and Character C lack Public Speaking.
>
> **Use:** Spot common growth themes (collective learning arc, peer mentoring opportunity) or individual gaps (Character B fears public speaking — psychological angle).

## 5. Important caveats

- **Dreyfus levels are heuristic.** The LLM judges level from evidence; this is educated guessing, not a validated skill test.
- **Evidence quality drives accuracy.** If competencies.md lists "Python" with no details, confidence is low. Details (projects, certifications, years) raise confidence.
- **Skill definition varies.** "Project Management" to one character might be "task coordination" to another. LLM tries to normalize but may mis-categorize.
- **No learning-barrier analysis.** If a gap exists, this skill flags it but doesn't explain why (psychological barriers, learning style mismatch, external constraints). Use PSY domain for that.
