# psy:arc-tracker — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

Three months ago, you ran `psy:hypothesis` on Character C: "If Character C gets the Scholarship X scholarship, he'll feel validated but then doubt himself." Now it's three months later. Did Character C actually get the scholarship? If so, did he feel validated and then doubt, as predicted? This skill reads his current profile, extracts growth signals, and compares them to the hypothesis prediction from three months ago. Score: prediction accuracy 85%. It also tracks: Is Character C's "earn scholarship" milestone marked ACHIEVED? Is his coping getting healthier or more avoidant? Trajectory: GROWTH or PLATEAU?

## 2. Core concepts (the mental model)

- **Trajectory extraction**: Reads psychological indicators (coping mechanisms evolving, crisis patterns, protective factors, timeline events). Classifies as GROWTH (positive shift), PLATEAU (stable), REGRESSION (negative shift).
- **Milestone tracking**: Compares `milestones.md` against actual timeline. Are milestones on schedule? Missed?
- **Hypothesis comparison**: If you have a past prediction, this skill diffs it against current profile. Did the prediction come true? Score accuracy.
- **Confidence levels**: Based on data richness. Full evidence = HIGH. Sparse profile = LOW confidence.

## 3. Learning path

**Growth trajectory:** `psy:arc-tracker --character character-c --trajectory` — assess current growth stage.

**Milestone review:** `psy:arc-tracker --character character-a --milestones` — check progress on planned milestones.

**Hypothesis validation:** `psy:arc-tracker --character character-b --compare 2026-03-15` — did March prediction hold?

**Full report:** `psy:arc-tracker --character hều --trajectory --milestones --report` — comprehensive.

## 4. Use cases (each = a sample conversation)

### Use case: Growth trajectory check

> You: "Where is Character A in his arc right now?"
> Skill: `psy:arc-tracker --character character-a --trajectory`
> → Indicators: coping mechanisms more adaptive (sublimation, humor consistently healthy). Crisis patterns: gambling crisis resolved, no new acute episodes. Protective factors: mentoring relationships strengthened. Trajectory: GROWTH (confidence: HIGH). Growth stage: "Recovery + re-engagement with mentoring."

### Use case: Milestone review

> You: "Did Character C hit the milestones we set?"
> Skill: `psy:arc-tracker --character character-c --milestones`
> → Milestone: "Pass Scholarship X interview" (Mar 2025) → ACHIEVED ✓ (evidence: timeline). "Get scholarship decision" (Jun 2025) → IN_PROGRESS (expected 2 weeks). "Begin studies" (Sep 2025) → NOT_STARTED (placeholder). Projection: 2/3 on track.

### Use case: Hypothesis validation

> You: "Three months ago I predicted Character B would spiral if his father called. Did it happen?"
> Skill: `psy:arc-tracker --character character-b --compare 2026-03-01`
> → Prediction: father contact → emotional destabilization → drinking escalation. Actual: father did contact (timeline entry), Character B coped through mentoring (Character A support). Prediction accuracy: 40% (expected spiral, got adaptation). Insight: protection from Character A changed outcome.

## 5. Important caveats

- **Trajectory is observational, not prescriptive**: GROWTH doesn't mean "cured." Plateau isn't failure. Regression might be necessary (processing trauma requires some regression).
- **Milestones vs reality drift**: A milestone might be outdated (set 1 year ago, conditions changed). Manual review needed.
- **Hypothesis comparison needs explicit prediction**: If you don't have a saved psy:hypothesis report, `--compare` won't work. Store predictions with dates.
- **Sparse profiles = low confidence**: If psychology/formulation.md has 10 lines, growth signals are thin. High-confidence trajectory needs rich profile.
- **Growth is contextual**: A character might show GROWTH in emotional regulation but REGRESSION in academic engagement. The skill assesses overall, but you read nuances.
