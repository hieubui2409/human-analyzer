# gro:milestone-tracker — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

You want to **track a character's career progress against their own goals.** Did they achieve that promotion by 30? Is the degree still in progress? Are they behind, on-track, or ahead? This skill tracks milestones — achieved, planned, and missed — from milestones.md and career-path.md. It surfaces completion rate, on-track status, next expected milestone, and whether progression matches career stage expectations. Useful for assessing character arc plausibility, motivation clarity, or narrative tension (goal-delay, overachievement).

## 2. Core concepts (the mental model)

**Script-gathers, LLM judges.** The Python script extracts milestone entries (name, target date, achieved date or status). The LLM then assesses:

1. **Completion rate:** How many milestones achieved vs planned?
2. **On-track assessment:** Are achieved milestones hitting target dates, or are they clustered early/late?
3. **Career-stage fit:** For someone in Exploration (age 20s–30s), are milestones education/exploration focused? For Establishment (30s–40s), are they role/family focused?
4. **Next milestone:** Given achieved milestones, what's the logical next step?

**Evidence-grounded.** LLM compares milestones.md (planned) against identity/achievements.md (verified achieved) to spot aspirational vs real progress.

## 3. Learning path

**First run:** `gro:milestone-tracker --character <name>` — see full timeline (achieved, planned, missed). Notice the completion rate and on-track status.

**Next:** `gro:milestone-tracker --all --pending-only` — focus on planned milestones across all 3 characters. See who has ambitious timelines vs conservative.

**Deepen:** Cross-reference with `gro:career-path --character <name>` — does milestone timeline match career trajectory? (e.g., someone in Establishment should have achieved core education milestones by now).

**As you grow:** Use milestone data to assess character motivation (driven vs aimless) or story tension (missing deadlines, overachievement, pivoted goals).

## 4. Use cases (each = a sample conversation)

### Use case: Assess career progression coherence

> **You:** "gro:milestone-tracker --character character-b"
>
> **Skill:** Extracts Character B's milestones. Finds: Education milestones achieved on-time. Early career promotion ahead of schedule. Recent mentoring goal still pending. Overall: 70% completion, ahead in career milestones, behind in personal-development ones.
>
> **Use:** Character B prioritizes career over personal growth. Useful for character motivation angle (ambitious but unbalanced) or story setup (pressure to pivot toward mentoring/giving-back).

### Use case: Spot milestone clusters for narrative tension

> **You:** "gro:milestone-tracker --all"
>
> **Skill:** Character A has tight timeline (milestones 6–12 months apart). Character B has loose timeline (1–2 years apart). Character C has stalled progression (2+ years between last two milestones).
>
> **Use:** Character A has high-pressure momentum (risk of burnout). Character B is methodical (lower stress, slower growth). Character C may be blocked (motivation check needed). Useful for group dynamics or individual character arcs.

## 5. Important caveats

- **Milestone timing is self-reported.** Accuracy depends on milestones.md and achievements.md; stale or vague data = unreliable assessment.
- **On-track is binary.** The skill flags milestones as achieved/pending/missed; it doesn't score "almost there" or "close call."
- **No causal analysis.** If a milestone is missed, this skill flags it but doesn't explain why (external blockers, personal priority shift, capacity issue). Use PSY or context review for that.
- **Next milestone is speculative.** The LLM suggests logical next steps, but real life diverges (new opportunities, life events). Treat it as a working hypothesis.
- **Boundary (Rule 15):** This skill tracks GRO milestones only (career, education, competency). It does not track psychological milestones (healing, attachment development, etc.) — those belong in PSY domain.
